import re
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
from app.core.config import settings
from app.core.logging import logger
from app.schemas.chat import CaseKeyFactors, SimilarCase
from app.models.court_case import CourtCase
from app.models.database import get_session_local


WEIGHTS = {
    "dispute_type": 0.30,
    "amount_involved": 0.20,
    "has_written_evidence": 0.15,
    "limitation_period": 0.10,
    "location": 0.10,
    "text_similarity": 0.15,
}


class SimilarCaseService:

    @staticmethod
    def _score_text(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        a_clean = re.sub(r"\s+", "", a)
        b_clean = re.sub(r"\s+", "", b)
        if not a_clean or not b_clean:
            return 0.0
        return SequenceMatcher(None, a_clean[:200], b_clean[:200]).ratio()

    @staticmethod
    def _score_dispute_type(target: Optional[str], case_val: Optional[str]) -> float:
        if not target or not case_val:
            return 0.3
        if target == case_val:
            return 1.0
        short_map = {
            "劳动": "劳动纠纷", "劳动争议": "劳动纠纷", "劳动合同": "劳动纠纷",
            "借款": "合同纠纷", "借贷": "合同纠纷", "欠款": "合同纠纷",
            "房屋": "房产纠纷", "房产": "房产纠纷", "租赁": "合同纠纷",
            "离婚": "婚姻家庭", "婚姻": "婚姻家庭", "抚养": "婚姻家庭",
            "继承": "继承纠纷", "遗产": "继承纠纷",
            "交通": "交通事故", "车祸": "交通事故",
            "侵权": "侵权纠纷", "伤害": "侵权纠纷",
            "刑事": "刑事案件",
            "行政": "行政纠纷",
        }
        t_norm = short_map.get(target, target)
        c_norm = short_map.get(case_val, case_val)
        if t_norm == c_norm:
            return 0.8
        if any(k in case_val for k in [target[:2]] if len(target) >= 2):
            return 0.6
        return 0.2

    @staticmethod
    def _score_amount(target: Optional[str], case_val: Optional[str]) -> float:
        if not target or not case_val:
            return 0.3
        if target == case_val:
            return 1.0
        order = ["不足1万", "1万-5万", "5万-10万", "10万-50万", "50万-100万", "100万以上"]
        try:
            ti = order.index(target)
            ci = order.index(case_val)
            diff = abs(ti - ci)
            if diff == 0:
                return 1.0
            elif diff == 1:
                return 0.7
            elif diff == 2:
                return 0.4
            else:
                return 0.1
        except ValueError:
            return SimilarCaseService._score_text(target, case_val)

    @staticmethod
    def _score_evidence(target: Optional[str], case_val: Optional[str]) -> float:
        if not target or not case_val:
            return 0.3
        if target.startswith(case_val[:1]) or case_val.startswith(target[:1]):
            return 1.0
        if target[:1] == "部" and case_val[:1] == "有":
            return 0.6
        if case_val[:1] == "部" and target[:1] == "有":
            return 0.6
        return 0.2

    @staticmethod
    def _score_limitation(target: Optional[str], case_val: Optional[str]) -> float:
        if not target or not case_val:
            return 0.3
        if target == case_val:
            return 1.0
        if target == "待查" or case_val == "待查":
            return 0.5
        return 0.1

    @staticmethod
    def _score_location(target: Optional[str], case_val: Optional[str]) -> float:
        if not target or not case_val:
            return 0.2
        if target in case_val or case_val in target:
            return 1.0
        t_province = target[:2] if len(target) >= 2 else target
        c_province = case_val[:2] if len(case_val) >= 2 else case_val
        if t_province == c_province:
            return 0.6
        return 0.1

    @classmethod
    def compute_similarity(
        cls,
        factors: CaseKeyFactors,
        case_row: CourtCase,
        query_text: str,
    ) -> Tuple[float, Dict[str, float]]:
        case_dict = case_row.to_dict()
        scores: Dict[str, float] = {}
        scores["dispute_type"] = cls._score_dispute_type(
            factors.dispute_type, case_dict.get("dispute_type")
        )
        scores["amount_involved"] = cls._score_amount(
            factors.amount_involved, case_dict.get("amount_involved")
        )
        scores["has_written_evidence"] = cls._score_evidence(
            factors.has_written_evidence, case_dict.get("has_written_evidence")
        )
        scores["limitation_period"] = cls._score_limitation(
            factors.limitation_period, case_dict.get("limitation_period")
        )
        scores["location"] = cls._score_location(
            factors.location, case_dict.get("province") or case_dict.get("city")
        )
        facts = case_dict.get("facts") or case_dict.get("summary") or ""
        scores["text_similarity"] = cls._score_text(query_text, facts)

        total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        return round(total, 4), scores

    @classmethod
    def search_similar_cases(
        cls,
        factors: CaseKeyFactors,
        query_text: str,
        top_k: Optional[int] = None,
    ) -> List[SimilarCase]:
        top_k = top_k or settings.SIMILAR_CASE_TOP_K
        db: Session = get_session_local()()
        try:
            query = db.query(CourtCase)
            if factors.dispute_type:
                like = f"%{factors.dispute_type[:2]}%"
                query = query.filter(
                    (CourtCase.dispute_type == factors.dispute_type) |
                    (CourtCase.dispute_type.like(like))
                )
            candidates = query.limit(100).all()
            logger.info(f"判例候选集: {len(candidates)} 条")

            scored: List[Tuple[float, Dict[str, float], CourtCase]] = []
            for row in candidates:
                score, detail = cls.compute_similarity(factors, row, query_text)
                if score >= 0.35:
                    scored.append((score, detail, row))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_rows = scored[:top_k]

            results: List[SimilarCase] = []
            for score, detail, row in top_rows:
                row_dict = row.to_dict()
                results.append(SimilarCase(
                    **row_dict,
                    similarity_score=score,
                ))
                logger.info(
                    f"相似判例: {row_dict['case_number']} | 得分={score:.3f} | "
                    f"分项={ {k: round(v,2) for k,v in detail.items()} }"
                )

            return results
        except Exception as e:
            logger.error(f"判例检索失败: {e}")
            return []
        finally:
            db.close()


similar_case_service = SimilarCaseService()
