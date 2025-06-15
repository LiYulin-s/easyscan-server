# EasyScan Server

EasyScan Server 是一个基于 FastAPI 和 Redis 的简易短链与二维码生成服务，支持实时更新和二维码展示。

## 功能特性
- 生成短链，自动分配唯一 key
- 支持自定义 key 的 URL 更新
- 实时 SSE（Server-Sent Events）推送，二维码页面自动刷新
- 基于 Redis 存储，支持高并发
- 提供二维码页面，扫码自动跳转

## 主要接口

### 1. 新建短链
- `POST /`
- 请求体：`{"url": "https://example.com", "name": "示例"}`
- 返回：`{"key": "xxxx", "url": "...", "name": "...", "success": true}`

### 2. 更新短链
- `POST /{key}`
- 请求体同上
- 返回：同上

### 3. 获取短链信息
- `GET /{key}`
- 返回：`{"key": "xxxx", "url": "...", "name": "..."}`

### 4. 跳转到原始链接
- `GET /{key}/redirect`
- 302 跳转到原始 URL

### 5. 获取二维码页面
- `GET /{key}/qrcode`
- 返回二维码 HTML 页面，支持实时更新

### 6. 实时推送（SSE）
- `GET /sse/{key}`
- 用于前端实时获取 URL/name 变更

## 快速启动

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 启动 Redis（本地或云服务，默认连接 `redis://localhost:6379`）

3. 启动服务
```bash
uvicorn easyscan-server.main:app --reload
```

4. 访问二维码页面
```
http://localhost:8000/{key}/qrcode
```

## 目录结构
```
├── easyscan-server/
│   ├── __init__.py
│   ├── main.py         # FastAPI 主入口
│   ├── domain.py       # Redis 读写与 key 生成
│   ├── type.py         # Pydantic 数据模型
│   ├── templates/
│   │   └── qrcode.html # 二维码页面模板
│   └── static/         # 静态资源（可选）
├── requirements.txt
├── pyproject.toml
├── README.md
```

## 环境变量
- `REDIS_URL`：Redis 连接地址（可选，默认 `redis://localhost:6379`）

## 依赖
- fastapi
- redis
- uvicorn
- pydantic
- jinja2

## License
AGPL-3.0

