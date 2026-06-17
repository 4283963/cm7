import re
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.core.logging import logger


@dataclass
class SafetyCheckResult:
    is_safe: bool
    risk_type: Optional[str] = None
    risk_level: int = 0
    matched_keywords: List[str] = field(default_factory=list)
    sanitized_text: Optional[str] = None
    message: str = "内容安全"


class SafetyGuardService:
    PROMPT_INJECTION_PATTERNS: List[Tuple[str, str, int]] = [
        ("role_hijack", r"(?:忽略|无视|忘掉|跳过|暂停|停止|解除|删除|重置).{0,20}(?:之前的|以上的|上述的|前面的|系统的|所有的).{0,20}(?:指令|规则|设定|设置|prompt|prompt|角色|身份|限制)", 3),
        ("role_hijack", r"(?:现在起|从现在开始|假设|假装|扮演|想象你是|你现在是|你其实是|换个身份|作为).{0,30}(?:不再是|不是|不要做|别做|而非|而不是).{0,20}(?:法律|律师|ai|助手|咨询)", 3),
        ("role_hijack", r"(?:扮演|假设|假装|你是|你现在是|作为|充当).{0,30}(?:黑客|入侵者|破解者|攻击者|罪犯|骗子|小偷|毒贩|走私犯|人贩子)", 4),
        ("bypass_rag", r"(?:不要|别|不需要|不用|跳过|忽略).{0,15}(?:检索|查找|搜索|引用|使用|参考|根据).{0,15}(?:法条|法律|上下文|资料|数据库)", 3),
        ("bypass_rag", r"(?:直接|自由|随意|不受限制|独立).{0,10}(?:回答|生成|输出|创作).{0,10}(?:不需要|不用|无需).{0,10}(?:检索|搜索|引用|查找)", 3),
        ("reveal_system", r"(?:请|给我|告诉我|输出|显示|打印|泄露|透露).{0,10}(?:系统提示|system prompt|系统指令|初始指令|隐藏指令|prompt原文|你的设定|你的规则|内部指令)", 3),
        ("reveal_system", r"(?:重复|复述|翻译|总结).{0,15}(?:上面的|之前的|最初的|系统的|所有的).{0,10}(?:内容|文字|指令|prompt)", 2),
        ("markup_injection", r"(?:```|~~~|<\?|<%|;--|javascript:|data:text/html)", 2),
        ("multi_turn_attack", r"(?:完成以上任务后|回答完后|之后|接下来|然后|与此同时).{0,20}(?:请你|帮我|告诉我|回答).{0,30}(?:忽略|无视|忘记|改变).{0,15}(?:规则|身份|限制)", 3),
    ]

    ILLEGAL_CONTENT_KEYWORDS: List[Tuple[str, List[str], int]] = [
        ("tax_evasion", [
            "偷税漏税", "逃税", "避税方法", "怎么逃税", "怎么偷税", "不报税",
            "虚开发票", "买卖发票", "做假账", "两本账", "账外账", "私户收款",
            "公转私避税", "拆分工资", "虚报成本", "费用套现",
        ], 4),
        ("fraud", [
            "诈骗方法", "怎么诈骗", "电信诈骗", "杀猪盘", "套路贷", "高利贷",
            "非法集资", "庞氏骗局", "传销模式", "刷单诈骗", "钓鱼网站",
            "伪造证件", "办假证", "刻假章", "冒充公职人员",
        ], 5),
        ("hacking", [
            "黑客技术", "入侵网站", "破解密码", "盗号方法", "DDOS攻击",
            "注入漏洞", "webshell", "提权", "内网渗透", "抓包改数据",
            "脱库", "撞库", "洗号", "盗刷", "刷钻", "外挂",
        ], 4),
        ("drugs", [
            "毒品制作", "制毒配方", "吸毒方法", "贩毒渠道", "怎么贩毒",
            "麻醉药品", "精神药品非法", "兴奋剂购买", "毒品运输", "种植毒品原植物",
        ], 5),
        ("violence", [
            "怎么杀人", "杀人方法", "报复社会", "恐怖袭击", "爆炸物制作",
            "自制武器", "枪支制造", "管制刀具售卖", "殴打技巧", "寻仇方法",
            "雇凶杀人", "买凶",
        ], 5),
        ("gambling", [
            "赌博方法", "出千技巧", "作弊方法", "赌球技巧", "百家乐赢钱",
            "老虎机破解", "网络赌博平台搭建",
        ], 3),
        ("property_crime", [
            "盗窃技巧", "怎么偷东西", "入室盗窃", "扒窃方法", "撬锁教程",
            "抢劫方法", "抢夺", "诈骗保险", "碰瓷技巧", "敲诈勒索",
        ], 5),
        ("cyber_crime", [
            "传播淫秽", "色情网站搭建", "VPN翻墙", "翻墙软件",
            "盗版资源", "破解软件", "游戏私服",
        ], 3),
        ("self_harm", [
            "自杀方法", "怎么自残", "自残教程", "厌世方法",
        ], 4),
        ("illegal_escape", [
            "怎么不被抓", "逃避侦查", "反侦察技巧", "销毁证据",
            "跑路方法", "偷渡", "洗钱方法", "资金外逃", "资产转移避查",
        ], 4),
        ("perjury", [
            "作伪证", "串供方法", "假口供", "翻供技巧", "证人收买",
        ], 4),
        ("legal_evasion", [
            "钻法律空子", "规避法律", "打法律擦边球", "合法伤害权",
            "合法报复", "恶心人不犯法",
        ], 2),
    ]

    CONTEXTUAL_LEGAL_KEYWORDS = [
        "法律", "法条", "律师", "法院", "起诉", "诉讼", "仲裁", "调解",
        "赔偿", "违约金", "合同", "劳动", "工伤", "离婚", "交通事故",
        "遗产", "继承", "侵权", "消费者", "权益", "证据", "法律援助",
    ]

    @classmethod
    def _compile_patterns(cls):
        compiled = []
        for name, pattern, level in cls.PROMPT_INJECTION_PATTERNS:
            try:
                compiled.append((name, re.compile(pattern, re.IGNORECASE | re.DOTALL), level))
            except re.error:
                logger.warning(f"正则编译失败: {pattern}")
        return compiled

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        normalized = text.lower()
        normalized = re.sub(r"\s+", "", normalized)
        normalized = normalized.replace(" ", "").replace("　", "")
        normalized = normalized.replace("你", "你").replace("您", "你")
        for ch in ["，", "。", "！", "？", "；", "：", "、", ",", ".", "!", "?", ";", ":"]:
            normalized = normalized.replace(ch, "")
        return normalized

    @classmethod
    def _check_prompt_injection(cls, text: str) -> Tuple[bool, List[str], int, List[str]]:
        normalized = cls._normalize_text(text)
        matched_types = set()
        matched_patterns = []
        max_level = 0

        for name, regex, level in cls._compile_patterns():
            if regex.search(normalized) or regex.search(text):
                matched_types.add(name)
                matched_patterns.append(name)
                max_level = max(max_level, level)

        suspicious_tokens = ["假设", "扮演", "假装", "无视", "忽略", "忘掉", "不要做法律",
                             "你是一个", "你现在是", "换个角色", "换个身份", "解除限制"]
        token_hits = [t for t in suspicious_tokens if t in text]
        if len(token_hits) >= 2:
            matched_types.add("suspicious_tokens")
            matched_patterns.extend(token_hits)
            max_level = max(max_level, 2)

        return len(matched_types) > 0, list(matched_types), max_level, matched_patterns

    @classmethod
    def _check_illegal_content(cls, text: str) -> Tuple[bool, List[str], int, List[str]]:
        matched_categories = set()
        matched_words = []
        max_level = 0

        for category, keywords, level in cls.ILLEGAL_CONTENT_KEYWORDS:
            for kw in keywords:
                if kw in text or kw in cls._normalize_text(text):
                    matched_categories.add(category)
                    matched_words.append(kw)
                    max_level = max(max_level, level)

        return len(matched_categories) > 0, list(matched_categories), max_level, matched_words

    @classmethod
    def _is_contextually_legal_query(cls, text: str) -> bool:
        hit_count = sum(1 for kw in cls.CONTEXTUAL_LEGAL_KEYWORDS if kw in text)
        return hit_count >= 1

    @classmethod
    def check_input(cls, text: str, case_info_context: Optional[str] = None) -> SafetyCheckResult:
        if not text or not text.strip():
            return SafetyCheckResult(is_safe=True, sanitized_text=text)

        has_injection, injection_types, injection_level, injection_matches = cls._check_prompt_injection(text)
        has_illegal, illegal_cats, illegal_level, illegal_words = cls._check_illegal_content(text)

        combined_matches = injection_matches + illegal_words
        combined_level = max(injection_level, illegal_level)

        if has_injection or has_illegal:
            risk_type = []
            if has_injection:
                risk_type.append(f"prompt注入({','.join(injection_types)})")
            if has_illegal:
                risk_type.append(f"违法内容({','.join(illegal_cats)})")

            if combined_level >= 4:
                logger.warning(f"[安全拦截] 高风险内容: {risk_type} | 命中: {combined_matches} | 原文: {text[:80]}...")
                return SafetyCheckResult(
                    is_safe=False,
                    risk_type="; ".join(risk_type),
                    risk_level=combined_level,
                    matched_keywords=combined_matches,
                    message="内容包含高风险违规信息，已拦截",
                )
            elif combined_level >= 2:
                if cls._is_contextually_legal_query(text) and case_info_context:
                    logger.info(f"[安全放行] 疑似诱导但结合上下文判定为法律咨询场景: {text[:60]}...")
                    return SafetyCheckResult(is_safe=True, sanitized_text=text)

                logger.warning(f"[安全警告] 中风险内容: {risk_type} | 命中: {combined_matches}")
                return SafetyCheckResult(
                    is_safe=False,
                    risk_type="; ".join(risk_type),
                    risk_level=combined_level,
                    matched_keywords=combined_matches,
                    message="内容可能存在风险，请重新规范表述",
                )

        return SafetyCheckResult(is_safe=True, sanitized_text=text)

    @classmethod
    def check_output(cls, text: str) -> SafetyCheckResult:
        if not text:
            return SafetyCheckResult(is_safe=True)

        _, illegal_cats, illegal_level, illegal_words = cls._check_illegal_content(text)

        hallucination_indicators = [
            "我将教你", "我来教你", "具体步骤", "具体方法如下", "操作步骤",
            "你可以这样做", "建议你", "推荐你", "只需要", "只要你",
        ]
        hallucination_hits = [h for h in hallucination_indicators if h in text[:500]]

        if illegal_level >= 3:
            logger.warning(f"[输出拦截] LLM 生成违法内容: {illegal_cats} | 命中: {illegal_words}")
            return SafetyCheckResult(
                is_safe=False,
                risk_type=f"违法输出({','.join(illegal_cats)})",
                risk_level=illegal_level,
                matched_keywords=illegal_words,
                message="输出内容违规",
            )

        if len(hallucination_hits) >= 3 and illegal_level >= 1:
            logger.warning(f"[输出警告] LLM 输出存在诱导性描述，结合违法关键词命中: {hallucination_hits}")
            return SafetyCheckResult(
                is_safe=False,
                risk_type="可疑越界输出",
                risk_level=2,
                matched_keywords=hallucination_hits + illegal_words,
            )

        return SafetyCheckResult(is_safe=True)

    @classmethod
    def get_safe_rejection_response(cls, result: SafetyCheckResult) -> str:
        if result.risk_type and "违法" in result.risk_type:
            return (
                "### ⚠️ 法律咨询范围提示\n\n"
                "非常抱歉，您咨询的内容涉及**违法犯罪活动**，我作为法律援助中心的AI法律顾问，"
                "**绝对不能提供任何违法活动的指导或建议**。\n\n"
                "### 📋 我可以为您提供的帮助包括：\n"
                "- 劳动合同纠纷、工资拖欠、工伤赔偿等劳动法律问题\n"
                "- 婚姻家庭、财产分割、子女抚养等民事问题\n"
                "- 合同违约、房产纠纷、交通事故赔偿等常见法律纠纷\n"
                "- 法律援助申请条件、诉讼程序等程序性咨询\n\n"
                "### ⛔ 若您或亲友正涉及违法活动，我强烈建议：\n"
                "1. **立即停止**相关行为，避免造成更严重的法律后果\n"
                "2. 主动向公安机关或相关部门自首/说明情况，争取宽大处理\n"
                "3. 拨打法律援助热线 **12348** 或前往当地法律援助中心，寻求专业执业律师的帮助\n\n"
                "法律是保护每一位公民合法权益的底线，请您遵守法律法规。"
                "如果您有正当的法律问题需要咨询，请重新描述，我会尽力为您解答。"
            )
        else:
            return (
                "### ⚠️ 输入内容安全提示\n\n"
                "我注意到您的表述中可能包含了尝试改变我身份设定或越界咨询的内容。"
                "作为**法律援助中心的官方AI法律顾问**，我的职责是严格基于中国现行法律法规，"
                "为您提供合法合规的法律咨询建议。\n\n"
                "### 📌 我的服务边界：\n"
                "- ✅ 解答各类民事、劳动、婚姻、合同等**合法法律问题**\n"
                "- ✅ 基于真实法条进行分析（所有引用均来自官方检索数据库）\n"
                "- ✅ 引导您通过合法途径维权\n"
                "- ❌ **不提供任何违法活动的指导或建议**\n"
                "- ❌ **不能改变身份设定或脱离法律范畴回答问题**\n\n"
                "如果您有合法的法律问题需要咨询，请**直接描述您的纠纷情况**（例如：公司拖欠工资、交通事故赔偿等），"
                "我会通过引导式提问帮您梳理案情并提供专业分析。\n\n"
                "如有紧急法律需求，可拨打法律援助热线：**12348**。"
            )


safety_guard_service = SafetyGuardService()
