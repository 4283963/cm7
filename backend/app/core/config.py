from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI法律咨询系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    MILVUS_COLLECTION_NAME: str = "chinese_laws"
    MILVUS_VECTOR_DIM: int = 768

    EMBEDDING_MODEL_NAME: str = "shibing624/text2vec-base-chinese"
    EMBEDDING_DEVICE: str = "cpu"

    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
