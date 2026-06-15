---
title: AI 简历作品集后端 API 规格
version: 1.0
date_created: 2026-06-14
last_updated: 2026-06-14
owner: 卢官有
tags: [api, backend, python, mysql, dify, sse, portfolio]
---

# AI 简历作品集后端 API 规格

## 1. 目的与范围

本文档定义 AI 简历作品集网站的后端 API 契约，供 React 前端、Python 后端和数据库实现使用。

后端技术栈：

- 语言：Python
- 推荐框架：FastAPI
- 数据库：MySQL
- AI 服务：Dify Chat API
- 流式协议：SSE，Server-Sent Events
- 文件存储：MVP 使用服务器本地 `uploads/` 目录，MySQL 保存文件元数据

MVP 目标：

- 提供 AI 简历助手流式问答接口。
- 提供项目列表和项目详情接口。
- 提供媒体文件上传和访问接口。
- 提供 PDF 简历下载接口。
- 提供后台管理接口，用于维护项目、媒体、简历、站点配置和 AI 预设问题。
- 提供管理员登录和管理接口鉴权，防止公开访客修改内容。
- 保护 Dify API Key，不允许前端直接访问 Dify。

## 2. 基础约定

### 2.1 Base URL

开发环境：

```text
http://localhost:8000/api
```

生产环境：

```text
https://your-domain.com/api
```

### 2.2 数据格式

普通接口：

```text
Content-Type: application/json; charset=utf-8
```

文件上传接口：

```text
Content-Type: multipart/form-data
```

流式聊天接口：

```text
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
```

### 2.3 通用响应格式

非 SSE 接口统一返回：

```json
{
  "success": true,
  "data": {},
  "message": "ok"
}
```

错误响应：

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不合法",
    "details": {}
  }
}
```

### 2.4 通用错误码

| 错误码 | HTTP 状态码 | 说明 |
|---|---:|---|
| BAD_REQUEST | 400 | 请求格式错误 |
| UNAUTHORIZED | 401 | 未登录或登录已过期 |
| FORBIDDEN | 403 | 已登录但无权访问 |
| VALIDATION_ERROR | 422 | 参数校验失败 |
| NOT_FOUND | 404 | 资源不存在 |
| PAYLOAD_TOO_LARGE | 413 | 上传文件过大 |
| UNSUPPORTED_MEDIA_TYPE | 415 | 文件类型不支持 |
| DIFY_UPSTREAM_ERROR | 502 | Dify 上游服务错误 |
| INTERNAL_ERROR | 500 | 后端内部错误 |

## 3. API 列表

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 健康检查 | GET | `/health` | 检查后端服务状态 |
| AI 对话 | POST | `/chat/stream` | Dify SSE 流式聊天 |
| 项目 | GET | `/projects` | 获取项目列表 |
| 项目 | GET | `/projects/{project_id}` | 获取项目详情 |
| 媒体 | POST | `/media` | 上传图片、视频或文档 |
| 媒体 | GET | `/media/{media_id}` | 获取媒体元数据 |
| 媒体 | GET | `/media/{media_id}/file` | 访问媒体文件 |
| 简历 | GET | `/resume/current` | 获取当前简历信息 |
| 简历 | GET | `/resume/download` | 下载当前 PDF 简历 |
| 站点配置 | GET | `/site/profile` | 获取公开站点基础信息 |
| 预设问题 | GET | `/prompt-questions` | 获取公开 AI 预设问题 |
| 管理鉴权 | POST | `/admin/auth/login` | 管理员登录 |
| 管理鉴权 | POST | `/admin/auth/logout` | 管理员退出 |
| 管理鉴权 | GET | `/admin/auth/me` | 获取当前管理员信息 |
| 后台项目 | GET | `/admin/projects` | 管理端项目列表 |
| 后台项目 | POST | `/admin/projects` | 新增项目 |
| 后台项目 | PUT | `/admin/projects/{project_id}` | 更新项目 |
| 后台项目 | DELETE | `/admin/projects/{project_id}` | 软删除项目 |
| 后台媒体 | GET | `/admin/media` | 管理端媒体列表 |
| 后台媒体 | POST | `/admin/media` | 上传媒体文件 |
| 后台媒体 | PUT | `/admin/media/{media_id}` | 更新媒体元数据 |
| 后台媒体 | DELETE | `/admin/media/{media_id}` | 软删除媒体 |
| 后台简历 | GET | `/admin/resumes` | 简历文件列表 |
| 后台简历 | POST | `/admin/resumes` | 上传简历 PDF |
| 后台简历 | PUT | `/admin/resumes/{resume_id}/current` | 设置当前简历 |
| 后台站点配置 | GET | `/admin/site/profile` | 获取站点配置 |
| 后台站点配置 | PUT | `/admin/site/profile` | 更新站点配置 |
| 后台预设问题 | GET | `/admin/prompt-questions` | 管理端预设问题列表 |
| 后台预设问题 | POST | `/admin/prompt-questions` | 新增预设问题 |
| 后台预设问题 | PUT | `/admin/prompt-questions/{question_id}` | 更新预设问题 |
| 后台预设问题 | DELETE | `/admin/prompt-questions/{question_id}` | 删除预设问题 |

## 4. 健康检查

### 4.1 GET `/health`

用于检查服务是否正常启动。

响应示例：

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

验收标准：

- 服务启动后请求 `/api/health` 返回 HTTP 200。
- 响应中 `data.status` 必须为 `ok`。

## 5. AI 简历助手接口

### 5.1 POST `/chat/stream`

调用 Dify Chat API，并将 Dify 的流式响应转发给前端。

#### 请求头

```text
Content-Type: application/json
Accept: text/event-stream
```

#### 请求体

```json
{
  "message": "请介绍一下你的核心项目",
  "conversation_id": "",
  "visitor_id": "web-visitor-001"
}
```

#### 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| message | string | 是 | 用户输入的问题，长度 1-1000 |
| conversation_id | string | 否 | Dify 会话 ID，首次对话可为空 |
| visitor_id | string | 否 | 访问者 ID，用于传给 Dify user 字段 |

#### 后端调用 Dify 的请求体

```json
{
  "inputs": {},
  "query": "请介绍一下你的核心项目",
  "response_mode": "streaming",
  "conversation_id": "",
  "user": "web-visitor-001"
}
```

#### SSE 返回事件

后端向前端输出标准 SSE 格式：

```text
event: message
data: {"answer":"我是卢官有，方向是 AI 全栈开发...","conversation_id":"dify-conv-id"}

event: message
data: {"answer":"我的核心项目包括 Dify 简历助手...","conversation_id":"dify-conv-id"}

event: done
data: {"conversation_id":"dify-conv-id"}
```

错误事件：

```text
event: error
data: {"code":"DIFY_UPSTREAM_ERROR","message":"Dify 服务暂时不可用"}
```

#### 前端处理要求

- 前端应将所有 `event: message` 的 `answer` 增量追加到当前 AI 回复中。
- 前端应保存 `conversation_id`，用于下一轮连续对话。
- 收到 `event: done` 后，输入框恢复可用。
- 收到 `event: error` 后，展示错误信息和重试按钮。

#### 验收标准

- Dify API Key 不出现在前端请求或前端源码中。
- 接口必须返回 `text/event-stream`。
- 用户输入合法问题后，前端可以逐步看到 AI 回复。
- Dify 上游失败时，后端必须返回 `event: error`，不能让连接无响应。

## 6. 项目接口

### 6.1 GET `/projects`

获取作品集项目列表。

#### Query 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| featured | boolean | 否 | 是否只返回精选项目 |
| limit | integer | 否 | 返回数量，默认 20 |

#### 响应示例

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "slug": "ai-resume-assistant",
      "title": "AI 简历助手",
      "subtitle": "可追问式智能简历作品集",
      "summary": "基于 Dify API 的 SSE 流式简历助手。",
      "project_type": "AI 应用",
      "role": "前端交互、后端代理、Dify 接入",
      "tech_stack": ["React", "Python", "Dify", "SSE"],
      "cover_media": {
        "id": 11,
        "url": "/uploads/projects/ai-resume-cover.png",
        "media_type": "image"
      },
      "is_featured": true,
      "sort_order": 10
    }
  ],
  "message": "ok"
}
```

#### 验收标准

- 默认按 `sort_order DESC, id DESC` 排序。
- `featured=true` 时只返回 `is_featured = 1` 的项目。
- 每个项目必须包含 `id`、`title`、`summary`、`tech_stack`。

### 6.2 GET `/projects/{project_id}`

获取项目详情。

#### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| project_id | integer | 项目 ID |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "id": 1,
    "slug": "ai-resume-assistant",
    "title": "AI 简历助手",
    "subtitle": "可追问式智能简历作品集",
    "summary": "基于 Dify API 的 SSE 流式简历助手。",
    "background": "传统 PDF 简历无法支持追问。",
    "goals": "让 HR 和面试官可以直接通过 AI 了解项目经历。",
    "features": [
      "预设问题",
      "SSE 流式回复",
      "连续追问",
      "简历下载"
    ],
    "role": "负责前端页面、后端代理、Dify 接入和移动端适配。",
    "challenges": [
      "SSE 流式响应解析",
      "Dify API Key 隔离",
      "移动端首屏交互布局"
    ],
    "solutions": [
      "使用 Python 后端代理 Dify",
      "前端使用 ReadableStream 逐步渲染",
      "首屏优先展示 AI 聊天模块"
    ],
    "tech_stack": ["React", "Python", "Dify", "SSE"],
    "links": [
      {
        "label": "在线 Demo",
        "url": "https://example.com",
        "link_type": "demo"
      }
    ],
    "media": [
      {
        "id": 11,
        "media_type": "image",
        "purpose": "cover",
        "url": "/uploads/projects/ai-resume-cover.png",
        "alt_text": "AI 简历助手封面截图"
      },
      {
        "id": 12,
        "media_type": "video",
        "purpose": "demo",
        "url": "/uploads/projects/ai-resume-demo.mp4",
        "alt_text": "AI 简历助手演示视频"
      }
    ]
  },
  "message": "ok"
}
```

#### 验收标准

- 项目不存在时返回 404。
- 详情必须包含项目基础字段和媒体列表。
- `tech_stack`、`features`、`challenges`、`solutions` 返回数组。

## 7. 媒体接口

### 7.1 POST `/media`

上传项目图片、项目视频或 PDF 简历。

MVP 可只允许开发者本地使用，不向公开用户暴露。

#### 请求格式

```text
Content-Type: multipart/form-data
```

#### 表单字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| file | file | 是 | 上传文件 |
| media_type | string | 是 | image / video / document |
| purpose | string | 否 | cover / screenshot / demo / resume / architecture |
| project_id | integer | 否 | 关联项目 ID |
| alt_text | string | 否 | 图片或视频说明 |

#### 文件限制

| 类型 | 允许格式 | 最大大小 |
|---|---|---:|
| image | jpg, jpeg, png, webp | 10 MB |
| video | mp4, webm | 50 MB |
| document | pdf | 20 MB |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "id": 21,
    "media_type": "image",
    "purpose": "cover",
    "original_filename": "cover.png",
    "url": "/uploads/projects/cover.png",
    "mime_type": "image/png",
    "file_size": 238102,
    "project_id": 1
  },
  "message": "uploaded"
}
```

#### 验收标准

- 不支持的文件类型返回 415。
- 超过大小限制返回 413。
- 成功上传后，MySQL 必须保存媒体元数据。
- 返回的 `url` 必须可被前端访问。

### 7.2 GET `/media/{media_id}`

获取媒体元数据。

响应示例：

```json
{
  "success": true,
  "data": {
    "id": 21,
    "media_type": "image",
    "purpose": "cover",
    "original_filename": "cover.png",
    "url": "/uploads/projects/cover.png",
    "mime_type": "image/png",
    "file_size": 238102,
    "project_id": 1,
    "created_at": "2026-06-14T10:00:00"
  },
  "message": "ok"
}
```

### 7.3 GET `/media/{media_id}/file`

访问媒体文件。

要求：

- 图片返回对应图片 MIME 类型。
- 视频返回对应视频 MIME 类型。
- PDF 返回 `application/pdf`。
- 文件不存在时返回 404。

## 8. 简历接口

### 8.1 GET `/resume/current`

获取当前简历文件信息。

响应示例：

```json
{
  "success": true,
  "data": {
    "id": 31,
    "title": "卢官有-AI全栈开发-简历-v3.pdf",
    "media_id": 21,
    "download_url": "/api/resume/download",
    "updated_at": "2026-06-14T10:00:00"
  },
  "message": "ok"
}
```

### 8.2 GET `/resume/download`

下载当前 PDF 简历。

要求：

- 返回 `application/pdf`。
- 建议响应头包含：

```text
Content-Disposition: attachment; filename="resume.pdf"
```

## 9. 站点配置与预设问题公开接口

### 9.1 GET `/site/profile`

获取公开作品集基础信息，用于前端渲染候选人摘要、联系方式和外部链接。

响应示例：

```json
{
  "success": true,
  "data": {
    "owner_name": "卢官有",
    "headline": "AI 应用开发 / 前端工程 / Python 后端",
    "summary": "把传统简历改成可追问的 AI 对话入口。",
    "email": "example@email.com",
    "phone": "",
    "wechat": "",
    "github_url": "https://github.com/example",
    "portfolio_url": "https://example.com"
  },
  "message": "ok"
}
```

### 9.2 GET `/prompt-questions`

获取公开展示的 AI 预设问题。

响应示例：

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "question": "你最适合什么岗位？为什么？",
      "sort_order": 100
    }
  ],
  "message": "ok"
}
```

## 10. 后台鉴权接口

后台管理接口路径统一以 `/admin` 开头。除 `/admin/auth/login` 外，所有后台接口必须携带管理员登录凭证。

MVP 推荐使用 Bearer Token：

```text
Authorization: Bearer <admin_access_token>
```

### 10.1 POST `/admin/auth/login`

管理员登录。

请求体：

```json
{
  "username": "admin",
  "password": "your-password"
}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "access_token": "jwt-token",
    "token_type": "bearer",
    "expires_in": 86400,
    "admin": {
      "id": 1,
      "username": "admin",
      "display_name": "管理员"
    }
  },
  "message": "ok"
}
```

验收标准：

- 用户名或密码错误时返回 401。
- 密码必须以哈希形式存储，不能明文存储。
- 登录接口不能返回 password_hash。

### 10.2 POST `/admin/auth/logout`

管理员退出。MVP 如果使用无状态 JWT，可由前端删除 token；后端仍提供该接口作为统一契约。

### 10.3 GET `/admin/auth/me`

获取当前管理员信息。

## 11. 后台项目管理接口

### 11.1 GET `/admin/projects`

返回所有未软删除项目，可按状态筛选。

Query 参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| status | string | 否 | draft / published / hidden |
| keyword | string | 否 | 按标题或摘要搜索 |
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20 |

### 11.2 POST `/admin/projects`

新增项目。

请求体：

```json
{
  "slug": "ai-resume-assistant",
  "title": "AI 简历助手",
  "subtitle": "可追问式智能简历作品集",
  "summary": "基于 Dify API 的 SSE 流式简历助手。",
  "project_type": "AI 应用",
  "background": "传统 PDF 简历无法支持追问。",
  "goals": "让 HR 和面试官可以直接通过 AI 了解项目经历。",
  "role": "负责前端页面、后端代理、Dify 接入和移动端适配。",
  "features": ["预设问题", "SSE 流式回复"],
  "challenges": ["SSE 流式响应解析", "Dify API Key 隔离"],
  "solutions": ["使用 Python 后端代理 Dify"],
  "tech_stack": ["React", "Python", "Dify", "SSE"],
  "links": [],
  "cover_media_id": 11,
  "is_featured": true,
  "sort_order": 100,
  "status": "published"
}
```

### 11.3 PUT `/admin/projects/{project_id}`

更新项目。请求体字段与新增项目一致，允许部分更新。

### 11.4 DELETE `/admin/projects/{project_id}`

软删除项目，设置 `deleted_at`，不立即删除关联媒体文件。

验收标准：

- 未登录访问任一后台项目接口返回 401。
- 新增项目后，公开 `/api/projects` 能看到已发布且精选的项目。
- 隐藏状态项目不出现在公开接口中。
- 删除项目后公开接口不再返回该项目。

## 12. 后台媒体管理接口

### 12.1 GET `/admin/media`

返回媒体资源列表。

Query 参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| media_type | string | 否 | image / video / document |
| project_id | integer | 否 | 项目 ID |
| purpose | string | 否 | cover / screenshot / demo / resume / architecture |

### 12.2 POST `/admin/media`

上传媒体文件。该接口替代公开 `POST /media`，MVP 阶段只允许管理员上传。

表单字段与 `POST /media` 一致。

### 12.3 PUT `/admin/media/{media_id}`

更新媒体元数据，例如 `purpose`、`project_id`、`alt_text`、`sort_order`、`status`。

### 12.4 DELETE `/admin/media/{media_id}`

软删除媒体。MVP 不立即删除物理文件。

## 13. 后台简历管理接口

### 13.1 GET `/admin/resumes`

获取简历文件列表。

### 13.2 POST `/admin/resumes`

上传 PDF 简历，并在 `media_assets` 和 `resume_files` 中创建记录。

表单字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| file | file | 是 | PDF 文件 |
| title | string | 是 | 简历标题 |
| version_label | string | 否 | 版本，例如 v3 |
| set_current | boolean | 否 | 是否设为当前简历 |

### 13.3 PUT `/admin/resumes/{resume_id}/current`

设置当前默认简历。设置成功后，公开 `/api/resume/download` 下载该版本。

## 14. 后台站点配置接口

### 14.1 GET `/admin/site/profile`

获取站点基础配置。

### 14.2 PUT `/admin/site/profile`

更新站点基础配置。

请求体：

```json
{
  "owner_name": "卢官有",
  "headline": "AI 应用开发 / 前端工程 / Python 后端",
  "summary": "把传统简历改成可追问的 AI 对话入口。",
  "email": "example@email.com",
  "phone": "",
  "wechat": "",
  "github_url": "",
  "portfolio_url": ""
}
```

## 15. 后台 AI 预设问题接口

### 15.1 GET `/admin/prompt-questions`

获取全部预设问题，包括隐藏项。

### 15.2 POST `/admin/prompt-questions`

新增预设问题。

请求体：

```json
{
  "question": "你最适合什么岗位？为什么？",
  "category": "positioning",
  "sort_order": 100,
  "status": "published"
}
```

### 15.3 PUT `/admin/prompt-questions/{question_id}`

更新预设问题。

### 15.4 DELETE `/admin/prompt-questions/{question_id}`

软删除预设问题。

## 16. 安全与环境变量

后端必须使用环境变量保存敏感信息：

```text
DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=<your-dify-api-key>
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=change_me
ADMIN_JWT_SECRET=change_me_to_a_long_random_secret
ADMIN_TOKEN_EXPIRE_SECONDS=86400
UPLOAD_DIR=uploads
PUBLIC_UPLOAD_BASE_URL=/uploads
```

要求：

- 前端不得出现 `DIFY_API_KEY`。
- 后端不得把 MySQL 密码返回给前端。
- 管理员密码必须哈希存储，禁止明文保存。
- 后台接口必须校验管理员 token。
- 上传文件名必须重新生成，不能直接使用用户原始文件名作为存储文件名。
- 文件访问路径不能允许 `../` 路径穿越。

## 17. 测试策略

### 17.1 接口测试

必须覆盖：

- `/api/health` 返回 200。
- `/api/projects` 返回数组。
- `/api/projects/{id}` 返回详情。
- `/api/chat/stream` 返回 `text/event-stream`。
- `/api/media` 拒绝不支持文件类型。
- `/api/resume/download` 返回 PDF。
- `/api/site/profile` 返回站点基础信息。
- `/api/prompt-questions` 返回已发布预设问题。
- `/api/admin/auth/login` 正确账号返回 token，错误账号返回 401。
- 未登录访问 `/api/admin/projects` 返回 401。
- 登录后可以新增、编辑、软删除项目。
- 登录后可以上传媒体并关联项目。

### 17.2 SSE 测试

必须验证：

- 输入合法 message 后，返回至少一个 `event: message`。
- 正常结束时返回 `event: done`。
- Dify 异常时返回 `event: error`。

### 17.3 后台管理测试

必须验证：

- 管理员登录后刷新页面仍能访问后台，token 过期后需要重新登录。
- 后台新增项目后，公开项目列表能看到已发布项目。
- 后台隐藏项目后，公开项目列表不再展示该项目。
- 后台上传截图后，项目详情媒体数组包含该截图。
- 后台上传新版简历并设为当前后，公开简历下载返回新版 PDF。

## 18. 相关文档

- [AI 简历作品集网站 PRD](../AI简历作品集网站PRD.md)
- [MySQL 表结构规格](./spec-data-portfolio-mysql.md)
