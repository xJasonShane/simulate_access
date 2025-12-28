from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
import threading
import time
import uuid

from config import Config
from simulator import AccessSimulator
from db import init_db, get_db, Task, TaskResult, TaskStatus, ResultStatus

# 初始化数据库
init_db()

app = FastAPI(title="网站访问模拟器 API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class SimulationConfig(BaseModel):
    url: str = Field(..., description="目标URL或IP地址")
    min_interval: int = Field(default=2, ge=1, description="最小访问间隔(秒)")
    max_interval: int = Field(default=5, ge=1, description="最大访问间隔(秒)")
    count: int = Field(default=10, ge=1, description="访问次数")
    timeout: int = Field(default=10, ge=1, description="请求超时时间(秒)")
    retries: int = Field(default=0, ge=0, description="重试次数")
    retry_delay: int = Field(default=1, ge=0, description="重试延迟(秒)")

class SimulationResultResponse(BaseModel):
    id: int
    status: str
    status_code: int
    message: str
    created_at: str
    
    class Config:
        from_attributes = True

class SimulationStatusResponse(BaseModel):
    id: str
    url: str
    min_interval: int
    max_interval: int
    count: int
    timeout: int
    retries: int
    retry_delay: int
    status: str
    success_count: int
    fail_count: int
    created_at: str
    updated_at: str
    results: List[SimulationResultResponse]
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    id: str
    url: str
    status: str
    success_count: int
    fail_count: int
    created_at: str
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

# 模拟访问线程函数
def run_simulation(task_id: str, db: Session):
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return
    
    # 初始化配置
    config = Config()
    config.set_url(task.url)
    config.set_interval(task.min_interval, task.max_interval)
    config.set_count(task.count)
    config.set_timeout(task.timeout)
    config.set_retries(task.retries)
    config.set_retry_delay(task.retry_delay)
    
    simulator = AccessSimulator(config)
    
    try:
        for i in range(1, task.count + 1):
            interval = simulator.get_random_interval()
            time.sleep(interval)
            success, status_code, message = simulator.make_request()
            
            # 创建任务结果
            result_status = ResultStatus.SUCCESS if success else ResultStatus.FAILURE
            task_result = TaskResult(
                task_id=task.id,
                status=result_status,
                status_code=status_code,
                message=message
            )
            db.add(task_result)
            
            # 更新任务状态
            task.success_count = simulator.success_count
            task.fail_count = simulator.fail_count
            db.commit()
            db.refresh(task)
        
        # 任务完成
        task.status = TaskStatus.COMPLETED
    except Exception as e:
        # 任务失败
        task.status = TaskStatus.FAILED
        task_result = TaskResult(
            task_id=task.id,
            status=ResultStatus.FAILURE,
            status_code=0,
            message=f"任务失败: {str(e)}"
        )
        db.add(task_result)
    finally:
        db.commit()
        db.refresh(task)

@app.post("/api/tasks", response_model=SimulationStatusResponse, status_code=201, summary="创建模拟访问任务")
async def create_simulation_task(
    config: SimulationConfig,
    db: Session = Depends(get_db)
):
    """创建一个新的模拟访问任务"""
    task_id = str(uuid.uuid4())
    
    # 创建任务
    task = Task(
        id=task_id,
        url=config.url,
        min_interval=config.min_interval,
        max_interval=config.max_interval,
        count=config.count,
        timeout=config.timeout,
        retries=config.retries,
        retry_delay=config.retry_delay,
        status=TaskStatus.RUNNING
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 启动模拟线程
    thread = threading.Thread(
        target=run_simulation,
        args=(task_id, db)
    )
    thread.daemon = True
    thread.start()
    
    return task

@app.get("/api/tasks", response_model=List[TaskListResponse], summary="获取所有任务列表")
async def get_all_tasks(
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """获取所有任务列表，可按状态筛选"""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    
    return query.order_by(Task.created_at.desc()).all()

@app.get("/api/tasks/{task_id}", response_model=SimulationStatusResponse, summary="获取任务详情")
async def get_task_detail(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取指定任务的详细信息和结果"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task

@app.delete("/api/tasks/{task_id}", response_model=MessageResponse, summary="删除任务")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """删除指定任务及其所有结果"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    
    return {"message": "任务已成功删除"}

@app.get("/api/health", summary="健康检查")
async def health_check():
    """检查API服务是否正常运行"""
    return {"status": "ok", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
