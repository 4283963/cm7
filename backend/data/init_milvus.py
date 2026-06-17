import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.milvus_store import milvus_service
from app.schemas.chat import LawInsertRequest
from app.core.logging import logger


SEED_FILE = Path(__file__).parent / "seed_laws.json"


def load_seed_data(drop_existing: bool = False):
    logger.info(f"开始初始化 Milvus 法条向量库，种子文件: {SEED_FILE}")

    if not SEED_FILE.exists():
        logger.error(f"种子文件不存在: {SEED_FILE}")
        return False

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    laws_data = data.get("laws", []) if isinstance(data, dict) else data
    if not laws_data:
        logger.error("种子文件为空")
        return False

    logger.info(f"解析到 {len(laws_data)} 条法条记录")

    if not milvus_service.connect():
        logger.error("Milvus 连接失败")
        return False

    if not milvus_service.create_collection(drop_existing=drop_existing):
        logger.error("集合创建失败")
        return False

    laws = []
    for item in laws_data:
        try:
            laws.append(LawInsertRequest(**item))
        except Exception as e:
            logger.warning(f"跳过无效法条 {item.get('law_id', 'unknown')}: {e}")

    logger.info(f"有效法条 {len(laws)} 条，开始向量化并插入...")

    batch_size = 50
    total_inserted = 0
    for i in range(0, len(laws), batch_size):
        batch = laws[i:i + batch_size]
        result = milvus_service.insert_laws(batch)
        if result.get("success"):
            total_inserted += result.get("insert_count", 0)
            logger.info(f"批次插入进度: {min(i + batch_size, len(laws))}/{len(laws)}, 累计插入: {total_inserted}")
        else:
            logger.error(f"批次插入失败: {result.get('message')}")

    stats = milvus_service.get_stats()
    logger.success(f"初始化完成！当前集合法条总数: {stats.get('count', 'N/A')}")
    logger.info(f"集合名称: {stats.get('name')}")
    return True


if __name__ == "__main__":
    drop = "--drop" in sys.argv
    if drop:
        logger.warning("使用 --drop 参数，将删除旧集合后重建！")
    success = load_seed_data(drop_existing=drop)
    sys.exit(0 if success else 1)
