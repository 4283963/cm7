import json
import re
from typing import Optional, Dict, Any
from app.schemas.chat import CaseInfo, CaseKeyFactors
from app.services.llm_service import llm_service
from app.core.logging import logger


EXTRACTION_PROMPT = """你是中国法律援助中心的法律要素提取专家。请从以下案情描述中，严格按 JSON 格式提取核心要素三元组。

【输出要求 - 必须输出合法 JSON，禁止输出任何其他内容】
{
  "dispute_type": "字符串，二级案由如：民间借贷、劳动合同、房屋租赁、离婚财产、交通事故人身损害等；不确定则为 null",
  "amount_involved": "字符串，涉案金额或金额区间，如'5万'、'5万-10万'、'不足1万'、'100万以上'；无法判断则为 null",
  "has_written_evidence": "字符串，只能是'有'、'无'、'部分'三选一；如有借条、合同、欠条、转账记录、聊天记录、证人证言等算'有'，不确定则为'部分'",
  "limitation_period": "字符串，只能是'已过'、'未过'、'待查'三选一；诉讼时效一般为3年，根据案情中提供的时间判断，无时间信息则为'待查'",
  "party_relationship": "字符串，当事人关系，如'朋友'、'同事'、'夫妻'、'房东-租客'、'用人单位-员工'、'陌生人'等；不确定则为 null",
  "location": "字符串，事件发生地，如'北京市朝阳区'、'上海市'；只有省份也可，不确定则为 null",
  "extra_factors": {
    "其他任意有用要素的键值对，如: 是否有担保、责任划分比例、伤残等级、违约方是哪一方等，没有可留空对象 {}"
  }
}

【案情信息】
纠纷类型：{dispute_type}
事件时间：{incident_time}
发生地点：{incident_location}
当事人信息：{parties}
案情详情：{details}
当事人最新补充：{latest_message}

请只输出 JSON，不要任何 Markdown 代码块标记或解释文字。"""


class KeyFactorExtractor:

    @staticmethod
    def _parse_amount(text: str) -> Optional[str]:
        if not text:
            return None
        patterns = [
            r"(\d+(?:\.\d+)?)\s*万?\s*[元块]",
            r"(\d+(?:\.\d+)?)\s*万",
            r"人民币\s*(\d+)",
            r"(\d+)\s*元",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                val = float(m.group(1))
                if "万" in m.group(0):
                    val = val * 10000
                if val < 10000:
                    return "不足1万"
                elif val < 50000:
                    return "1万-5万"
                elif val < 100000:
                    return "5万-10万"
                elif val < 500000:
                    return "10万-50万"
                elif val < 1000000:
                    return "50万-100万"
                else:
                    return "100万以上"
        return None

    @staticmethod
    def _parse_evidence(text: str) -> Optional[str]:
        if not text:
            return None
        positive_kw = ["借条", "欠条", "合同", "协议", "转账记录", "银行流水", "聊天记录",
                        "录音", "收据", "发票", "邮件", "证人", "证据", "签字", "盖章", "截图"]
        partial_kw = ["可能有", "应该有", "记得有", "好像有"]
        text_lower = text
        if any(k in text_lower for k in partial_kw):
            return "部分"
        if any(k in text_lower for k in positive_kw):
            return "有"
        if any(k in text_lower for k in ["没有证据", "无证据", "没证据", "没打欠条", "没签合同"]):
            return "无"
        return None

    @staticmethod
    def _fallback_extract(case_info: CaseInfo, latest_msg: str) -> CaseKeyFactors:
        combined = f"{case_info.details or ''} {case_info.parties or ''} {latest_msg}"
        return CaseKeyFactors(
            dispute_type=case_info.dispute_type.value if case_info.dispute_type else None,
            amount_involved=KeyFactorExtractor._parse_amount(combined),
            has_written_evidence=KeyFactorExtractor._parse_evidence(combined),
            limitation_period="待查",
            party_relationship=None,
            location=case_info.incident_location,
            extra_factors={},
        )

    @staticmethod
    def _strip_json(text: str) -> str:
        if not text:
            return "{}"
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= 0 and end > start:
            return text[start:end + 1]
        return "{}"

    @classmethod
    def extract(cls, case_info: CaseInfo, latest_message: str) -> CaseKeyFactors:
        has_llm = any([
            llm_service._provider and not isinstance(llm_service._provider, type) and
            "MockProvider" not in type(llm_service._provider).__name__
            for _ in [1]
        ])

        combined_text = f"{case_info.details or ''} {case_info.parties or ''} {latest_message}"
        if not combined_text.strip():
            return cls._fallback_extract(case_info, latest_message)

        try:
            provider_type = type(llm_service._get_provider()).__name__
        except Exception:
            provider_type = "MockProvider"

        if provider_type == "MockProvider":
            logger.info("使用 Mock LLM，启用规则引擎回退提取要素")
            return cls._fallback_extract(case_info, latest_message)

        prompt = EXTRACTION_PROMPT.format(
            dispute_type=case_info.dispute_type.value if case_info.dispute_type else "待识别",
            incident_time=case_info.incident_time or "未提供",
            incident_location=case_info.incident_location or "未提供",
            parties=case_info.parties or "未提供",
            details=case_info.details or "未提供",
            latest_message=latest_message,
        )

        try:
            raw = llm_service.chat(
                [
                    {"role": "system", "content": "你是严谨的法律要素提取器，只输出 JSON。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
            )
            json_text = cls._strip_json(raw)
            data: Dict[str, Any] = json.loads(json_text)

            factors = CaseKeyFactors(
                dispute_type=data.get("dispute_type") or (
                    case_info.dispute_type.value if case_info.dispute_type else None
                ),
                amount_involved=data.get("amount_involved") or cls._parse_amount(combined_text),
                has_written_evidence=data.get("has_written_evidence") or cls._parse_evidence(combined_text) or "部分",
                limitation_period=data.get("limitation_period") or "待查",
                party_relationship=data.get("party_relationship"),
                location=data.get("location") or case_info.incident_location,
                extra_factors=data.get("extra_factors") or {},
            )
            logger.info(f"要素提取(LLM): {factors.model_dump()}")
            return factors
        except Exception as e:
            logger.warning(f"LLM 要素提取失败，回退规则引擎: {e}")
            return cls._fallback_extract(case_info, latest_message)


key_factor_extractor = KeyFactorExtractor()
