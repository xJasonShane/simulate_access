from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
import threading
import time

from ..db import get_db, SessionLocal, Task, TaskResult, TaskStatus, ResultStatus
from ..core.config import Config
from ..services.simulator import AccessSimulator
from ..schemas import (
    SimulationConfig,
    SimulationStatusResponse,
    TaskListResponse,
    MessageResponse
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

# 模拟访问线程函数
def run_simulation(task_id: str):
    # 每个线程创建自己的数据库会话
    db = SessionLocal()
    try:
        # 获取任务
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        # 初始化配置
        config = Config()
        
        # 检查URL是否有效
        if not config.set_url(task.url):
            # 显式更新数据库中的任务状态
            db.query(Task).filter(Task.id == task.id).update({
                Task.status: TaskStatus.FAILED
            })
            task_result = TaskResult(
                task_id=task.id,
                status=ResultStatus.FAILURE,
                status_code=0,
                message=f"无效的URL: {task.url}"
            )
            db.add(task_result)
            db.commit()
            return
        
        config.set_interval(task.min_interval, task.max_interval)
        config.set_count(task.count)
        config.set_timeout(task.timeout)
        config.set_retries(task.retries)
        config.set_retry_delay(task.retry_delay)
        
        simulator = AccessSimulator(config)
        
        try:
            for i in range(1, task.count + 1):
                # 每次请求后直接更新数据库中的任务状态，不使用对象属性更新
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
                
                # 显式更新数据库中的任务状态和计数
                db.query(Task).filter(Task.id == task.id).update({
                    Task.success_count: simulator.success_count,
                    Task.fail_count: simulator.fail_count
                })
                
                # 提交事务
                db.commit()
            
            # 任务完成，显式更新数据库中的任务状态
            success_count = simulator.success_count
            fail_count = simulator.fail_count
            db.query(Task).filter(Task.id == task.id).update({
                Task.status: TaskStatus.COMPLETED,
                Task.success_count: success_count,
                Task.fail_count: fail_count
            })
            db.commit()
        except Exception as e:
            # 任务失败，显式更新数据库中的任务状态
            success_count = simulator.success_count
            fail_count = simulator.fail_count
            db.query(Task).filter(Task.id == task.id).update({
                Task.status: TaskStatus.FAILED,
                Task.success_count: success_count,
                Task.fail_count: fail_count
            })
            # 创建失败结果
            task_result = TaskResult(
                task_id=task.id,
                status=ResultStatus.FAILURE,
                status_code=0,
                message=f"任务失败: {str(e)}"
            )
            db.add(task_result)
            db.commit()
    finally:
        # 确保数据库会话被关闭
        db.close()

@router.post("", response_model=SimulationStatusResponse, status_code=201, summary="创建模拟访问任务")
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
        args=(task_id,)
    )
    thread.daemon = True
    thread.start()
    
    return task

@router.get("/{task_id}", response_model=SimulationStatusResponse, summary="获取任务详情")
async def get_task_detail(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取指定任务的详细信息和结果"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task
