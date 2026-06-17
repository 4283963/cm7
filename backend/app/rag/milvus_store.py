from typing import List, Dict, Any, Optional
from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    MilvusException,
)
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.rag.embedding import embedding_service
from app.schemas.chat import RetrievedLaw, LawInsertRequest


class MilvusService:
    _instance = None
    _collection: Optional[Collection] = None
    _connected: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def connect(cls) -> bool:
        if cls._connected:
            return True
        try:
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
            )
            cls._connected = True
            logger.success(f"Milvus 连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            return True
        except MilvusException as e:
            logger.error(f"Milvus 连接失败: {e}")
            return False
        except Exception as e:
            logger.error(f"Milvus 连接异常: {e}")
            return False

    @classmethod
    def _get_fields(cls) -> List[FieldSchema]:
        dim = settings.MILVUS_VECTOR_DIM
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=128),
            FieldSchema(name="law_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chapter", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="article", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="law_source", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]

    @classmethod
    def create_collection(cls, drop_existing: bool = False) -> bool:
        cls.connect()
        collection_name = settings.MILVUS_COLLECTION_NAME

        try:
            if utility.has_collection(collection_name):
                if drop_existing:
                    utility.drop_collection(collection_name)
                    logger.info(f"已删除旧集合: {collection_name}")
                else:
                    logger.info(f"集合已存在: {collection_name}")
                    cls._collection = Collection(collection_name)
                    return True

            schema = CollectionSchema(
                fields=cls._get_fields(),
                description="中国法律法条向量库",
                enable_dynamic_field=True,
            )
            cls._collection = Collection(
                name=collection_name,
                schema=schema,
                using="default",
                shards_num=2,
            )

            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            }
            cls._collection.create_index(
                field_name="embedding",
                index_params=index_params,
            )
            logger.success(f"集合创建并建立索引成功: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            return False

    @classmethod
    def get_collection(cls) -> Optional[Collection]:
        if cls._collection is None:
            cls.connect()
            collection_name = settings.MILVUS_COLLECTION_NAME
            if utility.has_collection(collection_name):
                cls._collection = Collection(collection_name)
        return cls._collection

    @classmethod
    def insert_laws(cls, laws: List[LawInsertRequest]) -> Dict[str, Any]:
        collection = cls.get_collection()
        if collection is None:
            return {"success": False, "message": "集合不存在"}

        texts_to_embed = []
        for law in laws:
            combined = f"{law.title} {law.chapter or ''} {law.article} {law.content}"
            texts_to_embed.append(combined)

        logger.info(f"正在向量化 {len(texts_to_embed)} 条法条...")
        embeddings = embedding_service.encode(texts_to_embed)

        ids = []
        law_ids = []
        titles = []
        chapters = []
        articles = []
        law_sources = []
        contents = []
        embed_list = []

        for i, law in enumerate(laws):
            ids.append(f"{law.law_id}_{i}")
            law_ids.append(law.law_id)
            titles.append(law.title)
            chapters.append(law.chapter or "")
            articles.append(law.article)
            law_sources.append(law.law_source or "")
            contents.append(law.content)
            embed_list.append(embeddings[i].tolist())

        data = [ids, law_ids, titles, chapters, articles, law_sources, contents, embed_list]

        try:
            mr = collection.insert(data)
            collection.flush()
            logger.success(f"插入法条成功: 插入 {mr.insert_count} 条")
            return {
                "success": True,
                "insert_count": mr.insert_count,
                "message": f"成功插入 {mr.insert_count} 条法条",
            }
        except Exception as e:
            logger.error(f"插入法条失败: {e}")
            return {"success": False, "message": f"插入失败: {str(e)}"}

    @classmethod
    def search_laws(
        cls,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[RetrievedLaw]:
        collection = cls.get_collection()
        if collection is None:
            logger.warning("Milvus 集合不存在，返回空结果")
            return []

        top_k = top_k or settings.RAG_TOP_K
        threshold = threshold or settings.RAG_SIMILARITY_THRESHOLD

        try:
            query_embedding = embedding_service.encode(query)[0]

            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 16},
            }

            collection.load()

            results = collection.search(
                data=[query_embedding.tolist()],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=None,
                output_fields=["law_id", "title", "chapter", "article", "content", "law_source"],
            )

            retrieved = []
            if results and len(results) > 0:
                for hit in results[0]:
                    similarity = float(hit.distance)
                    if similarity < threshold:
                        continue
                    entity = hit.entity
                    retrieved.append(
                        RetrievedLaw(
                            law_id=entity.get("law_id", ""),
                            title=entity.get("title", ""),
                            chapter=entity.get("chapter") or None,
                            article=entity.get("article", ""),
                            content=entity.get("content", ""),
                            similarity=similarity,
                            law_source=entity.get("law_source") or None,
                        )
                    )

            logger.info(f"法条检索完成: 命中 {len(retrieved)} 条 (阈值={threshold})")
            return retrieved
        except Exception as e:
            logger.error(f"法条检索失败: {e}")
            return []

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        collection = cls.get_collection()
        if collection is None:
            return {"exists": False}
        try:
            collection.load()
            return {
                "exists": True,
                "count": collection.num_entities,
                "name": settings.MILVUS_COLLECTION_NAME,
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}


milvus_service = MilvusService()
