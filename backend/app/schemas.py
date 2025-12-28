from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

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
    created_at: datetime
    
    model_config = {"from_attributes": True}

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
    created_at: datetime
    updated_at: datetime
    results: List[SimulationResultResponse]
    
    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    id: str
    url: str
    status: str
    success_count: int
    fail_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class MessageResponse(BaseModel):
    message: str
