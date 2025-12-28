from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Tuple
import threading
import time
import queue

from config import Config
from simulator import AccessSimulator

app = FastAPI(title="网站访问模拟器 API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 任务队列和结果存储
task_queue = queue.Queue()
task_results = {}
task_threads = {}

# Pydantic模型
class SimulationConfig(BaseModel):
    url: str
    min_interval: int = 2
    max_interval: int = 5
    count: int = 10
    timeout: int = 10
    retries: int = 0
    retry_delay: int = 1

class SimulationResult(BaseModel):
    success: bool
    status_code: int
    message: str

class SimulationStatus(BaseModel):
    task_id: str
    status: str  # running, completed, failed
    success_count: int = 0
    fail_count: int = 0
    results: List[SimulationResult] = []

# 模拟访问线程函数
def run_simulation(task_id: str, config: Config):
    simulator = AccessSimulator(config)
    results = []
    
    try:
        for i in range(1, config.count + 1):
            interval = simulator.get_random_interval()
            time.sleep(interval)
            success, status_code, message = simulator.make_request()
            
            result = SimulationResult(
                success=success,
                status_code=status_code,
                message=message
            )
            results.append(result)
            
            # 更新任务状态
            task_results[task_id] = SimulationStatus(
                task_id=task_id,
                status="running",
                success_count=simulator.success_count,
                fail_count=simulator.fail_count,
                results=results
            )
        
        # 任务完成
        task_results[task_id] = SimulationStatus(
            task_id=task_id,
            status="completed",
            success_count=simulator.success_count,
            fail_count=simulator.fail_count,
            results=results
        )
    except Exception as e:
        # 任务失败
        task_results[task_id] = SimulationStatus(
            task_id=task_id,
            status="failed",
            results=[SimulationResult(
                success=False,
                status_code=0,
                message=f"任务失败: {str(e)}"
            )]
        )

@app.post("/api/simulate", response_model=SimulationStatus)
async def start_simulation(config_data: SimulationConfig):
    """开始模拟访问"""
    import uuid
    task_id = str(uuid.uuid4())
    
    # 初始化配置
    config = Config()
    if not config.set_url(config_data.url):
        raise HTTPException(status_code=400, detail="无效的URL")
    
    if not config.set_interval(config_data.min_interval, config_data.max_interval):
        raise HTTPException(status_code=400, detail="无效的访问间隔")
    
    if not config.set_count(config_data.count):
        raise HTTPException(status_code=400, detail="无效的访问次数")
    
    if not config.set_timeout(config_data.timeout):
        raise HTTPException(status_code=400, detail="无效的超时时间")
    
    if not config.set_retries(config_data.retries):
        raise HTTPException(status_code=400, detail="无效的重试次数")
    
    if not config.set_retry_delay(config_data.retry_delay):
        raise HTTPException(status_code=400, detail="无效的重试延迟")
    
    # 初始化任务状态
    task_results[task_id] = SimulationStatus(
        task_id=task_id,
        status="running",
        success_count=0,
        fail_count=0,
        results=[]
    )
    
    # 启动模拟线程
    thread = threading.Thread(target=run_simulation, args=(task_id, config))
    thread.daemon = True
    thread.start()
    
    task_threads[task_id] = thread
    
    return task_results[task_id]

@app.get("/api/status/{task_id}", response_model=SimulationStatus)
async def get_simulation_status(task_id: str):
    """获取模拟任务状态"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task_results[task_id]

@app.get("/api/tasks")
async def get_all_tasks():
    """获取所有任务"""
    return list(task_results.values())

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id in task_results:
        del task_results[task_id]
    if task_id in task_threads:
        # 注意：无法直接停止线程，这里只能删除任务记录
        del task_threads[task_id]
    return {"message": "任务已删除"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
