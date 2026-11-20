# NULDL 已实施架构

**最后更新：** 2026 年 11 月 21 日
**对应进度：** Visual Refresh, Step V17
**当前状态：** Phase 1–4 已完成，Phase 5 已取消，Visual Refresh 进行中（第一轮 V1–V3、V5–V7 完成，V4 已取消；第二轮 Events 的 V8–V10 完成；第三轮 About 与 Beginners & Safety 的 V11–V13 完成；第四轮 Members 的 V14–V17 完成），Phase 6 尚未开始

## 一、当前架构结论

仓库当前包含项目治理文档、基础 Git 配置、可重现的 Python 与前端依赖元数据、能够通过 Django system check 的项目骨架、由 Docker Compose 管理的本地 PostgreSQL 环境、Development、Test、Production 分环境 settings、具有受保护身份状态转换的 Custom User、完整的 MemberProfile 数据与公开查询边界，以及可重复构建的本地静态资源 pipeline。Python 运行时限定为 3.13.x，后端依赖由 `uv` 锁定，前端依赖由 npm 锁定。Django 已能加载五个项目 App，并从主机 `uv` 环境连接容器中的 PostgreSQL 18.6。

当前已实现 App 边界、启动配置、本地数据库连接、环境隔离、Custom User schema、USYD/USU ID 领域规则、MemberProfile 数据边界，以及 django-allauth 注册、Email verification by code、Username/Password 登录、可选 Email Magic Code 登录、link-based Password reset、POST logout、会员 Account 身份信息管理和 USU ID Admin 审核闭环。邮箱验证成功会通过官方 signal 调用幂等 service，只建立一个默认隐藏的 MemberProfile。`/account/` 提供本人账户与身份信息管理；`/admin/` 通过专用权限、只读审核字段和受控 actions 实现最小权限人工审核。项目已有全局语义化页面壳、统一 allauth 页面、本地 Alpine 渐进增强、Tailwind 第一版响应式视觉、版本及 hash 可验证的 vendor assets，以及 Production manifest static storage；核心认证流程在禁用 JavaScript 时仍可用。Phase 1 具有本地与 CI 共用的质量安全门禁，以及从临时全新 uv environment 执行锁定安装、PostgreSQL migration、完整门禁、Development server 和 desktop/mobile Playwright smoke 的端到端验收入口。README 已记录首次安装、日常开发、自动验收和人工流程；项目负责人已确认自动化与人工验收通过。Phase 2 已建立可覆盖的 metadata/Open Graph head 边界、完整 `NULDL Armwrestling Club` 品牌命名、键盘可用的响应式 Header、公开页面复用样式，以及正式 Home、About 与 Beginners & Safety。三个正式公开页面使用获准英文内容和认证状态分支 CTA；Home 已在 Step 40 从 Phase 2 静态日程过渡为最多三条 Upcoming Event 的动态预览，并继续使用由受保护源图确定性生成的响应式 WebP Logo。Draft Risk Notice 以显式环境开关隔离：Development 开启、获准 Preview 必须显式开启、Test 默认关闭、Production 强制关闭；关闭时直接 URL 返回 404 且导航与 CTA 不公开入口。项目已注册 403、404 和 500 handlers，三个错误状态使用共享页面壳、正确状态码和不泄露内部信息的中性恢复页面。Home、About 和 Beginners & Safety 已固定获准 metadata 与 Open Graph 值；Open Graph URL 由 request 派生，未硬编码尚未确认的 canonical host。`/sitemap.xml` 通过显式 allowlist 公开 Home、About、Beginners & Safety 和 Members 列表，始终排除个人 Member detail、Draft、Events、认证、Account、Admin 和错误页面。Footer 只公开已批准的 Instagram，不公开联系邮箱或未经授权的 University Branding。desktop、mobile、键盘、200% content zoom 和无 JavaScript 场景均已通过相应浏览器验证。HTMX 现用于报名区域的局部渐进增强；活动地点只使用 Google Maps 外链，项目不分发地图库。后续架构和技术选型仍以 `design_document.md`、`tech_stack.md` 与 `implementation.md` 为准。只有后续步骤实际完成并通过验证后，才在本文档记录对应结构及其理由。

Phase 2 现有统一 Playwright accessibility 门禁覆盖全部正式公开页、Draft 及真实错误页，并在 desktop、mobile、200% 内容放大、键盘、无 JavaScript 和 reduced-motion 场景检查语义、Focus、触控目标、重排、对比度、替代文本、错误及网络边界。

Phase 2 已建立跨阶段共享项目门禁和全新临时 uv environment 端到端验收入口。初次完整验收通过 234 个测试并达到 94% branch coverage；阶段人工走查后的公开页面文案、CTA 与布局修订又通过 24 个 Django 页面测试、4 个相关 Playwright 场景及静态与 Ruff 检查。项目负责人已确认最终人工验收，Phase 2 状态为 `Complete`。

Phase 3 已建立仅限本人使用的 Profile 编辑入口。有效会员通过 Account 进入 `/profile/edit/`，服务端只按当前 authenticated User 查询一对一 MemberProfile；邮箱未验证、停用、Anonymous、目标对象伪造和受保护字段伪造均不能越过边界。普通保存只更新七个会员可写资料字段，不改变发布或管理员状态。Step 29 已通过 46 个专项回归及 245 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的 Avatar 生命周期现已落地。编辑流程保留原文件字节，验证扩展名、MIME、真实格式和 5 MB 边界；替换、主动删除与保存失败通过集中 service 协调数据库和 storage，使旧文件只在新状态成功保存后删除，并回收失败写入。Development 在 `DEBUG=True` 时提供本地 media serving，Production URLConf 不注册开发 helper。Step 30 已通过 45 个专项回归及 256 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的本人 Preview 与发布状态转换现已落地。有效会员可以在未发布状态查看未来公开字段，通过独立 confirmation 和 CSRF POST 幂等 Publish 或 Unpublish；事务 service 使用 row lock 更新本人 Profile，固定 redirect 不接受外部目标。管理员隐藏状态不会被会员发布操作修改，并继续优先于 `is_published` 决定公开 queryset 结果。Step 31 已通过 41 个专项回归及 276 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的公开 Members 目录现已落地。`/members/` 只消费 `MemberProfile.objects.public()`，按 Display name 或 Username 回退后的公开名称执行不区分大小写且具有确定次序的排序；摘要卡片只输出 Avatar/fallback、公开名称及已填写的 Experience level 与 Preferred arm。Header 已向所有访问者公开 `Members` 导航，empty state 和无 JavaScript 路径可用。Step 32 已通过 70 个专项回归及 285 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的公开 Member detail 与搜索边界现已落地。`/members/<username>/` 对保存的 Username 执行精确匹配并只消费公开 queryset；所有不可见状态和不存在路径统一进入同一 404 正文。详情复用 Preview 字段组件，只输出获准公开字段，外部链接使用安全属性，个人页面保持普通公开 robots 规则。Members 列表进入 sitemap，个人详情继续不被枚举。Step 33 已通过 43 个专项回归及 290 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的 Admin Hide/Unhide 现已落地。MemberProfile 后台继续使用 Django 标准 `change_memberprofile` 权限和 `LogEntry`；change form 只允许维护隐藏状态与 Executive role，会员自述、User、发布状态和时间戳保持只读，新增与删除入口关闭。隐藏不会改写资料、发布偏好或账户状态，但会立即使 Profile 离开统一公开 queryset；会员仍可登录、编辑和 Unpublish。Step 34 已通过 9 个专项测试及 299 个完整测试，且没有 schema 或 migration 变更。

Phase 3 的统一响应式、Accessibility 与隐私门禁现已落地。单一 Playwright 场景覆盖 Profile Edit、Avatar、Preview、Publish/Unpublish、Members 列表与 detail、empty state 和隐藏提示，并在 desktop、mobile、200% content zoom、禁用 JavaScript 与 reduced-motion 环境验证语义、Focus、24px 触控目标、长内容重排、媒体加载、普通 POST、page error 和同源网络边界。公开响应另由 Django 安全测试扫描私有身份与未发布资料，并固定首期不收集年龄、出生日期、监护人或紧急联系人。门禁发现并修复长 Username 溢出、20px 触控目标及持久化 Avatar 重复校验读取关闭文件的问题。Step 35 已通过 20 个专项测试及 304 个完整测试，且没有 schema 或 migration 变更。

Phase 3 已建立跨阶段共享门禁之上的全新环境验收入口，并完成最终人工验收。验收从临时 uv environment 执行锁定安装、PostgreSQL migration、静态资源、Ruff、Django、完整 branch coverage、Production deploy check、collectstatic 及 Phase 2/3 Development smoke；最终通过 `313` 个测试并达到 `95%` branch coverage。人工收尾将 Members cards 调整为左侧紧凑 Avatar 与右侧摘要，将 Account 收敛为三个主卡片并在 Account details 内提供 Profile 摘要、状态和操作，同时保留保存、Preview 与发布确认的独立安全边界。Phase 3 状态为 `Complete`，没有新增 migration、年龄逻辑、目录筛选、专用隐藏权限、排行榜或 Production media provider。

Phase 4 已建立 Risk Notice 合成版本、Event 与 EventRegistration 事务基础、公开活动浏览、报名、取消、重新报名及最小权限 Admin 名单。`/events/` 只提供 Upcoming/Past，`/events/<slug>/` 只展示已发布 Event；日期分类固定使用 `Australia/Sydney` 的当地零点，不依赖当前进程时区。Home 从同一 queryset 展示最多三条 Upcoming Event，详情页可输出 Admin 提供的 HTTPS 地图链接。符合资格的会员可在开放活动中通过 Alpine dialog 阅读当前合成 Risk Notice，并以普通 POST 或 HTMX 渐进增强完成确认；无 JavaScript 时使用独立确认页。取消使用同一渐进增强结构，保留原报名历史；重新报名建立新记录并再次确认当前 Risk Notice。Django Admin 通过内置 `view_eventregistration` 权限只向获授权 Staff 和 Superuser 展示会员联系资料、USU ID、报名状态及 Risk Notice 历史，并禁止后台写入。

当前 Notice 的读取集中在 `apps.safety.services.current_risk_notice`：环境开关关闭或数据库没有 `is_current=True` 记录时返回空值，Home、Events 列表和详情页消费同一结果。报名提交携带 Notice 主键；事务服务锁定全部版本后确认该主键仍对应当前版本，从而使过期页面必须重新确认。模板直接呈现数据库中的完整正文，不额外添加固定 banner，也不依赖换行格式解析首行。Phase 4 的并发、跨会员隐私、desktop/mobile/200% reflow、键盘、触控目标、HTMX、无 JavaScript 和浏览器网络边界已由统一回归覆盖。最终全新环境通过 `378` 个测试并达到 `94%` branch coverage，项目负责人完成全部人工走查；Phase 4 状态为 `Complete`，Production 报名仍关闭。

## 二、已实施的依赖架构

### 2.1 Python 层

- 项目要求 Python 3.13.x；当前验证运行时为 Python 3.13.17。
- Django 固定在 5.2 LTS 系列，不允许锁文件自动升级到 Django 6.x。
- Django、django-allauth、Pillow 与 Psycopg 属于运行依赖。
- pytest、pytest-django、coverage 与 Ruff 属于开发依赖组，不进入业务代码的运行时职责。
- `pyproject.toml` 声明直接依赖及精确版本，`uv.lock` 固定完整传递依赖图。

### 2.2 前端工具层

- HTMX 和 Alpine.js 用于浏览器端交互。原 Phase 5 取消后，MapLibre GL JS 依赖与本地资产已在代码清理第 1 批移除；活动地点只输出 Google Maps 外链。
- Tailwind CSS、Tailwind CLI 与 Playwright 属于开发工具依赖。
- Tailwind CSS 与 Tailwind CLI 使用相同版本 4.3.0，避免构建器与框架补丁版本不一致。
- `package.json` 声明精确直接依赖，`package-lock.json` 固定完整 npm 依赖树和包完整性信息。

### 2.3 本地生成目录

- `.venv/` 由 `uv sync` 根据 `uv.lock` 创建，只用于本地 Python 环境，不提交仓库。
- `node_modules/` 由 `npm ci` 根据 `package-lock.json` 创建，只用于本地前端依赖，并由 `.gitignore` 排除。
- 两个目录都可由锁文件重新生成，不承担持久化项目数据职责。

### 2.4 本地数据库层

- Django 在 Windows 主机的 `uv` 环境运行，数据库在 Docker Linux container 中运行。
- Compose 使用 `postgres:18.6-alpine`，主机端口由 `POSTGRES_PORT` 映射到容器 `5432`。
- Compose 从 `POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD` 和 `POSTGRES_PORT` 建立本地数据库；Django 只通过 `DATABASE_URL` 连接，Test settings 另从 `POSTGRES_TEST_DB` 读取测试数据库名。`.env.example` 注明 `DATABASE_URL` 必须与这些值一致（代码清理第 6 批前此处误记为 Django 直接读取 `POSTGRES_*`，未使用的 `POSTGRES_HOST` 已删除）。
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
| `core` | Home、About、Beginners & Safety、Home Upcoming Events 预览、全局页面壳、通用组件和 403/404/500 error pages | 后续 Phase 的业务页面 |
| `accounts` | Custom User、标准与专用审核权限、Email/USU ID 规范化、USYD 声明、状态转换、受控审核服务、signup、Magic Code request 与 Account identity forms、完整认证流程、`/account/` 本人身份信息管理，以及 `/admin/` 最小权限 USU ID 审核 | 统一认证页面表现及其他业务 App 的后台管理 |
| `members` | MemberProfile schema、字段与 Avatar 验证、公开 queryset、幂等创建 service、Email 验证成功 signal receiver、本人资料编辑、Avatar 文件生命周期、本人 Preview、Publish/Unpublish、公开 Members 列表与详情、会员字段白名单、使用标准 change 权限的 Admin hide/unhide、Executive role 与 Researcher 编号维护，以及 Phase 3 响应式、Accessibility、隐私与全新环境验收 | — |
| `events` | Event 模型、地点文字与可选 Google Maps 外链、公开查询、Sydney 日期分类、Event Admin、EventRegistration、报名与取消事务服务、Upcoming/Past 列表、已发布活动详情、报名/取消前台，以及最小权限只读 Admin 报名名单 | — |
| `safety` | 环境隔离的静态 Draft Risk Notice 页面、测试版本管理、事务化激活及报名确认集成 | 正式 Risk Notice |

`accounts` 管理 Custom User 及身份规则，`members` 管理 Profile 数据，`safety` 管理 Risk Notice 测试版本，`events` 管理 Event、地点文字与报名。原 Phase 5 取消后，`locations` App 骨架已在代码清理第 1 批移除；它没有 migration，因此不涉及 schema 变更。

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
- `MemberProfileForm` 使用显式字段白名单，只包含未来会员可管理的资料字段；`is_hidden_by_admin`、`executive_role`、`researcher_number`（V14 加入，见 3.61）、`created_at` 和 `updated_at` 不进入会员输入面。
- `MemberProfileAdmin` 提供列表、筛选和搜索，并使用标准 `change_memberprofile` 权限管理现有 Profile。User、会员自述、发布状态与时间戳只读，只有 `is_hidden_by_admin`、`executive_role` 与（V14 起）`researcher_number` 可编辑；新增与删除入口关闭，修改由 Django Admin `LogEntry` 记录。
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
- `templates/includes/forms/`（代码清理第 3 批前位于 `templates/account/includes/`）集中输出 form-level error、field 和完整 fields。字段继续使用 Django `as_field_group` 生成稳定的 error ID、`aria-invalid` 与 `aria-describedby`；非字段错误使用可聚焦的 `role="alert"` summary。
- `core/base.html` 加载本地 CSS 与 deferred Alpine.js，并在初始化后聚焦第一个无效字段或 error summary。skip link、普通 link、原生 form、CSRF 和服务端 validation 均不依赖 JavaScript。
- Signup 与 Account 使用同一 Alpine state 处理 USYD 声明：选中时显示 USU ID，取消时清空输入；服务端返回 USU ID 错误时强制保持显示。未使用 `x-cloak`，因此 JavaScript 被禁用或加载失败时字段仍可见。
- `AccountIdentityForm` 与 `SignupForm` 只增加 Alpine attributes，没有改变服务端字段白名单或 `update_usu_identity` 边界。审核状态仍只能通过既有受控 service 和 Admin workflow 修改。
- Email verification 与 Magic Code confirmation 使用项目 form override 提供 numeric input mode、`one-time-code` autocomplete 和数字格式；自定义 widget 对绑定值返回空值，避免错误 code 被重新写入响应 HTML。
- Password 与 code 的浏览器属性只改善输入体验，认证有效期、尝试次数、重发、单次使用、enumeration prevention 和日志保护仍由 Step 9–13 的服务端配置与测试负责。

### 3.16 静态资源、构建产物与联合验收边界

- `static_src/css/site.css` 是 Tailwind CSS v4 的唯一项目样式源；`static/css/site.css` 是 minified 构建产物。设计 token、字体声明、component classes、focus、mobile 和 reduced-motion 规则均从 source 构建，生成文件不应手工维护。
- 浏览器资产从精确锁定的 npm dependency 复制到 `static/`，运行页面不访问第三方 CDN。复制脚本同时生成 `static/vendor/manifest.json`，记录 package、version、source 和 SHA-256，使版本与文件内容都可检查。
- Alpine.js 负责小型客户端状态；HTMX 负责活动报名与取消区域的局部请求和替换（见 3.39–3.40），并只在 Event detail 页面加载。项目不分发地图库。
- Development/Test 通过 `STATICFILES_DIRS` 读取项目静态目录；Production 使用 `ManifestStaticFilesStorage` 和独立 `STATIC_ROOT`，由 `collectstatic` 生成内容哈希文件名。`staticfiles/` 是部署输出并被 Git 排除。
- `package.json` 将 vendor copy、hash check、Tailwind build/watch 与 watch smoke 暴露为固定 scripts。字体和前端 library 均由 `package-lock.json` 锁定，license 文件随本地分发资产保存。
- Step 17–18 曾由 `scripts/verify_steps_17_18.py` 作为原子验收入口；其职责已由共享门禁 `scripts/verify_project.py`（见 3.26）完整覆盖，该脚本已在代码清理第 1 批删除。
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

### 3.20 Home、响应式 Logo 与活动预览

- Home 继续由 `apps.core` 的既有根路径 view 服务，不新增 Model、migration 或业务 API。模板使用 `design_document.md` 已确认的英文 Hero、新手说明、训练内容、参与资格、Metadata 和 Open Graph 文案。
- Hero 与 Upcoming Session 的主要操作按认证状态在服务端分支：Anonymous 使用 `Join the Club` 进入 Signup，authenticated member 使用 `Account` 进入本人账户页；`New to Armwrestling?` 是普通页内锚点，全部操作在禁用 JavaScript 时仍可用。
- Phase 2 建立的静态 Upcoming Session 已在 Step 40 被动态活动预览取代。Home view 现查询最多三条已发布 Upcoming Event，模板复用 Events card，并提供详情和列表入口；无数据时使用明确 empty state。
- 当前 Home Logo 源图为透明背景的 `nuldl-club-logo-transparent.png`，以原始字节保存在 `static_src/images/brand/`：1254 × 1254 RGBA、1,580,788 bytes，SHA-256 为 `65114bdc25ca376408b3c715a02b100fa979ca1eba182c9f5baf87911eaa89d1`。它在 Phase 4 期间由项目负责人替换了原先获准的 `Logo_without_USYD.png`（1,776,890 bytes，SHA-256 `1bc738b3…8944`）。旧文件已无引用，经项目负责人确认后于代码清理收尾时删除，可从 Git 历史恢复。源文件不直接作为页面下载资产，且图形内容未被重新设计。
- `scripts/build_home_images.py` 使用锁定版 Pillow 从受 hash、格式、尺寸和透明通道保护的源图确定性生成 480、800、1200px 方形透明 WebP（quality 75、alpha_quality 70、method 6）。生成物分别为 70,114、156,624、279,676 bytes：透明通道是体积的主要来源，同一源图合成到页面底色后约为 33/67/112 KB；项目负责人在代码清理第 6 批选择保留透明度；`package.json` 将生成与漂移检查接入现有 `static:build` 和 `static:check`。
- Home `<picture>` 通过 width descriptor 与 `sizes` 选择响应式 Logo，`img` 保留明确宽高、方形 aspect ratio、非空替代文本和 `object-fit: contain`。Header 继续只使用文字品牌，没有缩放完整 Logo，也没有加入 University Branding。
- Phase 2 建立时的 Home 内容、Metadata、CTA、Logo 完整性与响应式图片构建仍由原测试保护；Step 40 另以 Event 页面和 Home 回归固定动态 Upcoming 预览、最多三条、详情/列表链接及 empty state。Playwright 继续验证 desktop、mobile 和禁用 JavaScript 时的 Logo、布局、Events 导航与同源网络边界。

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
- 阶段验收测试（代码清理第 4 批起合并为 `tests/test_acceptance.py`）锁定命令顺序、失败传播、运行中 server 清理及 README 验收入口；`tests/test_quality_gate.py` 直接验证共享门禁，防止兼容 wrapper 掩盖真实入口。
- 初次全新环境验收通过 234 个测试、94% branch coverage、Production 检查与 browser smoke。人工走查后的 Home、About 和 Beginners & Safety 内容与 CTA 收尾通过专项 Django/Playwright、静态与 Ruff 验证，项目负责人确认最终验收。
- 本节记录 Step 28 完成时的 Phase 2 验收边界；Phase 3 后续已按 3.27–3.34 实施并完成。Risk Notice 最终文本、University Branding、地点、Production Provider、数据保留和中文版本仍由后续批准或阶段处理。

### 3.27 本人 Profile 编辑与所有权边界

- `apps.members.urls` 提供命名路由 `members:profile_edit`，当前路径为 `/profile/edit/`；根 URLConf 只接入该 App URLConf，不建立尚未实施的公开 Members 路由。
- 编辑 view 先使用 Django 登录保护，再要求当前 User 启用且至少具有一条 verified EmailAddress；不满足资格的请求不能进入表单处理。
- Profile 查询固定使用 `request.user` 的一对一关系，不读取客户端提供的 User 或 Profile ID。有效会员缺少 Profile 时返回 404，不隐式建立可能掩盖数据异常的新记录。
- `MemberProfileForm` 使用七个字段的显式白名单并移除 `is_published`。Display name 冲突在表单层按不区分大小写检查并关联字段错误，数据库唯一约束继续防止并发或直接写入绕过。
- Instagram Username 在表单清理阶段去除一个开头 `@`，使 ModelForm 在执行 model field validator 前得到规范值；HTTPS social URL、Bio 纯文本及 Avatar 基础验证继续复用既有 model 边界。
- 成功 POST 保存同一 Profile、发送 Django message 并 redirect 回编辑页。伪造 `user`、`is_published`、`is_hidden_by_admin`、`executive_role` 或时间戳不会进入 cleaned data，原状态保持不变。
- 页面复用全局壳和认证表单 include，使用 CSRF、multipart 和普通 POST；JavaScript 不参与对象选择、权限或服务端验证。
- Step 29 本身没有实现 Avatar 文件替换/删除清理、Preview、Publish/Unpublish、公开目录、公开详情或 Admin hide/unhide；Avatar 职责随后由 Step 30 完成，其余职责继续由 Step 31–34 分别实施。

### 3.28 Avatar 原文件与 Storage 生命周期

- `MemberProfileForm` 使用普通 File input，并增加非 Model 字段 `remove_avatar`；同一提交同时上传和删除会形成字段错误，发布及管理员字段继续不进入会员输入面。
- Avatar validator 在既有 5 MB、允许格式、声明 MIME 与 Pillow 解码基础上，要求文件扩展名与真实格式对应。已保存 `FieldFile` 在每次校验前重新打开并在校验后关闭，既支持 ModelForm 与 model save 的重复校验，也避免 Windows 文件锁；尚未保存的上传对象保持打开。
- `save_member_profile_form` 在提交前从数据库读取旧 Avatar 名称。有效提交在数据库事务内保存 Profile；成功后才删除不同的旧文件，主动删除使用同一路径。
- 如果数据库保存在新文件写入后失败，service 根据 `FieldFile._committed` 识别并删除失败的新文件，旧数据库值及旧文件保持不变。表单验证失败不会调用 storage 写入。
- 原始上传字节直接进入 storage，不执行 EXIF 转向、metadata 清理、缩放或格式转换。页面只通过方形容器和 CSS `object-fit: cover` 控制呈现，并在上传字段旁显示 metadata 风险提示。
- Development 的 `MEDIA_URL` 为 `/media/`；根 URLConf 只在 `DEBUG=True` 时附加 Django local media patterns。Production 与 Test 默认 `DEBUG=False`，不会注册开发文件服务。
- 仓库忽略根 `media/`。Django 测试使用 pytest 临时目录；浏览器测试使用独立临时目录及测试专用 URLConf，不将 Development helper 扩展到 Production。

### 3.29 本人 Preview 与发布状态转换

- `apps.members.urls` 在既有编辑入口之外提供 `profile_preview`、`profile_publish` 和 `profile_unpublish` 三个命名路由；当前仍未建立公开 Members 列表或 detail 路由。
- 三个 view 复用同一所有权与资格边界：必须登录、账户启用、至少具有一条 verified EmailAddress，并且只通过 `request.user` 查询本人 Profile。
- Preview 使用共享公开字段 include 呈现未来 detail 的字段顺序。`Not specified` 值不输出，Bio 继续由 Django escaping 保护，外部社交链接使用新窗口安全属性；Email、USYD、USU ID、审核状态和 Executive role 不进入页面 context 输出。
- Publish 与 Unpublish 各有独立 confirmation。GET 不修改状态，POST 依赖 Django CSRF middleware；成功后固定 redirect 到本人 Preview，不读取客户端 `next`。
- `set_profile_publication` 在数据库事务中通过 `select_for_update()` 锁定当前会员 Profile，只在目标状态不同的时候保存，重复 POST 保持幂等。
- 发布操作只修改 `is_published`。`is_hidden_by_admin` 不进入会员写入路径，隐藏资料即使已发布也继续被 `MemberProfile.objects.public()` 排除。
- 隐藏状态在本人页面使用中性提示表达，不公开管理员身份、后台操作或隐藏原因；会员仍可编辑、Preview 和 Unpublish。
- Publish confirmation 显式告知 Username detail path、Display name 回退规则、全部公开字段及 Avatar metadata 风险；该 path 在 Step 31 只作为说明文字，并在 Step 33 开放公开 detail 路由。

### 3.30 Members 公开目录与摘要字段边界

- `members:list` 在 `/members/` 提供不要求认证的公开目录；view 只从 `MemberProfile.objects.public()` 构造 queryset，因此未发布、管理员隐藏、停用和邮箱未验证 Profile 不会进入 template。
- Queryset 使用 `select_related("user")` 避免逐卡读取 Username，并以 `Lower(Coalesce(display_name, user.username))` 形成公开名称排序键；Lower Username、原始 Username 和主键提供稳定的同名次序。
- 目录 template 不复用包含 Bio 和社交链接的 detail/Preview 组件，而是维护更窄的卡片字段白名单：Avatar 或非敏感首字母 fallback、Display name 或 Username，以及非 `Not specified` 的 Experience level 与 Preferred arm。
- Header 对登录与未登录访问者都输出普通 `Members` 链接，并依据 `members:list` view name 设置当前页状态；移动 disclosure 和禁用 JavaScript 的导航路径保持既有行为。
- 目录使用响应式 CSS Grid、方形 Avatar/fallback、长名称换行和明确 empty state。Step 32 建立时卡片没有详情链接；Step 33 后公开名称链接至 `/members/<username>/`。目录仍没有搜索、HTMX 或分页。
- Django 测试扫描响应中的账户、USYD/USU、Admin、Bio 和社交字段；Playwright 另覆盖 desktop、mobile、键盘、无 JavaScript、横向溢出、page error 和同源网络限制。

### 3.31 Member detail、统一 404 与搜索边界

- `members:detail` 在 `/members/<username>/` 提供公开 GET 页面；view 只从 `MemberProfile.objects.public().select_related("user")` 查询，并按保存的 Username 精确匹配。
- 未发布、管理员隐藏、停用、邮箱未验证、大小写不匹配和不存在的 Username 都无法离开公开 queryset，并统一进入项目 404 handler；可见错误正文不披露资料是否存在或不可见原因。
- Detail 与本人 Preview 复用 `profile_public_fields.html` 的字段顺序。Detail 将公开名称呈现为唯一 H1；Preview 继续以 H2 嵌入本人流程页面，不产生重复 H1（V16 起分节标题相应为 H2 / H3，见 3.63）。
- 详情字段白名单为公开名称、Username、Avatar/fallback、非默认 Experience level、非默认 Preferred arm、Bio、Instagram Username 和一个 HTTPS social URL。账户身份、USU 审核、Admin、Executive role 与时间戳不输出。
- Django 默认 escaping 继续保护公开文本；Bio 使用 `linebreaksbr` 保留纯文本换行。外部链接使用新窗口及 `noopener noreferrer`，其他社交链接继续受 HTTPS model 与数据库约束保护。
- Detail 使用全局默认 `index, follow`，不增加特殊 robots directive。显式 sitemap allowlist 只增加 `members:list`，不枚举任何 `members:detail` URL。
- Members card 以公开名称链接详情；Header 在列表与详情页都将 Members 标记为当前项。Playwright 覆盖卡片导航、直接 URL、desktop/mobile、无 JavaScript、robots、布局和同源网络边界。

### 3.32 MemberProfile Admin Hide/Unhide 与字段所有权

- MemberProfile Admin 依赖 Django 自动生成的标准 `members.change_memberprofile` 权限；普通会员和无该权限的 Staff 不能访问，拥有该权限的启用 Staff 与 Superuser 可以维护现有 Profile。
- change form 将 User、Display name、Avatar、Bio、Experience level、Preferred arm、Instagram Username、其他社交链接、`is_published`、创建时间和更新时间设为只读；仅 `is_hidden_by_admin` 与 `executive_role` 可编辑（V14 起另含 `researcher_number`，见 3.61）。
- Admin 不提供 MemberProfile 新增或删除入口，也不定义专用 permission 或自定义 action。Hide/Unhide 与 Executive role 修改沿用 Django change form，并由标准 `LogEntry` 留下修改记录。
- 隐藏操作只改变 `is_hidden_by_admin`。会员自述、Profile 所属 User、`is_published` 和账户启用状态保持原值；公开列表和 detail 继续通过同一 `MemberProfile.objects.public()` 边界排除隐藏资料。
- 被隐藏会员仍可登录、编辑本人 Profile、查看中性隐藏提示并执行 Unpublish。会员 Publish 或编辑流程不能清除管理员隐藏状态。
- 本边界没有增加原因字段、历史表、migration 或前台 Executive role 展示；统一 Phase 3 browser/accessibility 门禁已由 Step 35 完成。

### 3.33 Phase 3 统一响应式、Accessibility 与隐私门禁

- `phase3-accessibility.mjs` 以一个完整场景统一遍历本人 Profile Edit、Preview、Publish/Unpublish、公开 Members 列表与 detail；独立 empty 场景验证没有公开资料时的 desktop、mobile 和禁用 JavaScript 表现。
- Django wrapper 只建立合成已验证账户和临时 Avatar，并通过 authenticated Session 驱动真实浏览器。测试结束时清理临时 media 目录，Production 与 Development media 边界不因此改变。
- Desktop、mobile 与 200% content zoom 场景验证 landmarks、唯一 H1、可见 Label、表单错误关联、键盘 Focus、至少 24px 的交互目标、图片 alt/解码、长 Username、长 Bio、公开链接安全属性和无横向溢出。
- JavaScript disabled 场景实际保存 Profile、Unpublish 和 Publish，证明核心流程依赖普通 HTTP POST、CSRF 和服务端状态转换；管理员隐藏提示在整个流程中保持中性且可见。
- Reduced-motion 检查解析浏览器返回的全部 transition duration，并要求每项不超过项目 CSS 定义的 0.01ms；任何 page error 或非 live-server origin 请求都会使场景失败。
- `test_quality_security.py` 对 Members 列表与 detail 扫描 Email、USYD/USU ID、审核状态、Executive role、未发布资料和私有 sentinel；另固定 User、MemberProfile 与会员表单没有年龄、出生日期、监护人或紧急联系人字段。
- 门禁推动的生产修补限定为长动态标识断行、Profile checkbox/radio 和社交链接 24px 触控目标，以及已提交 Avatar 重复校验前重新打开文件；没有改变公开字段、权限、发布规则、schema 或 migration。

### 3.34 Phase 3 全新环境验收与人工收尾

- `scripts/accept_phase_3.py` 复用共享 `verify_project.py`，在 OS 临时目录创建独立 uv environment，等待 Docker PostgreSQL、执行 Development migration 和完整门禁，再启动可可靠清理的真实 Development server。
- Development server 依次运行 Phase 2 与 Phase 3 desktop/mobile smoke；Phase 3 smoke 固定 Members、Anonymous Profile redirect、统一不可见 404、Development media 和同源网络边界。验收脚本与测试传播所有非零结果，并在异常时输出 server log。
- Account view 查询当前 User 的 MemberProfile，只向本人页面 context 提供 Profile 摘要；模板保持 Account、USYD/USU 与 Security 三个主卡片，并在 Account details 内展示公开说明、字段摘要、状态及 Edit、Preview、Publish/Unpublish 操作。
- Profile 编辑保存继续只写会员字段且不改变发布状态，成功后返回 Account；Preview 继续复用公开字段组件并增加返回 Account 的普通链接。统一 Publish/Unpublish service、CSRF POST、幂等状态转换和管理员隐藏优先级没有改变。
- Members cards 使用响应式两列结构：Avatar/fallback 保持左侧固定紧凑尺寸，右侧显示允许的摘要字段；原始上传文件仍按既有规则保存，显示尺寸不改变 storage 或 Production media 决策。
- 人工走查补充了连续无空格 Bio、Profile 定义列表间距、Account 按钮层级与 Avatar cache/storage 核查。最终临时环境通过 `313` 个测试、`95%` branch coverage、Production deploy check、collectstatic 及两组 Development smoke，项目负责人确认全部视觉和交互符合预期。

### 3.35 Risk Notice 测试版本管理

- `RiskNoticeVersion` 保存唯一版本标识、正文、当前状态、创建时间和最近激活时间。PostgreSQL 条件唯一约束允许尚无当前版本，并保证最多一个当前版本。
- `activate_risk_notice` 先检查环境开关，再在事务中按主键顺序锁定现有版本并切换状态。重复激活当前版本不更新时间。旧版本继续保留，供后续报名记录引用。
- Admin 采用 Django 模型权限。创建表单要求正文首行标明 `SYNTHETIC TEST ONLY`。现有正文和版本标识只读，删除入口关闭。拥有修改权限的管理员可通过单选操作激活版本，切换写入 Django Admin 日志。
- Admin 和激活服务受 `RISK_NOTICE_DRAFT_VISIBLE` 约束。Development 已开启，Preview 要求显式开启，Test 默认关闭，Production 强制关闭。公开 `/risk-notice/` 继续渲染静态 Draft 模板。

### 3.36 Event 模型与 Admin

- Event 保存标题、唯一 slug、说明、起止时间、地点文字、可选地图 URL、公开与报名开关及时间戳。公开和报名开关默认关闭；`objects.public()` 只筛选已公开活动。
- 模型验证结束时间晚于开始时间及地图 URL 的 HTTPS 格式，PostgreSQL 约束同时保护时间顺序与 HTTPS 前缀。日期判断通过 Django 当前时区将结束时间转换为本地日期，与指定日期或当前本地日期比较；项目默认时区为 `Australia/Sydney`。
- EventAdmin 使用 Django 标准模型权限，支持活动编辑、列表筛选、搜索及 slug 预填。地图链接表单在未输入 scheme 时使用 HTTPS。
- Step 38 专项与 Risk Notice 回归通过 17 项，完整测试 330 项通过。EventRegistration 和活动前台页面留待后续步骤。

### 3.37 EventRegistration 与报名事务基础

- `EventRegistration` 关联 Event、User 与 RiskNoticeVersion，并记录 `registered`/`cancelled` 状态、报名时间、确认时间与取消时间。数据库条件唯一约束限制每个会员和活动最多一条有效报名；检查约束要求状态与取消时间一致。
- Event 和 Risk Notice 外键使用 `PROTECT`，User 外键使用 `CASCADE`。已取消记录在正常状态转换后保留，可供重新报名时与新记录并存；完整账户删除和数据保留规则仍待确认。
- `register_for_event` 在事务内锁定 Event、User 和按主键排序的现有 Risk Notice 版本，核对有效会员、活动公开与开放状态、当地日期、明确确认和当前版本。重复有效报名返回既有记录；过期版本和非合成正文被拒绝。
- 服务使用 `RISK_NOTICE_DRAFT_VISIBLE` 及正文首行 `SYNTHETIC TEST ONLY` 限定当前开发范围；Production 配置强制关闭该开关。取消服务、公开活动页面、报名表单和 Admin 名单仍属于后续步骤。
- Step 39 专项测试 `27 passed`，完整测试 `340 passed`；migration、Django check、Ruff lint 与 format check 均通过。

### 3.38 公开 Events 与 Home 数据流

- `EventQuerySet.upcoming()` 与 `past()` 明确使用 `ZoneInfo("Australia/Sydney")` 计算当地当日零点。`ends_at` 在该零点及之后属于 Upcoming，在该零点之前属于 Past；`Event.is_past` 与 `is_upcoming` 复用同一 Sydney 日历日语义。
- `events:list` 仅接受 `upcoming` 与 `past` 两种公开筛选；无效参数安全回退到 Upcoming。Upcoming 按开始时间升序，Past 按结束时间倒序，两者都先经过 `objects.public()` 限制。
- `events:detail` 按唯一 slug 查询已发布 Event，不暴露未发布对象。详情模板以 Sydney 时区显示起止时间，对可选地图 URL 使用 `target="_blank"` 和 `rel="noopener noreferrer"`。
- Home view 使用同一 `public().upcoming()` queryset 并限制三条，不复制活动日期规则。Home 与 Events 列表共用 `event_card.html`，保持字段、状态文字和链接行为一致。
- 公开层只提供 GET 浏览。Upcoming 显示报名不可用，Past 显示历史状态；现有 `register_for_event` 事务服务没有连接到任何公开 view 或 form，Production Draft/Risk Notice 开关继续强制关闭。
- `.event-card` 将共享 content card 恢复为自然高度，避免 Home 链接被拉伸卡片遮挡；`.event-list` 和 `.event-detail-actions` 只负责 Events 列表与详情操作的局部间距，不改变其他 card grid。（V6 起 `.event-card` 成为独立的网格卡片，不再基于 content card，见 3.53。）
- Django 测试固定可见性、Sydney 零点分类、排序、回退、安全外链和无表单边界；Playwright 在 desktop、mobile 和禁用 JavaScript 场景检查 Home 至 Events 的导航、筛选、详情、无水平溢出、page error 与同源网络边界。

### 3.39 会员报名与 Risk Notice 确认流

- `events:register` 只接受已发布 Event，并要求当前账户启用且至少一条 EmailAddress 已验证。可报名状态同时要求 `registration_open=True`、Event 尚未进入 Past、Development/Test Draft 开关开启，以及存在首行标记 `SYNTHETIC TEST ONLY` 的当前 RiskNoticeVersion。
- Event detail 使用 Alpine 原生 `<dialog>` 显示当前 Notice；确认按钮携带当前版本 ID 和明确同意值。HTMX 只替换 `#event-registration`，普通 POST 与禁用 JavaScript 路径通过独立确认页和 redirect 完成相同流程。
- `register_for_event` 保持唯一写入入口。视图不复制身份资料，只创建指向 User、Event 和 RiskNoticeVersion 的确认记录；姓名、Email 与 USU ID 可在后续名单中从关联 User 读取。
- 旧版本提交由服务层拒绝，视图重新装载当前版本并要求再次确认。报名成功显示 `Registered`；本步不提供取消操作，Step 42 才能改变该状态。
- 开放性由界面隐藏和服务端拒绝共同保护，避免旧页面、直接 POST 或并发状态变化绕过限制。Production settings 继续强制关闭 Draft/Risk Notice 能力。
- Django 测试覆盖普通 POST、HTMX、幂等重复提交、旧版本、资格及关闭状态；Playwright 覆盖 dialog、Risk Notice 正文、HTMX 更新、无 JavaScript 回退、布局、page error 与同源网络边界。

### 3.40 取消报名、历史保留与重新报名

- `cancel_event_registration` 在事务中锁定 Event、User 与其报名记录，重新验证启用账户、verified Email、公开活动、报名开关、Upcoming 状态及非 Production 环境。服务只把当前有效记录改为 `cancelled` 并写入 `cancelled_at`，不会删除原 Risk Notice 确认。
- 同一取消请求重复提交时返回最近的已取消记录，不建立额外数据或改写历史。活动关闭、进入 Past 或 Draft 开关关闭后，取消入口消失，服务端直接请求也被拒绝。
- `events:cancel` 提供普通 GET/POST 回退和 HTMX 局部响应。JavaScript 可用时由 Alpine 原生 dialog 要求确认；禁用 JavaScript 时使用独立确认页，两个路径调用同一事务服务。
- 取消后不再存在有效报名，详情页恢复 `Register`。重新报名继续经过 Step 41 的当前版本校验，建立新的 EventRegistration；旧记录保持 `cancelled` 并继续引用当时接受的 RiskNoticeVersion。
- 页面仍只显示当前有效状态，不公开历史记录或账户联系资料。历史名单与最小权限访问继续属于 Step 43。
- Django 与 Playwright 测试覆盖取消状态与时间、幂等提交、关闭/Past/Production 拒绝、普通 POST、HTMX、无 JavaScript，以及切换 Risk Notice 后重新报名并保留两条历史记录。

### 3.41 Admin 报名名单与最小权限

- `EventRegistrationAdmin` 使用 Django 自动生成的 `events.view_eventregistration` 权限提供只读名单；Event 的编辑权限不会隐式授予报名名单访问权，普通会员和无对应权限的 Staff 均被拒绝。
- 名单通过关联 User 即时显示姓名或 Username 回退、Username、Email 和可选 USU ID，不在报名记录中重复保存身份资料。联系方式以现有 Email 为准；系统当前不收集手机号。
- 列表及详情同时展示有效、取消和重新报名记录，以及每条记录对应的 Risk Notice 版本、报名时间、确认时间和取消时间，从而保留版本追溯关系。
- Admin 关闭新增、修改、删除及 actions；获授权 Staff 与 Superuser 均只能查看，伪造 change POST 不能改写报名状态或历史。
- 前台 Event 页面继续只显示当前会员本人的有效状态，不输出名单、联系资料、USU ID 或历史版本。Step 43 没有 Model、migration、service、前台模板或状态转换变更。

### 3.42 Phase 4 并发、隐私与浏览器门禁

- 报名事务测试在既有并发报名与 Risk Notice 切换覆盖之外，增加并发取消场景；同一 Event 与 User 的两个取消请求经现有行锁串行处理并返回同一历史记录，不产生重复取消行或非法状态。
- 前台隐私回归同时以 Anonymous 与另一名 verified member 请求 Home、Events 列表和详情，固定报名人的姓名、Username、Email、USU ID、取消历史与旧 Risk Notice 版本均不公开；其他会员的取消请求不能改变原报名。
- Events 浏览器场景覆盖 desktop、mobile、200% content zoom 与禁用 JavaScript，检查 landmarks、唯一 H1、键盘 Focus、至少 24px 的触控目标、文本重排、地图链接、筛选、横向溢出、page error 和同源网络限制。
- 报名浏览器场景覆盖 HTMX dialogs、报名、取消、重新报名、mobile dialog、200% content zoom 及无 JavaScript 完整确认页和普通 POST；这些测试复用真实 Django live server 与两个合成 verified member Session。
- Step 44 没有修改生产 template、CSS、Model、service、URL、settings 或 migration；现有实现直接通过新增门禁。

### 3.43 代码清理第 1 批

- 依据 `memory-bank/cleanup_audit.md` 的第 1 批清单，只做删除与明确纠错，不改变业务规则、权限、隐私边界、schema 或 migration。
- 删除 `apps.locations` App 骨架及其 `PROJECT_APPS` 注册；项目 App 现为 `core`、`accounts`、`members`、`events` 与 `safety`。该 App 从未建立 migration，因此不需要数据库变更。
- 移除 `maplibre-gl` npm 依赖，以及 vendor 复制清单、`static/vendor/maplibre/` 资产、对应 license 和 manifest 条目。前端运行时现在只分发 Alpine.js、HTMX 与本地字体。
- 删除已由 `scripts/verify_project.py` 取代的 `scripts/verify_steps_17_18.py`，以及 `scripts/accept_phase_1.py` 中未使用的 npm 常量；USU 审核 Admin action 直接调用 `review_usu_id`，不再经过无意义的别名。
- CSS 将 Members 名称链接中不存在的 `--color-text` 改为既有的 `--color-cream` token，并删除 Step 40 后已无引用的 `.session-details` 与 `.session-note` 规则；会员模板移除了 3 个没有对应样式的 class，页面布局不变。
- 审计初稿将 Home Logo WebP 增大归因于 `exact=True`；实测构建参数只影响约 5%，因此本批未修改 `scripts/build_home_images.py`，Logo 体积另行决策。
- 已通过 Ruff lint/format、Django system check 和 `npm run static:check`；在本地 Docker PostgreSQL 上以全新 test database 运行完整 pytest，`380 passed`，其中包含全部 Django 调用的 Playwright 浏览器场景。

### 3.44 代码清理第 2 批

- 依据 `memory-bank/cleanup_audit.md` 第 2 批清单，只合并重复的 Python 规则实现，不删除任何文档要求的防线：model 状态机、service 行锁与锁内复核、Event → User → RiskNoticeVersion 加锁顺序以及全部数据库约束均保持不变，也没有新增 migration。
- `apps/accounts/forms.py` 新增 `UsuIdentityFields` 基类，供 Account 身份表单与 allauth Signup 表单共用 USYD/USU 字段、Alpine widget attributes 与校验；“USU ID is only available to USYD students.” 改由 `apps/accounts/models.py` 的 `USU_ID_REQUIRES_USYD_MESSAGE` 常量统一提供。数字校验保持在 form 与 model 各自执行，以免同一字段出现重复错误。
- 新增 `apps/accounts/selectors.py::is_verified_active_member()`，统一“账户启用且存在 verified Email”判断，Members 本人流程、Events views 和 Events services 共用；Account 页面判断的是当前 Email 是否已验证，语义不同，保留原实现。
- 新增 `apps/core/validators.py`，集中提供 `validate_https_url` 与 `normalize_https_scheme`；Members 与 Events models 改为导入共享实现，既有 migration 引用的模块路径依旧可解析。非 HTTPS 链接现在先得到 “Use an HTTPS URL.”，这是本批唯一的用户可见文案变化。
- Event 新增 `accepts_registration(notice_available=...)`、`accepts_cancellation()` 与模块级 `sydney_midnight_today()`；`clean_fields()` 先规范化再执行字段校验，删除与字段 `blank=False` 重复的空值检查。`event_card.html` 无法向方法传参，保留模板条件，结果与新方法一致。
- `apps/events/views.py` 收敛 HTMX 判断、面板模板名和“HTMX 片段 / 整页 400”分支，并在一次请求内复用会员资格、当前 Notice 与有效报名查询；报名面板去掉冗余的 `registration_available` 条件。
- MemberProfile 新增 `public_experience_level` 与 `public_preferred_arm`，未指定时返回 `None`，公开模板不再硬编码 `not_spec`；`__str__` 复用 `resolved_display_name`，Publish 确认页的公开路径改用 `reverse()`。
- 已通过 Ruff lint/format、Django system check 与 `makemigrations --check`；在本地 Docker PostgreSQL 上以全新 test database 运行完整 pytest，`380 passed`，未修改任何测试。

### 3.45 代码清理第 3 批

- 依据 `memory-bank/cleanup_audit.md` 第 3 批清单合并重复的模板片段，验收标准是渲染输出不变。批次中用临时脚本在改动前后渲染 39 个页面状态，比较空白规范化后的 HTML：除下述 Avatar fallback 外完全一致。本批未修改 view、URL、Model、CSS、JavaScript 或 migration。
- Header 的当前页判断改由 `apps.core.context_processors.navigation_section` 提供：按 resolved `view_name` 映射到导航 section，Events 按 namespace 映射；`header.html` 只比较 `nav_section`。无法解析的请求（例如 404）不标记任何项。
- 通用表单片段由 `templates/account/includes/` 迁至 `templates/includes/forms/`，表明它们同时服务于 allauth、Account 与 Profile 编辑，而不只属于 allauth 覆盖目录。
- 新增共享片段：`accounts/includes/usyd_fields.html`（USYD 声明与条件 USU ID，Alpine state 仍由外层 form 声明，以保持 DOM 与间距不变）、`members/includes/profile_publication_action.html`（Publish/Unpublish 分支）、`members/includes/public_avatar.html`（Members 卡片与公开 detail/Preview 的 Avatar 或首字母 fallback）、`events/includes/confirm_page.html`（无 JavaScript 报名/取消确认页正文），以及 `core/errors/_error_page.html`（三个错误页的基模板）。原页面模板名全部保留。
- 公开 detail 与 Preview 的 Avatar fallback 改为与 Members 列表一致的 `aria-hidden="true"`；原无 role `div` 上的 `aria-label` 不会被辅助技术读出，公开名称始终在相邻标题中呈现。这是本批唯一的输出变化。
- Sydney 时区包裹移入 `event_card.html`，卡片可独立复用；Home 与 Events 列表不再包裹 `{% timezone %}`，详情页保持自身包裹。
- Header JavaScript 断点与 CSS 断点的单一来源（T2）、`<body>` 错误聚焦脚本外置（T15）推迟到 CSS 断点统一时一并决策。
- 已通过 Ruff lint/format、Django system check、`makemigrations --check` 与 `npm run static:check`；在本地 Docker PostgreSQL 上以全新 test database 运行完整 pytest（含浏览器场景），`380 passed`，未修改任何测试。

### 3.46 代码清理第 4 批

- 依据 `memory-bank/cleanup_audit.md` 第 4 批清单，只修改 `tests/` 与 `scripts/`，生产代码、模板、CSS、settings 与 migration 均未变动。
- 测试数据由 `tests/factories.py` 统一建立：`create_user` 以 `verified=None/True/False` 表示不建 EmailAddress、已验证或未验证，`create_member` 同时建立 MemberProfile；`tests/conftest.py` 提供共享 `verified_member` fixture。各测试文件只保留声明自身默认值的薄包装，所有数据仍为合成值。
- Python browser wrapper 统一通过 `tests/browser_runner.py::run_node_scenario` 启动 Node 场景，保持 UTF-8 输出解码和失败时输出完整日志。`tests/browser/browser-support.mjs` 集中提供会话 cookie、横向溢出、页面边界、landmark 结构、可见内容、触控目标与 Focus 断言；各场景以参数声明自身检查的元素范围。
- 四个 `scripts/accept_phase_N.py` 改为只声明门禁脚本与 smoke 列表的入口，共同调用 `scripts/_acceptance.py::run_acceptance`。共享流程保持临时 uv environment、PostgreSQL、migration、门禁、真实 Development server、smoke、server log 输出和可靠清理的顺序；直接执行脚本时通过导入回退定位共享模块，README 命令不变。`tests/test_acceptance.py` 取代四个阶段专属验收测试。
- 测试断言改为针对需求，不再依赖实现细节：
  - 不再读取模板源码，也不再断言 class 名或 Alpine 属性原文；
  - Canonical host 改由不同请求 host 下的 og:url 与 sitemap URL 验证；
  - 颜色对比度从 `static_src/css/site.css` 的 `@theme` 读取 token；
  - vendor manifest 与 `package.json` 依赖比对；
  - 项目 App 测试只验证可导入且名称与包路径一致。
- 公开页面隐私扫描通过 `tests/privacy.py::assert_no_private_values` 执行；各测试仍各自声明受保护的私有值，覆盖范围不变。
- README 测试只确认每个阶段的验收脚本及其门禁脚本命令存在；文档措辞由人工审阅，不再由测试固定。
- 已通过 Ruff lint/format、Django system check、`makemigrations --check` 与 `npm run static:check`；完整 pytest（含浏览器场景）通过；4 个 Development server smoke 对真实 runserver 通过；重构后的 `scripts/accept_phase_4.py` 在临时全新环境中完整通过，共享门禁 branch coverage 为 95%。

### 3.47 代码清理第 5 批

- 依据 `memory-bank/cleanup_audit.md` 第 5 批清单整理 `static_src/css/site.css`，验收标准是视觉不变。批次中用临时 Playwright 脚本在 desktop 1440×900 与 mobile 390×844 下为 26 个页面状态截取 51 张全页截图，并逐像素比较改动前后结果：除 Chrome 原生校验气泡淡出时机这一基线自身的抖动外，完全一致。
- 全部具体颜色集中在 `@theme`：新增 divider、border、border-strong、separator、input、header、overlay，以及 warning、error、CTA 三种 surface token。组件规则只引用 `var(--color-*)`，不再出现 hex 或 `rgb()` 字面量，满足 `design_document.md` 9.2 对 Design Tokens 集中管理的要求。
- 卡片表面（border、radius、surface）、头像边框与 `object-fit`、首字母 fallback，以及 `overflow-wrap: anywhere` 断行，分别由一条分组选择器统一声明，各组件只保留自己的间距与布局；模板 class 不变。
- 文本输入框选择器以 `:where()` 降低优先级，`.field [aria-invalid="true"]` 不再依赖 `!important`；现在仅 reduced-motion 规则使用 `!important`。导航选择器去掉多余的祖先限定。
- About 的大号 Join 使用 `.button--hero` 修饰类，并声明在 `.button` 各变体之后；Home Hero 在 mobile 下由 `:last-child:nth-child(odd)` 决定是否让最后一个操作独占一行，与按钮数量无关；Home 卡片标题使用 rem 字号。
- 删除与 Tailwind preflight 重复的 `box-sizing`、`body` margin、表单 `font: inherit`、对 Python 文件的 `@source` 扫描，以及 `.content-card` 的 `height: 100%` 与 `.event-card` 撤销补丁。
- Members 卡片保留 desktop `clamp()` 与 mobile 固定 `5.5rem` 的阶梯头像尺寸；断点的单一来源（与 Header JavaScript 共享）由第 6 批完成（见 3.48）。
- 已通过 Ruff lint/format 与 `npm run static:check`；完整 pytest（含全部浏览器场景）`385 passed`。构建产物由 21,532 bytes 降至 21,304 bytes。

### 3.48 代码清理第 6 批

- 第 6 批中风险项逐项经项目负责人确认方案后实施 E7、T8、T12、C4/C5/T2 与 Logo 编码；A6、A8、A15、A16、A19、T4/T5、T15、E5、E9 复核后关闭，理由记录在 `memory-bank/cleanup_audit.md`。
- 本地环境变量：`.env.example` 只保留实际使用的数据库变量，并说明 Compose 的 `POSTGRES_*` 与 Django 读取的 `DATABASE_URL` 必须一致（见 2.4）。
- allauth 页面统一继承 `templates/account/_page.html`，由 eyebrow、唯一 H1、intro 与 body 四个 block 组成，并复用 `account/includes/` 中的单按钮表单、验证码表单和放弃验证码阶段的登出表单。各页 H1 统一使用 `page-title` 作为 `aria-labelledby` 目标。
- Event 报名区约定如下：
  - 服务端只写 `data-open-dialog`（失败提交后重新打开的 dialog x-ref）或 `data-focus-status`（HTMX 成功后需要聚焦）；
  - Alpine 只根据这两个属性打开 dialog 或把焦点移到 `x-ref="status"`；
  - HTMX 只负责提交 dialog 表单并整体替换 `#event-registration`；
  - 状态文字自身带 `role="status"`，dialog 不再位于 live region 中；
  - 报名与取消表单片段由单一 `mode="dialog"` 参数区分 dialog 与整页回退。
- HTMX 报名或取消成功后，焦点移到新的状态元素，不再随被移除的 dialog 落回 `<body>`，由 `event-registration.mjs` 断言覆盖。
- 布局断点只在 `@theme` 中定义：`--breakpoint-hero: 54rem` 与 `--breakpoint-nav: 60rem`。响应式规则通过 `@variant hero`（`width >= 54rem`）和 `@variant max-nav`（`width < 60rem`）位于 `@layer components` 末尾，`@layer` 之外只保留 reduced-motion 规则。Header 不再在 JavaScript 中重复断点，而是根据 Menu `summary` 是否显示决定初始收起。Home Logo `sizes` 中的 54rem 以模板注释标明与 `--breakpoint-hero` 对应。
- Home Logo 保留透明度，并改用 quality 75、alpha_quality 70、method 6 编码，三个生成物合计由约 898 KB 降至约 506 KB（见 3.20）。
- 已通过 Ruff lint/format、Django system check、`makemigrations --check` 与 `npm run static:check`；完整 pytest（含浏览器场景）通过。T8 的 17 种 allauth 渲染情况除 heading id 外完全一致；C4/C5/T2 后的 51 张 desktop/mobile 截图与第 5 批前基线一致（仅 Chrome 原生校验气泡的淡出时机不同）。

### 3.49 Visual Refresh V1：视觉 Tokens 与资产管线

- Token 取值来自 Design canvas `NULDL Home hero concepts` 的 `E · Aligned · three-line title` 与 `design_document.md` 9.2，仍全部集中在 `static_src/css/site.css` 的 `@theme`。
- 既有 token 改为设计稿暖色系：`--color-ink` `#0a0908`（页面底色）、`--color-cream` `#ece4d3`（正文）、`--color-muted` `#c9c0ae`（次要文字）。这是 V1 唯一的全站可见变化。
- 新增金色材质色阶 `--color-gold-shadow` `#7e5015`、`--color-gold-metal` `#bf8933`、`--color-gold-highlight` `#f2bf5a`，装饰网格线 `--color-grid`（4.5% 金色），以及 `--font-mono`（JetBrains Mono）。平面金色 `--color-gold` / `--color-gold-bright` 不变，继续承担链接、Focus 与现有按钮；材质色阶留给 V2 组件。
- Tailwind v4 只输出被引用的 theme 变量，因此材质与网格颜色在 V2 组件使用前不会出现在构建产物中；`@font-face` 声明始终输出。
- JetBrains Mono 以精确版本 `@fontsource/jetbrains-mono@5.3.0` 加入运行依赖，`build-static-assets.mjs` 复制 Latin 400/500 字重与 OFL license，并写入 vendor manifest；运行页面仍不访问第三方 CDN。
- `scripts/build_home_images.py` 从单一 Logo 扩展为源图清单。每个源图声明 SHA-256、尺寸、mode、输出路径、宽度和编码参数；构建前校验完整性与透明通道，输出 method 6、去除 EXIF/XMP 的确定性 WebP，`images:check` 检测漂移。Logo 参数与输出字节不变。
- 新源图与生成物：
  - 金色材质 `static_src/images/brand/gold-texture-source.png` → `static/images/brand/gold-texture-{800,1600}.webp`（RGB，quality 80），供材质填充与金色展示文字使用。
  - Hero 背景照片 `static_src/images/home/hero-specimen-source.png` → `static/images/home/hero-specimen-{560,1120}.webp`（保留透明度，quality 78、alpha_quality 80），只供 V5 宽屏背景层使用。V5 中照片已由项目负责人替换，输出改为单一 `hero-specimen-1440.webp`（见 3.52）。
- 对比度门禁从 `@theme` 读取 token，新增 muted/surface-raised、ink/gold-metal、ink/gold-highlight 与 gold-metal/ink；另以材质图最暗 1% 像素对页面底色 ≥ 3:1 固定大号金色展示文字的下限。材质图作为小字号深色文字背景时局部低于 4.5:1，处理方式在 V2 决定。
- 本步没有修改模板、业务逻辑、URL、表单、settings 或 migration。已通过 `npm run static:check`、Ruff lint/format、Django check、`makemigrations --check`，完整 pytest（含浏览器与 Accessibility 门禁）`394 passed`。

### 3.50 Visual Refresh V2：全站共用组件、Header 与 Footer

- 项目负责人决定（已写入 `design_document.md` 9.2）：材质承载小号深色文字时使用提亮暗部的按钮专用贴图；链接与小号金色文字使用平面金 `#e2b04a`（悬停 `#f3d58a`），Focus 指示继续使用 `#ffd166`。
- 图片构建清单增加 `gold-texture-button-800.webp`：同一材质源图按像素暗度向 `--color-gold-highlight` 混合（`lift_darks=0.7`），最暗像素对 `--color-on-gold` 为 5.3:1；测试以每个像素 ≥ 4.5:1 固定该下限。
- 新增 token：`--color-gold-pale`、`--color-gold-glint`、`--color-gold-sheen`、`--color-gold-edge`、`--color-gold-depth`、`--color-on-gold`、`--color-gold-wash`，以及按 9.2 基准值补充的 `--color-subtle`（表格标签与低优先级文字）和 `--color-gold-line`（30% 金色细边框）；删除不再使用的 `--color-divider`。组件只引用 `var(--color-*)`，半透明效果使用 `color-mix()`。
- 按钮结构：`.button` 自身背景透明，材质填充与一次性悬停高光分别画在带同一切角 `clip-path` 的 `::before` 与 `::after` 上，文字在 `isolation: isolate` 建立的层叠上下文中位于其上。切角因此不会裁掉元素自身的 Focus outline。高光通过 `background-position` 过渡移动，不随元素平移超出切角；只在 `:hover` 声明过渡，离开时直接复位，reduced motion 下即时完成。
- `.button--secondary` 以 `::before` 绘制渐变描边、`::after` 内缩 1px 绘制内芯（切角补偿 0.6px 以保持斜边等宽）；内芯颜色读取所在表面声明的 `--button-ground`（共享卡片表面、报名 dialog、安全提示与 CTA 面板），悬停与 `aria-current` 使用 `--color-gold-wash`，当前项另加下划线。`.button--quiet` 关闭两层；`.button--compact` 为 Header 使用 8px 切角与 0.875rem 文字。
- 其他共用组件：`.gold-text`（材质贴图以 `background-clip: text` 裁切到文字，`box-decoration-break: clone` 使每个行片段上亮下暗，forced colors 或不支持文字裁切时回退为普通文字）、`.gold-rule` 与 Header/Footer 伪元素共用的金色渐变线、`.label-mono` 与 `.gold-tag` 等宽标签、`body` 的 2.5rem 金色坐标网格背景。`.gold-text`、`.label-mono`、`.gold-tag` 尚无页面使用，由 V3 Hero 首先使用。
- Header 按设计稿重排：品牌后紧跟页面导航，账户操作在最右；导航为次要文字色，当前页金色文字加 2px 下划线；`Join the Club` 改用 `.button .button--compact`。Footer 顶部金色渐变线、等宽大写版权行。
- Header、messages、页面主体与 Footer 共用 `min(80rem, 100% - 4rem)` 内容宽度（`max-nav` 下为 `100% - 2rem`），取代原 88rem。
- 浏览器门禁调整：`phase2-accessibility.mjs` 的对比度计算在元素背景透明时读取其 `::after`/`::before` 背景，并覆盖主按钮、描边按钮与 Header 按钮；必需内容与 Home 裁切检查限定在 `main`，避免把 mobile 收起菜单中的 Header 按钮计入；Home 宽度断言改为 80rem。
- 本步没有修改业务逻辑、权限、URL、表单字段或 migration；模板变更仅限 Header `Join the Club` 的 class 与 Footer 版权行 class。完整 pytest（含 Phase 2–4 浏览器与 Accessibility 门禁）`405 passed`；`static:check`、Ruff、Django check、`makemigrations --check` 与 Production `collectstatic`（材质图片 URL 均替换为带 hash 文件名）通过；desktop/mobile 截图走查经项目负责人确认。

### 3.51 Visual Refresh V3：Home Hero 布局

- Hero 由 `.home-hero__main`（文字栏 + Logo）与 `.home-hero__titleblock`（图纸标题栏；V3 时另有装饰说明，V5 中按项目负责人要求删除）两部分组成。文字栏依次为 `Research Field` 材质标签与等宽 eyebrow、唯一 H1、介绍文字和操作按钮；V2 定义的 `.gold-text`、`.label-mono`、`.gold-tag` 由此首次在页面使用。
- H1 由三个 `display: block` 行块组成（`Nonlinear` / `Upper Limb Dynamics` / `Laboratory`），每行内为 `.gold-text`；可访问名称仍为完整的 `Nonlinear Upper Limb Dynamics Laboratory`。标题换行由行块控制，原 `.home-hero__content h1` 的任意断行规则删除。
- 宽于 `--breakpoint-hero`（54rem）时，文字栏与 Logo 作为一组 flex 居中（栏间距 3.5rem）。文字栏 `width: min-content` 且标题行 `nowrap`，因此由最长的第二行决定栏宽，标签、介绍与按钮行全部对齐该宽度；主标题 `clamp(3rem, 6vw, 5.5rem)`、行高 0.92。窄于 54rem 时 Logo 移到文字栏下方，标题行允许换行以避免 320–390px 溢出。
- Hero 按钮以 `grid-auto-flow: column` 与 `grid-auto-columns: minmax(0, 1fr)` 在一行内平分宽度，`align-self: stretch` 覆盖 `.button-row` 的居中对齐以保持等高，因此会员视图只有两个按钮时同样平分一行；文字 `clamp(1rem, 1.5vw, 1.375rem)`。窄于 54rem 时为两列，奇数个时最后一个占满整行。按钮顺序、href 与认证状态分支不变。
- Logo 以 flex 在 18.75–31.25rem（300–500px）之间随剩余空间伸缩，`sizes` 相应改为桌面 31.25rem；带 12% 金色、40px 半径的 `drop-shadow` 外发光，仅用于与暗底分离。
- 图纸标题栏使用 `<dl>`（`Dwg no.`、`Scale`、`Est.`），对辅助技术可读；标签为 `--color-subtle`、数值为 `--color-cream`，边框为 `--color-gold-line`。
- Hero 内容宽度沿用 V2 的 80rem 共享宽度，未采用设计稿约 1360px 的宽度。背景彩蛋由 V5 实施（见 3.52）；原计划的 Hero 信息表（V4）因与 `Upcoming Events` 区重复，经项目负责人决定取消。
- 本步没有修改 view、URL、业务逻辑、表单字段或 migration。完整 pytest（含全部 Playwright 与 Accessibility 门禁）`408 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；1920–390px 截图走查经项目负责人确认。

### 3.52 Visual Refresh V5：Hero 背景彩蛋（V4 已取消）

- V4（Hero 近期活动信息表）经项目负责人决定取消：它只显示最近一场 Upcoming Event，与 Home `Upcoming Events` 区第一张卡片重复。其等宽信息行风格并入 V6 活动卡片；Home view 与查询因此没有改动。
- Hero 底部装饰文字 `Specimen 001 is kept in the dark. Bring a light.` 按项目负责人要求删除，图纸标题栏单独靠右。
- `.home-hero` 内新增 `aria-hidden="true"` 的 `.hero-specimen` 层：常态照片（不透明度 7%）与光照层内的同一照片（85%）。两者都铺满整个 Hero，位于文字与 Logo 之后（`.home-hero` 以 `isolation: isolate` 建立层叠上下文，照片层 `z-index: -1`），整层 `pointer-events: none`。原计划的受力标注（虚线圆、箭头、引线与 `Fig. 01`/`F = ?` 标签）在走查后由项目负责人决定删除，光照只显现照片。
- 照片只在 `@variant hero`（≥ 54rem，Logo 位于标题右侧）内的 `@media (hover: hover)` 中渲染；照片 URL 也只在该条件内以 CSS 背景声明，因此窄屏与不能悬停的设备不渲染该层，也不下载照片。HTML 不引用照片文件。
- 指针交互由 Hero 上的 Alpine 行内处理器完成：`pointermove`（忽略 touch）把指针相对 Hero 的坐标写入 `--light-x`/`--light-y` 并设置 `data-lit`，`pointerleave` 移除 `data-lit`。光照层以 `radial-gradient(circle 12.5rem …)` 遮罩形成跟随指针的 200px 柔边圆，`data-lit` 时不透明度 0 → 1（200ms 过渡，reduced motion 下即时）。没有持续动画、定时器或新增 JavaScript 文件。
- 照片源图已由项目负责人替换为多名成员对抗场景的拼贴：1448 × 1086、完全不透明的 RGBA PNG（黑色底）。图片构建清单新增 `opaque` 标记——该源图须保持完全不透明并编码为 RGB；由于照片以 `cover`（定位 `center 20%`）铺满约 1280px 宽的 Hero，只生成接近源图宽度的 `hero-specimen-1440.webp`，原 560/1120 透明 WebP 删除。照片四边各 12% 以遮罩渐隐，避免黑色底在页面上形成矩形边。
- `design_document.md` 9.6 记录：画面包含多名成员，按既有规则公开上线前需取得其同意，由项目负责人确认。
- 测试：Home 页面测试固定彩蛋层对辅助技术隐藏、不含标注、HTML 不引用照片、装饰文字已删除；Home 浏览器测试在 desktop 验证照片已请求、光照默认熄灭、指针进入后点亮并跟随、离开后熄灭、光照下 Hero 按钮仍可点击，在 390px mobile 与 1280px 触屏（`hover: none`）验证该层不显示且没有照片请求；图片测试以 `OPAQUE_SOURCES` 声明该源图不透明、生成物为 RGB。
- 本步没有修改 view、URL、业务逻辑、表单字段或 migration。完整 pytest（含全部 Playwright 与 Accessibility 门禁）`409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；1440/1920/900px 截图走查经项目负责人确认。

### 3.53 Visual Refresh V6：Home 其余区块与共享活动卡片

- 由于本会话无法访问 Design canvas，V6 先以 `design_document.md` 7.5、9.3、9.4 与 V2 组件制作临时 HTML mockup，经项目负责人确认后实施；mockup 只在临时目录，不进入仓库。
- 新增共用区块标题 `.section-heading`：等宽金色小标签、标题组与可选的右侧操作（窄屏换行）。Home 的 `New to Armwrestling?` 与 `Upcoming Events` 都使用它；`Join Us !` 使用 V2 的 `.gold-text`。
- `New to Armwrestling?` 卡片改为 `.feature-grid` / `.feature-card`：半透明金色边框、顶部金色渐变细线、对辅助技术隐藏的等宽编号 `01–04`，标题 1.375rem。文案不变。
- `Upcoming Events` 去掉整块 `.session-card` 面板；`View all events` 改为标题区右侧的紧凑次要按钮，卡片放在 `.event-stack` 中，空状态为 `.events-empty` 虚线框。
- `events/includes/event_card.html` 重写为 Home 与 Events 列表共用的网格卡片，整张卡片在 `Australia/Sydney` 时区下渲染：
  - 左侧日期块（星期、日、月份与年份），因与信息行重复而 `aria-hidden`；
  - 标题链接；
  - `<dl class="event-facts">` 图纸式信息行：起止在同一 Sydney 日期时为 `Date` + `Time`，跨天时为 `Starts` + `Ends`，各值带 `<time datetime>`；另有 `Location`；
  - 右侧状态标签与 `View details` 次要紧凑按钮，可访问名称为 `View details for <title>`（Tailwind `sr-only` 补充标题）。
- 状态标签 `.status-tag` 一律为不填充的细描边文字框，开放状态以 `.status-tag--open` 使用金色文字；状态分支、文案与 `event-status` class 不变。金色材质填充只用于主要操作，`View details` 保持描边按钮。状态标签与按钮等宽（`justify-items: stretch`），窄于 `--breakpoint-hero` 时卡片改为“日期块 + 标题 / 信息行 / 状态与按钮”三行，状态与按钮两等分并等高。
- 活动详情页的信息卡去掉了原有的 `event-card` class（V6 前它在详情页没有样式作用），避免继承新的列表卡片布局；详情页的视觉重做留给后续 Events 页面轮次。
- 删除 `.session-card`、`.home-events-action`、`.home-page .content-card h3` 与旧 `.event-card h3` 规则。
- 测试：状态标签断言改为新 class；Events 浏览器测试改为 `View all events` 位于卡片上方、精确匹配标题链接，并断言状态标签与按钮等宽且无背景图；Home 浏览器测试改为 `.feature-card h3` 22px；Accessibility 门禁新增卡片编号、卡片正文与空状态对比度。
- 本步没有修改 view、URL、业务逻辑、表单字段或 migration。完整 pytest（含全部 Playwright 与 Accessibility 门禁）`409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；Home 与 Events 列表 1440/390px 截图走查经项目负责人确认。

### 3.54 Visual Refresh V7：第一轮质量门禁

- 第一轮视觉优化（V1–V3、V5–V6）以既有的 `scripts/accept_phase_4.py` 作为质量门禁，没有新增脚本：它在 OS 临时目录建立全新 uv environment，执行共享门禁 `scripts/verify_project.py`（锁定 npm/Chromium 安装、静态资源 build/check/watch、Ruff、migration drift、Django check、干净 PostgreSQL branch coverage 测试、Production deploy check、manifest `collectstatic`），再在真实 Development server 上运行 Phase 2–4 desktop/mobile smoke。
- 结果：完整 pytest `409 passed`、branch coverage `95%`，`check --deploy --fail-level WARNING` 无问题，三组 smoke 全部通过；验收后工作区没有任何已跟踪文件变化。
- 人工走查使用 Development server 上 1440 × 900 与 390 × 844 的全页截图，覆盖 Home、About、Beginners & Safety、Events 列表、Event detail、Members、Log in 与 Sign up，均无横向溢出与 page error，经项目负责人确认。
- 第一轮的范围边界：全站共用 tokens、字体、按钮、Header/Footer，以及 Home 与 Events 列表卡片已经按新视觉实施；About、Beginners & Safety、Event detail、Members、认证与 Account、错误页仍沿用原有布局，只继承新的颜色、字体与按钮。后续按 `implementation.md` 九点五列出的页面顺序逐页设计确认后再展开步骤。
- 本步没有修改代码、view、URL、业务逻辑或 migration。

### 3.55 Visual Refresh V8：Events 列表页（第二轮）

- 第二轮从 Events 列表与详情开始：项目负责人先确认 mockup，规则写入 `design_document.md` 7.5，`implementation.md` 展开为 V8（列表）、V9（详情与报名区）、V10（第二轮质量门禁）。
- 新增共用页头 `.page-heading`（等宽金色小标签与大标题，供 Events 列表与后续详情页使用）。
- `Upcoming`/`Past` 筛选由两个描边按钮改为 `.filter-tabs`：`<nav aria-label="Event filters">` 中的普通链接，等宽大写文字、半透明金色底线，当前项金色文字加 2px 下划线（与 Header 当前页一致）。`?view=` 参数、`aria-current="page"`、无效参数回退与无 JavaScript 行为不变。
- 共享活动卡片在 Past 活动上加 `event-card--past`，日期数字改用 `--color-subtle`；状态文字仍为 `Past event`。`.event-list` 的上边距删除，由标签页提供间距。
- 测试新增 Past 卡片标记与标签页当前项断言；既有浏览器测试按链接名称与 `aria-current` 定位筛选，无需修改。
- 本步没有修改 view、URL、业务逻辑或 migration。完整 pytest `409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；Upcoming/Past 的 1440 与 390px 截图走查经项目负责人确认。

### 3.56 Visual Refresh V9：活动详情页与报名区（第二轮）

- 详情页为单栏、居中的结构：顶部 `.back-link`「← Back to events」（等宽小字，上下内边距保证 24px 以上触控目标）；`.page-heading--center` 页头第一行为 `.event-detail-kicker`（`Club activity` · 状态标签，间隔点 `aria-hidden`），第二行为 H1；其下为通栏 `<aside class="event-panel" aria-label="Event details and registration">`；最后为宽 `min(100%, 48rem)` 居中、段落左对齐的说明栏。面板在源码中位于说明之前，阅读顺序与视觉顺序一致。
- 页头状态与列表卡片使用同一判断（Past / `registration_available` / 其余为 Registration unavailable）。
- 信息面板第一行为 Sydney 时区的 `event-facts`（同日 `Date` 含星期与 `Time`，跨天 `Starts`/`Ends`，均含 `<time datetime>`；`Location`），以 `flex: 1 1 16rem` 整格换行，单独成行的格子拉伸填满，1px 间隙配金色底绘制分隔线；地图链接作为 `(View in Map)` 位于 `Location` 值之后（新窗口、`noopener noreferrer`）。第二行为居中、宽 `min(100%, 20rem)` 的报名区。`event-facts` 的网格位置只作用于 `.event-card`，以便在面板与无 JavaScript 确认页中复用。
- 报名区：Past、Registration unavailable 与 `Registered` 均为 `event-status status-tag`（`Registered` 加 `status-tag--open`，取代原警示色 `status-banner`）；`role="status"`、`tabindex="-1"`、`x-ref="status"`、`data-open-dialog`/`data-focus-status` 与 HTMX 整体替换 `#event-registration` 的契约不变。按钮与状态占满报名区宽度。
- 报名 dialog 的 H2 为 `Risk Notice`，上方 `.event-registration-dialog__action` 以 1.375rem 等宽金色大写显示 `Confirm registration`；`aria-labelledby` 引用两者，可访问名称为 `Confirm registration Risk Notice`。dialog 为金色细边框加阴影；`.risk-notice-copy` 为暖黑底细边框的可滚动区域，版本行为 `.notice-version`。取消 dialog 标题不变。无 JavaScript 确认页改用 `.page-heading` 与单行 `event-facts`（`Event`）。
- 走查中的修订（均经项目负责人确认）：宽屏左右两栏造成标题与面板错层和大片空白，改为通栏面板；信息行提前换行使按钮单列，改为“信息格整行 + 居中报名区”；标题区与说明栏居中；地图链接移入 `Location` 行并改为 `(View in Map)`；状态标签移到 `Club activity` 旁；dialog 大标题改为 `Risk Notice`。
- 走查截图使用一个只在本地临时存在的测试（在 test database 中建立合成活动、合成 Risk Notice 与两名合成会员，截图后删除），覆盖 1440、约 820 与 390px 下的全部报名状态、两个 dialog 与无 JavaScript 确认页；Development database 未写入数据。
- 测试：状态标签 class、顶部返回链接、页头状态、信息面板及其先于说明的源码顺序、`Registered` 为带 `role="status"` 的状态标签、`(View in Map)` 位于 `Location` 行内，以及 dialog 的精确可访问名称与 `Risk Notice` 标题。
- 本步没有修改 view、URL、业务逻辑、表单字段或 migration。完整 pytest `409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过。

### 3.57 Visual Refresh V10：第二轮质量门禁

- 第二轮（V8 Events 列表、V9 活动详情与报名区）沿用 V7 的门禁方式，没有新增脚本：`scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中执行共享门禁 `scripts/verify_project.py`，再在真实 Development server 上运行 Phase 2–4 desktop/mobile smoke。
- 结果：完整 pytest `409 passed`、branch coverage `95%`，Ruff、migration drift、Django check 与 `check --deploy --fail-level WARNING` 均无问题，三组 smoke 全部通过；验收后工作区没有任何已跟踪文件变化。
- 人工走查使用只在本地临时存在的测试（test database 中的合成开放、关闭与 Past 活动、合成 Risk Notice 与两名合成会员，截图后删除），在 1440 × 900 与 390 × 844 下各截 11 张：列表 Upcoming/Past、详情页 Anonymous/会员可报名/已报名/报名关闭/Past、报名与取消 dialog、禁用 JavaScript 的报名与取消确认页；均无横向溢出与 page error，经项目负责人确认。Development database 未写入数据。
- 走查中项目负责人决定保持禁用 JavaScript 的完整报名确认页现状：标题仍为 `Event registration` / `Confirm registration`（与 dialog 的 `Confirm registration` / `Risk Notice` 不同），Risk Notice 正文区沿用 dialog 的最大高度并在框内滚动。
- 第二轮完成后，Events 列表、详情、报名区与确认页已按新视觉实施；About、Beginners & Safety、Members、认证与 Account、错误页仍沿用原有布局，按 About、Beginners & Safety → Members → 认证与 Account → 403/404/500 的顺序逐页确认设计后再展开步骤。
- 本步没有修改代码、view、URL、业务逻辑或 migration。

### 3.58 Visual Refresh V11：About 页与共用报告分节（第三轮）

- 第三轮（About 与 Beginners & Safety）先由项目负责人确认 mockup，规则写入 `design_document.md` 7.9（页头小标签、`Join` 位置与 Draft Risk Notice 入口对齐写入 7.7），`implementation.md` 展开为 V11（About 与共用报告分节）、V12（Beginners & Safety）、V13（第三轮质量门禁）。走查中项目负责人选择让正文列延伸到右边缘（左右 1 : 2），并要求 `Join` 居中。
- 报告页结构：`public-page--report` 取代 `public-page--content` 窄栏，页面占满共享内容宽度；页头复用 `.page-heading`（等宽小标签 `About the club`、H1、`.lede`），左对齐。
- `.report-section` 是 About 与（V12 起）Beginners & Safety 共用的分节：上方金色细线；`.report-section__label` 内为对辅助技术隐藏的等宽 `01–04` 编号与 H2，`.report-section__body` 为正文。窄屏时编号与标题一行、正文在下；`@variant hero` 下为 `1fr : 2fr` 两列且编号与标题纵向排列，正文右缘与内容区右缘对齐。没有新增断点。
- `.report-note`（左侧 2px 金色细线、次要文字色）标出补充说明段落；About 中用于投票权与 Executive 资格的说明。
- `What We Do` 复用 Home 的 `.feature-grid` / `.feature-card`（编号 `aria-hidden`，项目名为 H3）；分节内的功能卡片以 `minmax(min(20rem, 100%), 1fr)` 自动排列，宽屏两列、窄屏一列，标题 1.25rem。
- Anonymous 的 `Join` 放在 `.report-action`（金色细线下居中）；`.button--hero` 改为 Home Hero 按钮尺寸（`min(100%, 16rem)` 宽、至少 3.5rem 高、1.375rem 文字），并在 `max-nav` 下保持该宽度，不随窄屏按钮默认占满整行。`data-public-primary`、Signup 链接与会员不显示的分支不变。
- 删除只被旧 About 使用的 `.card-grid`、`.public-card-list .content-card` 与 `.public-page__join-action`。
- 测试：Heading 顺序加入四个 H3，并断言页头小标签、4 张功能卡片与 4 个分节；浏览器测试断言宽屏分节两列且正文到达右缘、功能卡片两列、`Join` 的字号/高度/宽度与页面居中、手机上标题在正文之上且 `Join` 保持 16rem，并对 About 增加 200% 放大与无 JavaScript 检查。
- 本步没有修改 view、URL、Metadata、文案或 migration。完整 pytest `409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；1440/820/390px 截图走查经项目负责人确认。

### 3.59 Visual Refresh V12：Beginners & Safety 页（第三轮）

- Beginners & Safety 复用 V11 的报告页结构：`public-page--report`、`.page-heading`（等宽小标签 `Beginners & Safety`、H1、`.lede`）与五个 `.report-section`（`aria-hidden` 编号 `01–05`）；`If you are uncertain…` 段落使用 `.report-note`。
- `What to Expect` 为 `<ol class="procedure">`：每项左侧为 CSS 计数器生成的等宽编号方块（半透明金色细边框、页面底色），相邻方块之间以 `::after` 金色细竖线连接中心；有序列表语义不变。
- 风险说明为分节正文中的 `.risk-panel`：暖色底（`--color-warning-surface`）、半透明金色细边框与顶部金色渐变细线（与活动详情信息面板一致），取代左侧粗金条的 `.safety-panel`。`Read the Draft Risk Notice` 为面板内正文下方左对齐的描边次要按钮，仍只在 `draft_risk_notice_visible` 时输出，`data-draft-risk-notice` 不变；窄屏时按网站规则占满面板宽度。
- `During Training` 为 `<ul class="rule-list">`：单一金色细边框，行间细线分隔，每行前为金色小方块标记，取代五张独立卡片。
- 删除 `.step-list`、`.safety-list`、`.safety-panel`、`.safety-panel__action` 及其在共享卡片表面、末子元素间距与居中操作分组中的条目；`--color-warning`/`--color-warning-surface` 继续由 `.status-banner` 与表单使用。
- 测试：页头小标签、5 个分节、各 5 项的流程与规则列表；Draft 入口位于 `.risk-panel` 内、在面板内容左缘对齐并位于正文下方；Accessibility 门禁必需元素改为 `.procedure`、`.rule-list`、`.risk-panel`；宽屏流程方块同列且有连接线、规则 5 行、风险面板位于分节标题右侧。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server，Draft 关闭与开启两种状态，截图后删除），覆盖 1440、820、390px。
- 本步没有修改 view、URL、Metadata、文案、Draft 开关逻辑或 migration。完整 pytest `409 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；截图走查经项目负责人确认。

### 3.60 Visual Refresh V13：第三轮质量门禁

- 第三轮（V11 About、V12 Beginners & Safety）沿用 V7、V10 的门禁方式，没有新增脚本：`scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中执行共享门禁 `scripts/verify_project.py`，再在真实 Development server 上运行 Phase 2–4 desktop/mobile smoke。
- 结果：完整 pytest `409 passed`、branch coverage `95%`，Ruff、migration drift、Django check 与 `check --deploy --fail-level WARNING` 均无问题，三组 smoke 全部通过；验收后工作区没有任何已跟踪文件变化。
- 人工走查使用只在本地临时存在的测试（Test settings 的 live server、一名合成已验证会员，Draft Risk Notice 关闭与开启两种状态，截图后删除），在 1440 × 900 与 390 × 844 下覆盖 About 与 Beginners & Safety 的 Anonymous/会员 × Draft 开/关，共 16 张：About 仅对 Anonymous 显示居中的 `Join`；Beginners & Safety 风险面板内的 `Read the Draft Risk Notice` 与 Header 的 `Draft Risk Notice` 导航随 Draft 开关同步出现或消失。均无横向溢出与 page error，经项目负责人确认。Development database 未写入数据。
- 第三轮完成后，Home、Events 列表与详情、About、Beginners & Safety 已按新视觉实施；Members、认证与 Account、错误页仍沿用原有布局，按 Members → 认证与 Account → 403/404/500 的顺序逐页确认设计后再展开步骤。
- 本步没有修改代码、view、URL、业务逻辑或 migration。

### 3.61 Visual Refresh V14：Researcher 编号的数据与 Admin（第四轮）

- 第四轮（Members）先由项目负责人确认 mockup，规则写入 `design_document.md` 4.4、7.10 与 11.1，`implementation.md` 展开为 V14（编号数据与 Admin）、V15（Members 列表）、V16（Member detail 与 Preview）、V17（第四轮质量门禁）。项目负责人在三个编号来源中选择“管理员手动分配”，标签位置选择“名字上方”；本轮经批准新增一个字段与 migration，这是与前几轮“不改 migration”约束的唯一差异。
- `MemberProfile.researcher_number` 是可空 `PositiveIntegerField`：字段级 `unique=True` 建立唯一索引（PostgreSQL 允许多个 `NULL` 共存），`MinValueValidator(1)` 在 model 校验中拒绝 `0`，检查约束 `members_profile_researcher_number_positive` 在数据库层拒绝直接写入的 `0`。`save()` 既有的 `full_clean()` 因此在重复或越界时先给出字段错误，数据库约束作为 `QuerySet.update()` 等绕过路径的最终保护。
- `researcher_label` 属性集中显示格式：未分配为 `None`，否则为至少两位补零的 `Researcher 07`；后续模板只读取该属性，不各自格式化。
- `members.0002_memberprofile_researcher_number` 只增加该字段与检查约束，不回写 `0001_initial`，也不为现有资料赋值。
- MemberProfile Admin 的可编辑字段为 `is_hidden_by_admin`、`executive_role` 与 `researcher_number`，列表新增可排序的编号列；会员自述、User、发布状态与时间戳仍只读，仍使用标准 `change_memberprofile` 权限、`LogEntry`，不提供新增、删除或 action。号码不随发布、取消发布或隐藏变化，只由管理员修改。
- `MemberProfileForm` 的显式白名单没有改变，会员表单不能提交编号。Publish confirmation 的公开字段清单加入编号：已分配时显示具体标签，未分配时说明“if one has been assigned”。公开 Members 列表、详情与 Preview 的标签留给 V15–V16，本步没有修改公开页面、URL、公开 queryset 或 CSS。
- 测试覆盖显示格式（`01`、`07`、`42`、`100`）、空值共存、model 与数据库两层的重复和 `0` 拒绝、会员表单伪造提交、Admin 分配/修改/清除、无效与重复输入的字段错误、列表排序，以及确认页两种文字。完整 pytest `426 passed`；Ruff、Django check、`makemigrations --check` 与 `git diff --check` 通过；Admin 与确认页截图走查经项目负责人确认。

### 3.62 Visual Refresh V15：Members 列表页（第四轮）

- 列表页外层为 `.members-page`，页头复用 `.page-heading`（等宽小标签 `Club community`、H1、`.lede`），取代原 `eyebrow` 页头；与卡片网格的间距由 `.members-page` 的 grid gap 提供。
- `.member-directory` 以 `auto-fill` 与 `minmax(min(100%, 22rem), 1fr)` 排列，宽屏三列、约 820px 两列、手机一列，没有新增断点；取代 3.34 记录的两列横向 cards。
- `.member-card` 仍属于共享卡片表面分组，但边框改为 `--color-gold-line`，`::before` 绘制顶部金色渐变细线（与功能卡片、活动面板一致）；Avatar 与 fallback 为 6.5rem（`max-nav` 下 5rem）方形，金色细边框、直角，fallback 使用页面底色。
- 卡片内容顺序为：已分配时的 `gold-tag` Researcher 标签（读取 V14 的 `researcher_label`，未分配不输出）、H2 名称链接、`<dl class="member-facts">`。字段白名单、排序、详情 URL 与 `aria-labelledby` 不变；标签只在公开 queryset 内的卡片中出现，因此不公开未发布或隐藏资料的号码。
- 名称链接以 `::after` 覆盖整张卡片（卡片 `position: relative`），整卡成为单一点击目标；名称自身的 Focus outline 取消，由 `.member-card:has(.member-card__name-link:focus-visible)` 在卡片外框绘制与全站相同的金色 Focus 环。悬停只提亮边框与名称颜色，没有动画以外的状态依赖。
- `.member-facts` 是图纸式资料格组件（等宽大写、标签低优先级色居左、数值主文字色居右、行间以金色底上的 1px 间隙形成分隔线），取代 `.member-card__details`，V16 的详情面板将复用它。空状态沿用共享 `.empty-state` 卡片，7.10 未规定其新样式。
- 测试：页头小标签与 H1；标签只在已分配号码的卡片中、位于 H2 之前；未发布与隐藏资料的号码不出现；浏览器测试另断言标签位于名称正上方且左对齐、桌面卡片并排、键盘 Focus 时整卡出现 outline、点击卡片角落进入详情。
- 本步没有修改 view、URL、queryset、Metadata、文案或 migration。完整 pytest `429 passed`；`static:check`、Ruff、Django check 与 `git diff --check` 通过；1440/820/390px、Focus/悬停与空状态截图走查经项目负责人确认。

### 3.63 Visual Refresh V16：Member detail 与本人 Preview（第四轮）

- `profile_public_fields.html` 仍是详情与 Preview 的唯一公开字段组件，结构改为外层 `article.profile-public`：先是 `.profile-panel` 信息面板（Avatar/fallback；`.profile-kicker` 中的 `Member profile` 与已分配时的 Researcher `gold-tag`；名称；等宽 `@username`；`.member-facts` 资料格），再是 `Bio` 与 `Links` 两个 `.report-section`。公开字段白名单、Bio 的 `linebreaksbr` 与 escaping、外链 `target="_blank"` 与 `noopener noreferrer` 均不变。
- 没有内容的分节不输出，分节编号由模板按实际出现顺序给出（只有 Links 时为 `01`），什么都没填时只剩信息面板。
- 标题层级由 `public_profile_detail` 决定：详情页名称为唯一 H1、分节为 H2；Preview 名称为 H2、分节为 H3，从而修正了原先详情页 H1 之后直接出现 H3 的跳级。Preview 的 H2 名称与公开 H1 使用同一字号、字重与大写，报告分节的 H3 与 H2 同样式，使 Preview 与公开效果一致。
- `member_detail.html` 外层为 `.member-profile`，顶部使用与活动详情相同的 `.back-link`「← Back to members」；Preview 页面外壳（窄栏、隐藏提示、操作按钮）不变，留给认证与 Account 轮次。
- 面板宽于 `--breakpoint-hero` 时为 `15rem : 1fr` 两列，否则 Avatar 位于身份信息上方（`max-nav` 下 11rem）；面板内的 `.member-facts` 改为整格换行的横向格子，复用 V15 的资料格组件。`public_avatar.html` 以 `profile-panel` 为 block 输出 `profile-panel__avatar(-fallback)`。
- 删除 `.profile-public-card` 系列规则及其在共享卡片表面、Avatar、断行与 `max-nav` 分组中的条目，改为对应的 `profile-panel` / `profile-public` 项；长 Username 与 Bio 仍可任意断行。
- 测试：详情页返回链接、H1/H2 层级、kicker 标签位于 H1 之前、分节编号连续及缺失分节与未分配标签不输出；Preview 共用面板且层级为 H1 → H2 → H3；浏览器测试另断言桌面 Avatar 在身份信息左侧、手机在上方，以及标签位于名称上方。
- 本步没有修改 view、URL、queryset、Metadata、文案或 migration。完整 pytest `432 passed`（其后仅调整 Preview H2 样式，相关浏览器、Accessibility 与静态资源测试重跑 `28 passed`）；`static:check`、Ruff、Django check 与 `git diff --check` 通过；详情三种组合、Preview 与隐藏状态 Preview 的 1440/820/390px 截图走查经项目负责人确认。

### 3.64 Visual Refresh V17：第四轮质量门禁

- 第四轮（V14 Researcher 编号、V15 Members 列表、V16 Member detail 与 Preview）沿用 V7、V10、V13 的门禁方式，没有新增脚本：`scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中执行共享门禁 `scripts/verify_project.py`，再在真实 Development server 上运行 Phase 2–4 desktop/mobile smoke。
- 结果：完整 pytest `432 passed`、branch coverage `95%`，Ruff、migration drift（含 `members.0002`）、Django check 与 `check --deploy --fail-level WARNING` 均无问题，三组 smoke 全部通过；验收后工作区没有任何已跟踪文件变化。
- 人工走查使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、七名合成会员与程序生成的抽象头像，截图后删除），在 1440 × 900 与 390 × 844 下各 7 张：Members 列表（有/无编号与 Avatar、长名称，被管理员隐藏的编号资料不出现）与空状态，Member detail 的完整、只有 Links、未填写三种组合，以及本人 Preview 与隐藏状态 Preview；均无横向溢出与 page error，经项目负责人确认。Development database 未写入数据。
- 第四轮完成后，Home、Events、About、Beginners & Safety 与 Members（列表、详情、Preview 中的公开字段组件）已按新视觉实施；认证与 Account（含 Preview 页面外壳与 Publish/Unpublish 确认页）、错误页仍沿用原有布局，按认证与 Account → 403/404/500 的顺序逐页确认设计后再展开步骤。
- 本步没有修改代码、view、URL、业务逻辑或 migration。

## 四、当前文件职责

| 文件 | 当前作用 |
| --- | --- |
| `.gitattributes` | 无论各机器的 `core.autocrlf` 如何设置，都让文本文件统一以 LF 签出，并把图片、字体与 PDF 标记为 binary；保证 manifest 中带 hash 校验的 vendor 文件与 license 在全新 clone 中字节一致。 |
| `.gitignore` | 排除 Python 构建产物、虚拟环境、测试缓存、Django 本地数据库、本地 `media/` 上传目录、`.env`、其他本地 `.env.*`、`node_modules/`、Production `staticfiles/` 收集目录、日志和常见工具生成文件；明确保留 `.env.example` 与 `uv.lock`。 |
| `.env.example` | 声明本地 PostgreSQL、Django Development/Test 和 Production 配置所需变量及安全示例值，供开发者复制为未跟踪的 `.env`。 |
| `AGENTS.md` | 定义仓库级开发约束，包括编码前必读文档、架构变更审批、计划目录、测试原则、命名规范和敏感数据限制。 |
| `README.md` | 提供项目定位、工具要求、首次安装、日常开发、migration/static/runserver 命令、共享质量门禁、Phase 1–3 自动验收、Phase 3 合成账户与临时 media 人工流程、安全数据边界和目录职责；明确中性 NULDL Branding。 |
| `pyproject.toml` | 定义项目元数据、Python 3.13.x 要求、精确运行及开发依赖，并配置 pytest strict mode/test root、pytest-django Test settings、`apps`/`config` branch coverage 与 Python 3.13 Ruff lint/format；只保留 settings wildcard import 和 migration class attributes 所需的文件级豁免。 |
| `uv.lock` | 记录由 `uv` 解析的完整 Python 依赖图、版本和包来源，用于可重复安装；不手工编辑。 |
| `package.json` | 定义锁定的浏览器 library、字体（Inter、Barlow Condensed、JetBrains Mono）与前端开发工具，并提供 vendor copy/check、图片 build/check、Tailwind build/watch、watch smoke 和完整 static build/check scripts。 |
| `package-lock.json` | 记录完整 npm 依赖树、下载来源和完整性信息，供 `npm ci` 可重复安装；不手工编辑。 |
| `scripts/build-static-assets.mjs` | 按固定清单从锁定 npm packages 复制 Alpine.js、HTMX、Inter/Barlow Condensed/JetBrains Mono 字体与 license，并生成或校验包含版本和 SHA-256 的 vendor manifest。 |
| `scripts/build_home_images.py` | 按源图清单校验 Home Logo、金色材质与 Hero 背景照片源文件的 SHA-256、格式、尺寸、mode 与透明通道（或声明为不透明的源图保持完全不透明并编码为 RGB），并以锁定 Pillow 和逐源固定编码参数确定性生成或检查去除 metadata 的响应式 WebP 版本；按钮材质变体先将暗部向金色亮部提亮。 |
| `scripts/check-css-watch.mjs` | 在临时目录启动 Tailwind `--watch=always`，确认首次 watch build 完成后终止进程并清理临时输出。 |
| `scripts/verify_project.py` | 提供跨阶段共享的本地/CI 质量安全门禁，执行锁定依赖和浏览器准备、静态构建与 watch smoke、Ruff、migration/Django、干净 PostgreSQL branch coverage 测试、warning-level Production deploy check 与 manifest collectstatic，并传播所有子命令失败。 |
| `scripts/verify_phase_1.py` | 保留 Phase 1 命令兼容性，并将执行委派给 `scripts/verify_project.py`，不再维护独立门禁逻辑。 |
| `scripts/_acceptance.py` | 提供各阶段共享的全新环境验收流程：建立临时 uv environment、等待 PostgreSQL、执行 Development migration 与指定门禁、启动并可靠清理真实 Development server、依次运行 smoke，并在失败时输出 server log。 |
| `scripts/accept_phase_1.py` | Step 20 验收入口：以 `scripts/verify_phase_1.py` 为门禁，运行 Phase 1 desktop/mobile Development smoke。 |
| `scripts/accept_phase_2.py` | Step 28 验收入口：以共享项目门禁运行 Phase 2 desktop/mobile Development smoke。 |
| `scripts/accept_phase_3.py` | Step 36 验收入口：以共享项目门禁依次运行 Phase 2/3 desktop/mobile Development smoke。 |
| `static_src/css/site.css` | Tailwind CSS v4 项目样式源，声明 template source、local fonts（含 JetBrains Mono）、集中管理的全部颜色（含金色材质色阶、浮雕与近黑文字、网格线、低优先级文字和金色细边框）、字体（含等宽族）与圆角 tokens、坐标网格页面背景、共享内容宽度、金色材质主按钮/渐变描边次要按钮/安静按钮/Header 紧凑按钮、金色展示文字及其 forced-colors 回退、金色渐变分隔线、等宽标签与材质标签、共享卡片表面/头像/断行分组规则、全局基础规则、公开页面、Home（含 Hero 文字栏/Logo 分组、等宽按钮行、图纸标题栏，以及仅宽屏可悬停时渲染的背景照片、边缘渐隐与指针光照遮罩）、共用区块标题与页头（含居中变体）、Events 筛选标签页、活动详情返回链接/状态小标签行/通栏信息面板与报名区、报告页（About、Beginners & Safety）的左对齐页头、带编号的两列报告分节、补充说明段落、分节内功能卡片、居中页面操作、连线编号流程、带金色顶线的风险面板与单框规则列表、报名 dialog 与 Risk Notice 正文区、Home 编号功能卡片、Events 网格活动卡片（日期块、图纸式信息行、不填充的状态标签与等宽详情按钮）与报名 dialog、Profile、Account Profile 摘要、Members 列表页头与金色细边框网格卡片（Researcher 标签、整卡点击与卡片外框 Focus、图纸式资料格 `.member-facts`）、Member detail 与 Preview 共用的信息面板（Researcher 标签 kicker、面板内横向资料格）与编号分节、返回链接、Members empty state、连续字符断行、24px Profile 触控目标、响应式导航、focus 和 reduced-motion。 |
| `static/css/site.css` | 由 Tailwind CLI 从 `static_src/css/site.css` 生成的 minified 浏览器样式；作为部署输入提交，不手工编辑。 |
| `static_src/images/brand/nuldl-club-logo-transparent.png` | 当前 Home Logo 的透明 PNG 源文件；由固定 SHA-256 保护，不直接作为响应式页面资产。 |
| `static/images/brand/nuldl-club-logo-480.webp` | 从获准源图生成的 480 × 480 WebP，供窄屏 Home Hero 使用。 |
| `static/images/brand/nuldl-club-logo-800.webp` | 从获准源图生成的 800 × 800 WebP，并作为 Home Logo 默认 `img` fallback。 |
| `static/images/brand/nuldl-club-logo-1200.webp` | 从获准源图生成的 1200 × 1200 WebP，供较高像素密度或较宽 Hero 使用。 |
| `static_src/images/brand/gold-texture-source.png` | 金色锤纹材质的 1600 × 640 RGB PNG 源文件；由固定 SHA-256 保护，不直接作为页面资产。 |
| `static/images/brand/gold-texture-800.webp` | 从材质源图生成的 800 × 320 WebP，供 1x 材质填充与金色展示文字使用。 |
| `static/images/brand/gold-texture-1600.webp` | 从材质源图生成的 1600 × 640 WebP，供 2x 材质填充与金色展示文字使用。 |
| `static/images/brand/gold-texture-button-800.webp` | 从材质源图提亮暗部后生成的 800 × 320 WebP，供主按钮与材质标签使用，每个像素对 `--color-on-gold` 至少 4.5:1。 |
| `static_src/images/home/hero-specimen-source.png` | Home Hero 背景彩蛋照片的 1448 × 1086 不透明 RGBA PNG 源文件（项目负责人提供的成员对抗拼贴，黑金调色、黑色底）；由固定 SHA-256 保护。 |
| `static/images/home/hero-specimen-1440.webp` | 从照片源图生成的 1440 × 1080 RGB WebP；只由宽屏、可悬停设备上的 Hero 背景彩蛋层以 CSS 背景加载。 |
| `static/fonts/inter-latin-400-normal.woff2` | 本地 Inter Latin 400 字重文件，供正文常规文本使用。 |
| `static/fonts/inter-latin-500-normal.woff2` | 本地 Inter Latin 500 字重文件，供中等强调文本使用。 |
| `static/fonts/inter-latin-600-normal.woff2` | 本地 Inter Latin 600 字重文件，供按钮、导航与加重正文使用。 |
| `static/fonts/barlow-condensed-latin-600-normal.woff2` | 本地 Barlow Condensed Latin 600 字重文件，供次级标题使用。 |
| `static/fonts/barlow-condensed-latin-700-normal.woff2` | 本地 Barlow Condensed Latin 700 字重文件，供主要标题使用。 |
| `static/fonts/barlow-condensed-latin-800-normal.woff2` | 本地 Barlow Condensed Latin 800 字重文件，供高强调标题使用。 |
| `static/fonts/jetbrains-mono-latin-400-normal.woff2` | 本地 JetBrains Mono Latin 400 字重文件，供等宽标签与图纸标题栏使用。 |
| `static/fonts/jetbrains-mono-latin-500-normal.woff2` | 本地 JetBrains Mono Latin 500 字重文件，供等宽文字强调使用。 |
| `static/vendor/alpine/alpine.min.js` | 从锁定 Alpine.js package 复制的本地 minified runtime，负责当前 USYD 条件界面与错误焦点增强。 |
| `static/vendor/htmx/htmx.min.js` | 从锁定 HTMX package 复制的本地 minified runtime；只由 Event detail 页面加载，负责报名与取消区域的局部更新。 |
| `static/vendor/licenses/inter.txt` | 保存本地分发 Inter 字体对应 package 的 license 文本。 |
| `static/vendor/licenses/barlow-condensed.txt` | 保存本地分发 Barlow Condensed 字体对应 package 的 license 文本。 |
| `static/vendor/licenses/jetbrains-mono.txt` | 保存本地分发 JetBrains Mono 字体对应 package 的 OFL license 文本。 |
| `static/vendor/licenses/htmx.txt` | 保存本地分发 HTMX 对应 package 的 license 文本。 |
| `static/vendor/manifest.json` | 记录全部脚本管理 vendor/font 输出的 package、精确版本、源路径与 SHA-256，供 `assets:check` 检测漂移。 |
| `compose.yaml` | 定义本地 PostgreSQL 18.6 service、端口映射、健康检查、重启策略和持久化 named volume。 |
| `manage.py` | 本地运行 Django management command 的命令行入口，默认加载 `config.settings.development`。 |
| `config/__init__.py` | 将 `config` 标记为 Python package。 |
| `config/settings/__init__.py` | 将 `config.settings` 标记为环境配置 package，不隐式选择具体环境。 |
| `config/settings/base.py` | 保存公共 Django 配置、根级 template 目录、项目 static 目录与 `STATIC_ROOT`、`AUTH_USER_MODEL`、Django Admin、Sites、allauth Apps、认证 backend、认证行为、项目 allauth form overrides、数字 code 格式、redirect settings、allauth middleware、默认关闭的 Draft 开关、Safety 与导航 section context processors，以及严格的环境变量与 PostgreSQL URL 解析函数。 |
| `config/settings/development.py` | 定义本地 Debug、Console Email、`/media/` local media、环境变量驱动的 PostgreSQL 配置，并明确开启 Draft Risk Notice。 |
| `config/settings/test.py` | 定义关闭 Debug 的自动化测试环境、独立 PostgreSQL test database、in-memory Email、快速 Password hasher 及默认关闭的 Draft Risk Notice。 |
| `config/settings/preview.py` | 继承 Production 安全配置并要求显式的 Draft Risk Notice Boolean 开关；缺少变量时拒绝加载。 |
| `config/settings/production.py` | 定义环境变量驱动的 Production Secret、hosts、PostgreSQL、SMTP、HTTPS 安全设置及 `ManifestStaticFilesStorage`，并强制关闭 Draft Risk Notice；缺少必填值时拒绝加载。 |
| `config/urls.py` | 项目根 URL 配置，开放 `/admin/`，依次接入 core、events、safety、accounts 和 members URLConf，将 `/accounts/` 委托给 `allauth.urls`，注册 403、404 与 500 handlers，并只在 Debug 环境附加 local media patterns。 |
| `config/asgi.py` | 暴露 ASGI application 入口，默认加载 Production settings。 |
| `config/wsgi.py` | 暴露 WSGI application 入口，默认加载 Production settings。 |
| `apps/__init__.py` | 将 `apps` 标记为承载领域 App 的 Python package。 |
| `apps/core/__init__.py` | 将 `core` 标记为 Python package。 |
| `apps/core/apps.py` | 定义 `CoreConfig`，将 `apps.core` 注册为 Django App。 |
| `apps/core/views.py` | 提供查询最多三条已发布 Upcoming Event 的 Home view、无数据库的 About 与 Beginners & Safety views、基于显式 allowlist 和当前 request 构造绝对 URL 的 sitemap view（含 Members 列表、不含个人 detail 或 Events），以及不向模板传递异常详情的 403、404 与 500 handlers。 |
| `apps/core/validators.py` | 提供 Members 与 Events 共用的 HTTPS URL validator（先给出明确的 HTTPS 提示，再执行 `URLValidator`）和 `https://` scheme 小写规范化函数。 |
| `apps/core/urls.py` | 将空路径、`/about/`、`/beginners-safety/` 与 `/sitemap.xml` 映射为具名路由；精确匹配保证其他根级 URL 可继续交给对应 App。 |
| `apps/core/templates/core/base.html` | 定义前台全局 HTML 页面壳、skip link、语义化 landmarks、title、description、robots、Open Graph 与额外 head 扩展区块；加载本地 CSS 与 Alpine.js，并在初始化后恢复 validation error focus。 |
| `apps/core/templates/core/home.html` | 提供正式英文 Home、页面 Metadata、Hero（对辅助技术隐藏的背景照片与指针光照层及其 Alpine 坐标更新、材质标签与等宽 eyebrow、三行金色 H1、介绍、等宽按钮行、右侧响应式 Logo、图纸标题栏）、认证状态分支 CTA、页内新手入口与四张编号功能卡片，以及标题区带 `View all events` 的最多三条 Upcoming Event 预览和 empty state。 |
| `apps/core/templates/core/about.html` | 提供正式英文 About 与页面 Metadata：等宽小标签页头，四个带编号的报告分节（组织目的、以编号功能卡片呈现的活动内容、含补充说明的参与资格、训练方式），以及只向 Anonymous 显示、在页面末尾居中的 Hero 尺寸 `Join`。 |
| `apps/core/templates/core/beginners_safety.html` | 提供正式英文 Beginners & Safety 与页面 Metadata：等宽小标签页头，五个带编号的报告分节（连线编号的入门流程、风险面板、含补充说明的参与前提示、单框规则列表、共同责任）；仅在环境允许时于风险面板内增加 Draft Risk Notice 次级入口，不替代正式 Risk Notice，页面不提供招新按钮。 |
| `templates/account/_page.html` | allauth 页面共用骨架：eyebrow、唯一 H1（`page-title`）、可选 intro 与页面主体。 |
| `templates/account/includes/panel_form.html` | 输出带全部字段、CSRF、redirect 字段和单个提交按钮的 panel 表单，供登录、重置、设置/确认密码与验证码请求页复用。 |
| `templates/account/includes/code_form.html` | Email verification 与 Magic Code 共用的一次性 code 输入、确认与重发按钮。 |
| `templates/account/includes/cancel_sign_in_form.html` | 以 POST logout 放弃当前 code 阶段并返回登录页。 |
| `apps/core/context_processors.py` | 将当前请求解析到的 view name 或 Events namespace 映射为 `nav_section`，供 Header 统一输出 `aria-current="page"`。 |
| `apps/core/templates/core/errors/_error_page.html` | 三个错误页共用的基模板，提供 status code、标题、说明与 Return Home 操作的固定结构。 |
| `apps/core/templates/core/errors/403.html` | 继承错误页基模板，使用共享页面壳呈现中性 Access Denied 状态和 Return Home 操作，保持 HTTP 403。 |
| `apps/core/templates/core/errors/404.html` | 继承错误页基模板，使用共享页面壳呈现中性 Page Not Found 状态和 Return Home 操作，保持 HTTP 404。 |
| `apps/core/templates/core/errors/500.html` | 继承错误页基模板，使用共享页面壳呈现中性 Something Went Wrong 状态和 Return Home 操作，保持 HTTP 500。 |
| `apps/core/templates/core/sitemap.xml` | 输出符合 sitemap XML namespace 的公开 URL 列表；内容只来自 view 的显式 Production 公开页面 allowlist。 |
| `apps/core/templates/core/includes/header.html` | 输出完整文字品牌，为所有访问者提供 Home、About、Beginners & Safety 和 Members，根据认证状态提供 Login、Signup 或 Account，并仅在环境允许时加入 Draft Risk Notice；当前页标识统一读取 `nav_section`，Members 列表与 detail 共用同一标识，以原生 disclosure 和最小 Alpine 初始化实现 desktop/mobile、键盘及无 JavaScript 导航；页面导航紧跟品牌，Anonymous 的 `Join the Club` 使用紧凑金色材质按钮。 |
| `apps/core/templates/core/includes/messages.html` | 将 Django messages 输出到 polite live region，并为错误和非错误反馈提供相应 ARIA role。 |
| `apps/core/templates/core/includes/footer.html` | 提供等宽大写版权行（完整 `NULDL Armwrestling Club` 名称与动态年份）和已批准的 Instagram HTTPS 链接；不公开联系邮箱或未经授权的大学品牌资产。 |
| `apps/core/migrations/__init__.py` | 将 `core.migrations` 标记为 migration package；当前没有 migration。 |
| `apps/accounts/__init__.py` | 将 `accounts` 标记为 Python package。 |
| `apps/accounts/apps.py` | 定义 `AccountsConfig`，将 `apps.accounts` 注册为 Django App。 |
| `apps/accounts/models.py` | 定义 Custom User、专用 USU 审核权限、Email/USU ID 规范化、数字 validator、共享的 USU ID 资格错误文案常量、USU 状态转换、审核字段写入保护及三项数据库约束。 |
| `apps/accounts/selectors.py` | 提供 `is_verified_active_member()`，作为 Members 本人流程与 Events 报名/取消共用的“启用账户且拥有 verified Email”判断。 |
| `apps/accounts/admin.py` | 注册 Custom UserAdmin，提供 USU 审核列表、筛选、搜索、只读角色视图及 Verify/Reject actions，并隔离无权限 Staff。 |
| `apps/accounts/forms.py` | 定义共享 USYD/USU 字段与校验的 `UsuIdentityFields` 基类，以及基于它的 Account 身份更新与 allauth signup forms，另含 Magic Code request 及两类 code confirmation forms；通过字段白名单与既有 service 隔离只读/审核字段，并为 USYD 渐进增强和不回显数字 code 提供 widget attributes。 |
| `apps/accounts/views.py` | 提供登录保护的 Account GET/POST view，固定使用当前 User，查询本人 Email verification status 与 MemberProfile 摘要，并在成功更新后执行 redirect-after-POST。 |
| `apps/accounts/urls.py` | 将项目 Account view 暴露为命名路由 `account`，路径为 `/account/`。 |
| `apps/accounts/templates/accounts/account.html` | 继承全局页面壳，使用三个主卡片显示只读账户、Profile 摘要与发布操作、USYD/USU form、Password change 和 POST logout；使用 Alpine 条件显示 USU ID并保留无 JavaScript 普通 POST。 |
| `templates/includes/forms/form_errors.html` | 输出 form 非字段错误的可聚焦 alert summary，供认证、Account 与 Profile 编辑模板复用。 |
| `templates/includes/forms/field.html` | 通过 Django `as_field_group` 输出单个字段及其 label、help text、error 与 ARIA 关联。 |
| `templates/includes/forms/form_fields.html` | 组合 form-level error 与全部 visible/hidden fields，减少认证模板间的字段呈现差异。 |
| `apps/accounts/templates/accounts/includes/usyd_fields.html` | 输出 Signup 与 Account 共用的 USYD checkbox 和条件显示的 USU ID 字段；Alpine state 由外层 form 声明。 |
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
| `apps/members/models.py` | 定义 MemberProfile、字段 choices、规范化与验证（HTTPS 规则来自 `apps/core/validators.py`）、未指定时返回 `None` 的公开经验与惯用手 properties、管理员分配的唯一正整数 Researcher 编号及其 `Researcher 07` 显示属性、Avatar 大小/扩展名/MIME/真实格式检查、已提交 Avatar 重复校验时的安全 reopen/close、PostgreSQL 约束，以及只返回可公开 Profile 的 queryset。 |
| `apps/members/services.py` | 提供 Email 确认使用的幂等 Profile 创建入口、协调 Avatar storage 生命周期的 Profile 保存入口，以及使用 row lock 幂等更新本人发布状态的 service。 |
| `apps/members/signals.py` | 接收 allauth 官方 `email_confirmed` signal，并在 Email 验证成功后通过 service 确保 MemberProfile 存在。 |
| `apps/members/forms.py` | 定义七个会员可写资料字段、非 Model Avatar 删除控制、上传/删除冲突检查、Display name 重复检查和 Instagram Username 清理；隔离发布、管理员字段、User 及系统时间戳。 |
| `apps/members/views.py` | 提供只消费公开 queryset 的 Members 目录与 Username detail，以及登录保护且要求启用账户与 verified Email 的本人 Profile 编辑、Preview、Publish confirmation 和 Unpublish confirmation；本人流程固定按当前 User 查询对象。 |
| `apps/members/urls.py` | 暴露公开 `members:list`、`members:detail` 及本人 Profile edit、preview、publish 和 unpublish 命名路由。 |
| `apps/members/templates/members/member_list.html` | 呈现等宽小标签页头与公开 Members 网格卡片：Avatar/fallback、已分配时位于名称上方的 Researcher 金色标签、覆盖整张卡片的公开名称详情链接、非默认经验与惯用手资料格，以及没有公开 Profile 时的 empty state；不输出 detail-only 或敏感字段。 |
| `apps/members/templates/members/member_detail.html` | 使用普通公开 metadata/robots 与共享字段组件呈现单个公开 Profile，顶部提供等宽 `← Back to members` 返回链接。 |
| `apps/members/templates/members/profile_edit.html` | 使用全局页面壳呈现资料字段、当前方形 Avatar、删除控制、metadata 风险提示、CSRF、multipart、普通 POST 和 Preview 入口，并明确保存不会改变发布状态。 |
| `apps/members/templates/members/profile_preview.html` | 呈现仅本人可见的公开效果 Preview、当前隐藏提示及 Edit、Publish 或 Unpublish 操作入口。 |
| `apps/members/templates/members/profile_publish_confirm.html` | 列出全部公开字段（含已分配的 Researcher 编号或其未分配说明）、Username detail path、名称回退和 Avatar metadata 风险，并通过 CSRF POST 确认 Publish。 |
| `apps/members/templates/members/profile_unpublish_confirm.html` | 说明 Unpublish 影响并通过 CSRF POST 确认取消发布，不删除已保存资料。 |
| `apps/members/templates/members/includes/public_avatar.html` | 按调用方 BEM block 输出公开 Avatar 或装饰性首字母 fallback，供 Members 卡片与公开字段组件复用。 |
| `apps/members/templates/members/includes/profile_publication_action.html` | 根据本人 Profile 发布状态输出 Publish 或 Unpublish 入口，供 Account 与 Preview 复用。 |
| `apps/members/templates/members/includes/profile_public_fields.html` | 集中公开字段顺序和展示边界，供本人 Preview 与公开 detail 复用：信息面板（Avatar、`Member profile` 与已分配时的 Researcher 标签、名称、`@username`、资料格）与只在有内容时输出、编号连续的 Bio/Links 报告分节；按页面语义输出唯一 H1 + H2 分节或 H2 + H3 分节。 |
| `apps/members/templates/members/includes/profile_hidden_notice.html` | 在本人资料流程中输出不泄露管理员或后台信息的中性隐藏提示。 |
| `apps/members/admin.py` | 注册 MemberProfile 后台模型，依赖标准 change 权限提供列表、筛选和搜索；列表含可排序的 Researcher 编号列；change form 只允许维护隐藏状态、Executive role 与 Researcher 编号，会员自述、User、发布状态和时间戳只读，并关闭新增与删除入口。 |
| `apps/members/migrations/__init__.py` | 将 `members.migrations` 标记为 migration package。 |
| `apps/members/migrations/0001_initial.py` | 创建 MemberProfile 全部字段、One-to-one User 关系，以及显示名规范化、忽略大小写唯一和 HTTPS 社交链接数据库约束。 |
| `apps/members/migrations/0002_memberprofile_researcher_number.py` | 为 MemberProfile 增加可空、唯一的 `researcher_number`，并建立“为空或不小于 1”的数据库检查约束（Visual Refresh V14）。 |
| `apps/events/__init__.py` | 将 `events` 标记为 Python package。 |
| `apps/events/apps.py` | 定义 `EventsConfig`，将 `apps.events` 注册为 Django App。 |
| `apps/events/models.py` | 定义 Event、公开 queryset、共享的 Sydney 当地零点计算与 Upcoming/Past 分类、时间与地图 URL 验证（HTTPS 规则来自 `apps/core/validators.py`）、页面层报名/取消开放判断，以及 EventRegistration、确认记录与数据库约束。 |
| `apps/events/services.py` | 提供合成测试环境中的事务化报名与幂等取消入口；验证会员和活动状态，报名时确认当前 Risk Notice，取消时保留原确认历史。 |
| `apps/events/admin.py` | 定义 Event 后台表单与标准权限下的管理界面，并以 `view_eventregistration` 权限提供禁止新增、修改和删除的报名历史名单。 |
| `apps/events/forms.py` | 定义最小报名与取消确认表单；报名只接收当前 Risk Notice ID 和明确同意，取消只接收明确确认，不重复收集账户身份资料。 |
| `apps/events/views.py` | 提供公开 Upcoming/Past 列表、已发布 Event 详情及受登录和 verified Email 保护的报名/取消确认；协调普通 POST、HTMX 局部响应、旧版本重试与关闭状态拒绝；单次请求内复用会员资格、当前 Notice 与有效报名查询结果。 |
| `apps/events/urls.py` | 将 `/events/`、`/events/<slug>/`、`/events/<slug>/register/` 与 `/events/<slug>/cancel/` 暴露为具名路由。 |
| `apps/events/templates/events/event_list.html` | 呈现等宽标签页头、Upcoming/Past 标签页式筛选链接、纵向排列的共享 Event cards 和虚线框无结果状态；不提供 `All` 或报名操作。 |
| `apps/events/templates/events/event_detail.html` | 呈现顶部返回链接、居中页头（`Club activity` · 状态标签与 H1）、通栏信息面板（Sydney 时区信息格、`Location` 行内 `(View in Map)` 安全链接、共享报名区域）与居中说明栏，并只在本页加载本地 HTMX 渐进增强。 |
| `apps/events/templates/events/event_registration_confirm.html` | 提供禁用 JavaScript 或直接访问时的完整 Risk Notice 确认页，并保留返回 Event 的普通链接。 |
| `apps/events/templates/events/includes/registration_form.html` | 在暖黑底细边框区域中直接呈现当前 Risk Notice 的完整正文及等宽版本行，并集中错误、CSRF 与确认按钮，供 dialog 和完整确认页复用；不添加重复正文 banner。 |
| `apps/events/templates/events/event_cancellation_confirm.html` | 提供禁用 JavaScript 或直接访问时的完整取消确认页，并保留返回 Event 的普通链接。 |
| `apps/events/templates/events/includes/confirm_page.html` | 两张整页确认模板共用的正文结构，以等宽标签页头、单行活动信息格及传入的标题、heading id 与表单 include 呈现，并提供返回 Event 的普通链接。 |
| `apps/events/templates/events/includes/cancellation_form.html` | 集中取消说明、错误、CSRF 与确认按钮，供 cancellation dialog 和完整确认页复用。 |
| `apps/events/templates/events/includes/registration_panel.html` | 根据 Past、已报名、可报名、Anonymous 和不可操作状态呈现唯一报名区域，包含报名/取消 Alpine dialogs 与 HTMX target；服务端通过 `data-open-dialog`/`data-focus-status` 声明需要打开的 dialog 或聚焦的状态元素；状态以不填充的状态标签呈现，报名 dialog 以 `Risk Notice` 为标题并以 `Confirm registration` 为其上方的大号等宽标签。 |
| `apps/events/templates/events/includes/event_card.html` | 集中 Home 与 Events 列表共用的网格活动卡片：对辅助技术隐藏的日期块、标题链接、以 Sydney 时区显示的 `Date`/`Time`（跨天为 `Starts`/`Ends`）与 `Location` 信息行、根据 Past 与共享当前 Notice 可用性显示的状态标签（Past 卡片另加 `event-card--past` 弱化日期），以及可访问名称含标题的 `View details` 按钮。 |
| `apps/events/migrations/__init__.py` | 将 `events.migrations` 标记为 migration package。 |
| `apps/events/migrations/0001_initial.py` | 创建 Event 表及其数据库约束。 |
| `apps/events/migrations/0002_eventregistration.py` | 创建 EventRegistration 表、关系和数据库约束。 |
| `tests/test_event_model_admin.py` | 验证 Event 默认值、公开查询、字段约束、本地日期判断和后台权限。 |
| `tests/test_event_registration.py` | 验证报名与取消状态、确认版本与时间、历史保留、数据库约束、资格、关闭条件，以及并发报名、并发取消和版本切换行为。 |
| `tests/test_event_registration_admin.py` | 验证报名名单的内置查看权限、角色隔离、只读防伪造、有效/取消/重新报名历史、Risk Notice 版本追溯及公开页面隐私。 |
| `tests/test_event_registration_pages.py` | 验证报名/取消详情、确认正文、普通 POST、HTMX、幂等、旧版本重试、重新报名、资格、不可操作状态、跨会员报名隐私，以及 `Registered` 为带 `role="status"` 的状态标签。 |
| `tests/test_event_registration_browser.py` | 建立两个合成 verified member Session，并调用 Playwright 场景验证 JavaScript 与无 JavaScript 下的报名、取消和重新报名路径。 |
| `tests/test_event_pages.py` | 验证 Sydney 零点下 Upcoming/Past 分类、公开性、稳定排序、无效参数回退、Home 三条限制、详情 404、HTML escaping、安全地图链接、无表单边界、活动卡片状态标签、Past 卡片标记、筛选标签页当前项、详情页返回链接/页头状态/信息面板顺序及 `Location` 行内地图链接。 |
| `tests/test_event_pages_browser.py` | 以真实测试站点建立合成已发布 Event，并调用 Events Playwright 场景。 |
| `tests/browser/event-pages.mjs` | 在 desktop、mobile、200% 内容放大和禁用 JavaScript 场景验证 Home 到 Events 列表/详情的导航、Upcoming/Past、`View all events` 位于卡片上方、状态标签与详情按钮等宽且不填充、`(View in Map)` 地图链接、语义结构、键盘 Focus、触控目标、内容重排、page error 与同源网络边界。 |
| `tests/browser/event-registration.mjs` | 在真实 Chromium 中验证报名与取消 dialogs、Risk Notice、HTMX 状态更新、重新报名、mobile、200% 内容放大、无 JavaScript 完整确认页、Focus、触控目标、page error 与同源网络边界。 |
| `apps/safety/__init__.py` | 将 `safety` 标记为 Python package。 |
| `apps/safety/apps.py` | 定义 `SafetyConfig`，将 `apps.safety` 注册为 Django App。 |
| `apps/safety/context_processors.py` | 将当前环境是否允许 Draft Risk Notice 作为单一 Boolean 提供给全局 RequestContext，供 Header 与页面 CTA 同步控制可发现性。 |
| `apps/safety/urls.py` | 将 `/risk-notice/` 映射为命名路由 `safety:risk_notice`。 |
| `apps/safety/views.py` | 在 Draft 开关开启时渲染静态 Risk Notice；关闭时抛出 404，全程不访问数据库。 |
| `apps/safety/templates/safety/risk_notice.html` | 逐字呈现获准 Draft 正文、重复 acknowledgement、Draft banner 和 `noindex, nofollow`；不提供确认或报名表单。 |
| `apps/safety/models.py` | 定义 RiskNoticeVersion、唯一版本标识、状态时间和单一当前版本约束。 |
| `apps/safety/services.py` | 提供受环境开关保护的当前 Notice 查询，并以事务和行锁切换当前版本；Home、Events 列表与详情页共用该查询边界。 |
| `apps/safety/admin.py` | 管理合成版本创建、权限、只读历史与单选激活操作。 |
| `apps/safety/migrations/__init__.py` | 将 `safety.migrations` 标记为 migration package。 |
| `apps/safety/migrations/0001_initial.py` | 创建 Risk Notice 版本表与数据库约束。 |
| `tests/test_risk_notice_versions.py` | 验证版本切换、旧正文保留、唯一约束、环境隔离、后台权限和合成文本标记。 |
| `tests/__init__.py` | 将顶层 `tests` 标记为 Python package。 |
| `tests/conftest.py` | 提供全套测试自动启用的外部网络隔离，只允许 loopback、Django test host 和当前数据库 host，并对外部 DNS/socket 连接立即失败；另提供共享 `verified_member` fixture。 |
| `tests/factories.py` | 统一建立合成 User、可选 EmailAddress 验证状态、USU 审核权限及 MemberProfile，供各测试以显式参数声明差异。 |
| `tests/browser_runner.py` | 以 UTF-8 捕获输出启动 `tests/browser/` 下的 Node Playwright 场景，传入 live server URL 与额外环境变量，并在失败时附带完整输出。 |
| `tests/privacy.py` | 提供公开页面私有值扫描断言与 Email/USU ID/审核状态集合，一次报告全部泄露值。 |
| `tests/test_project_scaffold.py` | 验证每个 `PROJECT_APPS` 条目可导入，且 AppConfig 名称与所在包路径一致。 |
| `tests/test_database_settings.py` | 验证 PostgreSQL URL 解析、encoded credentials、连接 options、非 PostgreSQL 拒绝和必填变量失败行为。 |
| `tests/test_environment_settings.py` | 验证 Development、Test、Production 的环境职责、Production 安全设置、manifest static storage 和缺少 Secret 时的安全失败。 |
| `tests/test_user_model.py` | 验证 Custom User 创建、标准权限字段、身份与审核默认值、Email 必填与唯一，以及审核人 Self ForeignKey 的 `SET_NULL` 行为。 |
| `tests/test_user_identity_rules.py` | 验证 Email 和数字型 USU ID 规范化、全部 USU 状态转换、专用审核权限、前导零保留及数据库对直接写入的约束。 |
| `tests/test_member_profile.py` | 验证 MemberProfile schema、默认值、幂等创建、字段规范化、上传安全、公开查询、会员字段边界、Admin 配置，以及 Researcher 编号的显示格式、空值共存与 model/数据库两层的重复和非正数拒绝。 |
| `tests/test_member_profile_admin.py` | 验证 MemberProfile Admin 的四类角色权限、标准 change permission、只读字段、防伪造、Hide/Unhide、Executive role、Researcher 编号的分配/修改/清除、无效与重复输入错误及列表排序、Django LogEntry，以及隐藏后的公开与本人流程边界。 |
| `tests/test_profile_edit.py` | 验证 Profile 编辑访问资格、本人对象所有权、允许字段、Display name/Bio/Instagram/HTTPS 验证、伪造字段隔离、状态保持、保存后返回 Account 和普通 POST。 |
| `tests/test_profile_publication.py` | 验证本人 Preview、访问资格、所有权、GET 无副作用、Publish/Unpublish 幂等 POST、CSRF、固定 redirect、管理员隐藏优先级、公开说明（含 Researcher 编号已分配与未分配两种文字）、Preview 共用信息面板与 H1 → H2 → H3 层级，以及敏感字段隔离。 |
| `tests/test_member_directory.py` | 验证公开目录 URL、公开 queryset、稳定排序、名称与 Avatar fallback、卡片详情链接、字段白名单、默认值隐藏、页头小标签、Researcher 标签只在已分配时位于名称之前且不泄露非公开资料号码、empty state、导航状态及敏感字段隔离。 |
| `tests/test_member_detail.py` | 验证 Username 精确 URL、普通 robots、公开字段、安全外链、HTML escaping、默认值隐藏、返回链接、H1/H2 层级、kicker 中的 Researcher 标签、分节编号连续与空分节省略、敏感字段隔离及所有不可见状态的统一 404 正文。 |
| `tests/test_member_directory_browser.py` | 以真实测试站点调用 Members 目录与详情 Playwright 场景，并建立包含公开 Bio、社交链接与一个 Researcher 编号的合成已发布资料；固定卡片 Avatar 与摘要布局。 |
| `tests/test_avatar_lifecycle.py` | 使用隔离临时 media 验证 Avatar 原始字节、格式与大小边界、替换、主动删除、保留现有 Avatar 的重复校验、失败保护、孤立文件清理、页面提示和 Development/Production media URL 边界。 |
| `tests/test_avatar_browser.py` | 以真实测试站点和临时 media 调用 Avatar Playwright 场景，并通过 authenticated Session 验证本人编辑页。 |
| `tests/profile_media_urls.py` | 只为 Avatar 浏览器测试附加临时 media 文件服务；不进入 Production URLConf。 |
| `tests/test_authentication_configuration.py` | 验证 allauth Apps、backend、认证 settings、邮箱验证码与 Magic Code 生命周期配置、默认 rate limits、redirects、必需 URL 和排除功能的路由边界。 |
| `tests/test_signup_form.py` | 验证 signup 字段顺序与必填性、Email/Username 冲突、enumeration prevention、USYD/USU ID 服务端规则、数字规范化及无 JavaScript 的普通 POST 与 verification redirect。 |
| `tests/test_email_verification.py` | 验证待确认状态、正确、错误、过期与重复验证码、重发与即时限流、幂等 Profile 创建，以及日志不泄露完整 Email 或验证码。 |
| `tests/test_password_authentication.py` | 验证密码登录、通用凭据错误、未验证与停用账户、站内及外部 redirect、Password reset 枚举保护与密码更新，以及 GET/POST logout 边界。 |
| `tests/test_magic_code_authentication.py` | 验证 Magic Code 的有效、错误、过期、单次使用、重发、请求限制、账户资格、enumeration prevention、密码登录独立性及敏感日志边界。 |
| `tests/test_account_page.py` | 验证 Account 访问控制、本人数据隔离、Email verification、Profile 摘要与状态操作、三卡片结构、USYD/USU ID 状态转换、只读字段防伪造、Password change 和 POST logout。 |
| `tests/test_user_admin.py` | 验证 UserAdmin 配置、四类角色权限差异、Verify/Reject、直接编辑防护、重新提交、审核人停用及前台敏感信息边界。 |
| `tests/test_global_templates.py` | 验证全局页面壳、metadata/head blocks、完整品牌、Anonymous/Member Header、当前导航、已实施公开页面链接、无失效链接、skip link、landmarks、唯一 H1/title、消息播报、本地 Alpine 和普通导航/form 基线。 |
| `tests/test_public_foundation_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 21 公开页面 Playwright scenario。 |
| `tests/test_home_page.py` | 验证 Home 获准英文内容与 Metadata、Hero 三行标题、标签与 eyebrow、图纸标题栏、背景彩蛋层对辅助技术隐藏且照片只由 CSS 加载、动态 Upcoming Events 区域、empty state、Events 列表入口、无报名表单、响应式 Logo 引用、受限 Branding 边界及 Anonymous/Member CTA。 |
| `tests/test_home_images.py` | 参数化验证 Logo、金色材质（含按钮变体）与 Hero 照片（不透明源图、RGB 生成物）源文件的精确 hash、格式、尺寸与模式，以及全部 WebP 生成物的尺寸、格式、透明度、无 metadata、压缩和可重复性。 |
| `tests/test_home_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 22 Home Playwright scenario。 |
| `tests/test_public_information_pages.py` | 验证 About 与 Beginners & Safety 的 URL、模板、Metadata、获准文案与 Heading 顺序（含 About 功能卡片 H3）、About 页头小标签/功能卡片/报告分节、Beginners & Safety 页头小标签/报告分节/流程与规则列表、受限内容、Header 当前页、Anonymous/Member CTA 和未实施功能边界。 |
| `tests/test_public_information_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Step 23 公开信息页 Playwright scenario。 |
| `tests/test_draft_risk_notice.py` | 验证 Draft 环境矩阵、默认关闭、Production 强制关闭、Preview 显式开关、404、逐字正文、重复 acknowledgement、robots、条件链接（Beginners & Safety 的入口位于风险面板内）、无表单和零数据库查询。 |
| `tests/test_draft_risk_notice_browser.py` | 以开启 Draft 的 Django `StaticLiveServerTestCase` 调用 Step 24 Playwright scenario。 |
| `tests/error_urls.py` | 提供只在测试中使用的合成 403/500 endpoints，并复用项目 URL 与 handlers 验证真实 Django 错误分派；不进入生产 URLConf。 |
| `tests/test_error_pages.py` | 在 `DEBUG=False` 下验证真实 403、404、500 handlers 的状态码、模板、title、唯一 H1、Home link、CSS 和敏感内容隔离。 |
| `tests/test_error_pages_browser.py` | 以隔离错误 URLConf 启动真实测试站点并调用 Step 25 Playwright scenario。 |
| `tests/test_phase2_accessibility_browser.py` | 在 `DEBUG=False` 下开启 Draft 并复用隔离错误 URLConf，以真实静态 live server 调用 Step 27 统一 accessibility Playwright scenario。 |
| `tests/test_public_metadata_sitemap_footer.py` | 验证三个正式宣传页的准确 Metadata/Open Graph、环境派生 URL、无硬编码 canonical host、含 Members 列表且排除个人 detail 与 Draft 的 sitemap XML 精确 allowlist，以及 Footer 的获准 Instagram 与禁止内容边界。 |
| `tests/test_authentication_templates.py` | 验证项目认证模板覆盖、共享页面壳、Alpine/no-JavaScript 边界、ARIA error 关联、数字 code attributes 及 Password/code 不回显。 |
| `tests/test_static_assets.py` | 验证 static/template settings、vendor manifest 与 `package.json` 运行依赖一致及 SHA-256、无第三方 CDN、构建产物中的 design tokens、本地字体与 focus/reduced-motion、从 `@theme` 读取的关键颜色与金色材质 contrast，材质图作为大号展示文字时的最暗像素 contrast、按钮材质每个像素对近黑文字的 contrast，以及构建 CSS 引用的图片均存在。 |
| `tests/test_authentication_browser.py` | 以 Django `StaticLiveServerTestCase` 启动真实测试站点并调用 Node Playwright；显式按 UTF-8 捕获输出，失败时保留真实浏览器诊断。 |
| `tests/test_phase1_browser_flows.py` | 编排 Phase 1 Signup/verification、Password login/Account update、Magic Code 和 Admin USU review 浏览器流程，并从隔离的 Playwright storage state 读取服务端 Session code 以继续真实流程。 |
| `tests/test_acceptance.py` | 以参数化方式验证四个阶段验收入口的完整命令序列、smoke 失败时输出 server log 并停止 server、缺少 uv 时失败、terminate/kill 清理、脚本直接执行时的导入，以及 README 列出各阶段验收与门禁命令。 |
| `tests/test_phase3_accessibility_browser.py` | 以真实静态 live server、合成已验证账户和隔离临时 media 调用 Phase 3 统一 Playwright 场景，并分别验证完整资料流程、公开 empty state 和临时目录清理。 |
| `tests/test_quality_security.py` | 验证敏感文件及高置信凭据扫描、测试外部网络阻断、认证与身份日志隐私、Anonymous 页面和 Members 公开响应的私有字段隔离、Phase 3 不收集年龄/监护人资料，以及 HttpOnly Session cookie。 |
| `tests/test_quality_gate.py` | 验证统一门禁不会吞掉子命令失败，非零退出会作为验收失败传播。 |
| `tests/browser/browser-support.mjs` | 为 Playwright scenarios 提供必填环境变量读取、只允许当前 live-server origin 的 browser context、外部请求断言，以及共享的会话 cookie、溢出、页面边界、landmark、可见内容、触控目标与 Focus 断言。 |
| `tests/browser/authentication-ui.mjs` | 在 Chromium 中执行小屏、键盘、Alpine、整串 code 输入、无 JavaScript fallback 和服务端错误焦点的端到端断言，并复用同源网络隔离。 |
| `tests/browser/phase1-core-flows.mjs` | 在 Chromium 中执行 Phase 1 注册验证、两种登录、账户更新、登出和 Admin USU review 操作，所有场景均使用同源网络限制。 |
| `tests/browser/development-server-smoke.mjs` | 对真实 Development server 执行 desktop/mobile Home、Signup、Login、Account redirect、CSS、布局、page error、同源请求和 Branding smoke checks。 |
| `tests/browser/phase2-development-smoke.mjs` | 对真实 Development server 执行 Phase 2 desktop/mobile 正式页面、Draft 分支、错误页、认证入口、CSS、布局、page error 和同源请求 smoke checks。 |
| `tests/browser/phase3-development-smoke.mjs` | 对真实 Development server 执行 Phase 3 desktop/mobile Members、Anonymous Profile redirect、不可见详情、Development media、CSS、布局、page error 和同源请求 smoke checks。 |
| `tests/browser/phase4-development-smoke.mjs` | 对真实 Development server 执行 Phase 4 desktop/tablet/mobile Home、Events、详情、导航、报名状态、CSS、布局、page error 和同源请求 smoke checks。 |
| `scripts/accept_phase_4.py` | Step 45 验收入口：以共享项目门禁依次运行 Phase 2–4 Development smoke。 |
| `tests/browser/public-foundation.mjs` | 在 Chromium 中验证 Step 21 desktop/mobile Header、键盘 Focus、原生菜单开关、无 JavaScript 导航、布局和同源网络边界。 |
| `tests/browser/home-page.mjs` | 在 Chromium 中验证 Step 22 Home 的 desktop/mobile/no-JavaScript 内容、CTA、Logo 加载与比例、主内容内标题与按钮可见性、desktop Hero 按钮等宽等高、标题三行且第二行决定栏宽、Logo 在右侧且 300–500px、mobile Logo 位于标题下方、desktop 背景照片加载与指针光照点亮/跟随/熄灭且不遮挡按钮、mobile 与宽屏触屏不加载照片、Header/页面/Footer 共享 80rem 宽度、功能卡片标题 22px、无水平溢出和同源网络边界。 |
| `tests/browser/public-information.mjs` | 在 Chromium 中验证 About 与 Beginners & Safety 的 desktop/mobile、键盘、200% content zoom、无 JavaScript、CTA、内容可见性、无水平溢出和同源网络边界，以及 About 报告分节两列布局与正文到达右缘、功能卡片两列、`Join` 尺寸与居中、手机上分节标题在正文之上，以及 Beginners & Safety 流程方块同列且有连接线、规则 5 行、风险面板位于分节标题右侧。 |
| `tests/browser/draft-risk-notice.mjs` | 在 Chromium 中验证 Step 24 Draft Risk Notice 的条件入口（风险面板内左对齐、位于正文下方）、banner、robots、desktop/mobile、键盘、无 JavaScript、内容可见性、无水平溢出和同源网络边界。 |
| `tests/browser/error-pages.mjs` | 在 Chromium 中验证 Step 25 三个错误状态的正确响应、desktop/mobile、项目 CSS、键盘 Focus、无 JavaScript、无水平溢出和同源网络边界。 |
| `tests/browser/phase2-accessibility.mjs` | 在 Chromium 中统一验证全部 Phase 2 公开与错误页面的语义、Heading、link name、Focus、键盘顺序、触控目标、reflow、200% 放大、对比度、reduced motion、替代文本、无 JavaScript、错误与同源网络边界；导航顺序包含已上线的 Members 入口；按钮对比度读取 `::after`/`::before` 填充层，覆盖主按钮、描边按钮与 Header 按钮；Home 对比度覆盖 Hero 介绍、材质标签、eyebrow 与图纸标题栏（光照未点亮状态），以及功能卡片编号、正文与活动空状态。 |
| `tests/browser/avatar-edit.mjs` | 在 Chromium desktop/mobile 中验证当前 Avatar 加载、方形裁切、metadata 提示、删除控件、键盘 Focus、上传错误保持及同源网络边界。 |
| `tests/browser/member-directory.mjs` | 在 Chromium desktop/mobile/no-JavaScript 场景验证公开 Members cards、左侧紧凑 Avatar、右侧摘要、名称正上方的 Researcher 标签、桌面并排卡片、整卡 Focus 外框与整卡点击、稳定顺序、详情导航、详情信息面板桌面左右/手机上下布局与名称上方的标签、robots、安全外链、Focus、无溢出、page error 和同源网络边界。 |
| `tests/browser/phase3-accessibility.mjs` | 在 Chromium 中统一验证 Account/Profile/Members 全流程的 desktop/mobile、200% content zoom、键盘 Focus、24px 触控目标、表单错误关联、连续长内容重排、禁用 JavaScript 提交与返回 Account、reduced motion、page error 和同源网络边界。 |
| `memory-bank/design_document.md` | 产品与体验设计的权威来源，定义用户、页面、流程、权限、业务规则、隐私、Accessibility、内容和 Branding 边界。 |
| `memory-bank/tech_stack.md` | 技术决策的权威来源，定义框架、版本策略、单体架构、环境、安全、部署和运维边界。 |
| `memory-bank/implementation.md` | 代码实施顺序的权威来源，将当前 Phase 拆分为一次只执行一个的可验证步骤，并规定模型、配置、测试和 migration 要求。 |
| `memory-bank/项目开发_Roadmap.md` | 阶段、依赖、交付物、退出门槛、状态和外部阻塞事项的权威来源。 |
| `memory-bank/progress.md` | 记录实际完成的步骤、验证结果、仓库状态和遗留事项，供后续开发者继续执行。 |
| `memory-bank/architecture.md` | 记录已经实际实施并验证的架构、文件职责及重要技术理由；不把尚未实现的计划描述为现状。 |
| `memory-bank/cleanup_audit.md` | 记录 Phase 1–4 后的代码清理审计清单，包括每条问题的位置、建议、风险、受影响测试、优先级与分批计划，以及各批次的执行更正。 |

## 五、架构维护原则

- 产品行为冲突时以 `design_document.md` 为准。
- 技术选型冲突时以 `tech_stack.md` 为准。
- 实施顺序与代码级要求以 `implementation.md` 为准。
- 阶段和外部依赖以 `项目开发_Roadmap.md` 为准。
- 本文档只记录真实存在且已经验证的结构；后续新增文件时补充其职责，避免提前描述尚未建立的组件。
- 当前 `memory-bank/implementation.md` 含有 Step 1 执行前已存在的未提交修改，后续工作不得覆盖或回退该修改。
