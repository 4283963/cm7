from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, List
import json
from app.schemas.chat import LawInsertRequest, BatchLawInsertRequest, RetrievedLaw
from app.rag.milvus_store import milvus_service
from app.core.logging import logger

router = APIRouter(prefix="/api/laws", tags=["法条管理"])


@router.post("/insert", response_model=Dict[str, Any])
async def insert_law(law: LawInsertRequest) -> Dict[str, Any]:
    try:
        result = milvus_service.insert_laws([law])
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message", "插入失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"插入单条法条失败: {e}")
        raise HTTPException(status_code=500, detail=f"插入失败: {str(e)}")


@router.post("/batch-insert", response_model=Dict[str, Any])
async def batch_insert_laws(batch: BatchLawInsertRequest) -> Dict[str, Any]:
    try:
        if not batch.laws:
            raise HTTPException(status_code=400, detail="法条列表不能为空")
        result = milvus_service.insert_laws(batch.laws)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message", "批量插入失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量插入法条失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量插入失败: {str(e)}")


@router.post("/init-collection", response_model=Dict[str, Any])
async def init_collection(drop_existing: bool = False) -> Dict[str, Any]:
    try:
        success = milvus_service.create_collection(drop_existing=drop_existing)
        if not success:
            raise HTTPException(status_code=500, detail="集合初始化失败")
        return {"success": True, "message": "集合初始化成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"初始化集合失败: {e}")
        raise HTTPException(status_code=500, detail=f"初始化失败: {str(e)}")


@router.get("/search", response_model=List[RetrievedLaw])
async def search_laws(query: str, top_k: int = 5) -> List[RetrievedLaw]:
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="查询内容不能为空")
        return milvus_service.search_laws(query, top_k=top_k)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检索法条失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_laws_stats() -> Dict[str, Any]:
    try:
        return milvus_service.get_stats()
    except Exception as e:
        logger.error(f"获取法条统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-json", response_model=Dict[str, Any])
async def import_laws_from_json(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict) and "laws" in data:
            laws_data = data["laws"]
        elif isinstance(data, list):
            laws_data = data
        else:
            raise HTTPException(status_code=400, detail="JSON 格式错误")

        laws = []
        for item in laws_data:
            try:
                laws.append(LawInsertRequest(**item))
            except Exception as e:
                logger.warning(f"跳过格式错误的法条: {item.get('law_id', 'unknown')}, 错误: {e}")

        if not laws:
            raise HTTPException(status_code=400, detail="没有有效的法条数据")

        result = milvus_service.insert_laws(laws)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))

        result["total_parsed"] = len(laws_data)
        result["valid_count"] = len(laws)
        return result
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON 解析失败: {str(e)}")
    except Exception as e:
        logger.error(f"导入 JSON 法条失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
