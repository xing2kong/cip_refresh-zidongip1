# IP地址刷新工具 v2.0

一个用于从多个网站获取CloudFlare IP地址的高效工具，支持并发获取、智能验证、配置管理等功能。

## 功能特性

### 🚀 核心功能
- **并发获取**: 使用线程池并发请求多个URL，提高获取效率
- **智能验证**: 精确的IP地址验证，过滤无效和私有IP地址
- **自动去重**: 自动去除重复的IP地址
- **智能排序**: 按IP地址数值排序，非字符串排序
- **配置管理**: 支持JSON配置文件，灵活配置各种参数

### 🛡️ 可靠性保障
- **异常处理**: 完善的异常处理机制，单个URL失败不影响整体任务
- **文件备份**: 自动备份现有文件，防止数据丢失
- **日志记录**: 详细的日志记录，便于问题排查
- **超时控制**: 可配置的请求超时时间
- **重试机制**: 内置HTTP重试和错误恢复

### 📊 监控与调试
- **进度显示**: 实时显示获取进度和结果
- **详细日志**: 支持多级别日志输出
- **性能统计**: 显示获取到的IP数量和处理时间

## 安装依赖

```bash
pip install requests
```

## 使用方法

### 🤖 自动化运行（推荐）

本项目已配置GitHub Actions，可以自动定时更新IP列表：

- **定时运行**：每天北京时间8:00和20:00自动运行
- **手动触发**：在GitHub仓库的Actions页面可手动运行
- **自动提交**：有更新时自动提交到仓库
- **版本发布**：每周自动创建release版本

#### 获取最新IP列表

```bash
# 直接下载最新的ip.txt文件
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/ip.txt

# 或使用curl
curl -o ip.txt https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/ip.txt
```

### 💻 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行脚本
python ip_refresh.py
```

### 配置文件

工具支持通过 `config.json` 文件进行配置：

```json
{
  "urls": [
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes",
    "https://www.wetest.vip/page/cloudflare/address_v4.html"
  ],
  "output_file": "ip.txt",
  "timeout": 10,
  "max_workers": 4,
  "log_level": "INFO",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `urls` | Array | 见配置文件 | 要获取IP的URL列表 |
| `output_file` | String | "ip.txt" | 输出文件路径 |
| `timeout` | Integer | 10 | HTTP请求超时时间（秒） |
| `max_workers` | Integer | 4 | 并发线程数 |
| `log_level` | String | "INFO" | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `user_agent` | String | 见配置文件 | HTTP请求的User-Agent |

## 输出文件

- **ip.txt**: 主要输出文件，包含所有有效的IP地址
- **ip.txt.bak**: 自动备份的上一次结果
- **ip_refresh.log**: 详细的运行日志

## 代码架构

### 类设计

```
IPRefreshTool (主控制器)
├── IPRefreshConfig (配置管理)
├── IPFetcher (IP获取器)
│   └── IPValidator (IP验证器)
└── IPFileManager (文件管理器)
```

### 主要类说明

- **IPRefreshConfig**: 负责配置文件的加载、保存和管理
- **IPValidator**: 提供IP地址验证和提取功能
- **IPFetcher**: 负责并发获取IP地址，包含HTTP会话管理
- **IPFileManager**: 负责文件的备份、保存等操作
- **IPRefreshTool**: 主控制器，协调各个组件完成任务

## 错误处理

工具具备完善的错误处理机制：

- **网络错误**: 自动跳过失败的URL，继续处理其他URL
- **超时处理**: 可配置的超时时间，避免长时间等待
- **文件错误**: 自动创建目录，处理文件权限问题
- **配置错误**: 配置文件损坏时自动使用默认配置

## 性能优化

- **并发请求**: 使用ThreadPoolExecutor实现并发获取
- **连接复用**: 使用Session复用HTTP连接
- **内存优化**: 使用集合去重，避免重复存储
- **正则优化**: 使用编译后的正则表达式提高匹配效率

## 日志说明

日志文件 `ip_refresh.log` 包含详细的运行信息：

```
2024-01-01 12:00:00 - __main__ - INFO - 开始IP地址刷新任务
2024-01-01 12:00:01 - __main__ - INFO - 正在获取URL: https://ip.164746.xyz
2024-01-01 12:00:02 - __main__ - INFO - 从 https://ip.164746.xyz 获取到 50 个有效IP地址
2024-01-01 12:00:03 - __main__ - INFO - 成功保存 200 个IP地址到 ip.txt
```

## 🚀 GitHub Actions 自动化

### 配置说明

项目包含完整的GitHub Actions配置，位于 `.github/workflows/update-ip.yml`：

#### 触发条件
- **定时触发**：每天UTC 0:00和12:00（北京时间8:00和20:00）
- **手动触发**：在Actions页面点击"Run workflow"
- **代码更新**：推送到main/master分支时

#### 自动化流程
1. **环境准备**：设置Python 3.9环境
2. **依赖安装**：自动安装requirements.txt中的依赖
3. **执行脚本**：运行ip_refresh.py获取最新IP
4. **变更检测**：智能检测IP列表是否有更新
5. **自动提交**：有更新时自动提交到仓库
6. **版本发布**：每周自动创建release
7. **文件归档**：上传IP列表作为构建产物

#### 使用步骤

1. **Fork仓库**到你的GitHub账号
2. **启用Actions**：在仓库Settings > Actions中启用
3. **配置权限**：确保Actions有写入权限
   ```
   Settings > Actions > General > Workflow permissions
   选择 "Read and write permissions"
   ```
4. **手动运行**：Actions页面 > Update CloudFlare IP List > Run workflow

#### 获取结果

- **直接访问**：`https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/ip.txt`
- **Release下载**：在Releases页面下载最新版本
- **API获取**：使用GitHub API获取最新内容

### 监控和通知

- **执行状态**：Actions页面查看运行状态
- **提交历史**：查看自动提交的IP更新记录
- **错误处理**：失败时会在Actions页面显示详细日志

## 版本历史

### v2.1 (当前版本)
- ✨ 添加GitHub Actions自动化支持
- 🤖 支持定时自动更新IP列表
- 📦 自动创建release版本
- 🔄 智能变更检测和提交
- 📊 详细的执行摘要和统计

### v2.0
- 完全重构代码架构，采用面向对象设计
- 添加并发获取功能，提高效率
- 增强IP地址验证，过滤私有IP
- 添加配置文件支持
- 完善异常处理和日志记录
- 添加文件备份功能
- 优化性能和内存使用

### v1.0 (原始版本)
- 基本的IP获取功能
- 简单的去重和排序
- 基础的异常处理

## 故障排除

### 常见问题

1. **没有获取到IP地址**
   - 检查网络连接
   - 确认URL是否可访问
   - 查看日志文件了解详细错误信息

2. **配置文件错误**
   - 检查JSON格式是否正确
   - 确认文件编码为UTF-8
   - 删除配置文件使用默认配置

3. **权限错误**
   - 确保有写入当前目录的权限
   - 检查输出文件是否被其他程序占用

### 调试模式

设置日志级别为DEBUG获取更详细的信息：

```json
{
  "log_level": "DEBUG"
}
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。