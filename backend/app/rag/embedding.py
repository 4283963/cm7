import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_model(cls):
        if cls._model is None:
            logger.info(f"正在加载 Embedding 模型: {settings.EMBEDDING_MODEL_NAME}")
            try:
                cls._model = SentenceTransformer(
                    settings.EMBEDDING_MODEL_NAME,
                    device=settings.EMBEDDING_DEVICE,
                )
                logger.success(f"Embedding 模型加载成功: {settings.EMBEDDING_MODEL_NAME}")
            except Exception as e:
                logger.error(f"Embedding 模型加载失败: {e}")
                raise
        return cls._model

    @classmethod
    def encode(cls, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        model = cls.get_model()
        if isinstance(texts, str):
            texts = [texts]
        embeddings = model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype("float32")

    @classmethod
    def get_dimension(cls) -> int:
        return settings.MILVUS_VECTOR_DIM


embedding_service = EmbeddingService()
