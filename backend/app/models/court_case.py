from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, JSON, Index,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
from app.models.database import Base


class CourtCase(Base):
    __tablename__ = "court_cases"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    case_number = Column(String(64), unique=True, nullable=False, comment="案号")
    title = Column(String(255), nullable=False, comment="案件标题")
    dispute_type = Column(String(32), nullable=False, index=True, comment="纠纷类型")
    court_name = Column(String(128), nullable=True, comment="审理法院")
    province = Column(String(32), nullable=True, index=True, comment="省份")
    city = Column(String(64), nullable=True, index=True, comment="城市")
    trial_date = Column(Date, nullable=True, comment="审理日期")
    case_level = Column(String(16), nullable=True, comment="审理级别：一审/二审/再审")

    plaintiff = Column(String(128), nullable=True, comment="原告")
    defendant = Column(String(128), nullable=True, comment="被告")
    third_party = Column(String(128), nullable=True, comment="第三人")

    facts = Column(LONGTEXT, nullable=False, comment="案件事实")
    claims = Column(Text, nullable=True, comment="原告诉讼请求")
    defense = Column(Text, nullable=True, comment="被告答辩")
    judgment_reason = Column(LONGTEXT, nullable=True, comment="裁判理由")
    judgment_result = Column(LONGTEXT, nullable=True, comment="裁判结果")
    applicable_laws = Column(JSON, nullable=True, comment="适用法条列表 JSON")

    key_factors = Column(JSON, nullable=True, comment="核心要素三元组 JSON")
    amount_involved = Column(String(64), nullable=True, comment="涉案金额区间")
    has_written_evidence = Column(String(8), nullable=True, comment="是否有书面证据：有/无/部分")
    limitation_period = Column(String(16), nullable=True, comment="诉讼时效：已过/未过/待查")

    tags = Column(JSON, nullable=True, comment="标签 JSON 数组")
    summary = Column(Text, nullable=True, comment="案情摘要（供前端展示）")

    created_at = Column(DateTime, default=datetime.utcnow, comment="入库时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    __table_args__ = (
        Index("idx_dispute_amount", "dispute_type", "amount_involved"),
        {"comment": "法院判例卷宗库"},
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "case_number": self.case_number,
            "title": self.title,
            "dispute_type": self.dispute_type,
            "court_name": self.court_name,
            "province": self.province,
            "city": self.city,
            "trial_date": self.trial_date.isoformat() if self.trial_date else None,
            "case_level": self.case_level,
            "plaintiff": self.plaintiff,
            "defendant": self.defendant,
            "facts": self.facts,
            "claims": self.claims,
            "judgment_result": self.judgment_result,
            "applicable_laws": self.applicable_laws,
            "key_factors": self.key_factors,
            "amount_involved": self.amount_involved,
            "has_written_evidence": self.has_written_evidence,
            "limitation_period": self.limitation_period,
            "tags": self.tags,
            "summary": self.summary,
        }
