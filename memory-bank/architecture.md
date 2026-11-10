# NULDL 已实施架构

**最后更新：** 2026 年 10 月 29 日
**对应进度：** Phase 2, Step 28
**当前状态：** Phase 1 与 Phase 2 已完成；Phase 3 尚未开始

## 一、当前架构结论

仓库当前包含项目治理文档、基础 Git 配置、可重现的 Python 与前端依赖元数据、能够通过 Django system check 的项目骨架、由 Docker Compose 管理的本地 PostgreSQL 环境、Development、Test、Production 分环境 settings、具有受保护身份状态转换的 Custom User、完整的 MemberProfile 数据与公开查询边界，以及可重复构建的本地静态资源 pipeline。Python 运行时限定为 3.13.x，后端依赖由 `uv` 锁定，前端依赖由 npm 锁定。Django 已能加载六个项目 App，并从主机 `uv` 环境连接容器中的 PostgreSQL 18.6。

当前已实现 App 边界、启动配置、本地数据库连接、环境隔离、Custom User schema、USYD/USU ID 领域规则、MemberProfile 数据边界，以及 django-allauth 注册、Email verification by code、Username/Password 登录、可选 Email Magic Code 登录、link-based Password reset、POST logout、会员 Account 身份信息管理和 USU ID Admin 审核闭环。邮箱验证成功会通过官方 signal 调用幂等 service，只建立一个默认隐藏的 MemberProfile。`/account/` 提供本人账户与身份信息管理；`/admin/` 通过专用权限、只读审核字段和受控 actions 实现最小权限人工审核。项目已有全局语义化页面壳、统一 allauth 页面、本地 Alpine 渐进增强、Tailwind 第一版响应式视觉、版本及 hash 可验证的 vendor assets，以及 Production manifest static storage；核心认证流程在禁用 JavaScript 时仍可用。Phase 1 具有本地与 CI 共用的质量安全门禁，以及从临时全新 uv environment 执行锁定安装、PostgreSQL migration、完整门禁、Development server 和 desktop/mobile Playwright smoke 的端到端验收入口。README 已记录首次安装、日常开发、自动验收和人工流程；项目负责人已确认自动化与人工验收通过。Phase 2 已建立可覆盖的 metadata/Open Graph head 边界、完整 `NULDL Armwrestling Club` 品牌命名、键盘可用的响应式 Header、公开页面复用样式，以及正式 Home、About 与 Beginners & Safety。三个正式公开页面使用获准英文内容和认证状态分支 CTA；Home 另含无报名能力的静态日程及由受保护源图确定性生成的响应式 WebP Logo。Draft Risk Notice 以显式环境开关隔离：Development 开启、获准 Preview 必须显式开启、Test 默认关闭、Production 强制关闭；关闭时直接 URL 返回 404 且导航与 CTA 不公开入口。项目已注册 403、404 和 500 handlers，三个错误状态使用共享页面壳、正确状态码和不泄露内部信息的中性恢复页面。Home、About 和 Beginners & Safety 已固定获准 metadata 与 Open Graph 值；Open Graph URL 由 request 派生，未硬编码尚未确认的 canonical host。`/sitemap.xml` 通过显式 allowlist 只公开三个正式页面，始终排除 Draft、认证、Account、Admin、错误页面和后续 Phase 路由。Footer 只公开已批准的 Instagram，不公开联系邮箱或未经授权的 University Branding。desktop、mobile、键盘、200% content zoom 和无 JavaScript 场景均已通过相应浏览器验证。HTMX 与 MapLibre 仍只完成本地资产准备。后续架构和技术选型仍以 `design_document.md`、`tech_stack.md` 与 `implementation.md` 为准。只有后续步骤实际完成并通过验证后，才在本文档记录对应结构及其理由。

Phase 2 现有统一 Playwright accessibility 门禁覆盖全部正式公开页、Draft 及真实错误页，并在 desktop、mobile、200% 内容放大、键盘、无 JavaScript 和 reduced-motion 场景检查语义、Focus、触控目标、重排、对比度、替代文本、错误及网络边界。

Phase 2 已建立跨阶段共享项目门禁和全新临时 uv environment 端到端验收入口。初次完整验收通过 234 个测试并达到 94% branch coverage；阶段人工走查后的公开页面文案、CTA 与布局修订又通过 24 个 Django 页面测试、4 个相关 Playwright 场景及静态与 Ruff 检查。项目负责人已确认最终人工验收，Phase 2 状态为 `Complete`。

## 二、已实施的依赖架构

### 2.1 Python 层

- 项目要求 Python 3.13.x；当前验证运行时为 Python 3.13.17。
- Django 固定在 5.2 LTS 系列，不允许锁文件自动升级到 Django 6.x。
- Django、django-allauth、Pillow 与 Psycopg 属于运行依赖。
- pytest、pytest-django、coverage 与 Ruff 属于开发依赖组，不进入业务代码的运行时职责。
- `pyproject.toml` 声明直接依赖及精确版本，`uv.lock` 固定完整传递依赖图。

### 2.2 前端工具层

- HTMX、Alpine.js 与 MapLibre GL JS 属于浏览器端运行依赖。
- Tailwind CSS、Tailwind CLI 与 Playwright 属于开发工具依赖。
- Tailwind CSS 与 Tailwind CLI 使用相同版本 4.3.0，避免构建器与框架补丁版本不一致。
- MapLibre GL JS 6.15.0 的根入口仅提供 ESM `import` 导出；Node.js 检查和后续资产处理必须使用 ESM 兼容方式。
- `package.json` 声明精确直接依赖，`package-lock.json` 固定完整 npm 依赖树和包完整性信息。

### 2.3 本地生成目录

- `.venv/` 由 `uv sync` 根据 `uv.lock` 创建，只用于本地 Python 环境，不提交仓库。
- `node_modules/` 由 `npm ci` 根据 `package-lock.json` 创建，只用于本地前端依赖，并由 `.gitignore` 排除。
- 两个目录都可由锁文件重新生成，不承担持久化项目数据职责。

### 2.4 本地数据库层

- Django 在 Windows 主机的 `uv` 环境运行，数据库在 Docker Linux container 中运行。
- Compose 使用 `postgres:18.6-alpine`，主机端口由 `POSTGRES_PORT` 映射到容器 `5432`。
- Django PostgreSQL backend 从 `POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_HOST` 和 `POSTGRES_PORT` 读取全部连接值。
- 缺少必填数据库变量时 settings 会明确失败，不提供 SQLite 或其他回退。
- PostgreSQL 通过 `pg_isready` 提供容器健康检查。
- 数据存储在 Docker named volume `postgres_data`，挂载到 PostgreSQL 18 镜像使用的 `/var/lib/postgresql`；删除并重建容器不会删除该 volume。
- `.env.example` 只提供安全本地示例；实际 `.env` 不提交仓库。

## 三、已实施的 Django 骨架

### 3.1 启动与配置关系

```text
manage.py ─────────────→ config.settings.development
pytest-django ─────────→ config.settings.test
ASGI / WSGI ───────────→ config.settings.production
                                  ↓
                         config.settings.base
                    ┌─────────────┴─────────────┐
                    │ common Django configuration│
                    │ PostgreSQL URL parser      │
                    └─────────────┬─────────────┘
                                  ↓
                         PostgreSQL environment
                                  ↓
                         Docker PostgreSQL 18.6
                                  ↓
                         named volume postgres_data
```

- `manage.py` 默认使用 Development；ASGI 和 WSGI 默认使用 Production；显式 `DJANGO_SETTINGS_MODULE` 始终可以覆盖入口默认值。
- pytest-django 通过 `pyproject.toml` 默认使用 Test settings。
- `base.py` 将 Django 内置 App 与项目 App 分组，项目 App 使用完整 AppConfig 路径注册。
- 根 URL 配置开放 `/admin/`，在 `/account/` 接入项目 Account view，并将 `/accounts/` 委托给 `allauth.urls`；其他页面和业务 URL 将在对应步骤实现。
- PostgreSQL 是当前唯一配置的数据库 backend，连接值必须由环境变量提供。
- Production 没有 Secret、host、database 或 Email 的不安全默认值；缺少必填值时加载失败。

### 3.2 环境边界

| 环境 | Debug | Database | Email | Secret 与安全 |
| --- | --- | --- | --- | --- |
| Development | 开启 | 环境变量提供的 PostgreSQL | Console backend | Secret、hosts 和 CSRF origins 来自本地 `.env`；media 使用本地目录 |
| Test | 关闭 | PostgreSQL，并显式指定独立 test database 名称 | In-memory backend | 使用测试专用 Secret 和快速 Password hasher；不访问外部邮件服务 |
| Production | 关闭 | `DATABASE_URL` 提供的 PostgreSQL | 环境变量提供的 SMTP | Secret、hosts 和 CSRF origins 均为必填；启用 HTTPS redirect、secure cookies、HSTS、referrer policy 和 frame protection |

公共解析逻辑只接受 PostgreSQL URL，并支持 percent-encoded credentials 和连接 query options。Production SMTP Provider 尚未选择，当前只建立可替换的 Django SMTP 配置边界。

### 3.3 App 边界

| App | 已建立边界 | 当前未实现 |
| --- | --- | --- |
| `core` | Home、About、Beginners & Safety、全局页面壳、通用组件和 403/404/500 error pages | 后续 Phase 的业务页面 |
| `accounts` | Custom User、标准与专用审核权限、Email/USU ID 规范化、USYD 声明、状态转换、受控审核服务、signup、Magic Code request 与 Account identity forms、完整认证流程、`/account/` 本人身份信息管理，以及 `/admin/` 最小权限 USU ID 审核 | 统一认证页面表现及其他业务 App 的后台管理 |
| `members` | MemberProfile schema、字段验证、公开 queryset、幂等创建 service、Email 验证成功 signal receiver、会员字段白名单和 Admin 模型配置 | 资料编辑页面、预览、发布操作、公开列表和详情页 |
| `events` | 活动与报名功能的归属位置 | Event、EventRegistration、报名和取消逻辑 |
| `locations` | 地点与地图数据功能的归属位置 | Location、地点页面和地图输出 |
| `safety` | 环境隔离的静态 Draft Risk Notice 页面 | RiskNoticeVersion、正式 Risk Notice 和当前版本服务 |

`accounts` 已建立 Custom User、领域服务及两条业务 migrations；`members` 已建立完整 Profile 数据边界及首条 migration；其余四个业务 App 仍只具备 package、AppConfig 和空 migration package。

### 3.4 Custom User 与 migration 边界

- `accounts.User` 继承 `AbstractUser`，因此 Username、Password、账户启用状态、Staff、Superuser、Group 和 Permission 继续使用 Django 标准机制。
- Email 在 model validation 中必填、数据库列不允许 `NULL` 且具有唯一约束，并列入 `REQUIRED_FIELDS`。保存前会去除首尾空格并转换为小写，数据库约束要求存储值已经规范化。
- `is_usyd_student` 默认为 `False`；`usu_id`、`usu_reviewed_at` 和 `usu_reviewed_by` 允许为空；`usu_review_status` 默认为 `not_submitted`。
- `usu_reviewed_by` 是指向 User 自身的 ForeignKey，并使用 `SET_NULL`，避免审核人账户删除时级联删除被审核账户。
- `accounts.0001_initial` 是首条项目业务 migration。`AUTH_USER_MODEL` 在其生成前已确定，避免后续替换 User model 引发 migration 依赖和 ForeignKey 重构。
- 开发数据库中实际建立的用户表是 `accounts_user`，Django 可替换模型机制跳过了 `auth_user`。
- `accounts.0002_alter_user_usu_id_and_more` 增加 USU ID 数字 validator 及 Email、USU ID、USU 状态组合的数据库约束，没有回写或改动 `0001_initial`。

### 3.5 身份状态的三层保护

- Model 层负责 Email 和 USU ID 规范化、数字 validator、安全默认值及保存时状态转换。普通 `save()` 无法直接修改审核字段。
- Service 层使用 transaction 和 `select_for_update()` 序列化身份更新与审核。`update_usu_identity` 是未来注册和 Account form 的领域入口；`review_usu_id` 是未来 Admin 操作的受控入口。
- Database 层使用 `CheckConstraint` 拒绝未规范化 Email、非数字或未去空格的 USU ID，以及不可能的 ID/状态/审核元数据组合，防止 `QuerySet.update()` 绕过常规 model/service 路径。
- USU ID 以最长 64 字符的字符串存储，但规范化后只允许 `0–9`，因此能保留前导零且不会将 ID 当作可计算数值。
- 无 USU ID 时只允许 `not_submitted` 且审核信息为空；有 ID 的 `pending` 状态不允许审核信息；`verified` 或 `rejected` 必须具有审核时间。审核人删除后 ForeignKey 可由 `SET_NULL` 置空，审核时间仍保留。
- 审核服务要求 reviewer 是数据库中当前启用的 Staff，并具有 `accounts.review_usu_id` 专用权限；Superuser 通过 Django 标准权限机制满足该要求。

### 3.6 MemberProfile 数据与公开边界

- `MemberProfile.user` 是指向 Custom User 的必填 One-to-one relation，并使用 `CASCADE`；数据库保证每个账户最多一个 Profile，`ensure_member_profile` 使用 `get_or_create` 提供重复调用安全的创建入口。邮箱验证成功后，`email_confirmed` signal receiver 会调用该入口。
- Profile 默认不发布且不被管理员隐藏。`display_name`、Avatar、Bio、经验、惯用手、Instagram Username、一个 HTTPS 社交链接、发布控制、管理员字段和创建/更新时间戳均在 `members.0001_initial` 中一次建立。
- 可选文本保存前统一去除首尾空格并将空值转换为 `NULL`。`display_name` 通过 `Lower` 条件唯一约束实现非空值忽略大小写唯一，并通过 `CheckConstraint` 阻止直接写入未规范化值；为空时由 `resolved_display_name` 回退到 Username。
- Avatar validator 同时检查 5 MB 上限、允许扩展名、上传对象声明的 MIME 和 Pillow 解码得到的真实格式，只接受 JPG、PNG 与 WebP。validator 从 `ImageFieldFile` 的底层上传对象读取 MIME，避免 Django 包装后丢失检查来源。
- Bio 在 model validation 中拒绝 HTML，依赖 Django template 默认 escaping 保持后续输出为纯文本。Instagram 只保存清理后的 Username；其他社交链接在应用层限制 HTTPS，并由数据库约束防止直接写入非 HTTPS 值。
- `MemberProfile.objects.public()` 使用 allauth `EmailAddress` 的 `Exists` 子查询表达已验证邮箱条件，并同时过滤未发布、管理员隐藏及停用账户；公开页面建立前即可复用同一隐私边界。
- `MemberProfileForm` 使用显式字段白名单，只包含未来会员可管理的资料字段；`is_hidden_by_admin`、`executive_role`、`created_at` 和 `updated_at` 不进入会员输入面。
- `MemberProfileAdmin` 提供列表、筛选、搜索及只读时间戳。Django Admin App 与 `/admin/` URL 已启用；MemberProfile 的更细粒度 Admin 权限和 hide/unhide 工作流仍属于 Phase 3。
- `allauth.account` 的 EmailAddress schema 继续作为公开查询的已验证邮箱来源；完整认证基础配置见下一节，流程级行为仍按后续步骤逐项实施。

### 3.7 django-allauth 认证基础设施

- Django Sites framework、`allauth` 和 `allauth.account` 已进入公共 `INSTALLED_APPS`，`SITE_ID = 1`；开发数据库已应用 Sites migrations。
- 认证仅使用 `allauth.account.auth_backends.AuthenticationBackend`。该 backend 继承 Django `ModelBackend`，支持 Username/Password 和 Admin 认证，同时遵循 django-allauth 65.20.1 对 Username 匹配的安全修正。
- `ACCOUNT_LOGIN_METHODS` 只允许 Username；signup 基础字段要求 Username、Email、Password 和 Password confirmation。`ACCOUNT_FORMS` 将 signup 表单替换为项目 `apps.accounts.forms.SignupForm`，在基础字段后增加 USYD 声明和可选 USU ID。
- Email 必填且唯一，`ACCOUNT_EMAIL_VERIFICATION` 为 `mandatory`，Email verification by code 已启用。Link-based Email confirmation URL 因此未注册。
- Email Magic Code 入口已启用，使用 3 分钟有效期、3 次尝试上限和 2 次重发配额；`ACCOUNT_LOGIN_BY_CODE_REQUIRED` 保持关闭，密码登录不会被强制追加验证码。Password reset 使用 link-based 默认流程。
- Enumeration prevention 保持开启，`ACCOUNT_RATE_LIMITS` 未被项目覆盖，因此使用锁定版本为 signup、login、login code、password reset 和 verification 提供的默认限制。
- GET logout 保持关闭。`LOGIN_URL` 指向 allauth login；登录后路径预留为 `/account/`，登出后返回 `/`。
- 根 URL 将 `/account/` 交给项目 accounts URLConf，并将 `/accounts/` 委托给 `allauth.urls`。Social Account、MFA 和 Phone login Apps 均未安装，相应 URL 不存在。
- 当前配置提供可反向解析的 signup、login、logout、verification code 页面、Magic Code 请求与确认、Password reset 路由。全部认证服务端流程已实施并验证；项目模板继续由 Step 17 实施。

### 3.8 注册表单与身份写入边界

- `apps.accounts.forms.SignupForm` 继承锁定版本的 allauth `SignupForm`，使用 `ACCOUNT_FORMS` 作为 headed signup view 的唯一表单入口。选择完整 form override 是为了在 allauth 动态建立 Password 字段后显式固定全部字段顺序。
- 表单顺序为 Username、Email、Password、Confirm password、`Are you a USYD student?` 和 `USU ID`。最后两个字段都不是表单必填项；勾选 USYD 不会强制提交 USU ID。
- `clean_usu_id` 复用 User 的规范化函数，并复用同一数字 validator。Form-wide validation 拒绝非 USYD 用户携带非空 USU ID，因此普通 POST 无法绕过前端条件显示。
- allauth 的 parent `save()` 负责建立 User、Password 和 EmailAddress；项目表单随后调用 `update_usu_identity`，使注册与 Account 页未来的身份更新共享同一事务 service 及状态转换规则。
- 成功注册会保留未验证 EmailAddress 并进入 allauth 独立 verification code 页面。重复 Email 仍由 allauth enumeration prevention 返回通用成功路径，不建立新 User。
- Alpine.js 仅负责 Step 17 的 USU ID 条件显示和清除交互；当前服务端表单已可在 JavaScript 完全关闭时提交并执行相同校验。
- Verification code 的成功、错误、过期、重用、重发和 Profile 幂等创建已在 Step 11 实施并测试；Step 12 已验证未确认账户通过密码登录可以重新进入该流程。

### 3.9 Email verification code 与会员激活边界

- django-allauth 将待验证用户、Email、验证码、创建时间、失败次数和重发次数保存在服务端 Session 中；项目没有为验证码新增 Model 或 migration。
- 验证码有效期为 15 分钟，最多允许 3 次错误尝试。错误验证码不会验证 Email、创建 MemberProfile 或建立认证 Session。
- 项目启用验证码重发；锁定版本允许当前流程重发 2 次，并继续使用 allauth 默认 `confirm_email` rate limit（每个 key 每 10 秒 1 次）。限流拒绝不会替换当前验证码。
- 正确验证码先由 allauth 将 EmailAddress 标记为 verified，再发送官方 `email_confirmed` signal。`MembersConfig.ready()` 注册 receiver，receiver 调用幂等的 `ensure_member_profile`。
- 新建 Profile 保持 `is_published=False` 和 `is_hidden_by_admin=False`。验证流程 Session 随成功确认清除，signup 登录阶段结束后进入 `LOGIN_REDIRECT_URL`。
- 过期验证码沿用 allauth 标准行为：清除当前验证流程并重定向至登录页。未验证用户随后可以通过正确的 Username/Password 重新开始验证。
- 项目日志不记录完整 Email 或验证码；集成测试覆盖这一敏感数据边界。

### 3.10 密码认证、重置与登出边界

- Username/Password 登录由 allauth authentication backend 和 LoginView 处理。不存在的 Username 与错误 Password 使用完全相同的通用错误，避免通过凭据错误枚举账户。
- 已验证且启用的账户登录成功后优先返回经过安全校验的站内 `next`；没有有效原目标时进入 `LOGIN_REDIRECT_URL`。外部绝对 URL 会被丢弃，不能形成开放重定向。
- mandatory Email verification stage 位于建立 Django authenticated session 之前。未验证账户密码正确时会发送新验证码并进入现有验证流程；确认成功后才登录、创建 Profile 并返回原站内目标。
- 停用账户即使密码正确也不会建立 authenticated session，而是进入 allauth inactive account 响应。
- Password reset 使用 allauth link-based 流程。已知与未知 Email 得到相同 redirect 和邮件发送外观；有效 token 可以设置新密码，旧密码失效，当前配置不会在 reset 后自动登录。
- `ACCOUNT_LOGOUT_ON_GET=False` 保证 GET 只展示确认页面并保留 Session；POST 才执行 Django logout 并进入 `LOGOUT_REDIRECT_URL`。
- 本节没有新增项目 adapter、form、view、Model 或 migration；锁定版本 allauth 的既有行为由项目集成测试固定。

### 3.11 Email Magic Code 登录边界

- Magic Code 是与 Username/Password 并列的可选入口，使用 Email 请求 code；密码登录不会进入 Magic Code stage。
- 锁定版 allauth 默认会在 Magic Code 成功后调用 `verify_email_indirectly`。项目不允许 Pending user 以登录码替代注册邮箱验证，因此使用受支持的 `ACCOUNT_FORMS` override 替换 `request_login_code` form。
- 项目 `RequestLoginCodeForm` 先复用 allauth 的 active user 查询、enumeration prevention 和 request rate limit，再检查请求 Email 是否具有匹配的 verified EmailAddress。只有通过该检查的账户会关联至登录流程。
- 未验证、停用及未知 Email 得到相同 redirect 和邮件发送外观，Session 中不包含可用 code 或 User，无法完成登录。未验证用户通过 Username/Password 登录重新进入注册邮箱验证流程。
- 登录码有效期为 3 分钟，最多允许 3 次错误尝试。达到尝试上限、过期或已成功使用后，当前 login stage 被清除，code 不能继续使用。
- 重发最多允许 2 次，每次生成并发送新 code；达到配额后重发 action 不再替换 code 或发送邮件。初始请求继续使用 allauth 默认 `request_login_code` rate limit：每个 IP 每分钟 20 次、每个 Email key 每分钟 3 次。
- 成功确认 code 后才建立 authenticated session，并优先返回经过安全校验的站内 `next`。测试确认 code 和完整 Email 不进入日志。
- 本步没有新增 Model、view、URL 或 migration；生命周期保存在 allauth login Session state 中。

### 3.12 Account 页面与本人身份更新边界

- 项目根路径 `/account/` 由 `apps.accounts` 自有 URLConf 与 view 负责，并与既有 `LOGIN_REDIRECT_URL` 对齐。Django `login_required` 保证 Anonymous 返回 allauth login，同时保留安全的站内目标。
- Account view 始终以 `request.user` 构造 form 和查询 EmailAddress，不接受 URL 或 POST 中的目标 User 标识，因此会员不能借由对象 ID 查看或修改其他账户。
- 页面展示只读 Username、只读 Email、与当前 Email 匹配的 verification status，以及本人的 USU review status。审核人和审核时间不会进入页面 context 或输出。
- `AccountIdentityForm` 是 Account 更新的输入白名单，只接收 USYD 声明和可选 USU ID。伪造的 Username、Email、User ID 或审核字段会被 Django form 忽略。
- Form 复用 `update_usu_identity` 事务 service，Account 与 signup 因此共享相同的规范化、数字 validator、row lock 和状态转换。修改 ID 会撤销旧审核并进入 `pending`；取消 USYD 会清除 ID 与审核信息。
- 未绑定 form 从当前 User 初始化，验证失败时保留非敏感输入；成功提交采用 redirect-after-POST 并通过 Django messages 返回英文确认。
- Password change 继续由 allauth 路由处理；登出由带 CSRF 的 POST form 提交至 allauth logout。Account 页面没有 Email 修改、账户删除或审核操作。
- 当前 `account.html` 继承全局页面壳，并继续以不依赖 JavaScript 的普通 form 提供英文功能页面。统一认证页面、Alpine.js 条件显示、完整响应式视觉和静态资源继续由 Step 17–18 实施。
- 本步没有 Model 或 migration 变更；现有数据库约束仍作为 form/service 之外的最终一致性保护。

### 3.13 USU ID Admin 审核与权限边界

- `User.Meta` 声明专用权限 `accounts.review_usu_id`，由 `accounts.0003_alter_user_options` 写入 Django permission metadata；没有新增业务字段或改变现有数据库约束。
- `review_usu_id` 在 row lock 内重新读取 reviewer，并同时要求账户启用、具有 Staff 身份及专用权限。这样即使绕过 Admin 直接调用 service，无权限 Staff 也不能完成审核。
- Custom `UserAdmin` 只向拥有专用权限的启用 Staff 或 Superuser 暴露 User 模型。普通会员不能登录 Admin，无权限 Staff 的直接 User Admin URL 请求被拒绝。
- 获授权 Staff 的 queryset 仅包含声明为 USYD 且具有非空 USU ID 的账户，减少与审核无关的账户数据暴露；列表、筛选和搜索字段围绕 USU 审核工作流配置。
- Verify 和 Reject actions 是 Admin 中唯一的审核写入口，并逐项调用事务 service。无 ID 或状态不合法的目标会被跳过并显示通用 Admin message。
- 获授权 Staff 的 change view 只显示审核所需字段且全部只读，隐藏保存与删除操作；直接伪造 change POST 不能写入 User。新增和删除 User 只保留给 Superuser。
- Superuser 保留 Django UserAdmin 的标准账户管理能力，但 USYD 声明、USU ID、审核状态、审核时间和审核人仍为只读，审核必须经过 actions/service。
- 审核成功记录状态、当前 reviewer 与 timezone-aware 时间。会员修改 ID 后既有 model/service 会清除旧审计并回到 `pending`，随后可重新审核。
- reviewer 后续停用不会修改历史记录；Self ForeignKey 继续保留 reviewer，审核时间与状态不变。停用 reviewer 无法执行新的审核。
- 前台 Account 页面只展示本人 review status，不输出 reviewer 或 review time；Anonymous 响应不包含完整 USU ID。

### 3.14 全局模板、导航与渐进增强边界

- `apps.core` 拥有站点级 Home view 和根路径 URL；Home URL pattern 只匹配空路径，因此不会截获 `/account/`、`/admin/` 或 `/accounts/`。
- `core/base.html` 是前台页面的唯一公共页面壳，负责文档语言、字符集、viewport、标题区块、skip link 及 Header、messages、main、Footer 的组合；领域页面通过 template inheritance 填充标题和主内容。
- Header 根据 `request.user.is_authenticated` 切换 Anonymous 与 Member 操作。当前导航仅包含已经存在的 Home、Login、Signup 和 Account 路由，使用 URL name 判断并输出 `aria-current="page"`。
- Messages include 复用 Django messages framework；容器使用 polite live region，普通与成功消息使用 `status`，错误消息使用 `alert`，使 redirect-after-POST 反馈可被辅助技术感知。
- 主内容具有稳定的 `main-content` ID 与 programmatic focus target，页面开头的 skip link 可以绕过重复导航。每个现有页面只提供一个 H1。
- 全局导航和 Account 操作使用真实 link 及带 CSRF 的普通 POST form，不要求 JavaScript 才能完成核心流程。Alpine.js 与 Tailwind 增强保留这一服务端与语义 HTML 基线。
- Footer 使用中性实验室名称，没有引入尚未授权的 University Logo、Crest 或官方身份表述。Home 保持英文占位内容，不为未实施页面建立虚假导航。
- Step 16 没有新增 Model 或 migration；其页面壳已由 Step 17–18 的统一认证模板、渐进增强和静态资源 pipeline 复用。

### 3.15 认证模板、错误反馈与渐进增强边界

- 项目将根级 `templates/` 加入 Django template search path，并通过 `templates/account/` 覆盖当前启用的 allauth 页面。认证业务状态、URL 与 POST 处理仍由 allauth 负责，项目模板只统一呈现层和可访问性结构。
- `templates/account/includes/` 集中输出 form-level error、field 和完整 fields。字段继续使用 Django `as_field_group` 生成稳定的 error ID、`aria-invalid` 与 `aria-describedby`；非字段错误使用可聚焦的 `role="alert"` summary。
- `core/base.html` 加载本地 CSS 与 deferred Alpine.js，并在初始化后聚焦第一个无效字段或 error summary。skip link、普通 link、原生 form、CSRF 和服务端 validation 均不依赖 JavaScript。
- Signup 与 Account 使用同一 Alpine state 处理 USYD 声明：选中时显示 USU ID，取消时清空输入；服务端返回 USU ID 错误时强制保持显示。未使用 `x-cloak`，因此 JavaScript 被禁用或加载失败时字段仍可见。
- `AccountIdentityForm` 与 `SignupForm` 只增加 Alpine attributes，没有改变服务端字段白名单或 `update_usu_identity` 边界。审核状态仍只能通过既有受控 service 和 Admin workflow 修改。
- Email verification 与 Magic Code confirmation 使用项目 form override 提供 numeric input mode、`one-time-code` autocomplete 和数字格式；自定义 widget 对绑定值返回空值，避免错误 code 被重新写入响应 HTML。
- Password 与 code 的浏览器属性只改善输入体验，认证有效期、尝试次数、重发、单次使用、enumeration prevention 和日志保护仍由 Step 9–13 的服务端配置与测试负责。

### 3.16 静态资源、构建产物与联合验收边界

- `static_src/css/site.css` 是 Tailwind CSS v4 的唯一项目样式源；`static/css/site.css` 是 minified 构建产物。设计 token、字体声明、component classes、focus、mobile 和 reduced-motion 规则均从 source 构建，生成文件不应手工维护。
- 浏览器资产从精确锁定的 npm dependency 复制到 `static/`，运行页面不访问第三方 CDN。复制脚本同时生成 `static/vendor/manifest.json`，记录 package、version、source 和 SHA-256，使版本与文件内容都可检查。
- Alpine.js 负责当前小型客户端状态；HTMX 与 MapLibre GL JS 只完成本地资产准备，尚未建立业务行为或地图组件。资产存在不代表相应后续功能已经实施。
- Development/Test 通过 `STATICFILES_DIRS` 读取项目静态目录；Production 使用 `ManifestStaticFilesStorage` 和独立 `STATIC_ROOT`，由 `collectstatic` 生成内容哈希文件名。`staticfiles/` 是部署输出并被 Git 排除。
- `package.json` 将 vendor copy、hash check、Tailwind build/watch 与 watch smoke 暴露为固定 scripts。字体和前端 library 均由 `package-lock.json` 锁定，license 文件随本地分发资产保存。
- `scripts/verify_steps_17_18.py` 是 Step 17–18 的原子验收入口：安装锁定 npm dependency 与对应 Playwright Chromium、构建并校验资产、验证 watch、运行完整 pytest、migration、Django、Ruff 和 Production collectstatic。任一子命令失败即返回失败，两步不能分别标记完成。
- Playwright 测试使用真实 `StaticLiveServerTestCase` 和 Chromium，覆盖小屏布局、键盘焦点、Alpine 交互、整串 code 输入、无 JavaScript 回退和服务端错误恢复。Node 输出显式按 UTF-8 解码，避免 Windows locale 遮蔽真实浏览器错误。
- 静态资源测试同时检查版本/hash manifest、无第三方 CDN、核心 token、focus/reduced-motion 规则和关键颜色 contrast；这些自动检查补充真实浏览器流程，不替代后续页面内容层面的人工设计审查。

### 3.17 Phase 1 质量、安全与核心流程门禁

- `scripts/verify_phase_1.py` 是 Phase 1 完成后的统一验收入口，可由本地开发者或后续选定的 CI provider 调用。脚本按固定顺序准备锁定前端依赖与 Chromium、构建和校验资产、执行 Ruff、检查 migration 与 Django、重建 PostgreSQL test database、运行 branch coverage 测试、执行严格 Production deploy check，并完成 manifest `collectstatic`；任何非零子命令都会立即终止并向调用方传播失败。
- pytest 使用 strict config/markers 和固定 `tests` discovery root。Coverage 统计 `apps` 与 `config` 的 statement/branch 覆盖；当前实测总覆盖率为 93%，但仓库没有项目负责人批准的最低数字，因此没有设置会把暂定数字固化为契约的 `fail_under`。
- Ruff 以 Python 3.13 为 target，对全项目统一 lint 与 format；仅对 Django settings 的受控 wildcard import 和 Django migration 的 class-level declarations 保留文件级豁免。
- `tests/conftest.py` 在 pytest 进程中默认阻止外部 DNS 与 socket 连接，只允许 loopback、`testserver` 和测试数据库 host。Playwright 通过共享 browser context helper 将 HTTP(S) 请求限制为当前 live-server origin；Python 与浏览器两层隔离共同防止测试意外依赖外部服务。
- Phase 1 browser suite 通过真实 Django live server 与 Chromium 验证 Signup、Email verification、Password login、Magic Code、Account 更新、POST logout 和 Admin USU review。测试从浏览器 Session state 读取由服务端生成的一次性 code，不在生产页面或日志中公开 code。
- 安全回归会检查 Git tracked/unignored 文件中的禁止敏感文件与高置信凭据模式，验证认证 Password、verification/login code、完整 Email、USU ID 和 Session key 不进入捕获日志，并确认 Anonymous 页面不输出既有会员的私有身份字段。
- Production deploy check 注入仅供检查使用的长占位 Secret，并以 warning 为失败等级；该值不用于部署，真实 Production 继续通过 `DJANGO_SECRET_KEY` 环境变量提供 Secret。门禁不输出真实 Secret、Password、code、完整 USU ID 或 Session token。
- 锁定 dependency 安装和 Playwright browser 安装属于门禁环境准备，可以访问 package registry/CDN；进入 pytest 与 browser scenarios 后，业务测试必须保持外部网络隔离。

### 3.18 Phase 1 全新环境与端到端验收

- `scripts/accept_phase_1.py` 是 Step 20 验收入口，位于 Step 19 质量门禁之上。它先确认 Docker PostgreSQL healthy，再通过 `UV_PROJECT_ENVIRONMENT` 在 OS temporary directory 创建独立 uv environment，并从 `uv.lock` 安装全部运行及开发依赖；验收不依赖仓库现有 `.venv` 的包状态。
- 临时 environment 的 Python 负责执行 Development migrations、Step 19 门禁和 Development server。Step 19 门禁内部继续通过 `npm ci` 重建 `node_modules`、安装锁定 Playwright Chromium、构建静态资源、重建测试数据库并完成全部质量、安全和 Production 检查。
- Development server 绑定动态选择的 loopback port，并关闭 Django autoreloader，保证验收脚本只管理一个可终止 process。脚本在 server 提前退出或超时未就绪时失败；无论 browser smoke 成功或异常，都会先 terminate，必要时 kill 并等待 server 退出，再清理临时 environment。
- `development-server-smoke.mjs` 针对实际 `manage.py runserver` 检查 desktop 和 mobile viewport 下的 Home、Signup、Login、Anonymous Account redirect、项目 CSS、横向布局、JavaScript page errors、外部网络请求和 Branding。完整可写认证与 Admin browser flows 继续在隔离的 PostgreSQL test database 中执行，避免 Step 20 smoke 向 Development database 写入合成账户。
- README 是新开发者的操作入口，明确 PowerShell 工具检查、`.env.example` 复制、uv/npm 锁定安装、Compose PostgreSQL、migrate、static build、runserver、质量门禁、端到端验收和合成数据人工走查。Development console Email 仅用于本地读取 code；真实 SMTP 与 Production Provider 仍未选择。
- 自动验收在临时 environment 中通过 184 个测试并保持 93% branch coverage；项目负责人随后完成并确认注册、两种登录、Account、USU review、POST logout、键盘、mobile 和 Branding 人工走查。该结果满足 Phase 1 退出门槛，不代表 Phase 2 页面或 Production provider 已实施。

### 3.19 Phase 2 公开页面基础、品牌与响应式导航

- `core/base.html` 继续作为唯一前台页面壳，并在既有 title 之外增加 description、robots、Open Graph title/description、当前请求 URL 和额外 head 扩展区块。后续公开页面可以覆盖内容，不需要复制完整 `<head>`；最终页面 metadata 仍由对应页面及 Step 26 固定。
- 对外页面壳、Home 占位、Account、allauth 认证模板和 Footer 统一使用完整 `NULDL Armwrestling Club` 品牌名称。Header 的可访问名称与可见文字一致，不再以含义不完整的单独缩写作为品牌入口。
- Header 使用原生 `details`/`summary` 作为移动菜单控制。标记默认展开，使 desktop 和禁用 JavaScript 的 mobile 页面始终具有可访问链接；Alpine.js 仅在已加载且匹配手机宽度时执行初始收起，后续 Enter、Space、点击和展开状态均由浏览器原生 disclosure 行为负责。
- 导航继续依据认证状态输出 Anonymous 的 Login/Signup 或 Member 的 Account，并使用既有 URL name 标记当前页。Step 21 没有创建 About、Events、Members 或 Locations 链接，避免在对应页面建立前出现失效入口。
- `static_src/css/site.css` 增加 public page、section header、responsive card grid、content card、CTA panel 和 status banner 基础类；这些类只建立 Phase 2 页面复用边界，不代表 Home、About、安全页面或 Risk Notice 内容已经实施。
- Playwright 通过独立 public foundation scenario 验证 1440px desktop 与 390px mobile、skip link、可见 Focus、菜单键盘开关、无 JavaScript 链接、无水平溢出、page error 和同源网络边界。项目负责人完整回归共运行 186 个测试并全部通过。

### 3.20 Home、响应式 Logo 与静态日程

- Home 继续由 `apps.core` 的既有根路径 view 服务，不新增 Model、migration 或业务 API。模板使用 `design_document.md` 已确认的英文 Hero、新手说明、训练内容、参与资格、Metadata 和 Open Graph 文案。
- Hero 与 Upcoming Session 的主要操作按认证状态在服务端分支：Anonymous 使用 `Join the Club` 进入 Signup，authenticated member 使用 `Account` 进入本人账户页；`New to Armwrestling?` 是普通页内锚点，全部操作在禁用 JavaScript 时仍可用。
- Upcoming Session 是模板内的静态信息，只展示已确认的 `1 December 2026`、`3:00–7:00 pm`、`Training Session` 和 `Venue details to be confirmed`，并附已批准的后续信息说明。当前没有 Event model、报名状态、报名操作或 Events 路由。
- 已批准的 `Logo_without_USYD.png` 以原始字节保存在 `static_src/images/brand/`，尺寸为 1254 × 1254、大小为 1,776,890 bytes，SHA-256 为 `1bc738b3a7af5719a296bc0aecc67f2ea943d1acf7eadb499c3dd28592308944`。源文件不直接作为页面下载资产，且图形内容未被重新设计。
- `scripts/build_home_images.py` 使用锁定版 Pillow 从受 hash、格式、尺寸和色彩模式保护的源图确定性生成 480、800、1200px 方形 WebP。生成物分别为 32,364、69,400、125,860 bytes；`package.json` 将生成与漂移检查接入现有 `static:build` 和 `static:check`。
- Home `<picture>` 通过 width descriptor 与 `sizes` 选择响应式 Logo，`img` 保留明确宽高、方形 aspect ratio、非空替代文本和 `object-fit: contain`。Header 继续只使用文字品牌，没有缩放完整 Logo，也没有加入 University Branding。
- Django 测试锁定获准内容、Metadata、Anonymous/Member CTA、静态日程、无 Events 链接、源图完整性、生成图格式/尺寸/压缩与可重复性。Playwright 验证 desktop、mobile 和禁用 JavaScript 时的 Logo 加载与比例、无水平溢出、文字/CTA 不被裁切、CTA 目标及内容完整性；项目负责人完整回归共运行 195 个测试并全部通过。

### 3.21 About 与 Beginners & Safety 公开信息页

- About 与 Beginners & Safety 继续归属 `apps.core`，分别由 `/about/` 和 `/beginners-safety/` 具名路由提供；页面是无数据库依赖的服务端渲染公开内容，不引入 Model、migration 或 API。
- 两页各自覆盖全局 Metadata/Open Graph block，并使用 `design_document.md` 已批准的英文内容。About 明确呈现 student-led club 的定位，但不声明 University affiliation；Beginners & Safety 呈现 induction、supervised practice、dedicated equipment、主要风险和停止训练条件，但不充当版本化 Risk Notice。
- Header 在既有 Home 与认证操作之间加入两个公开页面链接，并继续使用 URL name 输出当前页状态。Anonymous CTA 指向 Signup，authenticated member CTA 指向 Account；导航和 CTA 均为普通链接，不依赖 JavaScript。
- 公开内容组件样式建立受限正文宽度、卡片列表、编号步骤、安全列表与提示面板，复用既有 tokens、focus 和 responsive page shell。页面不公开联系邮箱、具体地点或未经批准的 University Branding。
- Django 测试锁定 URL、模板、Metadata、文案、受限内容、导航与 CTA；Playwright 验证 desktop/mobile、键盘访问、200% content zoom、禁用 JavaScript、可见内容边界、无横向溢出和同源网络隔离。项目负责人完整回归共运行 207 个测试并全部通过。

### 3.22 Draft Risk Notice 环境隔离

- `RISK_NOTICE_DRAFT_VISIBLE` 在公共 settings 中默认关闭。Development 明确设为开启，Test 明确保持关闭，Production 强制关闭且不读取同名环境变量，因此部署环境无法通过变量意外公开 Draft。
- `config.settings.preview` 继承 Production 的 Secret、PostgreSQL、SMTP、HTTPS 与 manifest static 配置，并要求显式解析 `RISK_NOTICE_DRAFT_VISIBLE`。缺少该变量时 Preview settings 安全失败；只有获准私有 Preview 明确提供 `true` 才显示 Draft。
- `/risk-notice/` 由 `apps.safety` 的具名路由和无数据库 view 提供。路由始终可反向解析以支持条件模板链接，但 view 在开关关闭时抛出 404，不渲染 Draft template，也不查询数据库。
- Safety context processor 只向 RequestContext 暴露 Draft 可见性的 Boolean，不暴露环境变量或其他 settings。Header 和 Beginners & Safety 据此同时显示或隐藏链接，避免关闭状态留下可发现入口。
- Draft template 逐字保存获准的四段当前正文，包括重复 acknowledgement；页面使用明确 Draft banner、说明文字及 `noindex, nofollow`，没有 POST、checkbox、报名确认或责任限制文本改写。
- 本步没有创建 RiskNoticeVersion、Model、migration、Event 关系或 sitemap。正式版本管理、历史确认和报名事务仍属于 Phase 4；Step 26 建立 sitemap 时必须继续排除 Draft。
- Django 测试覆盖环境矩阵、默认关闭、404、逐字正文、重复段落、robots、条件导航、无表单和零数据库查询；Playwright 覆盖 desktop/mobile、键盘、禁用 JavaScript、布局及同源网络隔离。项目负责人完整回归共运行 216 个测试并全部通过。

### 3.23 全局 403、404 与 500 错误处理

- 项目根 URLConf 显式注册三个 Django error handlers。403 与 404 接受 Django 传入的 `exception` 关键字参数后立即丢弃；500 只接收 request。异常对象、错误消息和内部状态不会进入 template context。
- handlers 由 `apps.core.views` 提供，并分别以 403、404 和 500 状态渲染固定模板。错误响应因此保持原始 HTTP 语义，不通过 redirect 或 200 页面掩盖错误。
- 三个模板继承唯一全局页面壳，复用 Header、Footer、本地 CSS、Focus 与响应式基础；页面使用中性英文标题、唯一 H1 和普通 `Return Home` link，不提供虚构联系方式或依赖 JavaScript 的恢复操作。
- 错误页面不输出 traceback、Exception、内部文件路径、Secret 或异常原文。Step 25 没有引入错误监控 Provider、客户端错误上报、Model、migration 或外部资源。
- 测试使用独立 URLConf 将合成的 PermissionDenied、缺失路由和未处理异常送入真实 handlers，避免在生产 URL 中建立测试入口。Playwright 验证三个状态的 desktop/mobile、CSS、键盘 Focus、无 JavaScript、无横向溢出和同源网络隔离；项目负责人完整回归共运行 221 个测试并全部通过。

### 3.24 公开 Metadata、Sitemap 与 Footer 边界

- Home、About 和 Beginners & Safety 在各自模板中覆盖准确的 title、description 与 Open Graph title/description；公共页面壳统一提供 `website` type、`NULDL Armwrestling Club` site name 及由当前 request 派生的绝对 URL。
- 最终域名仍未确认，因此页面没有 canonical link，也不硬编码 `nuldl.com` 或测试 host；部署环境的 host 配置继续由对应 settings 控制。
- `/sitemap.xml` 由 `apps.core` 的无数据库 view 和 XML template 生成。公开范围由 `PUBLIC_SITEMAP_URL_NAMES` 显式 allowlist 决定，当前只包含 Home、About 和 Beginners & Safety，避免自动 URL 发现误收录认证、管理、错误、Draft 或未来路由。
- Draft Risk Notice 即使在 Development 或获准 Preview 开启，也始终保留 `noindex, nofollow` 且不进入 sitemap；Production 继续强制关闭 Draft 正文。
- Footer 公开唯一获准联系渠道 Instagram `@nuldl_armwrestlingclub` 的 HTTPS 链接，不公开 Email，也不加入 University Logo、Crest 或 affiliation 表述。
- Django 测试解析真实 sitemap XML 并锁定精确 allowlist，同时验证 metadata、环境派生 URL、Footer 与禁止内容；项目负责人专项回归 44 个测试、完整回归 230 个测试均通过。

### 3.25 Phase 2 统一 Accessibility 浏览器门禁

- `phase2-accessibility.mjs` 在一个锁定 Chromium 会话中统一遍历 Home、About、Beginners & Safety、Draft Risk Notice、403、404 和 500 页面，减少各步骤独立 smoke test 之间的覆盖差异。
- 测试使用既有 `browser-support.mjs` 建立只允许当前 live-server origin 的 context；任何外部 HTTP(S) 请求和浏览器 page error 都会使统一场景失败。
- Desktop 与 mobile 检查共享 landmarks、Heading 顺序、link name、图片 alt、页面特有组件、Footer、横向溢出及可见内容裁切。Home 另验证 Logo 解码、自然尺寸和替代文本。
- Mobile 场景打开原生 disclosure 后检查全部可见交互目标至少为 24px，并从 skip link、品牌、Menu 到全部导航操作验证真实 Tab 顺序、可见 Focus 和 viewport 内位置。
- 200% 内容放大使用 640px viewport 与根字体 200% 模拟 320 CSS px reflow；所有目标页面必须保持无横向溢出和可读内容边界。
- JavaScript disabled 场景要求相同公开与错误页面、Header 链接、主内容和 Footer 继续可用；`prefers-reduced-motion: reduce` context 验证媒体查询命中及 animation/transition 时长被压缩。
- 关键正文、弱化正文、主要按钮、Draft banner 和 Focus indicator 使用浏览器计算样式执行 WCAG 对比度计算；该自动化属于已实施页面的风险门禁，不表示形式化 WCAG 认证。
- Django wrapper 以 `DEBUG=False`、开启 Draft 并复用 `tests.error_urls` 启动 `StaticLiveServerTestCase`，因此同一场景可以验证真实 403/404/500 handler、静态资源和 Draft 环境分支，而不建立生产测试 URL。
- 本门禁没有引入新依赖、外部 accessibility service、Model 或 migration，也没有因测试结果修改生产 template 或 CSS。项目负责人专项 1 个测试、浏览器回归 7 个测试及完整 231 个测试均通过。

### 3.26 Phase 2 共享质量门禁与全新环境验收

- `scripts/verify_project.py` 取代阶段专属脚本成为共享项目门禁，固定执行 npm 锁定安装、Chromium 准备、静态资源 build/check/watch、Ruff lint/format、migration drift、Django check、干净 PostgreSQL branch coverage 测试、Production deploy check 和 manifest `collectstatic`，并传播任何子命令失败。
- `scripts/verify_phase_1.py` 保留为兼容 wrapper，使既有 Phase 1 命令继续委派到同一共享门禁，避免门禁逻辑分叉。
- `scripts/accept_phase_2.py` 使用 `UV_PROJECT_ENVIRONMENT` 在 OS 临时目录建立独立锁定环境，等待 Docker PostgreSQL、执行 Development migration 与共享门禁，再在动态 loopback port 启动真实 Development server 并运行 Phase 2 smoke；所有退出路径都会终止 server 并清理临时环境。
- `phase2-development-smoke.mjs` 在 desktop/mobile 下覆盖正式公开页、Draft 分支、错误页与认证入口，验证 CSS、响应式布局、页面错误及同源网络边界，不向 Development database 写入合成会员数据。
- `tests/test_phase2_acceptance.py` 锁定命令失败传播、运行中 server 清理及 README 验收说明；`tests/test_quality_gate.py` 直接验证共享门禁，防止兼容 wrapper 掩盖真实入口。
- 初次全新环境验收通过 234 个测试、94% branch coverage、Production 检查与 browser smoke。人工走查后的 Home、About 和 Beginners & Safety 内容与 CTA 收尾通过专项 Django/Playwright、静态与 Ruff 验证，项目负责人确认最终验收。
- 该架构只完成 Phase 2 已定义页面与验收边界。Risk Notice 最终文本、University Branding、地点、Production Provider、数据保留和中文版本仍由后续批准或阶段处理；Phase 3 尚未实施。

## 四、当前文件职责

| 文件 | 当前作用 |
| --- | --- |
| `.gitignore` | 排除 Python 构建产物、虚拟环境、测试缓存、Django 本地数据库、`.env`、其他本地 `.env.*`、`node_modules/`、Production `staticfiles/` 收集目录、日志和常见工具生成文件；明确保留 `.env.example` 与 `uv.lock`。 |
| `.env.example` | 声明本地 PostgreSQL、Django Development/Test 和 Production 配置所需变量及安全示例值，供开发者复制为未跟踪的 `.env`。 |
| `AGENTS.md` | 定义仓库级开发约束，包括编码前必读文档、架构变更审批、计划目录、测试原则、命名规范和敏感数据限制。 |
| `README.md` | 提供项目定位、工具要求、首次安装、日常开发、migration/static/runserver 命令、共享质量门禁、Phase 1/2 自动验收、人工核心流程、安全数据边界和目录职责；明确中性 NULDL Branding。 |
| `pyproject.toml` | 定义项目元数据、Python 3.13.x 要求、精确运行及开发依赖，并配置 pytest strict mode/test root、pytest-django Test settings、`apps`/`config` branch coverage 与 Python 3.13 Ruff lint/format；只保留 settings wildcard import 和 migration class attributes 所需的文件级豁免。 |
| `uv.lock` | 记录由 `uv` 解析的完整 Python 依赖图、版本和包来源，用于可重复安装；不手工编辑。 |
| `package.json` | 定义锁定的浏览器 library、字体与前端开发工具，并提供 vendor copy/check、Home 图片 build/check、Tailwind build/watch、watch smoke 和完整 static build/check scripts。 |
| `package-lock.json` | 记录完整 npm 依赖树、下载来源和完整性信息，供 `npm ci` 可重复安装；不手工编辑。 |
| `scripts/build-static-assets.mjs` | 按固定清单从锁定 npm packages 复制 Alpine.js、HTMX、MapLibre GL JS、字体与 license，并生成或校验包含版本和 SHA-256 的 vendor manifest。 |
| `scripts/build_home_images.py` | 校验获准 Home Logo 源文件的 SHA-256、格式、尺寸与模式，并以锁定 Pillow 确定性生成或检查三个响应式 WebP 版本。 |
| `scripts/check-css-watch.mjs` | 在临时目录启动 Tailwind `--watch=always`，确认首次 watch build 完成后终止进程并清理临时输出。 |
| `scripts/verify_steps_17_18.py` | 提供 Step 17–18 原子联合门禁，顺序执行依赖与 Chromium 准备、资产 build/check、watch smoke、完整测试、Django/Ruff 检查和 Production collectstatic。 |
| `scripts/verify_project.py` | 提供跨阶段共享的本地/CI 质量安全门禁，执行锁定依赖和浏览器准备、静态构建与 watch smoke、Ruff、migration/Django、干净 PostgreSQL branch coverage 测试、warning-level Production deploy check 与 manifest collectstatic，并传播所有子命令失败。 |
| `scripts/verify_phase_1.py` | 保留 Phase 1 命令兼容性，并将执行委派给 `scripts/verify_project.py`，不再维护独立门禁逻辑。 |
| `scripts/accept_phase_1.py` | 提供 Step 20 全新环境端到端验收：建立临时 uv environment、等待 PostgreSQL、执行 Development migration 与完整 Phase 1 门禁、启动并可靠清理本机 Django server，再运行 desktop/mobile Playwright smoke。 |
| `scripts/accept_phase_2.py` | 提供 Step 28 全新环境端到端验收：建立临时 uv environment、等待 PostgreSQL、执行 Development migration 与共享项目门禁、启动并可靠清理真实 Development server，再运行 Phase 2 desktop/mobile Playwright smoke。 |
| `static_src/css/site.css` | Tailwind CSS v4 项目样式源，声明 template source、local fonts、颜色与字体 tokens、全局基础规则、公开页面 section/card/list/CTA/status/safety panel、Home Hero/Logo/日程组件、响应式导航、focus 和 reduced-motion。 |
| `static/css/site.css` | 由 Tailwind CLI 从 `static_src/css/site.css` 生成的 minified 浏览器样式；作为部署输入提交，不手工编辑。 |
| `static_src/images/brand/Logo_without_USYD.png` | 保存获准 Home Logo 的未改动 PNG 源文件；由固定 SHA-256 保护，不直接作为响应式页面资产。 |
| `static/images/brand/nuldl-club-logo-480.webp` | 从获准源图生成的 480 × 480 WebP，供窄屏 Home Hero 使用。 |
| `static/images/brand/nuldl-club-logo-800.webp` | 从获准源图生成的 800 × 800 WebP，并作为 Home Logo 默认 `img` fallback。 |
| `static/images/brand/nuldl-club-logo-1200.webp` | 从获准源图生成的 1200 × 1200 WebP，供较高像素密度或较宽 Hero 使用。 |
| `static/fonts/inter-latin-400-normal.woff2` | 本地 Inter Latin 400 字重文件，供正文常规文本使用。 |
| `static/fonts/inter-latin-500-normal.woff2` | 本地 Inter Latin 500 字重文件，供中等强调文本使用。 |
| `static/fonts/inter-latin-600-normal.woff2` | 本地 Inter Latin 600 字重文件，供按钮、导航与加重正文使用。 |
| `static/fonts/barlow-condensed-latin-600-normal.woff2` | 本地 Barlow Condensed Latin 600 字重文件，供次级标题使用。 |
| `static/fonts/barlow-condensed-latin-700-normal.woff2` | 本地 Barlow Condensed Latin 700 字重文件，供主要标题使用。 |
| `static/fonts/barlow-condensed-latin-800-normal.woff2` | 本地 Barlow Condensed Latin 800 字重文件，供高强调标题使用。 |
| `static/vendor/alpine/alpine.min.js` | 从锁定 Alpine.js package 复制的本地 minified runtime，负责当前 USYD 条件界面与错误焦点增强。 |
| `static/vendor/htmx/htmx.min.js` | 从锁定 HTMX package 复制的本地 minified runtime；当前仅完成资产准备，尚未接入业务请求。 |
| `static/vendor/maplibre/maplibre-gl.mjs` | 从锁定 MapLibre GL JS package 复制的本地 ESM runtime；留待后续地图功能使用。 |
| `static/vendor/maplibre/maplibre-gl.css` | 与本地 MapLibre runtime 配套的控件样式；当前尚未加载到无地图页面。 |
| `static/vendor/licenses/inter.txt` | 保存本地分发 Inter 字体对应 package 的 license 文本。 |
| `static/vendor/licenses/barlow-condensed.txt` | 保存本地分发 Barlow Condensed 字体对应 package 的 license 文本。 |
| `static/vendor/licenses/htmx.txt` | 保存本地分发 HTMX 对应 package 的 license 文本。 |
| `static/vendor/licenses/maplibre-gl.txt` | 保存本地分发 MapLibre GL JS 对应 package 的 license 文本。 |
| `static/vendor/manifest.json` | 记录全部脚本管理 vendor/font 输出的 package、精确版本、源路径与 SHA-256，供 `assets:check` 检测漂移。 |
| `compose.yaml` | 定义本地 PostgreSQL 18.6 service、端口映射、健康检查、重启策略和持久化 named volume。 |
| `manage.py` | 本地运行 Django management command 的命令行入口，默认加载 `config.settings.development`。 |
| `config/__init__.py` | 将 `config` 标记为 Python package。 |
| `config/settings/__init__.py` | 将 `config.settings` 标记为环境配置 package，不隐式选择具体环境。 |
| `config/settings/base.py` | 保存公共 Django 配置、根级 template 目录、项目 static 目录与 `STATIC_ROOT`、`AUTH_USER_MODEL`、Django Admin、Sites、allauth Apps、认证 backend、认证行为、项目 allauth form overrides、数字 code 格式、redirect settings、allauth middleware、默认关闭的 Draft 开关与 Safety context processor，以及严格的环境变量与 PostgreSQL URL 解析函数。 |
| `config/settings/development.py` | 定义本地 Debug、Console Email、local media、环境变量驱动的 PostgreSQL 配置，并明确开启 Draft Risk Notice。 |
| `config/settings/test.py` | 定义关闭 Debug 的自动化测试环境、独立 PostgreSQL test database、in-memory Email、快速 Password hasher 及默认关闭的 Draft Risk Notice。 |
| `config/settings/preview.py` | 继承 Production 安全配置并要求显式的 Draft Risk Notice Boolean 开关；缺少变量时拒绝加载。 |
| `config/settings/production.py` | 定义环境变量驱动的 Production Secret、hosts、PostgreSQL、SMTP、HTTPS 安全设置及 `ManifestStaticFilesStorage`，并强制关闭 Draft Risk Notice；缺少必填值时拒绝加载。 |
| `config/urls.py` | 项目根 URL 配置，开放 `/admin/`，依次接入 core、safety 和 accounts URLConf，将 `/accounts/` 委托给 `allauth.urls`，并注册 403、404 与 500 handlers。 |
| `config/asgi.py` | 暴露 ASGI application 入口，默认加载 Production settings。 |
| `config/wsgi.py` | 暴露 WSGI application 入口，默认加载 Production settings。 |
| `apps/__init__.py` | 将 `apps` 标记为承载领域 App 的 Python package。 |
| `apps/core/__init__.py` | 将 `core` 标记为 Python package。 |
| `apps/core/apps.py` | 定义 `CoreConfig`，将 `apps.core` 注册为 Django App。 |
| `apps/core/views.py` | 提供 Home、About 与 Beginners & Safety 的无数据库公开页面 views、基于显式 allowlist 和当前 request 构造绝对 URL 的 sitemap view，以及不向模板传递异常详情的 403、404 与 500 handlers。 |
| `apps/core/urls.py` | 将空路径、`/about/`、`/beginners-safety/` 与 `/sitemap.xml` 映射为具名路由；精确匹配保证其他根级 URL 可继续交给对应 App。 |
| `apps/core/templates/core/base.html` | 定义前台全局 HTML 页面壳、skip link、语义化 landmarks、title、description、robots、Open Graph 与额外 head 扩展区块；加载本地 CSS 与 Alpine.js，并在初始化后恢复 validation error focus。 |
| `apps/core/templates/core/home.html` | 提供正式英文 Home、页面 Metadata、响应式 Logo、认证状态分支 CTA、页内新手入口、训练内容、参与资格和无报名能力的静态日程。 |
| `apps/core/templates/core/about.html` | 提供正式英文 About、页面 Metadata、组织目的、活动内容、参与资格、训练方式和认证状态分支 CTA。 |
| `apps/core/templates/core/beginners_safety.html` | 提供正式英文 Beginners & Safety、页面 Metadata、入门步骤、训练风险、停止条件、安全提示和认证状态分支 CTA；仅在环境允许时增加 Draft Risk Notice 次级入口，不替代正式 Risk Notice。 |
| `apps/core/templates/core/errors/403.html` | 使用共享页面壳呈现中性 Access Denied 状态和 Return Home 操作，保持 HTTP 403。 |
| `apps/core/templates/core/errors/404.html` | 使用共享页面壳呈现中性 Page Not Found 状态和 Return Home 操作，保持 HTTP 404。 |
| `apps/core/templates/core/errors/500.html` | 使用共享页面壳呈现中性 Something Went Wrong 状态和 Return Home 操作，保持 HTTP 500。 |
| `apps/core/templates/core/sitemap.xml` | 输出符合 sitemap XML namespace 的公开 URL 列表；内容只来自 view 的显式 Production 公开页面 allowlist。 |
| `apps/core/templates/core/includes/header.html` | 输出完整文字品牌，根据认证状态提供 Home、About、Beginners & Safety、Login、Signup 或 Account，并仅在环境允许时加入 Draft Risk Notice；以 URL name 标记当前页，以原生 disclosure 和最小 Alpine 初始化实现 desktop/mobile、键盘及无 JavaScript 导航。 |
| `apps/core/templates/core/includes/messages.html` | 将 Django messages 输出到 polite live region，并为错误和非错误反馈提供相应 ARIA role。 |
| `apps/core/templates/core/includes/footer.html` | 提供完整 `NULDL Armwrestling Club` 名称、动态年份和已批准的 Instagram HTTPS 链接；不公开联系邮箱或未经授权的大学品牌资产。 |
| `apps/core/migrations/__init__.py` | 将 `core.migrations` 标记为 migration package；当前没有 migration。 |
| `apps/accounts/__init__.py` | 将 `accounts` 标记为 Python package。 |
| `apps/accounts/apps.py` | 定义 `AccountsConfig`，将 `apps.accounts` 注册为 Django App。 |
| `apps/accounts/models.py` | 定义 Custom User、专用 USU 审核权限、Email/USU ID 规范化、数字 validator、USU 状态转换、审核字段写入保护及三项数据库约束。 |
| `apps/accounts/admin.py` | 注册 Custom UserAdmin，提供 USU 审核列表、筛选、搜索、只读角色视图及 Verify/Reject actions，并隔离无权限 Staff。 |
| `apps/accounts/forms.py` | 定义 Account 身份更新、allauth signup、Magic Code request 及两类 code confirmation forms；通过字段白名单与既有 service 隔离只读/审核字段，并为 USYD 渐进增强和不回显数字 code 提供 widget attributes。 |
| `apps/accounts/views.py` | 提供登录保护的 Account GET/POST view，固定使用当前 User，查询本人 Email verification status，并在成功更新后执行 redirect-after-POST。 |
| `apps/accounts/urls.py` | 将项目 Account view 暴露为命名路由 `account`，路径为 `/account/`。 |
| `apps/accounts/templates/accounts/account.html` | 继承全局页面壳，显示只读账户及审核状态、身份更新 form、Password change 入口和 POST logout；使用 Alpine 条件显示 USU ID，同时保留无 JavaScript 的可见字段和普通 POST。 |
| `templates/account/includes/form_errors.html` | 输出 form 非字段错误的可聚焦 alert summary，供所有项目认证模板复用。 |
| `templates/account/includes/field.html` | 通过 Django `as_field_group` 输出单个字段及其 label、help text、error 与 ARIA 关联。 |
| `templates/account/includes/form_fields.html` | 组合 form-level error 与全部 visible/hidden fields，减少认证模板间的字段呈现差异。 |
| `templates/account/signup.html` | 呈现项目 Signup 页面，并用 Alpine 渐进增强 USYD/USU ID 条件输入，保留服务端 POST 回退。 |
| `templates/account/login.html` | 呈现 Username/Password 登录与 Magic Code、Password reset、Signup 入口。 |
| `templates/account/request_login_code.html` | 呈现 Magic Code Email 请求 form，并维持 allauth enumeration-prevention 流程。 |
| `templates/account/confirm_login_code.html` | 呈现数字 Magic Code 确认与重发操作，复用不回显 code widget。 |
| `templates/account/confirm_email_verification_code.html` | 呈现注册 Email 数字验证码确认与重发操作，复用不回显 code widget。 |
| `templates/account/password_reset.html` | 呈现 Password reset Email 请求 form。 |
| `templates/account/password_reset_done.html` | 呈现 Password reset 请求完成后的通用说明，不泄露账户是否存在。 |
| `templates/account/password_reset_from_key.html` | 呈现有效 reset key 的新 Password 输入或无效 key 状态。 |
| `templates/account/password_reset_from_key_done.html` | 呈现 Password reset 完成状态及登录入口。 |
| `templates/account/password_change.html` | 呈现 authenticated member 的旧 Password 与新 Password 更新 form。 |
| `templates/account/password_set.html` | 呈现无可用 Password 账户的 Password 设置 form。 |
| `templates/account/logout.html` | 呈现带 CSRF 的 POST logout 确认，不通过 GET 改变认证状态。 |
| `templates/account/account_inactive.html` | 呈现停用账户状态及不虚构联系方式的中性支持说明。 |
| `templates/account/reauthenticate.html` | 呈现 allauth 敏感操作所需的 Password reauthentication form。 |
| `apps/accounts/services.py` | 提供事务化的 USYD/USU ID 更新和专用权限审核入口，使用 row lock 重新确认目标与 reviewer，避免并发覆盖及权限绕过。 |
| `apps/accounts/migrations/__init__.py` | 将 `accounts.migrations` 标记为 migration package。 |
| `apps/accounts/migrations/0001_initial.py` | 作为首条项目业务 migration，创建 `accounts_user`、自定义身份字段及 Django 标准 Group/Permission 关系。 |
| `apps/accounts/migrations/0002_alter_user_usu_id_and_more.py` | 为 USU ID 增加数字 validator，并在 PostgreSQL 中建立 Email 规范化、USU ID 规范化和 USU 状态组合约束。 |
| `apps/accounts/migrations/0003_alter_user_options.py` | 在 User model options 中声明 `review_usu_id` 专用权限，不改变业务字段或约束。 |
| `apps/members/__init__.py` | 将 `members` 标记为 Python package。 |
| `apps/members/apps.py` | 定义 `MembersConfig`，将 `apps.members` 注册为 Django App，并在 `ready()` 中加载 Email 确认 signal receiver。 |
| `apps/members/models.py` | 定义 MemberProfile、字段 choices、规范化与验证、Avatar 内容检查、PostgreSQL 约束，以及只返回可公开 Profile 的 queryset。 |
| `apps/members/services.py` | 提供幂等的 MemberProfile 创建入口，由 Email 确认 signal receiver 调用。 |
| `apps/members/signals.py` | 接收 allauth 官方 `email_confirmed` signal，并在 Email 验证成功后通过 service 确保 MemberProfile 存在。 |
| `apps/members/forms.py` | 定义会员可写资料字段白名单，隔离管理员字段和系统时间戳；当前尚未连接页面。 |
| `apps/members/admin.py` | 注册 MemberProfile 后台模型，提供列表、筛选、搜索和只读时间戳配置。 |
| `apps/members/migrations/__init__.py` | 将 `members.migrations` 标记为 migration package。 |
| `apps/members/migrations/0001_initial.py` | 创建 MemberProfile 全部字段、One-to-one User 关系，以及显示名规范化、忽略大小写唯一和 HTTPS 社交链接数据库约束。 |
| `apps/events/__init__.py` | 将 `events` 标记为 Python package。 |
| `apps/events/apps.py` | 定义 `EventsConfig`，将 `apps.events` 注册为 Django App。 |
| `apps/events/migrations/__init__.py` | 将 `events.migrations` 标记为 migration package；当前没有 migration。 |
| `apps/locations/__init__.py` | 将 `locations` 标记为 Python package。 |
| `apps/locations/apps.py` | 定义 `LocationsConfig`，将 `apps.locations` 注册为 Django App。 |
| `apps/locations/migrations/__init__.py` | 将 `locations.migrations` 标记为 migration package；当前没有 migration。 |
| `apps/safety/__init__.py` | 将 `safety` 标记为 Python package。 |
| `apps/safety/apps.py` | 定义 `SafetyConfig`，将 `apps.safety` 注册为 Django App。 |
| `apps/safety/context_processors.py` | 将当前环境是否允许 Draft Risk Notice 作为单一 Boolean 提供给全局 RequestContext，供 Header 与页面 CTA 同步控制可发现性。 |
| `apps/safety/urls.py` | 将 `/risk-notice/` 映射为命名路由 `safety:risk_notice`。 |
| `apps/safety/views.py` | 在 Draft 开关开启时渲染静态 Risk Notice；关闭时抛出 404，全程不访问数据库。 |
| `apps/safety/templates/safety/risk_notice.html` | 逐字呈现获准 Draft 正文、重复 acknowledgement、Draft banner 和 `noindex, nofollow`；不提供确认或报名表单。 |
| `apps/safety/migrations/__init__.py` | 将 `safety.migrations` 标记为 migration package；当前没有 migration。 |
| `tests/__init__.py` | 将顶层 `tests` 标记为 Python package。 |
| `tests/conftest.py` | 提供全套测试自动启用的外部网络隔离，只允许 loopback、Django test host 和当前数据库 host，并对外部 DNS/socket 连接立即失败。 |
| `tests/test_project_scaffold.py` | 验证六个 AppConfig 可导入、名称正确且没有额外项目 App 注册。 |
| `tests/test_database_settings.py` | 验证 PostgreSQL URL 解析、encoded credentials、连接 options、非 PostgreSQL 拒绝和必填变量失败行为。 |
| `tests/test_environment_settings.py` | 验证 Development、Test、Production 的环境职责、Production 安全设置、manifest static storage 和缺少 Secret 时的安全失败。 |
| `tests/test_user_model.py` | 验证 Custom User 创建、标准权限字段、身份与审核默认值、Email 必填与唯一，以及审核人 Self ForeignKey 的 `SET_NULL` 行为。 |
| `tests/test_user_identity_rules.py` | 验证 Email 和数字型 USU ID 规范化、全部 USU 状态转换、专用审核权限、前导零保留及数据库对直接写入的约束。 |
| `tests/test_member_profile.py` | 验证 MemberProfile schema、默认值、幂等创建、字段规范化、上传安全、公开查询、会员字段边界和 Admin 配置。 |
| `tests/test_authentication_configuration.py` | 验证 allauth Apps、backend、认证 settings、邮箱验证码与 Magic Code 生命周期配置、默认 rate limits、redirects、必需 URL 和排除功能的路由边界。 |
| `tests/test_signup_form.py` | 验证 signup 字段顺序与必填性、Email/Username 冲突、enumeration prevention、USYD/USU ID 服务端规则、数字规范化及无 JavaScript 的普通 POST 与 verification redirect。 |
| `tests/test_email_verification.py` | 验证待确认状态、正确、错误、过期与重复验证码、重发与即时限流、幂等 Profile 创建，以及日志不泄露完整 Email 或验证码。 |
| `tests/test_password_authentication.py` | 验证密码登录、通用凭据错误、未验证与停用账户、站内及外部 redirect、Password reset 枚举保护与密码更新，以及 GET/POST logout 边界。 |
| `tests/test_magic_code_authentication.py` | 验证 Magic Code 的有效、错误、过期、单次使用、重发、请求限制、账户资格、enumeration prevention、密码登录独立性及敏感日志边界。 |
| `tests/test_account_page.py` | 验证 Account 访问控制、本人数据隔离、Email verification 显示、form 初始化、USYD/USU ID 状态转换、只读与审核字段防伪造、Password change 和 POST logout 页面边界。 |
| `tests/test_user_admin.py` | 验证 UserAdmin 配置、四类角色权限差异、Verify/Reject、直接编辑防护、重新提交、审核人停用及前台敏感信息边界。 |
| `tests/test_global_templates.py` | 验证全局页面壳、metadata/head blocks、完整品牌、Anonymous/Member Header、当前导航、已实施公开页面链接、无失效链接、skip link、landmarks、唯一 H1/title、消息播报、本地 Alpine 和普通导航/form 基线。 |
| `tests/test_public_foundation_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 21 公开页面 Playwright scenario。 |
| `tests/test_home_page.py` | 验证 Home 获准英文内容与 Metadata、静态日程、无 Events/报名入口、响应式 Logo 引用、受限 Branding 边界及 Anonymous/Member CTA。 |
| `tests/test_home_images.py` | 验证获准 Logo 源文件的精确 hash、大小、格式、尺寸与模式，以及 WebP 生成物的尺寸、格式、压缩和可重复性。 |
| `tests/test_home_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 22 Home Playwright scenario。 |
| `tests/test_public_information_pages.py` | 验证 About 与 Beginners & Safety 的 URL、模板、Metadata、获准文案、受限内容、Header 当前页、Anonymous/Member CTA 和未实施功能边界。 |
| `tests/test_public_information_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 23 公开信息页 Playwright scenario。 |
| `tests/test_draft_risk_notice.py` | 验证 Draft 环境矩阵、默认关闭、Production 强制关闭、Preview 显式开关、404、逐字正文、重复 acknowledgement、robots、条件链接、无表单和零数据库查询。 |
| `tests/test_draft_risk_notice_browser.py` | 以开启 Draft 的 Django `StaticLiveServerTestCase` 调用 Step 24 Playwright scenario。 |
| `tests/error_urls.py` | 提供只在测试中使用的合成 403/500 endpoints，并复用项目 URL 与 handlers 验证真实 Django 错误分派；不进入生产 URLConf。 |
| `tests/test_error_pages.py` | 在 `DEBUG=False` 下验证真实 403、404、500 handlers 的状态码、模板、title、唯一 H1、Home link、CSS 和敏感内容隔离。 |
| `tests/test_error_pages_browser.py` | 以隔离错误 URLConf 启动真实测试站点并调用 Step 25 Playwright scenario。 |
| `tests/test_phase2_accessibility_browser.py` | 在 `DEBUG=False` 下开启 Draft 并复用隔离错误 URLConf，以真实静态 live server 调用 Step 27 统一 accessibility Playwright scenario。 |
| `tests/test_public_metadata_sitemap_footer.py` | 验证三个正式公开页面的准确 Metadata/Open Graph、环境派生 URL、无硬编码 canonical host、sitemap XML 精确 allowlist、Draft 永久排除，以及 Footer 的获准 Instagram 与禁止内容边界。 |
| `tests/test_authentication_templates.py` | 验证项目认证模板覆盖、共享页面壳、Alpine/no-JavaScript 边界、ARIA error 关联、数字 code attributes 及 Password/code 不回显。 |
| `tests/test_static_assets.py` | 验证 static/template settings、vendor manifest 精确版本与 SHA-256、无第三方 CDN、design tokens、focus/reduced-motion 和关键颜色 contrast。 |
| `tests/test_authentication_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Node Playwright；显式按 UTF-8 捕获输出，失败时保留真实浏览器诊断。 |
| `tests/test_phase1_browser_flows.py` | 编排 Phase 1 Signup/verification、Password login/Account update、Magic Code 和 Admin USU review 浏览器流程，并从隔离的 Playwright storage state 读取服务端 Session code 以继续真实流程。 |
| `tests/test_phase1_acceptance.py` | 验证 Step 20 验收命令失败传播、运行中 Development server 清理，以及 README 对锁定安装、自动验收和人工 Phase 1 流程的覆盖。 |
| `tests/test_phase2_acceptance.py` | 验证 Step 28 全新环境验收的命令顺序、失败传播、Development server 清理，以及 README 对共享门禁、自动验收和人工 Phase 2 流程的覆盖。 |
| `tests/test_quality_security.py` | 验证敏感文件及高置信凭据扫描、测试外部网络阻断、认证与身份日志隐私、Anonymous 页面私有字段隔离和 HttpOnly Session cookie。 |
| `tests/test_quality_gate.py` | 验证统一门禁不会吞掉子命令失败，非零退出会作为验收失败传播。 |
| `tests/browser/browser-support.mjs` | 为 Playwright scenarios 提供必填环境变量读取、只允许当前 live-server origin 的 browser context，以及外部请求断言。 |
| `tests/browser/authentication-ui.mjs` | 在 Chromium 中执行小屏、键盘、Alpine、整串 code 输入、无 JavaScript fallback 和服务端错误焦点的端到端断言，并复用同源网络隔离。 |
| `tests/browser/phase1-core-flows.mjs` | 在 Chromium 中执行 Phase 1 注册验证、两种登录、账户更新、登出和 Admin USU review 操作，所有场景均使用同源网络限制。 |
| `tests/browser/development-server-smoke.mjs` | 对真实 Development server 执行 desktop/mobile Home、Signup、Login、Account redirect、CSS、布局、page error、同源请求和 Branding smoke checks。 |
| `tests/browser/phase2-development-smoke.mjs` | 对真实 Development server 执行 Phase 2 desktop/mobile 正式页面、Draft 分支、错误页、认证入口、CSS、布局、page error 和同源请求 smoke checks。 |
| `tests/browser/public-foundation.mjs` | 在 Chromium 中验证 Step 21 desktop/mobile Header、键盘 Focus、原生菜单开关、无 JavaScript 导航、布局和同源网络边界。 |
| `tests/browser/home-page.mjs` | 在 Chromium 中验证 Step 22 Home 的 desktop/mobile/no-JavaScript 内容、CTA、Logo 加载与比例、文字可见性、无水平溢出和同源网络边界。 |
| `tests/browser/public-information.mjs` | 在 Chromium 中验证 Step 23 About 与 Beginners & Safety 的 desktop/mobile、键盘、200% content zoom、无 JavaScript、CTA、内容可见性、无水平溢出和同源网络边界。 |
| `tests/browser/draft-risk-notice.mjs` | 在 Chromium 中验证 Step 24 Draft Risk Notice 的条件入口、banner、robots、desktop/mobile、键盘、无 JavaScript、内容可见性、无水平溢出和同源网络边界。 |
| `tests/browser/error-pages.mjs` | 在 Chromium 中验证 Step 25 三个错误状态的正确响应、desktop/mobile、项目 CSS、键盘 Focus、无 JavaScript、无水平溢出和同源网络边界。 |
| `tests/browser/phase2-accessibility.mjs` | 在 Chromium 中统一验证全部 Phase 2 公开与错误页面的语义、Heading、link name、Focus、键盘顺序、触控目标、reflow、200% 放大、对比度、reduced motion、替代文本、无 JavaScript、错误与同源网络边界。 |
| `memory-bank/design_document.md` | 产品与体验设计的权威来源，定义用户、页面、流程、权限、业务规则、隐私、Accessibility、内容和 Branding 边界。 |
| `memory-bank/tech_stack.md` | 技术决策的权威来源，定义框架、版本策略、单体架构、环境、安全、部署和运维边界。 |
| `memory-bank/implementation.md` | 代码实施顺序的权威来源，将当前 Phase 拆分为一次只执行一个的可验证步骤，并规定模型、配置、测试和 migration 要求。 |
| `memory-bank/项目开发_Roadmap.md` | 阶段、依赖、交付物、退出门槛、状态和外部阻塞事项的权威来源。 |
| `memory-bank/progress.md` | 记录实际完成的步骤、验证结果、仓库状态和遗留事项，供后续开发者继续执行。 |
| `memory-bank/architecture.md` | 记录已经实际实施并验证的架构、文件职责及重要技术理由；不把尚未实现的计划描述为现状。 |

## 五、架构维护原则

- 产品行为冲突时以 `design_document.md` 为准。
- 技术选型冲突时以 `tech_stack.md` 为准。
- 实施顺序与代码级要求以 `implementation.md` 为准。
- 阶段和外部依赖以 `项目开发_Roadmap.md` 为准。
- 本文档只记录真实存在且已经验证的结构；后续新增文件时补充其职责，避免提前描述尚未建立的组件。
- 当前 `memory-bank/implementation.md` 含有 Step 1 执行前已存在的未提交修改，后续工作不得覆盖或回退该修改。
