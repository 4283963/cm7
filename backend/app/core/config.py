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

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "legal_aid"
    MYSQL_CHARSET: str = "utf8mb4"

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
    SIMILAR_CASE_TOP_K: int = 3

    @property
    def MYSQL_DSN(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset={self.MYSQL_CHARSET}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
