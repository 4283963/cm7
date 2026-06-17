import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.court_case import CourtCase
from app.core.config import settings
from app.core.logging import logger

SEED_FILE = Path(__file__).parent / "seed_cases.json"


def init_database_and_user():
    server_dsn = (
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/?charset={settings.MYSQL_CHARSET}"
    )
    try:
        engine = create_engine(server_dsn)
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()
        logger.success(f"数据库 `{settings.MYSQL_DATABASE}` 确保已创建")
        engine.dispose()
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")


def seed_cases(truncate: bool = False):
    if not SEED_FILE.exists():
        logger.error(f"判例种子文件不存在: {SEED_FILE}")
        return False

    init_database_and_user()

    from app.models.database import get_engine, get_session_local, init_db

    engine = get_engine()
    init_db()

    Session = get_session_local()
    db = Session()
    try:
        if truncate:
            db.query(CourtCase).delete()
            db.commit()
            logger.warning("已清空判例表")

        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cases = data.get("cases", [])
        logger.info(f"解析到 {len(cases)} 条判例")

        for item in cases:
            existing = db.query(CourtCase).filter_by(case_number=item["case_number"]).first()
            if existing:
                logger.info(f"跳过已存在的判例: {item['case_number']}")
                continue
            trial_date = item.get("trial_date")
            if trial_date:
                y, m, d = map(int, trial_date.split("-"))
                trial_date = date(y, m, d)
            row = CourtCase(
                case_number=item["case_number"],
                title=item["title"],
                dispute_type=item["dispute_type"],
                court_name=item.get("court_name"),
                province=item.get("province"),
                city=item.get("city"),
                trial_date=trial_date,
                case_level=item.get("case_level"),
                plaintiff=item.get("plaintiff"),
                defendant=item.get("defendant"),
                third_party=item.get("third_party"),
                facts=item["facts"],
                claims=item.get("claims"),
                defense=item.get("defense"),
                judgment_reason=item.get("judgment_reason"),
                judgment_result=item.get("judgment_result"),
                applicable_laws=item.get("applicable_laws"),
                key_factors=item.get("key_factors"),
                amount_involved=item.get("amount_involved"),
                has_written_evidence=item.get("has_written_evidence"),
                limitation_period=item.get("limitation_period"),
                tags=item.get("tags"),
                summary=item.get("summary"),
            )
            db.add(row)

        db.commit()
        total = db.query(CourtCase).count()
        logger.success(f"判例库初始化完成，现有判例 {total} 条")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"初始化判例失败: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    truncate = "--truncate" in sys.argv
    success = seed_cases(truncate=truncate)
    sys.exit(0 if success else 1)
