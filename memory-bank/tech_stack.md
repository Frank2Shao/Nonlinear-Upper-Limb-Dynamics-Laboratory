# NULDL 网站 Tech Stack

**项目名称：** Nonlinear Upper Limb Dynamics Laboratory Website  
**文档职责：** 定义技术选型、架构边界、环境、安全和运维方案  
**文档状态：** Baseline  
**最后更新：** 2026 年 10 月 22 日

## 一、文档边界

本文档回答“使用什么技术以及为什么”。产品目标和用户行为以 [design_document.md](design_document.md) 为准；代码级实现和执行顺序以 [implementation.md](implementation.md) 为准；阶段与进度以 [项目开发_Roadmap.md](项目开发_Roadmap.md) 为准。

## 二、架构结论

采用单体 Django 架构：

```text
Browser
  ├─ Django Templates
  ├─ HTMX
  ├─ Alpine.js
  └─ MapLibre GL JS
          ↓
Django application
  ├─ Accounts and permissions
  ├─ Public pages
  ├─ Member profiles
  ├─ Events and registrations
  ├─ Risk Notice versions
  └─ Django Admin
          ↓
PostgreSQL
```

Django 同时负责 HTML 页面、账户、业务逻辑、数据库访问和后台管理。首期不建立独立 frontend application 或 REST API。

## 三、技术选型

| 范围 | 选型 | 版本策略 | 决策理由 |
| --- | --- | --- | --- |
| Runtime | Python | 3.13.x | 满足 Django 5.2 支持范围并保持稳定运行时 |
| Web framework | Django | `~=5.2`，持续使用最新安全补丁 | LTS、认证体系、ORM、Admin 和服务端渲染完整 |
| Database | PostgreSQL | 托管平台支持的稳定版本 | 约束、事务、条件索引和生产可靠性 |
| Authentication | django-allauth | 锁定兼容版本并通过依赖更新流程升级 | 支持强制邮箱验证、验证码验证及 Magic Code 登录 |
| HTML | Django Templates | 跟随 Django | 避免独立前端复杂度 |
| Partial interaction | HTMX | 锁定 minor/patch | 适合报名、取消和筛选等局部交互 |
| Small UI state | Alpine.js | 锁定 minor/patch | 处理导航、条件字段和 dialog |
| CSS | Tailwind CSS | v4 系列锁定版本 | 统一响应式样式和 Design Tokens |
| CSS build | Tailwind CLI | `@tailwindcss/cli` 锁定版本 | 无需引入完整 SPA bundler |
| Map | MapLibre GL JS | 锁定 minor/patch | 开源、支持 Marker、Popup 和交互地图 |
| Admin | Django Admin | 跟随 Django | 低成本完成内容和审核管理 |
| Email | Django Email Backend + SMTP | Provider 待定 | 开发与生产配置可分离 |
| App server | WSGI server | 部署平台确定时锁定 | Django 同步业务足以满足首期需求 |
| Packaging | `pyproject.toml` | 精确锁定直接依赖 | 统一 Python 项目元数据和依赖 |
| Containers | Docker / Docker Compose | 锁定基础镜像 digest 或 patch | 统一开发数据库和生产构建 |

### 3.1 Django 版本策略

- 使用 Django 5.2 LTS；
- 依赖范围允许 5.2 系列安全补丁，不自动跨入 6.x；
- 开发和部署使用锁文件或可重现的依赖解析结果；
- 升级后必须运行 migrations 检查、测试套件和 `manage.py check --deploy`；
- 自定义 User 在第一次 migration 前建立，后续不更换 `AUTH_USER_MODEL`。

### 3.2 django-allauth 使用范围

启用：

- Username/Password 登录；
- 注册时强制邮箱验证；
- Email verification by code；
- 可选 Email Magic Code 登录；
- Password reset；
- 默认 rate limits 和 enumeration prevention。

不启用：

- Social login；
- MFA；
- Phone login；
- 强制每次密码登录追加验证码。

业务附加字段通过自定义 signup form 或 adapter 保存，权限和字段一致性仍由 Django model/form 层验证。

### 3.3 前端资产策略

- Django Templates 是页面来源；
- HTMX、Alpine.js 和 MapLibre 采用明确版本并作为静态资产管理；
- Tailwind v4 通过 `@tailwindcss/cli` 构建生产 CSS；
- 不在正式环境使用 Tailwind Play CDN；
- 不引入 Vite、Webpack、React 或 Vue；
- 生产构建生成压缩后的 CSS 和静态文件 manifest；
- JavaScript 失效时，核心表单和 POST 操作仍具备服务端回退路径。

## 四、Django 应用边界

| App | 职责 | 不负责 |
| --- | --- | --- |
| `core` | Home、About、全局布局、通用组件和 error pages | 会员及活动业务 |
| `accounts` | User、注册、登录、邮箱验证、USU ID 和账户设置 | 公开会员资料 |
| `members` | MemberProfile、公开列表、资料编辑和隐藏 | 身份认证 |
| `events` | Event、EventRegistration、报名及取消 | Risk Notice 正文版本管理 |
| `locations` | Location、地点页面和地图数据 | 地图瓦片服务 |
| `safety` | RiskNoticeVersion、安全页面及当前版本服务 | 活动报名记录 |

跨 App 关系通过 `settings.AUTH_USER_MODEL` 和显式 ForeignKey 建立。业务逻辑应放在 service function、form 或 model method 中，避免将复杂规则仅写在 template 或 signal 中。

## 五、数据与事务策略

### 5.1 PostgreSQL 使用原则

- 开发、测试和生产均以 PostgreSQL 为目标数据库；
- 不使用 SQLite 作为主要开发数据库，避免约束和条件索引行为差异；
- 关键业务规则同时使用应用层校验和数据库约束；
- 报名和 Risk Notice 确认在同一事务内提交；
- 当前 Risk Notice 切换使用事务，保证同一时间只有一个当前版本；
- 对管理员常用筛选字段建立必要索引，避免无依据的提前优化。

### 5.2 数据一致性重点

- Email 采用规范化处理并保持唯一；
- 非 USYD 用户不能保存 USU ID；
- 修改 USU ID 后审核状态必须回到 `pending`；
- 同一活动和用户不能同时存在两条有效报名；
- 取消记录不删除；
- 历史报名始终引用当时接受的 Risk NoticeVersion；
- MemberProfile 默认不公开。

## 六、环境与配置

### 6.1 环境划分

| 环境 | 用途 | Email | Database | DEBUG |
| --- | --- | --- | --- | --- |
| Development | 本地开发 | Console 或本地捕获工具 | Docker PostgreSQL | `True` |
| Test | 自动化测试 | In-memory backend | 独立 PostgreSQL test DB | `False` 或测试配置 |
| Preview | 私有验收 | 测试 SMTP | 独立托管 PostgreSQL | `False` |
| Production | 正式公开 | 正式 SMTP | 托管 PostgreSQL | `False` |

Preview 环境不得被搜索引擎索引，不应显示未经确认的正式声明。

### 6.2 Settings 划分

```text
config/settings/
├── base.py
├── development.py
├── test.py
└── production.py
```

环境变量至少包括：

```text
DJANGO_SETTINGS_MODULE
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
DATABASE_URL
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_USE_TLS
DEFAULT_FROM_EMAIL
```

Map tile provider、object storage 和 error monitoring 在选定供应商后增加对应变量。

### 6.3 Secret 管理

- `.env` 仅用于本地开发且不得提交；
- 仓库提供 `.env.example`，只包含变量名称和安全示例；
- Preview 与 Production 使用托管平台 Secret 管理；
- 不在日志、错误页面或测试快照中输出 Secret；
- Production 与非正式环境使用不同的 `SECRET_KEY` 和数据库凭据。

## 七、Email 架构

- Development 使用 Console Email Backend 或邮件捕获工具；
- Test 使用 Django 测试邮件 backend；
- Preview 和 Production 使用 SMTP；
- Sender domain 在上线前配置 SPF、DKIM，并根据 Provider 能力配置 DMARC；
- 邮件模板使用纯文本和 HTML 两种版本；
- 验证码和登录码不得写入应用日志；
- Provider 尚未确定，代码通过 Django Email Backend 保持可替换。

## 八、地图架构

- MapLibre GL JS 负责地图渲染和交互；
- Location 数据由 Django 输出；
- 只公开已确认的地点记录；
- 地点卡片作为地图的无 JavaScript 回退；
- Map tile provider 尚未确定；
- Provider 选定前不得假设免费额度、请求限制或 attribution 条款。

## 九、Media 与静态文件

### 9.1 Static files

- Tailwind 输出、JavaScript、Logo 和其他固定资源进入 `static/`；
- Production 执行 `collectstatic`；
- 静态文件使用 hashed filenames 和长期缓存；
- 是否使用 CDN 由部署平台决定。

### 9.2 User media

- Development 使用本地 `MEDIA_ROOT`；
- Avatar 文件类型和大小必须校验；
- Production 需要持久化 media storage；
- Object storage 或平台持久卷的最终选择在部署阶段确定；
- 用户上传内容不得作为可执行文件提供。

## 十、安全基线

- Production 强制 HTTPS；
- `DEBUG = False`；
- 正确配置 `ALLOWED_HOSTS` 和 `CSRF_TRUSTED_ORIGINS`；
- 启用 Secure、HttpOnly 和合适 SameSite 的 session cookie；
- 保留 Django CSRF middleware；
- 登出使用 POST；
- 注册、验证码、登录和密码重置使用 django-allauth rate limits；
- 保持 enumeration prevention；
- 后台路径和权限不替代强认证与最小权限；
- 上传文件执行扩展名、MIME、大小和图像解码验证；
- 生产部署运行 `python manage.py check --deploy`；
- 日志不得记录 Password、验证码、完整 USU ID 或 session token；
- 依赖升级需要安全公告检查和测试验证。

## 十一、测试与质量工具

### 11.1 测试层级

- Model tests：字段规则、状态转换和约束；
- Form tests：注册、账户、资料和报名输入；
- View tests：权限、状态码、redirect 和公开边界；
- Service tests：报名事务、Risk Notice 版本和审核状态；
- Integration tests：django-allauth 注册与登录流程；
- Browser tests：核心注册、登录、报名和取消流程；
- Accessibility checks：语义、键盘和关键页面自动检查。

### 11.2 工具

- `pytest` + `pytest-django` 用于自动化测试；
- `coverage` 记录覆盖范围；
- `Ruff` 用于 lint 和格式化；
- Django system checks 用于配置检查；
- 浏览器端测试工具在 Phase 1 建立前确定并锁定，默认优先 Playwright；
- CI Provider 尚未确定，但所有检查必须可以通过单一脚本在本地执行。

覆盖率只作为风险提示，不能替代关键业务流程测试。账户、权限、报名和 Risk Notice 规则必须有明确行为断言。

## 十二、日志、监控与备份

### 12.1 日志

- 使用结构化应用日志；
- 区分 INFO、WARNING 和 ERROR；
- 记录请求关联标识，但不记录敏感表单值；
- 管理员关键操作通过模型历史或审计字段保留必要信息。

### 12.2 监控

正式环境至少需要：

- Health check；
- Error monitoring；
- Email 发送失败可见性；
- Database 可用性监控；
- 磁盘或 media storage 使用监控。

具体 Provider 在 Phase 6 决定。

### 12.3 备份

- PostgreSQL 使用自动备份；
- 上线前执行一次恢复演练；
- Media storage 纳入备份策略；
- 记录保留周期和删除规则需等待正式数据保留决定。

## 十三、部署拓扑

```text
Internet
   ↓ HTTPS
Reverse proxy / Managed platform
   ↓
Django WSGI application
   ├─ Hosted PostgreSQL
   ├─ SMTP provider
   ├─ Persistent media storage
   └─ Map tile provider
```

正式托管平台、SMTP、media storage、监控及 tile provider 均未确定。选型时评估：

- 澳大利亚访问延迟；
- 月度成本；
- PostgreSQL 与备份能力；
- 持久化 media 支持；
- Secret 管理；
- 日志与回滚；
- 域名和 TLS 配置；
- 数据位置和服务条款。

## 十四、不采用的方案

### 14.1 React 或 Vue SPA

首期页面和交互复杂度不足以抵消独立前端带来的 API、状态管理、认证和部署成本。

### 14.2 独立 REST API

当前没有移动客户端或第三方集成需求。Django Views 和 HTMX 可以覆盖首期业务。

### 14.3 Redis 与 Celery

首期没有必须异步执行的长任务。Email 先同步发送；只有出现可测量的延迟或可靠性需求后再评估队列。

### 14.4 独立 CMS

公开内容量有限，Django Admin 足以管理。引入 CMS 会增加模型、权限和维护成本。

### 14.5 SQLite 作为主要开发数据库

项目依赖 PostgreSQL 的生产行为和条件唯一约束。主要开发和 CI 应尽量保持数据库一致。

## 十五、开放技术决策

1. Production hosting provider；
2. SMTP provider；
3. Media storage；
4. Map tile provider；
5. Error monitoring provider；
6. CI Provider；
7. WSGI server 与平台启动方式；
8. 正式数据保留和备份周期。

这些决定在对应阶段开始前完成 ADR 或更新本文档，不在代码中隐式确定。

## 十六、官方参考资料

- [Django supported versions](https://www.djangoproject.com/download/)
- [Django custom User model](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/)
- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django constraints reference](https://docs.djangoproject.com/en/5.2/ref/models/constraints/)
- [django-allauth account configuration](https://docs.allauth.org/en/latest/account/configuration.html)
- [django-allauth rate limits](https://docs.allauth.org/en/latest/account/rate_limits.html)
- [HTMX documentation](https://htmx.org/docs/)
- [Alpine.js documentation](https://alpinejs.dev/start-here)
- [Tailwind CLI](https://tailwindcss.com/docs/installation/tailwind-cli)
- [MapLibre GL JS documentation](https://maplibre.org/maplibre-gl-js/docs/)
