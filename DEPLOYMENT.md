# AI 简历作品集最简部署文档

这份文档走“服务器已有 MySQL”的路线：前端和后端交给 Docker Compose 管理，数据库使用 Linux 服务器上已经安装好的 MySQL。

## 一、部署架构

```text
Browser
  |
  v
服务器公网端口，例如 8180 或 443
  |
  v
frontend 容器，Nginx:80
  |-- 静态文件：/usr/share/nginx/html/dify
  |-- 代理接口：/dify/api -> backend:8000/api
  |-- 代理文件：/dify/uploads -> backend:8000/dify/uploads
  v
backend 容器，FastAPI:8000
  |
  v
Linux 宿主机上的 MySQL:3306
```

默认只对外暴露前端端口 `8180`。MySQL 不需要暴露到公网，但要允许 Docker 后端容器从宿主机网关访问。

## 二、服务器准备

服务器只需要安装：

- Docker
- Docker Compose plugin
- MySQL Server，也就是你已经装好的远程服务器 MySQL
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

先在服务器 MySQL 里准备数据库和账号。如果你已经有可用账号，可以跳过创建用户，只确认它有 `portfolio` 数据库权限。

```bash
sudo mysql
```

```sql
CREATE DATABASE IF NOT EXISTS portfolio DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'portfolio_user'@'%' IDENTIFIED BY '换成服务器 MySQL 用户密码';
GRANT ALL PRIVILEGES ON portfolio.* TO 'portfolio_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

这里用 `'%'` 是因为后端跑在 Docker 容器里，连到宿主机 MySQL 时通常不会被 MySQL 识别成 `localhost`。

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

MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=换成服务器 MySQL 里这个用户的密码

ADMIN_JWT_SECRET=换成一串很长的随机字符串
ADMIN_TOKEN_EXPIRE_SECONDS=86400

UPLOAD_DIR=uploads
APP_ROOT_PATH=/dify
PUBLIC_API_BASE_URL=/dify/api
PUBLIC_UPLOAD_BASE_URL=/dify/uploads

VITE_API_BASE_URL=/dify/api
VITE_APP_BASE_PATH=/dify/
FRONTEND_PORT=8180
DOCKER_CORS_ORIGINS=http://你的服务器IP:8180
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
```

如果有正式域名和 HTTPS：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

关键点：

- `.env` 不要提交到代码仓库。
- `MYSQL_HOST=host.docker.internal` 表示后端容器连接 Linux 宿主机上的 MySQL。
- `MYSQL_USER` 和 `MYSQL_PASSWORD` 要填写服务器 MySQL 中真实存在、并且有 `portfolio` 数据库权限的账号。
- `ADMIN_JWT_SECRET` 必须换成长随机字符串。
- `DIFY_API_KEY` 可以先留空，只会影响 AI 对话相关能力。
- `PIP_INDEX_URL` 和 `NPM_CONFIG_REGISTRY` 用于加快国内服务器安装 Python/npm 依赖。

如果你的 MySQL 只监听 `127.0.0.1`，Docker 容器可能连不上。需要让 MySQL 监听宿主机网关地址或 `0.0.0.0`，并用防火墙保证 `3306` 不对公网开放。

## 五、启动服务

在项目根目录执行：

```bash
docker compose up -d --build
```

### 构建特别慢或卡在下载镜像

如果服务器构建卡了很久，先按 `Ctrl+C` 停掉当前构建，然后拉取最新代码再重建：

```bash
git pull
docker compose build --progress=plain --no-cache backend frontend
docker compose up -d
```

当前后端镜像不再依赖 `ghcr.io/astral-sh/uv`，默认使用清华 PyPI 镜像；前端默认使用 npmmirror。第一次构建仍然需要下载 `python`、`node`、`nginx` 基础镜像，但不应该再卡几个小时。

查看状态：

```bash
docker compose ps
```

期望看到 `backend`、`frontend` 都是 running 或 healthy。

如果失败，先看日志：

```bash
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
访问路径：http://你的服务器IP:8180/dify/admin
用户名：admin
密码：admin123
```

上线后请尽快在后台改掉默认密码。

## 七、验证部署

访问前台：

```text
http://你的服务器IP:8180/dify/
```

访问后台：

```text
http://你的服务器IP:8180/dify/admin
```

验证接口：

```bash
curl http://127.0.0.1:8180/dify/api/health
curl http://127.0.0.1:8180/dify/api/health/db
```

第一个接口只说明后端进程正常；第二个接口会检查 MySQL 是否能连接、核心表是否已经创建。两个接口都正常后，作品、简历、后台登录这类依赖数据库的接口才应该正常。

`/dify/api/health` 期望返回：

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
curl http://127.0.0.1:8180/dify/api/health
curl http://127.0.0.1:8180/dify/api/health/db
```

## 九、数据持久化和备份

MySQL 数据保存在服务器本机 MySQL 的数据目录中，不由 Docker Compose 管理。

上传文件保存在宿主机目录：

```text
backend/uploads/
```

建议定期备份：

```bash
mysqldump -uportfolio_user -p portfolio > portfolio.sql
tar -czf uploads.tar.gz backend/uploads
cp .env env.backup
```

## 十、忘记数据库密码怎么办

这份 Compose 不再管理 MySQL 容器，所以数据库密码需要在服务器本机 MySQL 里处理。通常做法是用服务器上的 MySQL root 或 sudo 权限登录后修改用户密码，然后同步更新项目根目录的 `.env`：

```bash
sudo mysql
```

```sql
ALTER USER 'portfolio_user'@'%' IDENTIFIED BY '新的强密码';
FLUSH PRIVILEGES;
```

如果你的用户是 `'portfolio_user'@'localhost'` 或其他 host，请按实际用户记录修改。改完 `.env` 后重启后端：

```bash
docker compose up -d --build backend
docker compose exec backend python scripts/init_db.py
```

## 十一、域名和 HTTPS

简单测试可以直接用：

```text
http://你的服务器IP:8180/dify/
```

正式上线建议在服务器上用 Nginx 或 Caddy 做 HTTPS 反向代理：

```text
https://your-domain.com -> http://127.0.0.1:8180
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
curl http://127.0.0.1:8180/dify/api/health
curl http://127.0.0.1:8180/dify/api/health/db
docker compose logs --tail=100 backend
```

如果 `/dify/api/health` 正常，但 `/dify/api/health/db` 返回 `503`，问题通常在数据库配置或初始化，而不是前端。

常见原因：

- 后端容器没有启动。
- `.env` 的 `DOCKER_CORS_ORIGINS` 和访问地址不一致。
- 后端容器连不上宿主机 MySQL，检查 `MYSQL_HOST`、MySQL 监听地址、用户授权和防火墙。
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
FRONTEND_PORT=8181
DOCKER_CORS_ORIGINS=http://你的服务器IP:8181
```

然后重启：

```bash
docker compose up -d --build
```
