import random
import time
import logging
import requests
from typing import Dict, Tuple
from ..core.config import Config
from constants import USER_AGENTS, DEFAULT_HEADERS, LOG_CONFIG


class AccessSimulator:
    def __init__(self, config: Config):
        self.config = config
        self.user_agents = USER_AGENTS
        self.success_count = 0
        self.fail_count = 0
        self.logger = self._setup_logger()
        self.session = requests.Session()  # 使用会话提高性能

    def _setup_logger(self) -> logging.Logger:
        """获取日志记录器"""
        return logging.getLogger(__name__)

    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.user_agents)

    def get_random_interval(self) -> int:
        """获取随机访问间隔"""
        return random.randint(self.config.min_interval, self.config.max_interval)

    def _prepare_headers(self) -> Dict[str, str]:
        """准备请求头"""
        headers = DEFAULT_HEADERS.copy()
        headers['User-Agent'] = self.get_random_user_agent()
        return headers

    def make_request(self) -> Tuple[bool, int, str]:
        """发送HTTP请求"""
        headers = self._prepare_headers()
        retries = 0
        
        while retries <= self.config.retries:
            try:
                response = self.session.get(
                    self.config.url,
                    headers=headers,
                    timeout=self.config.timeout
                )
                response.raise_for_status()  # 检查HTTP错误
                
                message = f"成功 - 状态码: {response.status_code}"
                self.logger.info(message)
                self.success_count += 1
                return (True, response.status_code, message)
                
            except requests.exceptions.Timeout:
                retries += 1
                if retries > self.config.retries:
                    message = f"失败 - 请求超时（重试{self.config.retries}次后仍失败）"
                    self.logger.error(message)
                    self.fail_count += 1
                    return (False, 0, message)
                self.logger.warning(f"请求超时，{self.config.retry_delay}秒后重试 ({retries}/{self.config.retries})")
                time.sleep(self.config.retry_delay)
                
            except requests.exceptions.ConnectionError:
                retries += 1
                if retries > self.config.retries:
                    message = f"失败 - 连接错误（重试{self.config.retries}次后仍失败）"
                    self.logger.error(message)
                    self.fail_count += 1
                    return (False, 0, message)
                self.logger.warning(f"连接错误，{self.config.retry_delay}秒后重试 ({retries}/{self.config.retries})")
                time.sleep(self.config.retry_delay)
                
            except requests.exceptions.HTTPError as e:
                message = f"失败 - HTTP错误: {str(e)}"
                self.logger.error(message)
                self.fail_count += 1
                return (False, e.response.status_code if hasattr(e, 'response') else 0, message)
                
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > self.config.retries:
                    message = f"失败 - {str(e)}（重试{self.config.retries}次后仍失败）"
                    self.logger.error(message)
                    self.fail_count += 1
                    return (False, 0, message)
                self.logger.warning(f"请求错误，{self.config.retry_delay}秒后重试 ({retries}/{self.config.retries})")
                time.sleep(self.config.retry_delay)

    def simulate_access(self, current: int, total: int) -> bool:
        """模拟单次访问"""
        interval = self.get_random_interval()
        print(f"[{current}/{total}] 等待 {interval} 秒后访问 {self.config.url}")
        self.logger.info(f"[{current}/{total}] 等待 {interval} 秒后访问 {self.config.url}")
        
        time.sleep(interval)
        success, status_code, message = self.make_request()
        
        print(f"[{current}/{total}] {message}")
        
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1

        return success

    def run(self):
        """运行模拟访问"""
        print(f"\n开始模拟访问 {self.config.url}")
        print(f"配置: 访问次数={self.config.count}, 间隔={self.config.min_interval}-{self.config.max_interval}秒, 超时={self.config.timeout}秒, 重试次数={self.config.retries}")
        print("-" * 60)
        
        self.logger.info(f"开始模拟访问 {self.config.url}")
        self.logger.info(f"配置: {str(self.config)}")
        
        try:
            for i in range(1, self.config.count + 1):
                self.simulate_access(i, self.config.count)
        except KeyboardInterrupt:
            print("\n\n用户中断，停止访问")
            self.logger.info("用户中断，停止访问")
        except Exception as e:
            print(f"\n\n发生意外错误: {str(e)}")
            self.logger.error(f"发生意外错误: {str(e)}")
        
        print("-" * 60)
        print(f"访问完成! 成功: {self.success_count}, 失败: {self.fail_count}, 成功率: {self.success_count / self.config.count * 100:.1f}%")
        
        self.logger.info(f"访问完成! 成功: {self.success_count}, 失败: {self.fail_count}, 成功率: {self.success_count / self.config.count * 100:.1f}%")
