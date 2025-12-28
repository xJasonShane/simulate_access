import argparse
from config import Config
from simulator import AccessSimulator


def get_input(prompt: str, default=None, validator=None):
    """获取用户输入并验证"""
    while True:
        try:
            value = input(prompt).strip()
            if default and not value:
                value = str(default)
            
            if validator:
                result = validator(value)
                if result is not False:
                    return result
                print("输入无效，请重新输入")
            else:
                return value
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            exit(0)
        except Exception as e:
            print(f"错误: {e}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='网站访问模拟器')
    parser.add_argument('--url', type=str, help='目标URL或IP')
    parser.add_argument('--min-interval', type=int, help='最小访问间隔(秒)')
    parser.add_argument('--max-interval', type=int, help='最大访问间隔(秒)')
    parser.add_argument('--count', type=int, help='访问次数')
    parser.add_argument('--timeout', type=int, help='请求超时时间(秒)')
    parser.add_argument('--retries', type=int, help='重试次数')
    parser.add_argument('--retry-delay', type=int, help='重试延迟(秒)')
    return parser.parse_args()


def interactive_config(config: Config):
    """交互式配置"""
    url = get_input(
        "请输入目标URL或IP (例如: https://example.com 或 example.com): ",
        validator=lambda x: config.set_url(x) if x else False
    )

    min_interval = int(get_input(
        f"请输入最小访问间隔(秒) [默认: {config.min_interval}]: ",
        default=config.min_interval,
        validator=lambda x: int(x) if x.isdigit() and int(x) >= 1 else False
    ))

    max_interval = int(get_input(
        f"请输入最大访问间隔(秒) [默认: {config.max_interval}]: ",
        default=config.max_interval,
        validator=lambda x: int(x) if x.isdigit() and int(x) >= min_interval else False
    ))

    if not config.set_interval(min_interval, max_interval):
        print("间隔设置无效")
        return False

    count = int(get_input(
        f"请输入访问次数 [默认: {config.count}]: ",
        default=config.count,
        validator=lambda x: int(x) if x.isdigit() and int(x) > 0 else False
    ))

    if not config.set_count(count):
        print("访问次数设置无效")
        return False

    timeout = int(get_input(
        f"请输入请求超时时间(秒) [默认: {config.timeout}]: ",
        default=config.timeout,
        validator=lambda x: int(x) if x.isdigit() and int(x) > 0 else False
    ))

    if not config.set_timeout(timeout):
        print("超时时间设置无效")
        return False

    retries = int(get_input(
        f"请输入重试次数(失败后重试次数，0表示不重试) [默认: {config.retries}]: ",
        default=config.retries,
        validator=lambda x: int(x) if x.isdigit() and int(x) >= 0 else False
    ))

    if not config.set_retries(retries):
        print("重试次数设置无效")
        return False

    retry_delay = int(get_input(
        f"请输入重试延迟(秒) [默认: {config.retry_delay}]: ",
        default=config.retry_delay,
        validator=lambda x: int(x) if x.isdigit() and int(x) >= 0 else False
    ))

    if not config.set_retry_delay(retry_delay):
        print("重试延迟设置无效")
        return False

    return True


def command_line_config(config: Config, args):
    """命令行参数配置"""
    if args.url:
        if not config.set_url(args.url):
            print(f"无效的URL: {args.url}")
            return False
    
    if args.min_interval and args.max_interval:
        if not config.set_interval(args.min_interval, args.max_interval):
            print(f"无效的访问间隔: {args.min_interval}-{args.max_interval}秒")
            return False
    elif args.min_interval or args.max_interval:
        print("错误: --min-interval 和 --max-interval 必须同时使用")
        return False
    
    if args.count:
        if not config.set_count(args.count):
            print(f"无效的访问次数: {args.count}")
            return False
    
    if args.timeout:
        if not config.set_timeout(args.timeout):
            print(f"无效的超时时间: {args.timeout}")
            return False
    
    if args.retries:
        if not config.set_retries(args.retries):
            print(f"无效的重试次数: {args.retries}")
            return False
    
    if args.retry_delay:
        if not config.set_retry_delay(args.retry_delay):
            print(f"无效的重试延迟: {args.retry_delay}")
            return False
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("           网站访问模拟器")
    print("=" * 60)
    print("警告: 请勿用于非法用途，仅用于测试和学习")
    print("=" * 60)
    print()

    # 解析命令行参数
    args = parse_arguments()
    
    config = Config()
    
    # 命令行模式
    if args.url:
        if not command_line_config(config, args):
            return
        
        print("\n配置确认:")
        print(f"  目标: {config.url}")
        print(f"  访问间隔: {config.min_interval}-{config.max_interval} 秒")
        print(f"  访问次数: {config.count}")
        print(f"  超时时间: {config.timeout} 秒")
        print(f"  重试次数: {config.retries}")
        print(f"  重试延迟: {config.retry_delay} 秒")
        
        confirm = input("\n确认开始访问? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    
    # 交互式模式
    else:
        if not interactive_config(config):
            return
        
        print("\n配置确认:")
        print(f"  目标: {config.url}")
        print(f"  访问间隔: {config.min_interval}-{config.max_interval} 秒")
        print(f"  访问次数: {config.count}")
        print(f"  超时时间: {config.timeout} 秒")
        print(f"  重试次数: {config.retries}")
        print(f"  重试延迟: {config.retry_delay} 秒")
        
        confirm = input("\n确认开始访问? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    
    # 运行模拟器
    simulator = AccessSimulator(config)
    simulator.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
