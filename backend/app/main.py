from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.routers import consulting, laws
from app.rag.milvus_store import milvus_service

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 法律咨询系统 - 基于 RAG 的中国法律智能助手",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(consulting.router)
app.include_router(laws.router)


@app.on_event("startup")
async def startup_event():
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        milvus_service.connect()
        milvus_service.create_collection(drop_existing=False)
        stats = milvus_service.get_stats()
        logger.info(f"Milvus 状态: {stats}")
    except Exception as e:
        logger.warning(f"启动时 Milvus 初始化失败（不影响启动）: {e}")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常捕获: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "error_type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
