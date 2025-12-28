# db.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# 数据库URL - 使用SQLite作为轻量级数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./simulator.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite特定参数
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 任务状态枚举
class TaskStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 任务结果枚举
class ResultStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"

# 任务模型
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    min_interval = Column(Integer)
    max_interval = Column(Integer)
    count = Column(Integer)
    timeout = Column(Integer)
    retries = Column(Integer)
    retry_delay = Column(Integer)
    status = Column(Enum(TaskStatus), default=TaskStatus.RUNNING)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    results = relationship("TaskResult", back_populates="task", cascade="all, delete-orphan")

# 任务结果模型
class TaskResult(Base):
    __tablename__ = "task_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String, ForeignKey("tasks.id"))
    status = Column(Enum(ResultStatus))
    status_code = Column(Integer)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    task = relationship("Task", back_populates="results")

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
