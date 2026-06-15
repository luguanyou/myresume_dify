---
title: AI 简历作品集 MySQL 表结构规格
version: 1.0
date_created: 2026-06-14
last_updated: 2026-06-14
owner: 卢官有
tags: [data, mysql, schema, portfolio, media, dify]
---

# AI 简历作品集 MySQL 表结构规格

## 1. 目的与范围

本文档定义 AI 简历作品集网站 MVP 版本的 MySQL 数据库表结构。

数据库主要支持：

- 项目列表与项目详情展示。
- 项目图片、视频、PDF 简历等媒体资源管理。
- 当前简历文件配置。
- 后台管理员登录与内容管理。
- 站点基础信息配置。
- AI 预设问题维护。
- AI 对话日志，可选，用于排查问题和优化预设问题。

MVP 不包含：

- 公开用户登录注册。
- 多管理员角色和复杂权限系统。
- 多用户账号体系。
- 评论系统。
- 复杂 CMS。

## 2. 数据库约定

### 2.1 数据库名称

```sql
CREATE DATABASE IF NOT EXISTS portfolio
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 2.2 通用字段约定

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT UNSIGNED | 主键，自增 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| deleted_at | DATETIME NULL | 软删除时间，可为空 |

### 2.3 状态字段约定

`status` 使用字符串枚举：

| 值 | 说明 |
|---|---|
| draft | 草稿 |
| published | 已发布 |
| hidden | 隐藏 |

### 2.4 JSON 字段约定

以下字段使用 MySQL JSON 类型：

- `tech_stack`
- `features`
- `challenges`
- `solutions`
- `links`
- `metadata`

后端返回给前端时必须转换为数组或对象，不能返回 JSON 字符串。

## 3. 表清单

| 表名 | 说明 | MVP 必需 |
|---|---|---|
| projects | 项目基础信息与详情内容 | 是 |
| media_assets | 图片、视频、PDF 等媒体资源 | 是 |
| resume_files | 当前简历文件配置 | 是 |
| admin_users | 后台管理员账号 | 是 |
| site_profile | 站点基础信息配置 | 是 |
| prompt_questions | AI 预设问题 | 是 |
| chat_logs | AI 对话日志 | 可选 |
| admin_audit_logs | 后台操作审计日志 | 可选 |

## 4. projects 表

### 4.1 用途

保存作品集项目的基础信息、详情内容、技术栈和展示排序。

### 4.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS projects (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '项目 ID',
  slug VARCHAR(100) NOT NULL COMMENT '项目唯一标识，用于 URL 或前端定位',
  title VARCHAR(120) NOT NULL COMMENT '项目名称',
  subtitle VARCHAR(200) NULL COMMENT '项目副标题',
  summary VARCHAR(500) NOT NULL COMMENT '项目一句话或短摘要',
  project_type VARCHAR(60) NOT NULL COMMENT '项目类型，例如 AI 应用、3D 前端、后端项目',
  background TEXT NULL COMMENT '项目背景',
  goals TEXT NULL COMMENT '项目目标',
  role TEXT NULL COMMENT '个人职责',
  features JSON NULL COMMENT '主要功能数组',
  challenges JSON NULL COMMENT '技术难点数组',
  solutions JSON NULL COMMENT '解决方案数组',
  tech_stack JSON NOT NULL COMMENT '技术栈数组',
  links JSON NULL COMMENT '相关链接数组，例如 Demo、GitHub、文档',
  cover_media_id BIGINT UNSIGNED NULL COMMENT '封面媒体 ID，关联 media_assets.id',
  is_featured TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否精选项目',
  sort_order INT NOT NULL DEFAULT 0 COMMENT '排序值，越大越靠前',
  status VARCHAR(30) NOT NULL DEFAULT 'published' COMMENT '状态：draft/published/hidden',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '软删除时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_projects_slug (slug),
  KEY idx_projects_status_sort (status, sort_order, id),
  KEY idx_projects_featured_sort (is_featured, sort_order, id),
  KEY idx_projects_cover_media_id (cover_media_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品集项目表';
```

### 4.3 字段说明

| 字段 | 必填 | 说明 |
|---|---:|---|
| slug | 是 | 英文或拼音短标识，例如 `ai-resume-assistant` |
| title | 是 | 项目名称 |
| summary | 是 | 用于项目卡片 |
| project_type | 是 | 项目类型 |
| role | 否 | 个人职责 |
| features | 否 | 功能点数组 |
| challenges | 否 | 难点数组 |
| solutions | 否 | 解决方案数组 |
| tech_stack | 是 | 技术栈数组 |
| links | 否 | 链接数组 |
| cover_media_id | 否 | 封面图媒体 ID |
| is_featured | 是 | 首页是否展示 |
| sort_order | 是 | 排序 |
| status | 是 | 发布状态 |

### 4.4 JSON 示例

`tech_stack`：

```json
["React", "Python", "Dify", "SSE"]
```

`features`：

```json
["预设问题", "SSE 流式回复", "连续追问", "简历下载"]
```

`links`：

```json
[
  {
    "label": "在线 Demo",
    "url": "https://example.com",
    "link_type": "demo"
  },
  {
    "label": "GitHub",
    "url": "https://github.com/example/repo",
    "link_type": "github"
  }
]
```

## 5. media_assets 表

### 5.1 用途

保存图片、视频、PDF 简历等文件的元数据。

实际文件存储在服务器本地 `uploads/` 目录，或后续迁移到对象存储。

### 5.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS media_assets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '媒体 ID',
  project_id BIGINT UNSIGNED NULL COMMENT '关联项目 ID，可为空',
  media_type VARCHAR(30) NOT NULL COMMENT '媒体类型：image/video/document',
  purpose VARCHAR(50) NOT NULL DEFAULT 'general' COMMENT '用途：cover/screenshot/demo/resume/architecture/general',
  original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
  stored_filename VARCHAR(255) NOT NULL COMMENT '存储文件名',
  storage_path VARCHAR(500) NOT NULL COMMENT '服务端存储路径',
  public_url VARCHAR(500) NOT NULL COMMENT '前端可访问 URL',
  mime_type VARCHAR(120) NOT NULL COMMENT 'MIME 类型',
  file_ext VARCHAR(20) NOT NULL COMMENT '文件扩展名',
  file_size BIGINT UNSIGNED NOT NULL COMMENT '文件大小，单位 byte',
  width INT UNSIGNED NULL COMMENT '图片或视频宽度，可为空',
  height INT UNSIGNED NULL COMMENT '图片或视频高度，可为空',
  duration_seconds DECIMAL(10,2) NULL COMMENT '视频时长，单位秒，可为空',
  alt_text VARCHAR(255) NULL COMMENT '图片或视频说明',
  sort_order INT NOT NULL DEFAULT 0 COMMENT '同项目内排序',
  status VARCHAR(30) NOT NULL DEFAULT 'published' COMMENT '状态：draft/published/hidden',
  metadata JSON NULL COMMENT '扩展元数据',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '软删除时间',
  PRIMARY KEY (id),
  KEY idx_media_project (project_id, sort_order, id),
  KEY idx_media_type_purpose (media_type, purpose),
  KEY idx_media_status (status),
  CONSTRAINT fk_media_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='媒体资源表';
```

### 5.3 字段说明

| 字段 | 必填 | 说明 |
|---|---:|---|
| project_id | 否 | 关联项目，简历文件可为空 |
| media_type | 是 | `image` / `video` / `document` |
| purpose | 是 | `cover` / `screenshot` / `demo` / `resume` / `architecture` / `general` |
| original_filename | 是 | 用户上传时的原文件名 |
| stored_filename | 是 | 后端生成的安全文件名 |
| storage_path | 是 | 服务端真实路径 |
| public_url | 是 | 前端访问路径 |
| mime_type | 是 | 文件 MIME 类型 |
| file_ext | 是 | 文件扩展名 |
| file_size | 是 | 文件大小 |
| alt_text | 否 | 用于前端 `alt` 或说明 |
| metadata | 否 | 额外信息 |

### 5.4 文件类型限制

| media_type | file_ext | mime_type | 最大大小 |
|---|---|---|---:|
| image | jpg/jpeg/png/webp | image/jpeg, image/png, image/webp | 10 MB |
| video | mp4/webm | video/mp4, video/webm | 50 MB |
| document | pdf | application/pdf | 20 MB |

### 5.5 public_url 示例

```text
/uploads/projects/20260614/ai-resume-cover-9f8a2c.png
/uploads/projects/20260614/ai-resume-demo-a21d3e.mp4
/uploads/resume/20260614/resume-v3.pdf
```

## 6. resume_files 表

### 6.1 用途

保存简历文件配置，支持后续替换简历版本。

### 6.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS resume_files (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '简历记录 ID',
  title VARCHAR(160) NOT NULL COMMENT '简历标题',
  media_id BIGINT UNSIGNED NOT NULL COMMENT 'PDF 媒体 ID，关联 media_assets.id',
  version_label VARCHAR(60) NULL COMMENT '版本标识，例如 v3 或 2026-06',
  is_current TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否当前默认简历',
  status VARCHAR(30) NOT NULL DEFAULT 'published' COMMENT '状态：draft/published/hidden',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '软删除时间',
  PRIMARY KEY (id),
  KEY idx_resume_current_status (is_current, status),
  KEY idx_resume_media_id (media_id),
  CONSTRAINT fk_resume_media
    FOREIGN KEY (media_id) REFERENCES media_assets(id)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='简历文件配置表';
```

### 6.3 约束建议

- 同一时间只能有一个 `is_current = 1` 且 `status = 'published'` 的简历。
- 应用层在设置新当前简历时，需要先把旧简历 `is_current` 置为 0。

## 7. admin_users 表

### 10.1 用途

保存后台管理员账号。MVP 阶段只需要一个管理员角色，不做复杂角色权限。

### 10.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS admin_users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '管理员 ID',
  username VARCHAR(80) NOT NULL COMMENT '登录用户名',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希，禁止保存明文密码',
  display_name VARCHAR(120) NULL COMMENT '显示名称',
  email VARCHAR(160) NULL COMMENT '管理员邮箱',
  status VARCHAR(30) NOT NULL DEFAULT 'active' COMMENT '状态：active/disabled',
  last_login_at DATETIME NULL COMMENT '最近登录时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '软删除时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_admin_username (username),
  KEY idx_admin_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='后台管理员表';
```

### 7.3 安全要求

- `password_hash` 必须使用安全哈希算法生成，例如 bcrypt、argon2 或同等级方案。
- 后端 API 永远不能返回 `password_hash`。
- `status = 'disabled'` 的管理员不能登录后台。

## 8. site_profile 表

### 8.1 用途

保存公开作品集的基础信息，用于前台候选人摘要和联系方式展示，也用于后台站点设置页维护。

### 8.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS site_profile (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置 ID',
  owner_name VARCHAR(80) NOT NULL COMMENT '姓名',
  headline VARCHAR(160) NOT NULL COMMENT '岗位方向或标题',
  summary TEXT NULL COMMENT '个人简介',
  email VARCHAR(160) NULL COMMENT '邮箱',
  phone VARCHAR(80) NULL COMMENT '手机号',
  wechat VARCHAR(120) NULL COMMENT '微信',
  github_url VARCHAR(500) NULL COMMENT 'GitHub 链接',
  portfolio_url VARCHAR(500) NULL COMMENT '作品集链接',
  extra_links JSON NULL COMMENT '其他链接数组',
  status VARCHAR(30) NOT NULL DEFAULT 'published' COMMENT '状态：published/hidden',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_site_profile_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站点基础信息配置表';
```

### 8.3 约束建议

- MVP 阶段只保留一条 `status = 'published'` 的有效配置。
- 应用层更新配置时优先更新 ID 最小的配置行，不需要做复杂版本管理。

## 9. prompt_questions 表

### 9.1 用途

保存首页 AI 简历助手的预设问题，支持后台新增、编辑、隐藏、排序。

### 9.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS prompt_questions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '预设问题 ID',
  question VARCHAR(300) NOT NULL COMMENT '展示给访问者的问题',
  category VARCHAR(80) NULL COMMENT '分类，例如 positioning/project/frontend/backend/agent',
  sort_order INT NOT NULL DEFAULT 0 COMMENT '排序值，越大越靠前',
  status VARCHAR(30) NOT NULL DEFAULT 'published' COMMENT '状态：draft/published/hidden',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '软删除时间',
  PRIMARY KEY (id),
  KEY idx_prompt_status_sort (status, sort_order, id),
  KEY idx_prompt_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI 预设问题表';
```

### 9.3 初始化建议

MVP 建议初始化 5 个问题：

- 你最适合什么岗位？为什么？
- Dify 简历助手你负责了哪部分？
- 有哪些可以验证的项目截图或视频？
- 前端、后端和 AI 应用能力分别体现在哪？
- 如果接手业务型 AI Agent，你会怎么落地？

## 10. chat_logs 表

### 7.1 用途

保存 AI 简历助手的对话日志。MVP 可选。

建议上线初期保留该表，便于排查 Dify 调用失败、优化预设问题和分析常见提问。

### 7.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS chat_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '对话日志 ID',
  visitor_id VARCHAR(120) NULL COMMENT '访问者 ID',
  conversation_id VARCHAR(120) NULL COMMENT 'Dify conversation_id',
  user_message TEXT NOT NULL COMMENT '用户问题',
  assistant_answer MEDIUMTEXT NULL COMMENT 'AI 完整回答，可为空',
  request_status VARCHAR(30) NOT NULL DEFAULT 'started' COMMENT '状态：started/succeeded/failed',
  error_code VARCHAR(80) NULL COMMENT '错误码',
  error_message VARCHAR(500) NULL COMMENT '错误信息',
  latency_ms INT UNSIGNED NULL COMMENT '总耗时，单位毫秒',
  user_agent VARCHAR(500) NULL COMMENT '浏览器 UA',
  ip_address VARCHAR(64) NULL COMMENT '访问者 IP，可按隐私策略决定是否保存',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_chat_conversation (conversation_id),
  KEY idx_chat_visitor_created (visitor_id, created_at),
  KEY idx_chat_status_created (request_status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI 对话日志表';
```

### 10.3 隐私建议

- 如果不需要分析访问来源，可以不保存 `ip_address`。
- 不要保存用户输入的敏感个人信息。
- 对外展示页面不需要暴露该表数据。

## 11. admin_audit_logs 表

### 11.1 用途

保存后台关键操作日志。MVP 可选，但建议保留，便于排查是谁修改了项目、媒体或简历。

### 11.2 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS admin_audit_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '审计日志 ID',
  admin_id BIGINT UNSIGNED NULL COMMENT '管理员 ID',
  action VARCHAR(80) NOT NULL COMMENT '操作类型，例如 project.create/media.delete',
  target_type VARCHAR(80) NOT NULL COMMENT '操作对象类型',
  target_id BIGINT UNSIGNED NULL COMMENT '操作对象 ID',
  detail JSON NULL COMMENT '操作详情',
  ip_address VARCHAR(64) NULL COMMENT '管理员 IP',
  user_agent VARCHAR(500) NULL COMMENT '浏览器 UA',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_audit_admin_created (admin_id, created_at),
  KEY idx_audit_target (target_type, target_id),
  KEY idx_audit_action_created (action, created_at),
  CONSTRAINT fk_audit_admin
    FOREIGN KEY (admin_id) REFERENCES admin_users(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='后台操作审计日志表';
```

## 12. 初始化数据示例

### 12.1 插入项目

```sql
INSERT INTO projects (
  slug,
  title,
  subtitle,
  summary,
  project_type,
  background,
  goals,
  role,
  features,
  challenges,
  solutions,
  tech_stack,
  links,
  is_featured,
  sort_order,
  status
) VALUES (
  'ai-resume-assistant',
  'AI 简历助手',
  '可追问式智能简历作品集',
  '基于 Dify API 的 SSE 流式简历助手，让访问者可以直接追问项目经历、技术栈和岗位匹配度。',
  'AI 应用',
  '传统 PDF 简历无法支持追问，招聘方理解成本较高。',
  '把简历、项目证据和 AI 问答整合成一个可交互作品集。',
  '负责前端页面、SSE 流式渲染、Python 后端代理、Dify 接入和移动端适配。',
  JSON_ARRAY('预设问题', 'SSE 流式回复', '连续追问', '简历下载'),
  JSON_ARRAY('SSE 流式响应解析', 'Dify API Key 隔离', '移动端首屏交互布局'),
  JSON_ARRAY('使用 Python 后端代理 Dify', '前端逐步渲染 answer 增量', '首屏优先展示 AI 聊天模块'),
  JSON_ARRAY('React', 'Python', 'Dify', 'SSE'),
  JSON_ARRAY(),
  1,
  100,
  'published'
);
```

### 12.2 插入媒体资源

```sql
INSERT INTO media_assets (
  project_id,
  media_type,
  purpose,
  original_filename,
  stored_filename,
  storage_path,
  public_url,
  mime_type,
  file_ext,
  file_size,
  alt_text,
  sort_order,
  status
) VALUES (
  1,
  'image',
  'cover',
  'ai-resume-cover.png',
  'ai-resume-cover-20260614.png',
  'uploads/projects/20260614/ai-resume-cover-20260614.png',
  '/uploads/projects/20260614/ai-resume-cover-20260614.png',
  'image/png',
  'png',
  238102,
  'AI 简历助手封面截图',
  100,
  'published'
);
```

### 12.3 设置项目封面

```sql
UPDATE projects
SET cover_media_id = 1
WHERE id = 1;
```

### 12.4 插入当前简历

```sql
INSERT INTO media_assets (
  media_type,
  purpose,
  original_filename,
  stored_filename,
  storage_path,
  public_url,
  mime_type,
  file_ext,
  file_size,
  alt_text,
  status
) VALUES (
  'document',
  'resume',
  '卢官有-AI全栈开发-简历-v3.pdf',
  'resume-ai-fullstack-v3.pdf',
  'uploads/resume/resume-ai-fullstack-v3.pdf',
  '/uploads/resume/resume-ai-fullstack-v3.pdf',
  'application/pdf',
  'pdf',
  339227,
  '卢官有 AI 全栈开发简历',
  'published'
);

INSERT INTO resume_files (
  title,
  media_id,
  version_label,
  is_current,
  status
) VALUES (
  '卢官有-AI全栈开发-简历-v3.pdf',
  LAST_INSERT_ID(),
  'v3',
  1,
  'published'
);
```

### 12.5 插入管理员账号

`password_hash` 必须由后端命令或初始化脚本生成。下面只示意字段，不提供真实哈希。

```sql
INSERT INTO admin_users (
  username,
  password_hash,
  display_name,
  email,
  status
) VALUES (
  'admin',
  '<generated-password-hash>',
  '管理员',
  NULL,
  'active'
);
```

### 12.6 插入站点基础信息

```sql
INSERT INTO site_profile (
  owner_name,
  headline,
  summary,
  email,
  phone,
  wechat,
  github_url,
  portfolio_url,
  extra_links,
  status
) VALUES (
  '卢官有',
  'AI 应用开发 / 前端工程 / Python 后端',
  '把传统简历改成可追问的 AI 对话入口，同时保留项目截图、视频和职责说明。',
  'example@email.com',
  '',
  '',
  '',
  '',
  JSON_ARRAY(),
  'published'
);
```

### 12.7 插入 AI 预设问题

```sql
INSERT INTO prompt_questions (
  question,
  category,
  sort_order,
  status
) VALUES
('你最适合什么岗位？为什么？', 'positioning', 100, 'published'),
('Dify 简历助手你负责了哪部分？', 'project', 90, 'published'),
('有哪些可以验证的项目截图或视频？', 'proof', 80, 'published'),
('前端、后端和 AI 应用能力分别体现在哪？', 'skills', 70, 'published'),
('如果接手业务型 AI Agent，你会怎么落地？', 'agent', 60, 'published');
```

## 13. 常用查询

### 13.1 查询首页精选项目

```sql
SELECT
  p.id,
  p.slug,
  p.title,
  p.subtitle,
  p.summary,
  p.project_type,
  p.role,
  p.tech_stack,
  p.cover_media_id,
  m.public_url AS cover_url
FROM projects p
LEFT JOIN media_assets m ON p.cover_media_id = m.id
WHERE p.status = 'published'
  AND p.deleted_at IS NULL
  AND p.is_featured = 1
ORDER BY p.sort_order DESC, p.id DESC;
```

### 13.2 查询项目详情和媒体

```sql
SELECT *
FROM projects
WHERE id = ?
  AND status = 'published'
  AND deleted_at IS NULL;

SELECT *
FROM media_assets
WHERE project_id = ?
  AND status = 'published'
  AND deleted_at IS NULL
ORDER BY sort_order DESC, id ASC;
```

### 13.3 查询当前简历

```sql
SELECT
  r.id,
  r.title,
  r.version_label,
  m.id AS media_id,
  m.public_url,
  m.storage_path,
  m.mime_type,
  m.file_size
FROM resume_files r
JOIN media_assets m ON r.media_id = m.id
WHERE r.is_current = 1
  AND r.status = 'published'
  AND r.deleted_at IS NULL
LIMIT 1;
```

## 14. 实现注意事项

### 14.1 外键顺序

因为 `projects.cover_media_id` 指向 `media_assets.id`，而 `media_assets.project_id` 也指向 `projects.id`，MVP 建议：

1. 先创建 `projects` 表，不为 `cover_media_id` 加外键。
2. 创建 `media_assets` 表，并添加 `project_id` 外键。
3. 应用层维护 `cover_media_id` 的有效性。

本文档的 `projects` 表只为 `cover_media_id` 创建普通索引，不强制外键。

### 14.2 删除策略

- 项目删除使用软删除，设置 `deleted_at`。
- 媒体删除也使用软删除，避免误删文件导致页面图片失效。
- 真正删除文件应作为后续维护任务单独执行。
- 后台删除项目时，不应自动删除关联媒体文件；只解除公开展示关系或软删除项目。
- 后台删除媒体时，应检查该媒体是否正在作为项目封面或当前简历使用。

### 14.3 后台管理约束

- 管理员密码只保存哈希，不保存明文。
- MVP 只需要一个管理员角色，不需要权限分级表。
- 站点基础信息可只维护一条发布中的配置。
- 后台上传文件必须写入 `media_assets`，不能只把文件放进目录。
- 后台设置当前简历时，需要把其他简历的 `is_current` 置为 0。

### 14.4 MVP 简化策略

MVP 版本可以先：

- 使用后台上传图片、视频、PDF 到 `uploads/`。
- 使用后台维护项目、媒体、简历和预设问题。
- 暂不做视频转码和缩略图生成。

## 15. 验收标准

- MySQL 可以成功执行建表 SQL。
- `projects` 至少能保存 3 个精选项目。
- `media_assets` 能保存图片、视频、PDF 的元数据。
- `resume_files` 能标记一个当前简历。
- `admin_users` 能保存至少 1 个可登录管理员账号。
- `site_profile` 能保存公开站点基础信息。
- `prompt_questions` 能保存首页 AI 预设问题。
- 后端项目列表接口可以通过 SQL 查询返回封面图 URL。
- 后端项目详情接口可以返回项目媒体数组。
- 后台可以通过数据库表支持项目、媒体、简历、站点配置和预设问题 CRUD。
- 前端不需要硬编码项目图片、视频和简历路径。

## 16. 相关文档

- [AI 简历作品集网站 PRD](../AI简历作品集网站PRD.md)
- [后端 API 规格](./spec-api-portfolio-backend.md)
