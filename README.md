# AI 简历作品集网站

这是一个面向个人展示和求职沟通的 AI 简历作品集网站。项目包含公开作品集页面、AI 对话入口、简历下载、后台管理系统、媒体上传和 MySQL 数据持久化。

本 README 只描述传统部署方式：直接在服务器上安装 Python、Node.js、MySQL、Nginx，不使用 Docker。

## 功能概览

### 前台展示

- 个人简介、岗位定位、联系方式展示。
- 项目作品集列表和项目详情展示。
- 技术栈、项目背景、职责、功能、难点和解决方案展示。
- 当前简历 PDF 下载。
- 预设问题引导访客提问。
- AI 对话面板，通过后端转发到 Dify Chat API，并使用 SSE 流式返回回答。

### 后台管理

- 管理员登录，使用 JWT Bearer Token 鉴权。
- 作品项目管理：新增、编辑、删除、发布状态、排序、封面关联。
- 媒体资源管理：上传图片、视频、文档，关联项目或简历。
- 简历管理：上传多个简历版本，设置当前简历。
- 站点资料管理：维护姓名、标题、简介、邮箱、电话、链接等。
- 预设问题管理：维护前台 AI 对话的推荐问题。

### 后端能力

- FastAPI 提供公开 API、后台 API、健康检查和文件访问。
- SQLAlchemy + PyMySQL 连接 MySQL。
- `scripts/seed.py` 初始化表结构和示例数据。
- `/api/health` 检查服务进程。
- `/api/health/db` 检查 MySQL 连接和核心表是否存在。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | React 19、TypeScript、Vite |
| 后端 | Python 3.12、FastAPI、SQLAlchemy、Uvicorn |
| 数据库 | MySQL 8.x |
| AI 对话 | Dify Chat API、SSE |
| 部署 | Nginx 静态文件服务 + 反向代理、systemd 后台服务 |

## 目录结构

```text
myresume/
|-- backend/                 # FastAPI 后端
|   |-- app/                 # API、模型、配置、服务代码
|   |-- scripts/             # 数据库初始化和种子数据脚本
|   |-- tests/               # 后端测试
|   |-- pyproject.toml
|   `-- requirements.txt
|-- frontend/                # React + Vite 前端
|   |-- src/
|   |-- public/
|   |-- package.json
|   `-- vite.config.ts
|-- .env.example             # 环境变量示例
`-- README.md
```

## 访问路径

项目默认部署在 `/dify/` 子路径下：

| 地址 | 说明 |
| --- | --- |
| `/dify/` | 前台作品集 |
| `/dify/admin` | 后台管理 |
| `/dify/api/health` | 后端健康检查 |
| `/dify/api/health/db` | 数据库健康检查 |
| `/dify/uploads/` | 上传文件访问路径 |

如果你想部署在根路径 `/`，需要同步调整 `APP_ROOT_PATH`、`PUBLIC_API_BASE_URL`、`PUBLIC_UPLOAD_BASE_URL`、`VITE_API_BASE_URL`、`VITE_APP_BASE_PATH` 和 Nginx 配置。

## 本地开发安装

### 1. 准备环境

建议版本：

- Python 3.12+
- Node.js 20+
- MySQL 8.x
- Git

### 2. 克隆项目

```bash
git clone <your-repo-url> myresume
cd myresume
```

### 3. 初始化 MySQL

登录 MySQL：

```bash
mysql -uroot -p
```

创建数据库和用户：

```sql
CREATE DATABASE portfolio DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'portfolio_user'@'localhost' IDENTIFIED BY 'replace_with_a_strong_password';
GRANT ALL PRIVILEGES ON portfolio.* TO 'portfolio_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 配置后端环境变量

后端从当前工作目录读取 `.env`。本地开发时，把示例文件复制到 `backend/.env`：

```bash
cp .env.example backend/.env
```

编辑 `backend/.env`，至少修改这些值：

```env
SERVICE_NAME=portfolio-api
API_VERSION=1.0
API_TITLE="AI Resume Portfolio API"
CORS_ORIGINS=http://localhost:5173
APP_ROOT_PATH=/dify

DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=replace_with_your_dify_api_key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=replace_with_a_strong_password

ADMIN_JWT_SECRET=replace_with_a_long_random_secret
ADMIN_TOKEN_EXPIRE_SECONDS=86400

UPLOAD_DIR=uploads
PUBLIC_API_BASE_URL=/dify/api
PUBLIC_UPLOAD_BASE_URL=/dify/uploads
```

说明：

- `DIFY_API_KEY` 可以先留空，留空时 AI 对话会返回未配置错误，其他功能不受影响。
- `ADMIN_JWT_SECRET` 上线前必须改成足够长的随机字符串。
- `.env` 不要提交到代码仓库。

### 5. 安装并启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

验证：

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
```

默认后台账号：

```text
用户名：admin
密码：admin123
```

如果要在初始化时覆盖默认账号，请在运行种子脚本时传入环境变量：

```bash
SEED_ADMIN_USERNAME=admin SEED_ADMIN_PASSWORD='your_password' python scripts/seed.py
```

### 6. 安装并启动前端

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

本地访问：

```text
http://localhost:5173/dify/
http://localhost:5173/dify/admin
```

Vite 开发服务器会把 `/dify/api` 代理到 `http://127.0.0.1:8000/api`。

## 传统生产部署

下面以 Ubuntu / Debian 风格服务器为例，部署目录使用 `/var/www/myresume`。

### 1. 安装系统依赖

```bash
sudo apt update
sudo apt install -y git nginx mysql-server python3.12 python3.12-venv python3-pip nodejs npm
```

如果系统仓库里的 Node.js 版本太旧，请使用 NodeSource、nvm 或服务器发行版推荐方式安装 Node.js 20+。

### 2. 拉取代码

```bash
sudo mkdir -p /var/www
sudo chown -R $USER:$USER /var/www
cd /var/www
git clone <your-repo-url> myresume
cd myresume
```

### 3. 创建生产数据库

```bash
sudo mysql
```

```sql
CREATE DATABASE portfolio DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'portfolio_user'@'localhost' IDENTIFIED BY 'replace_with_a_strong_password';
GRANT ALL PRIVILEGES ON portfolio.* TO 'portfolio_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. 配置后端

```bash
cd /var/www/myresume/backend
cp ../.env.example .env
nano .env
```

生产环境建议配置：

```env
SERVICE_NAME=portfolio-api
API_VERSION=1.0
API_TITLE="AI Resume Portfolio API"
CORS_ORIGINS=https://your-domain.com
APP_ROOT_PATH=/dify

DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=replace_with_your_dify_api_key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=replace_with_a_strong_password

ADMIN_JWT_SECRET=replace_with_a_long_random_secret
ADMIN_TOKEN_EXPIRE_SECONDS=86400

UPLOAD_DIR=/var/www/myresume/backend/uploads
PUBLIC_API_BASE_URL=/dify/api
PUBLIC_UPLOAD_BASE_URL=/dify/uploads
```

如果暂时只用服务器 IP 访问，把 `CORS_ORIGINS` 改成实际访问地址，例如：

```env
CORS_ORIGINS=http://your-server-ip
```

### 5. 安装后端依赖并初始化数据

```bash
cd /var/www/myresume/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
```

如果你希望初始化默认管理员密码：

```bash
SEED_ADMIN_USERNAME=admin SEED_ADMIN_PASSWORD='your_password' python scripts/seed.py
```

### 6. 配置 systemd 后端服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/myresume-backend.service
```

写入：

```ini
[Unit]
Description=AI Resume Portfolio Backend
After=network.target mysql.service

[Service]
Type=simple
WorkingDirectory=/var/www/myresume/backend
EnvironmentFile=/var/www/myresume/backend/.env
ExecStart=/var/www/myresume/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myresume-backend
sudo systemctl status myresume-backend
```

查看日志：

```bash
sudo journalctl -u myresume-backend -f
```

### 7. 构建前端

```bash
cd /var/www/myresume/frontend
npm install
VITE_API_BASE_URL=/dify/api VITE_APP_BASE_PATH=/dify/ npm run build
```

构建产物会生成到：

```text
/var/www/myresume/frontend/dist
```

### 8. 配置 Nginx

创建站点配置：

```bash
sudo nano /etc/nginx/sites-available/myresume
```

写入以下配置，把 `your-domain.com` 换成你的域名；如果暂时没有域名，可以先写服务器 IP 或 `_`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/myresume/frontend/dist;
    index index.html;

    client_max_body_size 20m;

    location = /dify {
        return 301 /dify/;
    }

    location /dify/api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }

    location = /dify/api {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /dify/uploads/ {
        proxy_pass http://127.0.0.1:8000/dify/uploads/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /dify/docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Prefix /dify;
    }

    location /dify/redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Prefix /dify;
    }

    location /dify/openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Prefix /dify;
    }

    location /dify/ {
        try_files $uri $uri/ /dify/index.html;
    }

    location = / {
        return 302 /dify/;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/myresume /etc/nginx/sites-enabled/myresume
sudo nginx -t
sudo systemctl reload nginx
```

### 9. 验证部署

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
curl http://your-domain.com/dify/api/health
```

浏览器访问：

```text
http://your-domain.com/dify/
http://your-domain.com/dify/admin
```

后台默认账号是 `admin / admin123`，如果初始化时设置了 `SEED_ADMIN_PASSWORD`，则使用你设置的密码。上线后请尽快修改默认密码或重新初始化管理员密码。

## HTTPS

正式上线建议使用 HTTPS。以 Certbot 为例：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

签发 HTTPS 后，把 `backend/.env` 里的 `CORS_ORIGINS` 改成 HTTPS 域名：

```env
CORS_ORIGINS=https://your-domain.com
```

然后重启后端：

```bash
sudo systemctl restart myresume-backend
```

## 更新部署

```bash
cd /var/www/myresume
git pull

cd backend
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
sudo systemctl restart myresume-backend

cd ../frontend
npm install
VITE_API_BASE_URL=/dify/api VITE_APP_BASE_PATH=/dify/ npm run build

sudo nginx -t
sudo systemctl reload nginx
```

## 常用运维命令

### 查看后端状态

```bash
sudo systemctl status myresume-backend
sudo journalctl -u myresume-backend -f
```

### 检查接口

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/db
curl http://your-domain.com/dify/api/health
```

### 备份数据库

```bash
mysqldump -uportfolio_user -p portfolio > portfolio.sql
```

### 备份上传文件

```bash
tar -czf uploads.tar.gz /var/www/myresume/backend/uploads
```

### 恢复数据库

```bash
mysql -uportfolio_user -p portfolio < portfolio.sql
```

## 测试

### 后端测试

```bash
cd backend
source .venv/bin/activate
pytest
```

### 前端检查

```bash
cd frontend
npm run lint
npm run test
npm run build
```

## 常见问题

### 页面能打开，但接口请求失败

检查 Nginx 代理和后端服务：

```bash
sudo systemctl status myresume-backend
sudo journalctl -u myresume-backend -n 100
curl http://127.0.0.1:8000/api/health
curl http://your-domain.com/dify/api/health
```

重点确认：

- `myresume-backend` 是否运行。
- Nginx 的 `/dify/api/` 是否代理到 `http://127.0.0.1:8000/api/`。
- `backend/.env` 里的 `CORS_ORIGINS` 是否等于实际访问域名。

### `/dify/api/health` 正常，但 `/dify/api/health/db` 失败

说明后端进程正常，但数据库连接或表结构有问题。检查：

```bash
cd /var/www/myresume/backend
source .venv/bin/activate
python scripts/seed.py
```

同时确认 `backend/.env` 中的 MySQL 主机、端口、数据库名、用户名和密码。

### 后台登录失败

先确认数据库已经初始化：

```bash
cd /var/www/myresume/backend
source .venv/bin/activate
python scripts/seed.py
```

默认账号：

```text
admin / admin123
```

如果你用 `SEED_ADMIN_PASSWORD` 初始化过，请使用对应密码。

### 上传文件无法访问

确认后端上传目录和 Nginx 代理：

```bash
ls -lah /var/www/myresume/backend/uploads
curl http://your-domain.com/dify/uploads/resume/resume-current.pdf
```

Nginx 中 `/dify/uploads/` 应代理到：

```text
http://127.0.0.1:8000/dify/uploads/
```

### AI 对话不可用

检查 `backend/.env`：

```env
DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=your_dify_api_key
```

修改后重启后端：

```bash
sudo systemctl restart myresume-backend
```
