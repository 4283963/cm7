from typing import List, Tuple
from app.schemas.chat import CaseInfo, RetrievedLaw, Message, MessageRole


SYSTEM_PROMPT_TEMPLATE = """你是中国法律援助中心的专业AI法律顾问，执业资格号：AI-LAW-2024-CN。请严格按照以下规则提供法律咨询服务：

【身份定位】
- 你是熟悉中华人民共和国现行法律法规的资深律师
- 回答必须基于检索到的真实法条，禁止编造法律条文
- 如检索法条不足以回答问题，必须如实告知，不得臆造

【核心铁则】
1. 所有法律引用必须来源于下方【检索法条上下文】部分，原文引用并标注来源
2. 不得引用、编造上下文以外的任何法条内容
3. 如法条与案情无关，不得强行套用
4. 涉及刑事/重大风险时，必须明确建议当事人立即寻求线下律师协助
5. 咨询意见仅作参考，不构成正式法律文书或执业代理关系

【回答结构要求】
请按以下结构输出回答：
### 一、案情归纳
简要归纳当事人提供的案件信息（2-3句话）

### 二、法律分析
结合检索法条进行逐条分析，每一条法律分析需明确：
- 适用法条名称及条款号
- 法条原文引用（引号括起来）
- 结合案情的具体分析

### 三、结论与建议
- 明确法律结论
- 给出可执行的具体建议（步骤、注意事项）
- 需准备的证据清单
- 建议的维权途径（协商/调解/仲裁/诉讼等）

### 四、免责声明
本咨询意见仅供参考，具体案件请咨询执业律师或法律援助中心。

【检索法条上下文（必须仅以此为法律依据）】
{retrieved_laws_section}

【当前已收集案情（多维结构化）】
{structured_case_info}
"""


class PromptBuilder:

    @staticmethod
    def _format_retrieved_laws(laws: List[RetrievedLaw]) -> str:
        if not laws:
            return "⚠️ 未检索到匹配的法条，回答时需如实告知当事人并建议线下咨询。"

        sections = []
        for i, law in enumerate(laws, 1):
            similarity_pct = round(law.similarity * 100, 1)
            header = f"【法条{i}】《{law.title}》{law.chapter or ''} {law.article}（相似度: {similarity_pct}%）"
            if law.law_source:
                header += f" [{law.law_source}]"
            content = f"内容：\"{law.content}\""
            sections.append(f"{header}\n{content}")
        return "\n\n".join(sections)

    @staticmethod
    def _format_structured_case(case_info: CaseInfo) -> str:
        fields = []
        label_map = {
            "dispute_type": "纠纷类型",
            "incident_time": "事件时间",
            "incident_location": "发生地点",
            "parties": "当事人关系",
            "details": "案情细节",
            "evidence": "现有证据",
            "demands": "当事人诉求",
        }

        if case_info.dispute_type:
            fields.append(f"- {label_map['dispute_type']}：{case_info.dispute_type.value}")
        if case_info.incident_time:
            fields.append(f"- {label_map['incident_time']}：{case_info.incident_time}")
        if case_info.incident_location:
            fields.append(f"- {label_map['incident_location']}：{case_info.incident_location}")
        if case_info.parties:
            fields.append(f"- {label_map['parties']}：{case_info.parties}")
        if case_info.details:
            fields.append(f"- {label_map['details']}：{case_info.details}")
        if case_info.evidence:
            fields.append(f"- {label_map['evidence']}：{case_info.evidence}")
        if case_info.demands:
            fields.append(f"- {label_map['demands']}：{case_info.demands}")

        if not fields:
            return "（案情信息收集中，请回答AI的引导问题以完善信息）"
        return "\n".join(fields)

    @classmethod
    def build_system_prompt(
        cls,
        case_info: CaseInfo,
        retrieved_laws: List[RetrievedLaw],
    ) -> str:
        laws_section = cls._format_retrieved_laws(retrieved_laws)
        case_section = cls._format_structured_case(case_info)
        return SYSTEM_PROMPT_TEMPLATE.format(
            retrieved_laws_section=laws_section,
            structured_case_info=case_section,
        )

    @staticmethod
    def build_case_summary_query(case_info: CaseInfo, user_message: str) -> str:
        parts = []
        if case_info.dispute_type:
            parts.append(f"纠纷类型：{case_info.dispute_type.value}")
        if case_info.incident_time:
            parts.append(f"时间：{case_info.incident_time}")
        if case_info.incident_location:
            parts.append(f"地点：{case_info.incident_location}")
        if case_info.parties:
            parts.append(f"当事人：{case_info.parties}")
        if case_info.details:
            parts.append(f"详情：{case_info.details}")
        parts.append(f"最新补充：{user_message}")
        return "；".join(parts)

    @classmethod
    def build_messages(
        cls,
        case_info: CaseInfo,
        retrieved_laws: List[RetrievedLaw],
        history: List[Message],
        current_user_message: str,
        is_completed: bool,
    ) -> List[dict]:
        system_prompt = cls.build_system_prompt(case_info, retrieved_laws)
        messages = [{"role": "system", "content": system_prompt}]

        if not is_completed:
            intro_msg = (
                "目前还在收集案情信息阶段。请以引导式语气回答当事人，"
                "同时继续追问引导问题以完善案情。回答要简洁友好，"
                "不要在信息不全时给出过于具体的法律结论。"
            )
            messages.append({"role": "system", "content": intro_msg})

        for msg in history:
            role = "assistant" if msg.role == MessageRole.ASSISTANT else "user"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": current_user_message})
        return messages


prompt_builder = PromptBuilder()
