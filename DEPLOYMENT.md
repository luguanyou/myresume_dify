# AI 简历作品集最简部署文档

这份文档走最省心的路线：前端、后端、MySQL 全部交给 Docker Compose 管理。你不需要知道一台远程 MySQL 的旧密码，只需要在 `.env` 里设置一组新的数据库密码。

## 一、部署架构

```text
Browser
  |
  v
服务器公网端口，例如 8080 或 443
  |
  v
frontend 容器，Nginx:80
  |-- 静态文件：/usr/share/nginx/html
  |-- 代理接口：/api -> backend:8000
  |-- 代理文件：/uploads -> backend:8000
  v
backend 容器，FastAPI:8000
  |
  v
mysql 容器，MySQL:3306
```

默认只对外暴露前端端口 `8080`。MySQL 不会暴露到公网。

## 二、服务器准备

服务器只需要安装：

- Docker
- Docker Compose plugin
- Git，如果你要在服务器上直接拉代码

验证 Docker：

```bash
docker --version
docker compose version
```

## 三、获取项目代码

```bash
git clone <your-repo-url> myresume
cd myresume
```

如果是手动上传项目目录，请确认至少包含：

```text
backend/
frontend/
docker-compose.yml
.env.example
```

## 四、配置环境变量

复制示例文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
nano .env
```

最小生产配置示例：

```env
SERVICE_NAME=portfolio-api
API_VERSION=1.0
API_TITLE="AI Resume Portfolio API"

DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=

MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=换成一个新的强密码
MYSQL_ROOT_PASSWORD=再换成另一个新的强密码

ADMIN_JWT_SECRET=换成一串很长的随机字符串
ADMIN_TOKEN_EXPIRE_SECONDS=86400

UPLOAD_DIR=uploads
PUBLIC_UPLOAD_BASE_URL=/uploads

VITE_API_BASE_URL=/api
FRONTEND_PORT=8080
DOCKER_CORS_ORIGINS=http://你的服务器IP:8080
```

如果有正式域名和 HTTPS：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

关键点：

- `.env` 不要提交到代码仓库。
- `MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD` 是新密码，不用找旧数据库密码。
- `ADMIN_JWT_SECRET` 必须换成长随机字符串。
- `DIFY_API_KEY` 可以先留空，只会影响 AI 对话相关能力。

## 五、启动服务

在项目根目录执行：

```bash
docker compose up -d --build
```

查看状态：

```bash
docker compose ps
```

期望看到 `mysql`、`backend`、`frontend` 都是 running 或 healthy。

如果失败，先看日志：

```bash
docker compose logs --tail=100 mysql
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
```

## 六、初始化数据库

首次部署需要创建表和初始数据：

```bash
docker compose exec backend python scripts/init_db.py
```

默认后台账号：

```text
访问路径：http://你的服务器IP:8080/admin
用户名：admin
密码：admin123
```

上线后请尽快在后台改掉默认密码。

## 七、验证部署

访问前台：

```text
http://你的服务器IP:8080
```

访问后台：

```text
http://你的服务器IP:8080/admin
```

验证接口：

```bash
curl http://127.0.0.1:8080/api/health
```

期望返回：

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "portfolio-api",
    "version": "1.0"
  },
  "message": "ok"
}
```

## 八、更新部署

```bash
git pull
docker compose up -d --build
docker compose exec backend python scripts/init_db.py
```

重新验证：

```bash
docker compose ps
curl http://127.0.0.1:8080/api/health
```

## 九、数据持久化和备份

MySQL 数据保存在 Docker volume：

```text
mysql_data
```

上传文件保存在宿主机目录：

```text
backend/uploads/
```

建议定期备份：

```bash
docker compose exec mysql mysqldump -uroot -p portfolio > portfolio.sql
tar -czf uploads.tar.gz backend/uploads
cp .env env.backup
```

## 十、忘记数据库密码怎么办

如果你使用的是这份 Compose 部署，通常最简单是：

1. 如果不需要保留旧数据，直接换 `.env` 里的 `MYSQL_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`，然后删除旧 volume 后重建：

```bash
docker compose down
docker volume rm myresume_mysql_data
docker compose up -d --build
docker compose exec backend python scripts/init_db.py
```

2. 如果必须保留旧数据，不要删 volume。需要进入 MySQL 容器用 root 或跳过权限的方式重置密码，步骤更复杂，建议先备份再操作。

## 十一、域名和 HTTPS

简单测试可以直接用：

```text
http://你的服务器IP:8080
```

正式上线建议在服务器上用 Nginx 或 Caddy 做 HTTPS 反向代理：

```text
https://your-domain.com -> http://127.0.0.1:8080
```

启用域名后，把 `.env` 改成：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

然后重启：

```bash
docker compose up -d --build
```

## 十二、常见问题

### 页面能打开，但接口失败

```bash
curl http://127.0.0.1:8080/api/health
docker compose logs --tail=100 backend
```

常见原因：

- 后端容器没有启动。
- `.env` 的 `DOCKER_CORS_ORIGINS` 和访问地址不一致。
- 数据库还没有初始化，需要运行 `docker compose exec backend python scripts/init_db.py`。

### 后台登录失败

先确认已经初始化数据库：

```bash
docker compose exec backend python scripts/init_db.py
```

默认账号是：

```text
admin / admin123
```

### 上传文件重启后丢失

检查挂载目录：

```bash
ls -lah backend/uploads
docker compose exec backend ls -lah /app/uploads
```

### 端口被占用

修改 `.env`：

```env
FRONTEND_PORT=8081
DOCKER_CORS_ORIGINS=http://你的服务器IP:8081
```

然后重启：

```bash
docker compose up -d --build
```
