#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址获取和刷新工具
从多个网站获取CloudFlare IP地址，去重排序后保存到文件

Author: Backend Engineer
Version: 2.0
"""

import requests
import re
import os
import logging
import json
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Optional
from pathlib import Path


class IPRefreshConfig:
    """配置管理类"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.default_config = {
            'urls': [
                'https://ip.164746.xyz',
                'https://cf.090227.xyz',
                'https://stock.hostmonit.com/CloudFlareYes',
                'https://www.wetest.vip/page/cloudflare/address_v4.html',
                'https://api.uouin.com/cloudflare.html'
            ],
            'output_file': 'ip.txt',
            'timeout': 10,
            'max_workers': 4,
            'log_level': 'INFO',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置和用户配置
                return {**self.default_config, **config}
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"配置文件加载失败，使用默认配置: {e}")
        return self.default_config
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"配置文件保存失败: {e}")


class IPValidator:
    """IP地址验证器"""
    
    # 更精确的IPv4正则表达式
    IP_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )
    
    @classmethod
    def is_valid_ip(cls, ip: str) -> bool:
        """验证IP地址是否有效"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @classmethod
    def is_public_ip(cls, ip: str) -> bool:
        """检查是否为公网IP地址"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            return ip_obj.is_global
        except ipaddress.AddressValueError:
            return False
    
    @classmethod
    def extract_ips_from_text(cls, text: str) -> Set[str]:
        """从文本中提取有效的IP地址"""
        potential_ips = cls.IP_PATTERN.findall(text)
        valid_ips = set()
        
        for ip in potential_ips:
            if cls.is_valid_ip(ip) and cls.is_public_ip(ip):
                valid_ips.add(ip)
        
        return valid_ips


class IPFetcher:
    """IP地址获取器"""
    
    def __init__(self, config: IPRefreshConfig):
        self.config = config.config
        self.session = self._create_session()
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def fetch_ips_from_url(self, url: str) -> Set[str]:
        """从单个URL获取IP地址"""
        try:
            self.logger.info(f"正在获取URL: {url}")
            response = self.session.get(
                url, 
                timeout=self.config['timeout'],
                allow_redirects=True
            )
            response.raise_for_status()
            
            # 提取IP地址
            ips = IPValidator.extract_ips_from_text(response.text)
            self.logger.info(f"从 {url} 获取到 {len(ips)} 个有效IP地址")
            return ips
            
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接错误: {url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP错误 {e.response.status_code}: {url}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求异常: {url} - {e}")
        except Exception as e:
            self.logger.error(f"未知错误: {url} - {e}")
        
        return set()
    
    def fetch_all_ips(self) -> Set[str]:
        """并发获取所有URL的IP地址"""
        all_ips = set()
        urls = self.config['urls']
        max_workers = min(self.config['max_workers'], len(urls))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_url = {
                executor.submit(self.fetch_ips_from_url, url): url 
                for url in urls
            }
            
            # 收集结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    ips = future.result()
                    all_ips.update(ips)
                except Exception as e:
                    self.logger.error(f"处理URL {url} 时发生异常: {e}")
        
        return all_ips
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()


class IPFileManager:
    """IP文件管理器"""
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        self.logger = logging.getLogger(__name__)
    
    def backup_existing_file(self) -> Optional[str]:
        """备份现有文件"""
        if self.output_file.exists():
            backup_file = self.output_file.with_suffix('.bak')
            try:
                self.output_file.rename(backup_file)
                self.logger.info(f"已备份现有文件到: {backup_file}")
                return str(backup_file)
            except OSError as e:
                self.logger.error(f"备份文件失败: {e}")
        return None
    
    def save_ips(self, ips: Set[str]) -> bool:
        """保存IP地址到文件"""
        if not ips:
            self.logger.warning("没有IP地址需要保存")
            return False
        
        try:
            # 按IP地址数值排序
            sorted_ips = sorted(ips, key=lambda ip: tuple(map(int, ip.split('.'))))
            
            # 确保目录存在
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for ip in sorted_ips:
                    f.write(f"{ip}\n")
            
            self.logger.info(f"成功保存 {len(sorted_ips)} 个IP地址到 {self.output_file}")
            return True
            
        except OSError as e:
            self.logger.error(f"保存文件失败: {e}")
            return False


class IPRefreshTool:
    """IP刷新工具主类"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config = IPRefreshConfig(config_file)
        self._setup_logging()
        self.fetcher = IPFetcher(self.config)
        self.file_manager = IPFileManager(self.config.config['output_file'])
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.config['log_level'].upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('ip_refresh.log', encoding='utf-8')
            ]
        )
    
    def run(self) -> bool:
        """执行IP刷新任务"""
        self.logger.info("开始IP地址刷新任务")
        
        try:
            # 备份现有文件
            self.file_manager.backup_existing_file()
            
            # 获取IP地址
            self.logger.info(f"开始从 {len(self.config.config['urls'])} 个URL获取IP地址")
            all_ips = self.fetcher.fetch_all_ips()
            
            if not all_ips:
                self.logger.error("未获取到任何有效的IP地址")
                return False
            
            self.logger.info(f"总共获取到 {len(all_ips)} 个唯一的有效IP地址")
            
            # 保存到文件
            success = self.file_manager.save_ips(all_ips)
            
            if success:
                self.logger.info("IP地址刷新任务完成")
                print(f"✅ 成功获取并保存了 {len(all_ips)} 个IP地址到 {self.config.config['output_file']}")
            else:
                self.logger.error("保存IP地址失败")
                print("❌ 保存IP地址失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"执行过程中发生异常: {e}")
            print(f"❌ 执行失败: {e}")
            return False


def main():
    """主函数"""
    try:
        tool = IPRefreshTool()
        success = tool.run()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        exit(1)
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        exit(1)


if __name__ == '__main__':
    main()