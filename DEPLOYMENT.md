# AI 简历作品集部署文档

本文档用于将本项目部署到一台 Linux 服务器。当前推荐部署方式是：

- 前端：React/Vite 构建后由 Nginx 容器提供静态文件服务
- 后端：FastAPI 容器运行在 `8000` 端口
- 数据库：MySQL 8 安装在服务器宿主机上
- 编排方式：Docker Compose

部署完成后，用户访问前端地址；前端容器里的 Nginx 会把 `/api` 和 `/uploads` 请求转发到后端容器。

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
宿主机 MySQL:3306
```

默认对外暴露端口由 `.env` 中的 `FRONTEND_PORT` 控制，默认值是 `8080`。

## 二、服务器准备

服务器需要安装：

- Docker
- Docker Compose plugin
- MySQL 8 或兼容版本
- Git，如果计划在服务器上直接拉取代码

验证 Docker：

```bash
docker --version
docker compose version
```

验证 MySQL：

```bash
mysql -u root -p -e "SELECT VERSION();"
```

## 三、获取项目代码

在服务器上克隆仓库：

```bash
git clone <your-repo-url> myresume
cd myresume
```

如果是手动上传项目目录，请确认至少包含这些文件和目录：

```text
backend/
frontend/
docker-compose.yml
.env.example
```

## 四、配置生产环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
nano .env
```

推荐生产配置模板：

```env
# Backend
SERVICE_NAME=portfolio-api
API_VERSION=1.0
API_TITLE="AI Resume Portfolio API"
CORS_ORIGINS=http://localhost:5173

DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=your_dify_api_key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=your_mysql_password

ADMIN_JWT_SECRET=replace_with_a_long_random_secret
ADMIN_TOKEN_EXPIRE_SECONDS=86400

UPLOAD_DIR=uploads
PUBLIC_UPLOAD_BASE_URL=/uploads

# Frontend
VITE_API_BASE_URL=/api

# Docker deployment
FRONTEND_PORT=8080
DOCKER_MYSQL_HOST=host.docker.internal
DOCKER_CORS_ORIGINS=http://your-server-ip:8080
```

如果绑定正式域名并启用 HTTPS：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

关键说明：

- `.env` 不要提交到代码仓库。
- `ADMIN_JWT_SECRET` 必须换成长随机字符串，生产环境不要留空。
- `DIFY_API_KEY` 如果不配置，AI 对话相关能力可能不可用。
- `DOCKER_MYSQL_HOST=host.docker.internal` 用于让后端容器访问宿主机 MySQL。
- `VITE_API_BASE_URL=/api` 表示前端通过同域 `/api` 调用后端。

## 五、创建 MySQL 数据库账号

登录 MySQL：

```bash
mysql -u root -p
```

创建应用账号并授权：

```sql
CREATE USER IF NOT EXISTS 'portfolio_user'@'%' IDENTIFIED BY 'your_mysql_password';
GRANT ALL PRIVILEGES ON portfolio.* TO 'portfolio_user'@'%';
FLUSH PRIVILEGES;
```

退出 MySQL：

```sql
exit;
```

确保这里的用户名、密码、数据库名和 `.env` 保持一致。

## 六、允许容器访问宿主机 MySQL

先检查 MySQL 当前监听地址：

```bash
sudo ss -ltnp | grep 3306
```

如果只看到 `127.0.0.1:3306`，Docker 容器通常无法访问宿主机 MySQL。需要修改 MySQL 配置文件，常见路径：

```text
/etc/mysql/mysql.conf.d/mysqld.cnf
/etc/my.cnf
```

找到或添加：

```ini
bind-address = 0.0.0.0
```

重启 MySQL：

```bash
sudo systemctl restart mysql
```

安全提醒：不要把 MySQL 的 `3306` 端口开放到公网。这里只是为了让同一台服务器上的 Docker 容器能访问宿主机 MySQL。

## 七、启动容器

在项目根目录执行：

```bash
docker compose up -d --build
```

查看容器状态：

```bash
docker compose ps
```

期望结果：

- `backend` 处于 running 或 healthy 状态
- `frontend` 处于 running 状态

如果 `frontend` 没有启动，通常是因为它依赖 `backend` 健康检查通过。先查看后端日志：

```bash
docker compose logs --tail=100 backend
```

## 八、初始化数据库

首次部署需要创建数据库表并写入初始数据：

```bash
docker compose exec backend python scripts/init_db.py
```

该脚本会执行：

- 创建配置中的 MySQL 数据库
- 创建 SQLAlchemy 数据表
- 写入作品集项目、站点资料、简历文件记录、提示问题和管理员账号

默认管理员账号：

```text
访问路径：http://your-server-ip:8080/admin
用户名：admin
密码：admin123
```

生产环境上线后，请尽快更换默认管理员密码。当前种子脚本支持通过 `SEED_ADMIN_USERNAME` 和 `SEED_ADMIN_PASSWORD` 覆盖默认账号，但需要在首次初始化前把这两个变量加入 `docker-compose.yml` 的 `backend.environment`。

## 九、验证部署

访问前台页面：

```text
http://your-server-ip:8080
```

访问后台页面：

```text
http://your-server-ip:8080/admin
```

验证后端健康检查：

```bash
curl http://your-server-ip:8080/api/health
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

验证文件访问：

```bash
curl -I http://your-server-ip:8080/uploads/resume/resume-current.pdf
```

如果初始化时服务器上没有源简历 PDF，该文件可能不存在；这不影响接口健康状态。

## 十、更新部署

进入项目目录：

```bash
cd myresume
```

拉取最新代码：

```bash
git pull
```

重新构建并启动：

```bash
docker compose up -d --build
```

如果后端模型、种子数据或数据库结构有变化，重新运行初始化脚本：

```bash
docker compose exec backend python scripts/init_db.py
```

最后验证：

```bash
docker compose ps
curl http://127.0.0.1:${FRONTEND_PORT:-8080}/api/health
```

## 十一、查看日志

查看后端日志：

```bash
docker compose logs -f backend
```

查看前端 Nginx 日志：

```bash
docker compose logs -f frontend
```

查看最近 100 行后端日志：

```bash
docker compose logs --tail=100 backend
```

## 十二、文件上传与持久化

上传文件保存在宿主机目录：

```text
backend/uploads/
```

`docker-compose.yml` 已配置卷挂载：

```yaml
volumes:
  - ./backend/uploads:/app/uploads
```

因此重新构建容器不会删除上传文件。备份时请同时备份：

- MySQL 数据库
- `backend/uploads/`
- 生产 `.env`

示例备份命令：

```bash
mysqldump -u portfolio_user -p portfolio > portfolio.sql
tar -czf uploads.tar.gz backend/uploads
cp .env env.backup
```

## 十三、域名和 HTTPS

简单测试时，可以直接开放：

```text
http://your-server-ip:8080
```

正式上线建议在宿主机上使用 Nginx 或 Caddy 做 HTTPS 反向代理：

```text
https://your-domain.com
  -> http://127.0.0.1:8080
  -> frontend 容器
  -> backend 容器
```

宿主机 Nginx 示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用域名后，修改 `.env`：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

然后重新构建：

```bash
docker compose up -d --build
```

## 十四、常见问题

### 1. 页面能打开，但接口请求失败

先检查健康接口：

```bash
curl http://127.0.0.1:${FRONTEND_PORT:-8080}/api/health
```

如果失败，查看后端日志：

```bash
docker compose logs --tail=100 backend
```

常见原因：

- MySQL 没有启动
- `.env` 中的 MySQL 用户名或密码错误
- `DOCKER_MYSQL_HOST` 没有设置为 `host.docker.internal`
- `DOCKER_CORS_ORIGINS` 和实际访问地址不一致

### 2. 后端连不上 MySQL

先在服务器宿主机测试账号：

```bash
mysql -u portfolio_user -p -h 127.0.0.1 -P 3306 portfolio
```

如果宿主机登录失败，优先修复 MySQL 账号、密码或权限。

如果宿主机能登录，但容器仍然失败，确认 `docker-compose.yml` 中存在：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

同时确认 MySQL 没有只监听 `127.0.0.1`。

### 3. 后台登录失败

确认已经运行初始化脚本：

```bash
docker compose exec backend python scripts/init_db.py
```

确认默认账号：

```text
admin / admin123
```

如果修改过种子账号，请使用 `SEED_ADMIN_USERNAME` 和 `SEED_ADMIN_PASSWORD` 对应的值。

### 4. 上传文件重启后丢失

检查宿主机目录是否存在：

```bash
ls -lah backend/uploads
```

检查容器挂载：

```bash
docker compose exec backend ls -lah /app/uploads
```

如果宿主机目录为空，说明文件可能没有成功写入挂载目录，继续查看后端上传接口日志。

### 5. 浏览器跨域报错

检查 `.env`：

```env
DOCKER_CORS_ORIGINS=http://your-server-ip:8080
```

或正式域名：

```env
DOCKER_CORS_ORIGINS=https://your-domain.com
```

修改后重启：

```bash
docker compose up -d --build
```

### 6. 前端构建失败

本地或服务器上单独验证前端：

```bash
cd frontend
npm ci
npm run build
```

如果 Docker 构建失败，查看构建日志中具体的 TypeScript 或依赖错误。

### 7. 后端启动失败

本地或服务器上单独验证后端：

```bash
cd backend
uv sync
uv run pytest
```

如果容器内失败，查看日志：

```bash
docker compose logs --tail=100 backend
```

## 十五、部署检查清单

- [ ] 服务器已安装 Docker 和 Docker Compose plugin。
- [ ] 服务器已安装并启动 MySQL。
- [ ] `.env` 已从 `.env.example` 复制并填入生产值。
- [ ] `ADMIN_JWT_SECRET` 已换成长随机字符串。
- [ ] `MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE` 与 MySQL 授权一致。
- [ ] `DOCKER_MYSQL_HOST=host.docker.internal`。
- [ ] `DOCKER_CORS_ORIGINS` 与实际访问地址一致。
- [ ] `docker compose up -d --build` 执行成功。
- [ ] `docker compose ps` 显示服务正常运行。
- [ ] `docker compose exec backend python scripts/init_db.py` 执行成功。
- [ ] `/api/health` 返回 `status: ok`。
- [ ] 前台页面可以访问。
- [ ] `/admin` 后台可以登录。
- [ ] MySQL 端口没有开放到公网。
- [ ] 已备份 `.env`、MySQL 数据和 `backend/uploads/`。
