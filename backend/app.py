from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.db import init_db
from .app.api.tasks import router as tasks_router

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

# 注册路由
app.include_router(tasks_router, prefix="/api")

# 健康检查
@app.get("/api/health", summary="健康检查")
async def health_check():
    """检查API服务是否正常运行"""
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
