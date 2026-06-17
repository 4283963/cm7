from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    LawInsertRequest,
    BatchLawInsertRequest,
)
from app.services.consulting_service import legal_consulting_service
from app.rag.milvus_store import milvus_service
from app.core.logging import logger

router = APIRouter(prefix="/api/consulting", tags=["法律咨询"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        return await legal_consulting_service.process_chat(request)
    except Exception as e:
        logger.error(f"咨询接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"咨询服务内部错误: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    milvus_stats = milvus_service.get_stats()
    return {
        "status": "ok",
        "service": "AI法律咨询系统",
        "milvus": milvus_stats,
    }
