# EasyScan Server

一个基于FastAPI的URL短链接服务，支持实时二维码生成和Server-Sent Events (SSE) 推送更新。

## 🚀 功能特性

- **URL短链接服务**: 生成短链接并支持重定向
- **实时二维码**: 动态生成二维码，支持实时更新
- **Server-Sent Events**: 实时推送URL和名称变更
- **Redis存储**: 支持Redis和FakeRedis（开发/测试）
- **RESTful API**: 完整的REST API接口
- **Docker支持**: 容器化部署
- **可选名称**: 为URL添加自定义名称

## 📦 安装

### 使用 pip 安装

```bash
pip install easyscan-server
```

### 从源码安装

```bash
git clone https://github.com/your-username/easyscan-server.git
cd easyscan-server
pip install -e .
```

## 🏃 快速开始

### 启动服务器

```bash
# 使用默认配置启动
python -m easyscan_server

# 自定义主机和端口
python -m easyscan_server --host 0.0.0.0 --port 8080
```

### 使用Docker

```bash
# 构建镜像
docker build -t easyscan-server .

# 运行容器
docker run -p 8000:8000 easyscan-server
```

## 🔧 配置

### 环境变量

- `USE_REAL_REDIS`: 设置此变量以使用真实的Redis（否则使用FakeRedis）
- `REDIS_URL`: Redis连接URL（默认: `redis://localhost:6379`）

### 示例配置

```bash
# 使用真实Redis
export USE_REAL_REDIS=1
export REDIS_URL=redis://localhost:6379

# 启动服务
python -m easyscan_server
```

## 📚 API 文档

### 创建短链接

```http
POST /
Content-Type: application/json

{
    "url": "https://example.com",
    "name": "示例网站"
}
```

**响应:**
```json
{
    "key": "abc123def456",
    "url": "https://example.com",
    "name": "示例网站",
    "success": true
}
```

### 获取URL信息

```http
GET /{key}
```

**响应:**
```json
{
    "key": "abc123def456",
    "url": "https://example.com",
    "name": "示例网站"
}
```

### 更新现有链接

```http
POST /{key}
Content-Type: application/json

{
    "url": "https://newexample.com",
    "name": "新示例网站"
}
```

### 重定向到目标URL

```http
GET /{key}/redirect
```

### 查看二维码页面

```http
GET /{key}/qrcode
```

### Server-Sent Events

```http
GET /sse/{key}
```


## 🏗️ 项目结构

```
easyscan-server/
├── __init__.py
├── __main__.py          # 程序入口点
├── main.py             # FastAPI应用主文件
├── domain.py           # 数据层和业务逻辑
├── type.py             # Pydantic模型定义
└── templates/
    └── qrcode.html     # 二维码页面模板
```

## 🧪 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/your-username/easyscan-server.git
cd easyscan-server

# 安装依赖
pip install -e .

# 运行开发服务器
python -m easyscan_server --host 0.0.0.0 --port 8000
```

### 依赖项

- **FastAPI**: Web框架
- **Uvicorn**: ASGI服务器
- **Redis**: 数据存储
- **FakeRedis**: 测试用Redis模拟器
- **Pydantic**: 数据验证
- **Jinja2**: 模板引擎
- **Typer**: CLI工具

## 🐳 Docker 部署

### 基本部署

```bash
docker run -p 8000:8000 easyscan-server
```

### 使用真实Redis部署

```bash
# 启动Redis容器
docker run -d --name redis redis:alpine

# 启动EasyScan Server并连接Redis
docker run -p 8000:8000 \
  -e USE_REAL_REDIS=1 \
  -e REDIS_URL=redis://redis:6379 \
  --link redis:redis \
  easyscan-server
```

### Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  easyscan-server:
    image: easyscan-server
    ports:
      - "8000:8000"
    environment:
      - USE_REAL_REDIS=1
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
```

## 📝 许可证

本项目采用 GNU Affero General Public License v3.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请阅读我们的贡献指南并提交Pull Request。

## 📞 支持

如果您遇到问题或有功能建议，请创建一个 [Issue](https://github.com/your-username/easyscan-server/issues)。

## 🙏 鸣谢

感谢以下开源项目和技术为EasyScan Server提供支持：

### 核心技术
- **[FastAPI](https://fastapi.tiangolo.com/)** - 现代、快速的Python Web框架
- **[Uvicorn](https://www.uvicorn.org/)** - 高性能ASGI服务器
- **[Redis](https://redis.io/)** - 内存数据结构存储
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - 数据验证和设置管理

### 开发工具
- **[Typer](https://typer.tiangolo.com/)** - 构建CLI应用的现代库
- **[Jinja2](https://jinja.palletsprojects.com/)** - 现代且设计友好的模板引擎
- **[FakeRedis](https://github.com/cunla/fakeredis-py)** - Redis的Python模拟器，用于测试

### 前端技术
- **[QRCode.js](https://github.com/davidshimjs/qrcodejs)** - JavaScript二维码生成库
- **[Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)** - 实时数据推送技术

### 部署和打包
- **[Docker](https://www.docker.com/)** - 容器化平台
- **[uv](https://github.com/astral-sh/uv)** - 现代Python包管理器
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD自动化

特别感谢所有开源社区的贡献者们，是你们让这个项目成为可能！ 🚀

---

**EasyScan Server** - 让URL分享变得简单快捷！ 🚀
