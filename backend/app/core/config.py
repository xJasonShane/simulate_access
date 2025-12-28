import re
import logging
from constants import DEFAULT_CONFIG, LOG_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG['level']),
    format=LOG_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
        logging.StreamHandler()  # 添加控制台输出
    ]
)


class Config:
    def __init__(self):
        self.url: str = ""
        self.min_interval: int = DEFAULT_CONFIG['min_interval']
        self.max_interval: int = DEFAULT_CONFIG['max_interval']
        self.count: int = DEFAULT_CONFIG['count']
        self.timeout: int = DEFAULT_CONFIG['timeout']
        self.retries: int = DEFAULT_CONFIG['retries']
        self.retry_delay: int = DEFAULT_CONFIG['retry_delay']
        self.batch_size: int = DEFAULT_CONFIG['batch_size']

    def validate_url(self, url: str) -> bool:
        if not url:
            return False
        
        # 支持IP地址直接访问（没有http/https的情况）
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', url):
            self.url = f"http://{url}"
            return True
        
        # 支持域名直接访问（没有http/https的情况）
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(url):
            self.url = url
            return True
        return False

    def validate_interval(self, min_interval: int, max_interval: int) -> bool:
        if min_interval < 1 or max_interval < 1:
            return False
        if min_interval > max_interval:
            return False
        return True

    def validate_count(self, count: int) -> bool:
        return count > 0

    def validate_timeout(self, timeout: int) -> bool:
        return timeout > 0

    def validate_retries(self, retries: int) -> bool:
        return retries >= 0

    def validate_retry_delay(self, retry_delay: int) -> bool:
        return retry_delay >= 0

    def validate_batch_size(self, batch_size: int) -> bool:
        return batch_size >= 1

    def set_url(self, url: str) -> bool:
        return self.validate_url(url)

    def set_interval(self, min_interval: int, max_interval: int) -> bool:
        if not self.validate_interval(min_interval, max_interval):
            return False
        self.min_interval = min_interval
        self.max_interval = max_interval
        return True

    def set_count(self, count: int) -> bool:
        if not self.validate_count(count):
            return False
        self.count = count
        return True

    def set_timeout(self, timeout: int) -> bool:
        if not self.validate_timeout(timeout):
            return False
        self.timeout = timeout
        return True

    def set_retries(self, retries: int) -> bool:
        if not self.validate_retries(retries):
            return False
        self.retries = retries
        return True

    def set_retry_delay(self, retry_delay: int) -> bool:
        if not self.validate_retry_delay(retry_delay):
            return False
        self.retry_delay = retry_delay
        return True

    def set_batch_size(self, batch_size: int) -> bool:
        if not self.validate_batch_size(batch_size):
            return False
        self.batch_size = batch_size
        return True

    def is_valid(self) -> bool:
        return all([
            bool(self.url),
            self.validate_interval(self.min_interval, self.max_interval),
            self.validate_count(self.count),
            self.validate_timeout(self.timeout),
            self.validate_retries(self.retries),
            self.validate_retry_delay(self.retry_delay),
            self.validate_batch_size(self.batch_size)
        ])

    def __str__(self) -> str:
        return (
            f"配置信息:\n"
            f"  目标URL: {self.url}\n"
            f"  访问间隔: {self.min_interval}-{self.max_interval}秒\n"
            f"  访问次数: {self.count}\n"
            f"  超时时间: {self.timeout}秒\n"
            f"  重试次数: {self.retries}\n"
            f"  重试延迟: {self.retry_delay}秒\n"
            f"  批量大小: {self.batch_size}"
        )
