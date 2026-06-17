from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(
                settings.MYSQL_DSN,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.DEBUG,
            )
            logger.info(f"MySQL 引擎创建成功: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
        except Exception as e:
            logger.error(f"MySQL 引擎创建失败: {e}")
            raise
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def get_db():
    db: Session = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def init_db():
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.success("MySQL 数据库表初始化完成")
    except Exception as e:
        logger.error(f"MySQL 表初始化失败: {e}")
