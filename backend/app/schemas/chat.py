from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class DisputeType(str, Enum):
    LABOR = "劳动纠纷"
    CONTRACT = "合同纠纷"
    PROPERTY = "房产纠纷"
    MARRIAGE = "婚姻家庭"
    INHERITANCE = "继承纠纷"
    TORT = "侵权纠纷"
    TRAFFIC = "交通事故"
    CRIMINAL = "刑事案件"
    ADMINISTRATIVE = "行政纠纷"
    OTHER = "其他纠纷"


class GuideStep(str, Enum):
    GREETING = "greeting"
    DISPUTE_TYPE = "dispute_type"
    TIME = "time"
    LOCATION = "location"
    DETAILS = "details"
    PARTIES = "parties"
    COMPLETED = "completed"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class CaseInfo(BaseModel):
    dispute_type: Optional[DisputeType] = None
    incident_time: Optional[str] = None
    incident_location: Optional[str] = None
    parties: Optional[str] = None
    details: Optional[str] = None
    evidence: Optional[str] = None
    demands: Optional[str] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GuideQuestion(BaseModel):
    step: GuideStep
    question: str
    options: Optional[List[str]] = None
    required: bool = True


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一标识")
    user_message: str
    case_info: Optional[CaseInfo] = None
    history: List[Message] = Field(default_factory=list)


class RetrievedLaw(BaseModel):
    law_id: str
    title: str
    chapter: Optional[str] = None
    article: str
    content: str
    similarity: float
    law_source: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    guide_next: Optional[GuideQuestion] = None
    case_info: CaseInfo
    retrieved_laws: List[RetrievedLaw] = Field(default_factory=list)
    is_completed: bool = False
    references: List[str] = Field(default_factory=list)


class LawInsertRequest(BaseModel):
    law_id: str
    title: str
    chapter: Optional[str] = None
    article: str
    content: str
    law_source: Optional[str] = None
    tags: Optional[List[str]] = None


class BatchLawInsertRequest(BaseModel):
    laws: List[LawInsertRequest]
