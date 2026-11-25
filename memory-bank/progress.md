# NULDL 开发进度

**最后更新：** 2026 年 11 月 14 日
**当前阶段：** Phase 4 — 活动、Risk Notice 与报名
**当前步骤：** Step 45 — Phase 4 质量门禁与阶段验收
**状态：** Phase 4 已通过自动化与人工验收，Phase 5 已取消，Phase 6 尚未开始

## Step 1 — 建立执行基线

### 已完成

- 完整读取 `architecture.md`、`design_document.md`、`tech_stack.md`、`implementation.md` 和 `项目开发_Roadmap.md`。
- 检查仓库根目录、现有文件、Git 分支、HEAD、工作树和暂存区状态。
- 确认仓库仍处于初始文档阶段，尚未建立 Django 项目、依赖元数据、数据库配置或测试套件。
- 确认 `architecture.md` 与本文件在执行前均为空。
- 确认现有待定事项均已在项目文档中明确标识，不会在后续实施中被隐式补全。

### 仓库基线

- 分支：`main`，跟踪 `origin/main`。
- 基线提交：`99246b2`（`docs: add repository guidelines and project memory bank`）。
- 已跟踪的项目内容包括 `.gitignore`、`AGENTS.md`、`README.md` 及 `memory-bank/` 中的六份项目文档。
- 工作树存在一项执行前已有的未提交修改：`memory-bank/implementation.md`。
- 暂存区无修改。
- 未发现 Django 源码、Python 或 npm 依赖文件、migration、测试、数据库文件、`.env`、Secret、真实会员数据或用户上传文件。

### 文档一致性与待定事项

- 未发现会阻塞 Step 1 或 Phase 1 起步的文档冲突。
- Risk Notice 最终文本、未成年人未来措施、University Branding、Logo、地点资料、正式 hosting/SMTP/media/monitoring/map provider、数据保留规则和中文版本仍待项目负责人或相关方确认。
- 上述事项不得由开发者自行决定；按现有 Roadmap，它们不阻塞 Step 2 的依赖元数据工作。
- `memory-bank/implementation.md` 的未提交修改视为项目负责人现有工作，后续修改必须保留。

### 验证结果

- 所有必读文档均可访问并已完整读取。
- 文件清单和 Git 状态已通过只读命令核对。
- 当前没有可运行的自动化测试；Step 1 的验证仅涉及文档可访问性、仓库状态和阻塞项识别。
- 项目负责人已确认写入本基线记录。

### 下一步门槛

Step 1 已通过项目负责人确认，Step 2 已获授权并完成。

## Step 2 — 建立 Python 与前端依赖元数据

### 已完成

- 新建 `pyproject.toml` 和 `uv.lock`，使用 `uv` 管理 Python 依赖及锁定结果。
- 新建 `package.json` 和 `package-lock.json`，使用 npm 管理前端依赖及锁定结果。
- 将项目 Python 版本限定为 Python 3.13.x，并在本地安装和验证 Python 3.13.17。
- 安装并验证 `uv 0.13.5`；本机 `uv` 可以发现受管的 Python 3.13.17。
- Python 运行依赖精确锁定为 Django 5.2.18、django-allauth 65.20.1、Pillow 13.0.0 和 Psycopg 3.3.6。
- Python 开发依赖精确锁定为 pytest 9.1.1、pytest-django 4.14.0、coverage 7.16.2 和 Ruff 0.17.1。
- 前端依赖精确锁定为 HTMX 2.0.11、Alpine.js 3.17.5、MapLibre GL JS 6.15.0、Tailwind CSS 4.3.0、Tailwind CLI 4.3.0 和 Playwright 1.64.1。
- 将 Tailwind CSS 与 Tailwind CLI 对齐到同一补丁版本，并通过安全的传递依赖升级消除 npm audit 报告的问题。

### 验证结果

- `python -m uv sync --locked` 从锁文件成功建立 `.venv` 并安装 17 个包。
- Python 3.13.17、Django 5.2.18、pytest 9.1.1、Ruff 0.17.1 和 coverage 7.16.2 均可调用。
- `npm.cmd ci` 从锁文件成功安装 59 个包，审计结果为 `0 vulnerabilities`。
- npm 顶层依赖版本与 `package.json` 一致。
- Tailwind CLI 4.3.0 和 Playwright 1.64.1 均可调用。
- HTMX、Alpine.js 和 MapLibre GL JS 均可从本地 `node_modules` 解析。
- MapLibre GL JS 6.15.0 仅提供 ESM 根导出；已使用 `import.meta.resolve` 验证其入口，CommonJS `require.resolve` 不适用于该包。
- `uv.lock` 与 `pyproject.toml` 一致，`git diff --check` 未发现新增格式错误。

### 执行说明

- 首次 `npm.cmd ci` 在依赖下载期间收到 `SIGINT`，日志未显示依赖、网络响应或完整性错误；重新执行后成功。
- `.venv` 与 `node_modules` 均为本地生成目录；`.venv` 已由现有 `.gitignore` 排除，`node_modules` 当前仍显示为未跟踪目录且不得提交，正式 ignore 规则按实施计划在 Step 4 处理。
- 未创建 Django 项目、App、settings、数据库配置或业务代码。

### 下一步门槛

Step 2 已通过项目负责人验证，Step 3 已获授权并完成。

## Step 3 — 创建 Django 项目骨架

### 已完成

- 创建 `manage.py` 以及 `config` Python package，并建立根 URL、ASGI、WSGI 和临时 scaffold settings。
- 创建 `apps` Python package，并建立 `core`、`accounts`、`members`、`events`、`locations` 和 `safety` 六个约定的业务 App。
- 为每个业务 App 创建可导入的 AppConfig 和空 migration package；尚未创建业务模型、视图、URL 或 Admin 实现。
- 在 `INSTALLED_APPS` 中注册六个项目 App，并将 Django 内置组件与项目 App 分组声明。
- 创建 `tests/test_project_scaffold.py`，验证全部 AppConfig 可导入、名称正确且没有注册额外业务 App。
- 使用 Django dummy database backend 作为 Step 3 的临时配置，未引入 SQLite；PostgreSQL 连接仍保留给 Step 4。
- 使用明确标记为 scaffold 专用的公开占位 `SECRET_KEY`；分环境 settings 和正式 Secret 管理仍保留给 Step 5。

### 验证结果

- `python -m uv run pytest tests/test_project_scaffold.py` 通过，共执行 2 个测试。
- `python -m uv run python manage.py check` 通过，Django 报告 `System check identified no issues (0 silenced)`。
- 首次 Ruff 检查发现测试文件 import 区域存在一个排版问题；删除一行多余空行后重新验证通过。
- `python -m uv run ruff check manage.py config apps tests` 最终报告 `All checks passed!`。
- 六个项目 App 的目录和注册名称与 `implementation.md` 一致，没有创建额外业务 App。

### 当前边界

- 当前项目可以加载 Django 配置和全部 App，但尚未连接实际数据库。
- 当前没有业务模型或业务 migration，也未执行 `migrate`，避免在 Step 6 自定义 User 建立前生成项目业务 migration。
- 尚未建立 PostgreSQL 容器、环境变量示例或持久化 volume；这些内容属于 Step 4。
- 尚未拆分 `base`、`development`、`test` 和 `production` settings；这些内容属于 Step 5。

### 下一步门槛

Step 3 已通过项目负责人验证，Step 4 已获授权并完成。

## Step 4 — 配置 PostgreSQL 本地环境

### 已完成

- 创建 `compose.yaml`，使用官方 `postgres:18.6-alpine` 镜像提供本地 PostgreSQL service。
- 为 PostgreSQL 配置映射端口、`pg_isready` 健康检查、重启策略和 named volume。
- PostgreSQL 18 数据卷挂载到 `/var/lib/postgresql`，避免使用旧版本镜像的数据目录约定。
- 创建 `.env.example`，提供数据库名、用户、开发占位密码、主机和端口的安全本地示例。
- 将 `config/settings.py` 从 dummy backend 改为 PostgreSQL backend，并要求所有数据库连接值来自环境变量。
- 缺少或留空必填数据库变量时抛出明确的 `ImproperlyConfigured`，没有加入 SQLite 或其他数据库回退。
- 更新 `.gitignore`，排除 `node_modules/`、`.env` 和其他本地 `.env.*` 文件，同时保留 `.env.example`。
- 创建 `tests/test_database_settings.py`，验证 PostgreSQL backend、环境变量映射和缺失变量失败行为。

### 验证结果

- `docker compose config` 成功解析 service、环境变量、端口、健康检查和 volume 配置。
- `docker compose up -d --wait postgres` 成功启动 PostgreSQL，容器状态为 `healthy`。
- `python -m uv run --env-file .env python manage.py check --database default` 通过，无 system check 问题。
- Django 主机环境成功连接 PostgreSQL，报告 vendor 为 `postgresql`、server version 为 `180006`。
- `tests/test_project_scaffold.py` 与 `tests/test_database_settings.py` 共 4 个测试全部通过。
- `python -m uv run --env-file .env ruff check manage.py config apps tests` 报告 `All checks passed!`。
- 创建持久化测试表后执行 `docker compose down` 并重新创建容器，测试记录仍存在，确认 named volume 有效；验证后已删除测试表。
- 停止 PostgreSQL 后，Django 连接以 `django.db.utils.OperationalError` 明确失败，确认没有 SQLite 或其他回退；验证后已恢复容器，最终状态为 `healthy`。
- `git check-ignore` 确认 `.env` 与 `node_modules/` 被排除；`git ls-files` 确认 `.env`、`node_modules`、SQLite 文件和其他数据库文件均未被跟踪。

### 当前边界

- Django 在本机 `uv` 环境运行，通过 `127.0.0.1:5432` 连接 Docker 中的 PostgreSQL。
- 本地 `.env` 由 `.env.example` 复制生成并保持未跟踪；当前示例值只用于本地开发。
- PostgreSQL named volume 由 Docker 管理，不位于项目工作树中。
- 当前仍使用单一 `config.settings`；环境拆分、Production Secret 和安全设置属于 Step 5。
- 当前没有业务模型或业务 migration，数据库中未保留本步骤的临时测试表。

### 下一步门槛

Step 4 已通过项目负责人验证，Step 5 已获授权并完成。

## Step 5 — 拆分环境 Settings

### 已完成

- 将单文件 `config/settings.py` 替换为 `config/settings/` package，并建立 `base.py`、`development.py`、`test.py` 和 `production.py`。
- 将 Apps、Middleware、Templates、时区、静态资源和通用环境变量解析逻辑集中到 `base.py`。
- 建立严格的必填字符串、CSV、Boolean 和 PostgreSQL `DATABASE_URL` 解析；拒绝 SQLite 和其他数据库 scheme。
- Development settings 启用 Debug、Console Email、本地 media，并从环境变量读取 Secret、hosts、CSRF origins 和 PostgreSQL URL。
- Test settings 关闭 Debug，使用独立 PostgreSQL test database 名称、in-memory Email Backend 和快速 Password hasher，不依赖外部邮件服务。
- Production settings 关闭 Debug，强制读取 Secret、hosts、CSRF origins、PostgreSQL URL 和 SMTP 配置，并启用 HTTPS redirect、secure cookies、HSTS、referrer policy 和 frame protection。
- `manage.py` 默认加载 Development settings；ASGI 和 WSGI 默认加载 Production settings；均允许显式 `DJANGO_SETTINGS_MODULE` 覆盖。
- 在 `pyproject.toml` 中将 pytest-django 默认 settings 指向 `config.settings.test`。
- 扩展 `.env.example`，加入 settings、test database、database URL、CSRF 和 Email 所需变量的安全示例；本地 `.env` 仍保持未跟踪。
- 更新数据库配置测试，并新增环境 settings 测试；未创建业务模型或 migration。

### 验证结果

- Development settings 的 Django system check 通过，无问题。
- Test settings 的 Django system check 通过，无问题。
- pytest-django 确认使用 `config.settings.test`，项目骨架、数据库配置和环境 settings 共 9 个测试全部通过。
- Production settings 缺少 `DJANGO_SECRET_KEY` 时抛出 `ImproperlyConfigured`，错误明确指出缺失变量。
- 使用完整测试环境变量时，Production `check --deploy` 通过，无 security check 问题。
- 首次 Ruff 检查发现 20 个未使用的 `noqa` 注释；删除这些注释且不改变配置逻辑后，最终 Ruff 检查报告 `All checks passed!`。
- PostgreSQL 容器在验证期间保持 `healthy`。

### 当前边界

- Development、Test 和 Production 使用同一公共配置基础，但环境行为和 Secret 来源已隔离。
- PostgreSQL 是所有环境唯一配置的数据库 backend；Test 指定独立数据库名称。
- Test Email 保持内存内运行，Production SMTP 只完成配置验证，没有连接尚未确定的真实 Provider。
- Production 使用的完整变量均为验证用合成值，仓库没有真实 Secret。
- 当前没有 Custom User、业务模型或业务 migration；这些内容属于 Step 6 及后续步骤。

### 下一步门槛

Step 5 已通过项目负责人验证，Step 6 已获授权并完成。

## Step 6 — 创建 Custom User 初始模型

### 已完成

- 创建 `apps.accounts.User`，继承 Django `AbstractUser`，保留 Username、Password、Staff、Superuser、Group 和 Permission 等标准认证与权限字段。
- 将 Email 重新声明为必填且唯一，并将 `email` 加入 `REQUIRED_FIELDS`。
- 增加 `is_usyd_student`、可空 `usu_id`、`usu_review_status`、可空 `usu_reviewed_at` 和可空 `usu_reviewed_by`。
- 审核状态定义为 `not_submitted`、`pending`、`verified` 和 `rejected`，默认为 `not_submitted`。
- `usu_reviewed_by` 使用可空 Self ForeignKey，审核人被删除时通过 `SET_NULL` 保留被审核账户。
- 在公共 settings 中设置 `AUTH_USER_MODEL = "accounts.User"`，确保后续关系均使用自定义 User。
- 生成首条业务 migration `accounts.0001_initial`，由其创建 Custom User 表和标准权限关系。
- 创建 `tests/test_user_model.py`，覆盖 User 创建、标准权限字段、安全默认值、Email 必填与唯一、审核字段可空性及 Self ForeignKey 的 `SET_NULL` 行为。
- 为 Django migration 文件的框架约定 class attributes 配置 Ruff `RUF012` 定向豁免；业务模型的 `REQUIRED_FIELDS` 使用 `ClassVar` 明确类属性语义。

### 验证结果

- Custom User 专项测试共 5 个，全部通过。
- 项目完整 pytest 套件共 14 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，确认 model 与 migration 同步。
- 开发数据库从空表状态成功执行 Django 内置 migrations 和 `accounts.0001_initial`。
- Django system check 通过，无问题。
- 表结构检查确认 `accounts_user` 存在，`auth_user` 不存在，未创建 Django 默认 User 业务表。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。

### 当前边界

- Step 6 只建立数据结构和安全默认值，未实施 Email 或 USU ID 规范化。
- 尚未实施非 USYD 用户禁止保存 USU ID、修改 ID 后回到 `pending` 或管理员受控审核流程；这些属于 Step 7。
- 开发数据库现已应用 Step 6 migrations；测试继续使用独立 PostgreSQL test database。

### 下一步门槛

Step 6 已通过项目负责人验证，Step 7 已获授权并完成。

## Step 7 — 实施 USYD 与 USU ID 领域规则

### 已完成

- Email 在 model 保存前去除首尾空格并转换为小写；PostgreSQL 约束拒绝空字符串或未规范化的 Email。
- USU ID 继续使用字符串存储以保留前导零，去除首尾空格后只允许 ASCII 数字 `0–9`；空字符串统一保存为 `NULL`。
- User model 保存路径实施状态转换：首次提交或修改 ID 进入 `pending`，并清除原审核人和时间；清空 ID 进入 `not_submitted`；取消 USYD 声明时清除 ID 及全部审核信息。
- User model 拒绝通过普通 `save()` 直接修改审核字段，`verified` 和 `rejected` 只能通过受控审核服务写入。
- 创建 `update_usu_identity` 事务服务，通过 row lock 更新 USYD 声明和 USU ID，并对非 USYD 用户提交 ID 返回验证错误。
- 创建 `review_usu_id` 事务服务，仅允许数据库中当前为启用状态的 Staff 审核已提交 ID，并记录状态、审核人和时间。
- 增加 Email 规范化、USU ID 规范化及 USU 状态组合三项 PostgreSQL `CheckConstraint`，防止 `QuerySet.update()` 绕过应用层写入非法行状态。
- 生成并应用 `accounts.0002_alter_user_usu_id_and_more`，未修改已应用的 `accounts.0001_initial`。
- 新增 `tests/test_user_identity_rules.py`，并调整原 User model 测试以符合新状态约束。

### 验证结果

- User model 与身份领域规则专项测试共 24 个，全部通过。
- 项目完整 pytest 套件共 33 个测试，全部通过；本步没有 pytest 失败。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- `accounts.0002_alter_user_usu_id_and_more` 在开发 PostgreSQL 上成功应用。
- Django system check 通过，无问题。
- 首次 Ruff 检查发现两个问题：`models.py` import 区与模块常量之间多一个空行，以及 `Meta.constraints` 缺少类属性标注而触发 `RUF012`。
- 针对性删除多余空行，并将 `Meta.constraints` 标注为 `ClassVar[list[models.CheckConstraint]]`；未改变业务逻辑或 migration。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。

### 当前边界

- Step 7 使用 service 层实现未来 form 需要调用的领域行为；当前尚未创建注册或 Account form。
- 受控审核服务当前建立启用 Staff 基线；Django Admin 集成和更细粒度的 Staff 权限属于 Step 15。
- 尚未创建 MemberProfile；该工作属于 Step 8。

### 下一步门槛

Step 7 已通过项目负责人验证，Step 8 已获授权并完成。

## Step 8 — 创建完整 MemberProfile 数据结构

### 已完成

- 创建 `apps.members.MemberProfile`，通过必填 One-to-one relation 关联 Custom User，并在账户删除时级联删除 Profile。
- 一次建立 `display_name`、`avatar`、`bio`、`experience_level`、`preferred_arm`、`instagram_handle`、`other_social_url`、发布状态、管理员隐藏状态、Executive 角色和时间戳字段。
- `display_name` 保存前去除首尾空格，空值统一为 `NULL`，非空值由 PostgreSQL 条件唯一约束保证忽略大小写后唯一；显示名为空时回退到 Username。
- Avatar 限制为真实 JPG、PNG 或 WebP，校验扩展名、声明 MIME、实际图像内容和 5 MB 上限；Development 继续使用既有本地 media 配置。
- Bio 限制为 500 字符以内的纯文本；Instagram 输入去除开头 `@` 并只接受 Username 字符；其他社交链接只接受 HTTPS。
- 建立 `MemberProfile.objects.public()`，只返回会员主动发布、未被管理员隐藏、账户启用且至少具有一条已验证 EmailAddress 的 Profile。
- 建立 `ensure_member_profile` 幂等 service，供 Step 11 邮箱验证成功流程调用；本步未提前连接验证 signal。
- 建立 `MemberProfileForm` 的会员可写字段白名单，排除管理员隐藏状态、Executive 角色和时间戳。
- 启用 Django Admin App 并注册 `MemberProfileAdmin`；本步未公开 Admin URL，也未实施 Step 15 的 USU 审核界面和细粒度权限。
- 在公共 settings 中启用 `allauth.account` 及其必需 middleware，只使用 EmailAddress 数据层表达公开查询的邮箱验证边界；认证 backend、URL 和流程配置仍属于 Step 9。
- 生成并应用 `members.0001_initial`，同时应用新增的 allauth account 与 Django admin migrations。
- 新增 `tests/test_member_profile.py`，覆盖关系、默认值、时间戳、幂等 service、规范化、数据库约束、上传验证、choices、公开边界、会员 form 和 Admin 配置。

### 验证结果

- MemberProfile 专项测试共 23 个，最终全部通过。
- 项目完整 pytest 套件共 56 个测试，最终全部通过。
- 首次运行专项测试为 21 个通过、2 个失败；完整测试为 54 个通过、2 个失败。
- 第一个失败来自测试错误地将可空 ImageField 的空文件名预期为空字符串；按 Django 实际行为将断言改为 `avatar.name is None`，未修改业务逻辑。
- 第二个失败暴露 Avatar MIME validator 只读取 `ImageFieldFile` 外层对象，遗漏底层上传对象的 `content_type`；针对性读取底层文件 MIME 后，伪装 MIME 测试通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- 开发 PostgreSQL 成功应用 `account.0001` 至 `account.0009`、`admin.0001` 至 `admin.0003` 及 `members.0001_initial`。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。
- Step 8 新增文件通过 Ruff format check，`git diff --check` 未发现新增格式错误。

### 当前边界

- Profile 创建 service 已存在，但自动调用时机仍按计划留到 Step 11 的邮箱验证成功流程。
- allauth 当前只提供 EmailAddress 数据模型和 middleware 基础，尚未配置登录、注册、验证、Magic Code、Password reset、rate limits 或项目认证 URL。
- 会员编辑页面、预览、发布操作和公开 Members 页面属于 Phase 3；本步只建立 schema、验证、公开查询边界、受限 form 和后台模型配置。
- Production persistent media storage 仍未确定；当前没有隐式选择 Provider。

### 下一步门槛

Step 8 已通过项目负责人验证，Step 9 已获授权并完成。

## Step 9 — 接入 django-allauth

### 已完成

- 按照锁定的 django-allauth 65.20.1 本地源码及官方文档核对当前 setting 名称、authentication backend、条件路由和默认 rate limits。
- 在公共 settings 中启用 `allauth`、`allauth.account` 和 Django Sites framework，并设置 `SITE_ID = 1`。
- 将 authentication backend 配置为 `allauth.account.auth_backends.AuthenticationBackend`；未额外加入 Django `ModelBackend`，符合锁定版本的安全指导且保留 Username/Password 与 Admin 认证能力。
- 配置 Username 登录、必填且唯一的 Email、强制 Email verification、Email verification by code、可选 Email Magic Code、password reset 和 enumeration prevention。
- 明确保持 `ACCOUNT_LOGIN_BY_CODE_REQUIRED = False`，避免密码登录被强制追加验证码；Phone verification、Social login 和 MFA 未启用。
- 未覆盖 `ACCOUNT_RATE_LIMITS`，继续使用 allauth 65.20.1 对 signup、login、login code、password reset 和 Email verification 的默认限制。
- 保持 GET logout 禁用，登录后目标预留为 `/account/`，登出后目标为 `/`；实际 Account 页面仍属于 Step 14。
- 在根 URL 中将 `/accounts/` 接入 `allauth.urls`；尚未创建自定义认证模板或业务表单。
- 新增 `tests/test_authentication_configuration.py`，验证 Apps、backend、settings、默认 rate limits、redirects、必需 URL 及排除功能的 URL 不可用性。

### 验证结果

- django-allauth 配置与路由专项测试共 19 个，全部通过。
- 项目完整 pytest 套件共 75 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- 开发 PostgreSQL 成功应用 `sites.0001_initial` 和 `sites.0002_alter_domain_unique`。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。
- 本步没有测试失败或针对性代码修补。

### 当前边界

- Step 9 只建立认证基础配置和 URL；Step 10 才扩展单页注册表单并接入 USYD/USU ID 字段。
- Email verification code、密码登录、Password reset 和 Magic Code 的具体成功、错误、过期、重发及日志行为分别由 Step 11–13 完成和测试。
- 强制 Email verification 已配置；未验证账户的完整页面引导和 Magic Code 业务边界仍需在对应认证流程步骤进行行为测试。
- 当前使用 allauth 自带模板作为路由基础；项目统一认证页面表现属于 Step 17。
- Social Account、MFA 和 Phone login 对应 Apps 与路由均未启用。

### 下一步门槛

Step 9 已通过项目负责人验证，Step 10 已获授权并完成。

## Step 10 — 实施单页注册表单

### 已完成

- 新建 `apps/accounts/forms.py`，使用 allauth 支持的 `ACCOUNT_FORMS` 完整 signup form override，并保持注册字段顺序为 Username、Email、Password、Confirm password、`Are you a USYD student?` 和 `USU ID`。
- `is_usyd_student` 与 `usu_id` 为注册附加字段；USU ID 可留空，规范化后只允许 ASCII 数字并保留前导零。
- Form 层拒绝未勾选 USYD 时伪造提交 USU ID，确保服务端不依赖条件显示的前端行为。
- 注册用户由 allauth 建立后，表单调用现有 `update_usu_identity` 事务 service 保存 USYD 声明与 USU ID，不重复实现身份状态规则。
- 成功的普通 HTTP POST 在创建未验证 EmailAddress 后 redirect 至独立 Email verification code 页面；本步未实施 code 生命周期。
- 保持 allauth enumeration prevention：已存在 Email 的注册提交返回与正常注册一致的验证页面 redirect，不建立第二个用户。
- 新建 `tests/test_signup_form.py`，覆盖字段顺序、必填项、任意有效 Email domain、重复 Username、重复 Email、USYD 条件输入、伪造绕过、数字校验、前导零与无 JavaScript 的普通 POST。

### 验证结果

- 项目负责人运行 Step 10 专项测试，共 15 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 90 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed`。

### 测试期间的针对性修补

- 首次专项测试为 3 个通过、12 个失败。allauth 的 `ACCOUNT_SIGNUP_FORM_CLASS` 附加字段会排在动态建立的 Password 字段前，无法满足已确认顺序；改用官方支持的 `ACCOUNT_FORMS` signup override，并在项目表单初始化后显式排序。
- 直接实例化 allauth signup form 也会查询 Username 和 Email 唯一性；为表单行为测试增加 pytest database 标记，未通过 mock 绕开真实 PostgreSQL 行为。
- 两个集成场景最初复用同一 Email，命中 allauth 默认 verification Email rate limit；将独立场景改为不同合成 Email，保留默认 rate limits 不变。
- 第二次专项测试为 9 个通过、6 个失败；集成测试已通过，剩余失败来自单元测试仍实例化 allauth 原始类。将测试改为实例化项目 `SignupForm` 后全部通过。
- 首次完整回归的 90 个测试已全部通过；Ruff 另发现一处测试 import 分组顺序，移动 import 后最终通过，未改变业务行为。

### 当前边界

- 本步建立注册表单数据和服务端行为；Alpine.js 条件显示、项目 account templates 和表单视觉表现仍属于 Step 17。
- Email verification code 的正确、错误、过期、重用和重发路径，以及验证成功后的 MemberProfile 幂等创建属于 Step 11。
- 当前使用 allauth 自带 signup template；本步不提前建立全局页面外壳或前端资产。

### 下一步门槛

Step 10 已通过项目负责人验证，Step 11 已获授权并完成。

## Step 11 — 完成注册邮箱验证码流程

### 已完成

- 按照锁定的 django-allauth 65.20.1 官方文档与本地源码核对 Email verification by code 的 session、超时、尝试次数、重发和成功 redirect 行为。
- 在公共 settings 中启用 Email verification code 重发，并明确保持 3 次错误尝试上限和 15 分钟有效期。
- 保持 allauth 默认 `confirm_email` rate limit：同一 Email 每 10 秒最多发送一次 verification Email，立即重发返回 HTTP 429 且不替换当前 code。
- 新建 `apps/members/signals.py`，监听 allauth 官方 `email_confirmed` signal，并调用现有 `ensure_member_profile` 幂等 service 为已验证用户建立默认隐藏 Profile。
- 在 `MembersConfig.ready()` 中显式导入 signal receiver，使验证成功后的 Profile 创建与 App 启动周期稳定连接。
- 正确 code 会验证 Email、清除 verification session、完成 signup login stage 并 redirect 至现有 `LOGIN_REDIRECT_URL`；错误 code 保持待验证状态。
- 已确认采用 allauth 标准过期行为：code 过期后清除当前 verification process 并 redirect 至 login；未验证用户通过登录重新获得 code 的流程留给 Step 12。
- 新建 `tests/test_email_verification.py`，覆盖验证前会员边界、正确 code、错误 code、过期、重复使用、重发、重发限流、Profile 唯一性和敏感日志边界。
- 扩展认证配置测试，锁定 verification code 尝试次数、超时时间和重发配额。

### 验证结果

- 项目负责人运行 Email verification 与认证配置专项测试，共 27 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 98 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。
- 本步的首次专项测试、完整回归和所有质量检查均直接通过，没有测试失败或针对性代码修补。

### 当前边界

- 验证前的 User 具有未验证 EmailAddress，但不获得 authenticated session，也不建立 MemberProfile。
- 验证成功后 EmailAddress 被标记为 verified，Profile 只建立一次且 `is_published` 与 `is_hidden_by_admin` 均保持安全默认值。
- 测试日志不包含 verification code 或完整 Email；正式的结构化日志链和全局敏感信息扫描仍属于 Step 19。
- 密码登录、未验证账户的登录引导、Password reset 和 POST logout 属于 Step 12。
- 项目自定义 verification template、验证码输入交互和移动端表现仍属于 Step 17。

### 下一步门槛

Step 11 已通过项目负责人验证，Step 12 已获授权并完成。

## Step 12 — 完成密码登录、重置与登出

### 已完成

- 按照锁定的 django-allauth 65.20.1 本地源码核对 Username/Password 登录、mandatory Email verification stage、inactive account、redirect 安全校验、link-based Password reset 和 logout 方法边界。
- 验证已确认邮箱的启用账户可使用 Username/Password 登录，并在没有原目标时进入现有 `LOGIN_REDIRECT_URL`。
- 验证站内 `next` 参数会在登录后保留，外部绝对 URL 会被拒绝并回退到 `LOGIN_REDIRECT_URL`，防止开放重定向。
- 验证不存在的 Username 与错误 Password 返回相同的通用凭据错误，不泄露账户是否存在。
- 验证未确认邮箱的账户即使密码正确也不会建立 authenticated session；登录会发送新验证码并进入既有验证流程，验证成功后返回原站内目标并幂等创建 MemberProfile。
- 验证停用账户即使凭据正确也不会建立 authenticated session，并进入 allauth inactive account 响应。
- 验证 Password reset 对已知与未知 Email 返回相同 redirect，并分别发送对应邮件以保持 enumeration prevention；有效 reset link 可以设置新密码，旧密码随即失效，reset 本身不会自动登录。
- 验证 GET logout 只展示确认页面且保留 Session，POST logout 才清除 authenticated session 并进入 `LOGOUT_REDIRECT_URL`。
- 新建 `tests/test_password_authentication.py`，通过真实 allauth views、Session、Email backend 和 PostgreSQL 行为覆盖上述正常、失败与安全路径。
- 现有 allauth 配置已完整满足本步要求，因此没有修改生产代码、settings、adapter、form、schema 或 migration。

### 验证结果

- 项目负责人运行 Step 12 专项测试，共 9 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 107 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。
- 本步的首次专项测试、完整回归和所有质量检查均直接通过，没有测试失败或针对性代码修补。

### 当前边界

- 本步复用 allauth 自带页面验证服务端流程；项目统一登录、Password reset、inactive account 和 logout 页面表现仍属于 Step 17。
- `LOGIN_REDIRECT_URL` 继续预留为 `/account/`；实际 Account 页面及其访问控制属于 Step 14。
- 停用账户的项目联系入口与用户文案将在认证模板实施时完成；当前服务端已安全拒绝认证。
- Email Magic Code 登录尚未实施，其请求、确认、错误、过期、重用、未验证账户和 rate-limit 边界属于 Step 13。

### 下一步门槛

Step 12 已通过项目负责人验证，Step 13 已获授权并完成。

## Step 13 — 完成 Email Magic Code 登录

### 已完成

- 按照锁定的 django-allauth 65.20.1 本地源码核对 Magic Code 请求、确认、Session state、过期、错误尝试、重发、enumeration prevention 和成功登录流程。
- 明确配置 Magic Code 有效期为 3 分钟、最多 3 次错误尝试并允许最多 2 次重发；继续使用默认 `request_login_code` rate limit（每个 IP 每分钟 20 次、每个 Email key 每分钟 3 次）。
- 保持 `ACCOUNT_LOGIN_BY_CODE_REQUIRED = False`，Magic Code 继续作为独立可选入口，Username/Password 登录不会被强制追加 code。
- 发现锁定版 allauth 的默认 Magic Code 成功路径会通过 `verify_email_indirectly` 将未确认 Email 标记为 verified，这与项目要求不符。
- 新建项目 `RequestLoginCodeForm` override，在 allauth 已完成统一查询、active filtering、rate limit 和 enumeration prevention 后，只允许具有匹配 verified EmailAddress 的账户保留为可登录用户。
- 未验证、停用及未知 Email 继续获得相同 HTTP redirect 和邮件发送外观，但 Session 不包含可用 login code 或 User，因此不能完成 Magic Code 登录。未验证账户继续使用 Step 12 的 Username/Password 路径重新进入注册邮箱验证。
- 验证有效 code 可登录并返回安全的站内原目标；错误、超过尝试次数、过期和重复使用 code 均不能建立 authenticated session。
- 验证前两次重发会生成新 code，达到配额后不再发送邮件或替换 code；请求频率限制按 Email key 生效。
- 验证 Magic Code 和完整 Email 不出现在应用测试日志中。
- 新建 `tests/test_magic_code_authentication.py`，覆盖有效、错误、尝试上限、过期、重复使用、重发、请求 rate limit、未验证、停用、未知 Email、密码登录独立性和敏感日志边界。
- 扩展 `tests/test_authentication_configuration.py`，锁定 Magic Code 尝试次数、有效期和重发配额。

### 验证结果

- 项目负责人运行 Magic Code 与认证配置专项测试，共 31 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 119 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。

### 测试期间的针对性修补

- 首次专项测试为 28 个通过、3 个失败；生产行为已正确阻止未验证和停用账户获得有效 code。
- 两个失败来自测试将未知流程的 `user_pk=None` 当作字符串执行包含检查；改为直接断言 `user_pk is None`。
- rate-limit 测试最初在同一 Session 连续访问请求页；allauth Account middleware 会将已有待处理登录阶段直接重定向至确认页，因此后续请求没有再次经过 form 或消耗 rate limit。测试改为每次已接受请求后清除 Session，同时保留共享 cache，随后确认第四次真实请求被拒绝。
- 上述修正仅调整测试对 allauth Session 和 middleware 行为的表达，没有追加生产代码修补。

### 当前边界

- 本步使用 allauth 自带 request 与 confirm 页面验证服务端流程；项目统一 Magic Code 页面、未验证用户提示和入口文案仍属于 Step 17。
- 未验证账户不会通过 Magic Code 自动完成 Email verification；其恢复验证路径是使用正确 Username/Password 登录后进入既有 verification code 流程。
- Account 页面与 USYD/USU ID 本人更新尚未实施，属于 Step 14。

### 下一步门槛

Step 13 已通过项目负责人验证，Step 14 已获授权并完成。

## Step 14 — 建立 Account 页面与 USU 信息更新

### 已完成

- 新建登录保护的 `/account/` 页面，并使现有 `LOGIN_REDIRECT_URL` 指向实际可访问的会员账户页面；Anonymous 会由 Django 登录保护重定向至 allauth login，并保留站内 `next`。
- 页面只展示当前 authenticated user 的 Username、Email、Email verification status、USYD 声明、条件 USU ID 和本人 USU review status，不查询或展示其他会员信息。
- Username 与 Email 仅作为只读值输出；Phase 1 没有 Email 修改入口。
- 新建 `AccountIdentityForm`，会员输入白名单仅包含 `is_usyd_student` 与 `usu_id`；Username、Email、目标 User、审核状态、审核时间和审核人等伪造 POST 字段均不参与写入。
- Account form 复用现有 `update_usu_identity` 事务 service，继续执行数字型 USU ID、前导零保留、非 USYD 拒绝、修改 ID 后回到 `pending`，以及取消 USYD 后清除 ID 和审核信息等既有领域规则。
- GET form 从当前会员已有的 USYD 声明与 USU ID 初始化；成功 POST 使用 redirect-after-POST 并显示英文成功消息。
- 页面提供 allauth Password change 入口，以及带 CSRF 的 POST logout form；没有开放 GET logout 操作。
- 新建最小英文 `account.html` 功能模板，以支持本步服务端流程；全局布局、视觉样式、Alpine.js 条件显示及统一认证页面继续属于 Step 16–17。
- 新建 `tests/test_account_page.py`，覆盖 Anonymous redirect、本人数据隔离、Email verification 显示、GET 初始化、数字校验、状态转换、只读及审核字段防伪造、其他用户防修改、Password change 和 POST logout 页面边界。

### 验证结果

- 项目负责人运行 Step 14 专项测试，共 12 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 131 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。

### 测试与复查期间的针对性修补

- 首次专项测试为 9 个通过、2 个失败；两个失败均来自测试在 `review_usu_id` 后继续使用审核前的旧 User 实例。`force_login` 更新 `last_login` 时，该旧实例携带过期审核字段并正确触发既有审核写入保护。测试改为使用审核 service 返回的最新锁定实例，未修改生产审核逻辑。
- 差异复查发现 GET view 会以 `None` 作为 form 的首个位置参数，原初始化判断因此未载入已有 USYD/USU ID。表单改为在 Django 判定 `is_bound=False` 后填充初始值，并增加对应回归测试；最终专项测试增至 12 个并全部通过。

### 当前边界

- 当前 Account template 是 Step 14 的最小功能页面；统一 Header、Footer、消息框架、黑金视觉、响应式样式与 Alpine.js 条件交互尚未实施。
- 普通会员只能读取本人 review status，不能读取 review actor/time，也不能写入任何审核字段。
- Django Admin USU ID 审核界面、专用权限与 Staff 最小权限属于 Step 15，当前没有提前实施。
- Account 页面没有 Email 修改、账户删除或数据保留流程，符合 Phase 1 范围。

### 下一步门槛

Step 14 已通过项目负责人验证，Step 15 已获授权并完成。

## Step 15 — 建立 USU ID 管理后台

### 已完成

- 为 Custom User 增加专用 Django permission `accounts.review_usu_id`，并生成 `accounts.0003_alter_user_options`；该 migration 只变更 model options，不新增或修改业务字段。
- 将 `review_usu_id` service 的 reviewer 边界从任意启用 Staff 收紧为启用 Staff 且具有专用审核权限；Superuser 继续通过 Django 标准权限机制获得审核资格。
- 新建 Custom `UserAdmin`，提供 Username、Email、USYD 声明、USU ID、审核状态和账户启用状态的列表列，并支持按审核状态、USYD 声明和账户启用状态筛选，以及按 Username、Email 和 USU ID 搜索。
- 新增 Verify 与 Reject 两个 Admin actions；两者均调用既有事务审核 service，记录当前管理员、审核时间及最终状态，不直接写入审核字段。
- 普通会员不能进入 Admin；没有专用权限的 Staff 不能访问 User Admin；获授权 Staff 只能看到已提交 USU ID 的账户，并只能通过审核 actions 操作，不能新增、删除或直接编辑 User。
- Superuser 保留标准 UserAdmin 的用户管理能力；USYD/USU ID 及审核字段对所有 Admin 角色继续保持只读，确保审核写入只能经过受控 action/service。
- 在项目根 URL 开放 `/admin/` Django Admin 入口；未增加自定义 Admin template 或 Step 16 页面框架。
- 验证 Verify、Reject、修改 ID 后重新提交并再次审核，以及审核人后来停用后历史状态、审核人关系与审核时间继续保留。
- 验证 Account 响应不输出审核人或审核时间，Anonymous 响应不泄露完整 USU ID。
- 新建 `tests/test_user_admin.py`，并更新既有 User model、身份规则和 Account 测试，为合法 reviewer 显式授予专用权限。

### 验证结果

- 项目负责人运行 UserAdmin、身份规则与 Account 专项测试，共 46 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 146 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- `accounts.0003_alter_user_options` 已成功应用到本地开发数据库；项目负责人再次运行 `migrate` 时报告 `No migrations to apply`。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。
- `git diff --check` 未发现格式错误；仅报告现有文档的 LF/CRLF 转换警告。

### 测试期间的针对性修补

- Step 15 的 46 个专项测试首次全部通过。
- 首次完整回归为 145 个通过、1 个失败；失败来自旧 `test_user_model.py` 仍按 Step 7 基线假设任意 Staff 可以调用审核 service。
- 为该测试中的合法 reviewer 显式授予 `review_usu_id` 权限后，完整 146 个测试全部通过；生产权限逻辑未放宽。

### 当前边界

- 专用权限需要由 Superuser 通过 Django 权限或 Group 管理分配；本步不建立硬编码管理员名单或自动授权。
- UserAdmin 只处理 USU ID 人工审核，不实现 MemberProfile 发布审核、活动管理或其他后续阶段后台功能。
- `/admin/` 使用 Django 默认 Admin 页面；项目全局模板、Header、Footer 和前台消息框架属于 Step 16。
- 审核人停用不会删除历史审计关系；已停用 reviewer 不能执行新的审核。

### 下一步门槛

Step 15 已通过项目负责人验证，Step 16 已获授权并完成。

## Step 16 — 建立全局模板与导航

### 已完成

- 为 `core` 新建 Home view 与根路径 URL，提供英文 Home 占位页面；根 URLConf 先匹配精确的 Home 路径，再继续匹配项目 Account 和 allauth 路由。
- 新建全局 `base.html` 页面壳，统一声明英文文档、字符集、移动端 viewport、页面标题区块、skip link，以及 Header、messages、main 和 Footer 结构。
- 新建 Header include，Anonymous 显示 `Log in` 与 `Join the Club`，authenticated member 显示 `Account`；Home 与 Account 当前项使用 `aria-current="page"`。
- Header 只链接已经存在的路由，没有提前加入 About、Events、Members 或 Locations 等尚未实施的页面，也没有使用未经授权的 University Branding。
- 新建 Django messages include，使用 `aria-live="polite"` 和 `aria-atomic="true"`，并按消息级别提供 `status` 或 `alert` role。
- 新建中性 Footer include，并使用 Django `now` tag 输出当前年份。
- 将既有 Account template 改为继承全局页面壳，保留 Step 14 的只读账户信息、USYD/USU ID form、Password change 与 POST logout 行为。
- 页面壳和导航全部使用普通 HTML link/form，不依赖 JavaScript；skip link、语义化 landmarks、唯一主标题、当前页标识和移动端 viewport 建立了后续视觉实现可复用的 Accessibility 基线。
- 新建 `tests/test_global_templates.py`，覆盖 Anonymous/Member Header 差异、全局 landmarks、skip link、当前导航、唯一 H1、移动端 viewport、messages live region 和无 JavaScript 导航。

### 验证结果

- 项目负责人运行全局模板与 Account 专项测试，共 18 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 152 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff 对 `manage.py`、`config`、`apps` 和 `tests` 的最终检查报告 `All checks passed!`。

### 测试期间的针对性修补

- 首次专项测试为 17 个通过、1 个失败；失败来自新增测试断言使用了并不存在的 USU ID 专用成功文案。
- 测试改为断言 Step 14 Account view 已实际使用的 `Your account information has been updated.`；messages live region 与生产页面行为未修改。

### 当前边界

- Step 16 只建立语义化全局页面壳与导航基线，没有提前实施 allauth 统一认证模板；Signup、Login、Email verification、Magic Code、Password reset、Password change、Logout 和 inactive account 页面属于 Step 17。
- 当前没有引入 Tailwind 构建、黑金视觉、Logo、Alpine.js 条件交互或 HTMX 行为；前端静态资源与完整响应式视觉按后续步骤实施。
- Home 目前是英文占位内容；About、Events、Members 与 Locations 路由尚不存在，因此 Header 不提供失效链接。

### 下一步门槛

Step 16 已通过项目负责人验证；项目负责人随后授权将 Step 17 与 Step 18 合并实施并使用同一验收门禁，两步现已完成。

## Step 17 — 统一认证与账户页面体验

### 已完成

- 在项目级 `templates/account/` 中覆盖当前启用的 allauth 认证页面，使 Signup、Login、Email verification、Magic Code、Password reset/change/set、Logout、reauthentication 和 inactive account 全部继承项目全局页面壳。
- 建立共享 form error、field 和 fields includes；字段错误由 Django `as_field_group` 与对应 input 建立 `aria-invalid`、`aria-describedby` 关系，非字段错误提供可聚焦的 `alert` summary。
- 全局页面壳在页面载入后优先聚焦首个无效字段或错误 summary，同时保留 skip link、语义 landmarks、普通 link/form 与 CSRF 基线。
- 为 Email verification 和 Magic Code 确认 form 提供数字移动键盘、`one-time-code` autocomplete 和整串 code 输入；无效敏感 code 与 Password 不回显到 HTML。
- Signup 与 Account 的 USYD 身份字段使用 Alpine.js 渐进增强：选中时显示 USU ID，取消时清空；存在服务端错误时保持显示；禁用 JavaScript 时字段继续可见并可由服务端完整校验。
- Account 页面与所有认证页面采用同一响应式 form、panel、button 和 feedback 结构，没有改变 Step 9–15 已验证的认证、权限或领域规则。

### 验证结果

- 认证页面集成测试覆盖全局页面壳、字段错误关联、焦点目标、敏感输入不回显、数字 code 配置、Alpine 标记和普通 POST 回退。
- Playwright 浏览器测试在 `390 × 844` viewport 验证无水平溢出、skip link 键盘焦点、USYD 条件显示与清空、整串 code 输入、无 JavaScript 回退，以及服务端错误后的字段显示与焦点恢复。
- Step 17 与 Step 18 按项目负责人要求共用下述联合门禁；任一部分失败时两步均不标记完成。

### 当前边界

- 所有核心认证和 Account 操作继续由 Django/allauth 服务端处理；Alpine.js 只负责可逆的界面状态增强。
- 当前没有为认证流程加入 HTMX 请求，也没有改变认证 URL、Session、rate limit、verification 或权限边界。
- inactive account 页面使用中性联系说明，没有虚构尚未确认的俱乐部联系方式。

## Step 18 — 接入静态资源并完成第一版视觉

### 已完成

- 建立 Tailwind CSS v4 source/build/watch 流程；`static_src/css/site.css` 是样式源文件，`static/css/site.css` 是提交并部署的 minified 构建产物。
- 建立黑色、炭色、奶油色和金色 design tokens、Inter 正文字体、Barlow Condensed 标题字体，以及统一的 panel、form、button、navigation、message、focus、mobile 和 reduced-motion 样式。
- 将锁定版本的 Alpine.js、HTMX、MapLibre GL JS 和字体文件从 `node_modules` 确定性复制到 `static/`；浏览器运行时不依赖第三方 CDN。
- `static/vendor/manifest.json` 记录每个 vendor 文件的 npm 包、精确版本、来源路径和 SHA-256；`assets:check` 验证生成结果与锁定依赖一致。
- Development/Test 使用普通 StaticFiles storage；Production 使用 Django `ManifestStaticFilesStorage`，`collectstatic` 生成内容哈希文件名及 manifest。
- 新增 Tailwind watch smoke script、静态资源构建 script，以及原子化的 `verify_steps_17_18.py` 联合验收入口。
- 联合验收会执行锁定 npm 安装、锁定 Playwright Chromium 安装、静态资源 build/check、Tailwind watch smoke、完整 pytest、migration check、Django check、Ruff lint/format 和 Production `collectstatic`。

### 联合验收结果

- 项目负责人于 2026 年 10 月 24 日至 25 日期间运行 `python -m uv run --env-file .env python scripts/verify_steps_17_18.py`，最终完整通过。
- `npm ci --ignore-scripts` 安装 61 个 package，npm audit 报告 `0 vulnerabilities`；项目锁定的 Playwright 1.64.1 成功安装 Chromium、Headless Shell、FFmpeg 和 Winldd。
- Tailwind production build、vendor hash check 和 Tailwind watch smoke 全部通过。
- 完整 pytest 套件共 171 个测试，全部通过，其中包含真实 Playwright 浏览器测试。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；本次修改的 9 个 Python 文件通过 Ruff format check。
- Production `collectstatic` 使用 manifest storage 成功完成；联合脚本最终输出 `Step 17–18 acceptance gate passed.`。

### 测试期间的针对性修补

- 首次项目负责人运行暴露 Windows 默认 GBK 无法解码 Node/Chromium UTF-8 输出，导致读取线程失败并以次生 `NoneType` 错误遮蔽真实原因；浏览器测试随后显式使用 UTF-8 并安全合并可空 stdout/stderr。
- 解码修补后确认真实环境问题为缺少 `chromium_headless_shell-1248`；联合验收脚本加入项目本地锁定 Playwright 的 `install chromium`，使同一验收入口能够补齐对应浏览器运行时。
- 上述修补只涉及测试输出处理和可重复测试环境准备，没有放宽断言或改变生产认证行为。

### 当前边界

- HTMX 与 MapLibre GL JS 已作为锁定本地资产建立，但尚未用于未实施的动态页面或地图功能。
- Home 仍是英文占位内容；About、Events、Members 与 Locations 页面、Logo 和 University Branding 均未在本步提前实施。
- `static/css/site.css` 和 `static/vendor/` 是受脚本管理的构建产物；修改来源应分别进入 `static_src/css/site.css` 或锁定 npm 依赖与复制清单。

### 下一步门槛

Step 17 与 Step 18 已作为同一验收单元通过项目负责人验证。不得开始 Step 19，直至项目负责人明确授权。

## Step 19 — 建立质量、安全与核心流程门禁

### 已完成

- 在 `pyproject.toml` 中启用 pytest strict config/markers、固定 `tests` 测试目录，并为 `apps` 与 `config` 配置 branch coverage；项目当前没有已批准的最低覆盖率数字，因此本步记录实际结果但不擅自设置 `fail_under`。
- 明确 Ruff 的 Python 3.13 target、行宽和 lint 规则，保留 Django settings wildcard import 与 migration class attributes 所需的最小文件级豁免；对全项目 Python 文件执行 Ruff format。
- 新建 `tests/conftest.py` 自动网络隔离 fixture：测试进程只允许 loopback、Django `testserver` 和当前测试数据库 host，其他 DNS 与 socket 连接立即失败。
- 为 Playwright browser context 增加同源请求限制并复用于既有认证 UI smoke；浏览器请求若离开当前 `StaticLiveServerTestCase` origin 会被中止并导致测试失败。
- 新增 Phase 1 核心浏览器流程，覆盖 Signup、Email verification、Account、POST logout、Username/Password 登录、本人 USU 信息更新、Magic Code 登录，以及具备专用权限的 Staff 通过 Django Admin 审核 USU ID。
- 新增质量与安全测试，扫描 Git tracked/unignored 文件中的高置信凭据与禁止提交的敏感文件，验证测试网络隔离、认证及身份敏感值不进入日志、公开页面不输出私有身份字段，并确认 Session cookie 保持 HttpOnly。
- 新增门禁失败传播测试，确认任一子命令非零退出会终止验收脚本并保留非零状态。
- 新建 `scripts/verify_phase_1.py` 作为 Phase 1 本地与 CI 共用的单入口门禁，依次执行锁定 npm 安装、Playwright Chromium 准备、静态资源 build/check、Tailwind watch smoke、Ruff lint/format、migration 漂移检查、Django check、干净 PostgreSQL test database 全套 branch coverage 测试、严格 Production deploy check 和 `collectstatic`。
- Production deploy check 使用专用的非部署占位 Secret，并以 `--fail-level WARNING` 执行；真实 Production Secret 仍必须由部署环境提供，门禁不会读取或输出部署凭据。

### 验证结果

- 项目负责人于 2026 年 10 月 25 日运行 `python -m uv run --env-file .env python scripts\verify_phase_1.py`，单入口门禁完整通过并输出 `Phase 1 quality and security gate passed.`。
- `npm ci --ignore-scripts` 安装 61 个 package，npm audit 报告 `0 vulnerabilities`；锁定的 Playwright Chromium 准备成功。
- 静态资源 production build、vendor version/hash check 与 Tailwind watch smoke 全部通过。
- Ruff lint 报告 `All checks passed!`，Ruff format check 报告 78 个文件均已格式化。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 无问题。
- 使用 `pytest --create-db` 在干净 PostgreSQL test database 上运行 181 个测试，全部通过；coverage 启用 branch measurement，当前总覆盖率为 93%。
- Production `check --deploy --fail-level WARNING` 报告无问题；Manifest static `collectstatic` 成功完成。

### 测试与门禁调试期间的针对性修补

- 安全测试初次运行的三个失败来自测试实现与项目既有接口不一致：Email verification 使用了错误 URL name、身份更新后测试未刷新旧 User instance、网络拦截错误文案断言过窄。修正测试后 6 个安全与门禁测试全部通过，没有修改或放宽生产安全逻辑。
- Playwright 核心流程初次运行发现 Magic Code confirm URL 需要尾斜杠、Account heading locator 需要 exact match，并发现 Profile 字段实际命名为 `is_published`；按真实路由、无障碍名称和模型字段修正测试后，5 个浏览器测试全部通过。
- 首次直接以系统 Python 启动门禁时，系统解释器没有项目 Ruff；确认标准入口必须由 `uv run` 启动，以保证使用锁定的项目虚拟环境。
- 严格 Production deploy check 首次暴露门禁脚本写入了错误的 Secret 环境变量名；由 `SECRET_KEY` 更正为 settings 实际读取的 `DJANGO_SECRET_KEY` 后，warning-level deploy check 干净通过。该修补加强了门禁，未绕过 Django security check。

### 当前边界

- 单入口脚本可由本地开发与任意 CI provider 调用；仓库尚未确定 CI provider，因此本步没有擅自新增 provider-specific workflow 文件。
- 当前 93% 是实测 branch coverage，不是已批准的长期最低阈值；后续如需 `fail_under`，应先由项目负责人确认目标。
- 外部网络隔离覆盖 pytest Python 进程和项目 Playwright browser contexts；门禁准备依赖时的 `npm ci` 与 Playwright browser installation 仍需要 package registry/CDN 网络访问。
- Step 19 只建立 Phase 1 门禁，没有实现 Step 20 的文档收尾、运营准备或 Phase 2 功能。

### 下一步门槛

Step 19 已通过项目负责人验证。不得开始 Step 20，直至项目负责人明确授权。

## Step 20 — Phase 1 端到端验收

### 已完成

- 将 `README.md` 从最简项目说明扩展为可执行的英文开发指南，记录工具前置条件、首次安装、日常开发、migration、静态资源构建、Development server、自动验收、人工走查、安全边界和项目目录职责。
- README 明确本项目使用中性 NULDL Branding，不声明 University 官方身份，也不包含未经批准的 University Logo、Crest 或其他品牌资产。
- 新建 `scripts/accept_phase_1.py` 作为 Step 20 端到端验收入口；脚本启动并等待 PostgreSQL，在临时目录建立全新 uv environment，从 `uv.lock` 安装依赖，执行 Development migrations 和 Step 19 完整门禁，再启动本机 Django Development server 并运行 Playwright smoke test。
- 验收脚本使用动态 loopback port 和 `--noreload` 启动 Django，成功或失败都会终止 server；任一安装、migration、门禁、启动或浏览器检查失败均向调用方传播非零结果。
- 新建 `tests/browser/development-server-smoke.mjs`，在 `1440 × 900` desktop 与 `390 × 844` mobile viewport 验证 Home、Signup、Login、Account 登录保护、CSS 加载、无水平溢出、无 page error、同源网络边界及未授权 Branding 边界。
- 新建 `tests/test_phase1_acceptance.py`，验证验收子命令失败传播、运行中 server 的正常终止，以及 README 包含完整的新环境安装、验收命令和人工核心流程说明。
- 使用合成身份完成 README 人工走查，覆盖注册、Email verification、POST logout、Username/Password 登录、Account USYD/USU ID 更新、Magic Code、Django Admin USU ID 审核，以及 desktop/mobile、键盘和 Branding 检查。

### 验证结果

- 项目负责人于 2026 年 10 月 25 日运行 `python -m uv run --env-file .env python scripts\accept_phase_1.py`，最终输出 `Phase 1 end-to-end acceptance passed.`。
- 临时全新 uv environment 使用 Python 3.13.17，从锁文件成功安装 17 个 package；没有复用项目 `.venv` 作为验收 Python 环境。
- PostgreSQL container 成功进入 healthy 状态，Development migrations 报告 `No migrations to apply`。
- `npm ci --ignore-scripts` 安装 61 个 package，npm audit 报告 `0 vulnerabilities`；Playwright Chromium、静态资源 production build、vendor hash check 和 Tailwind watch smoke 全部通过。
- Ruff lint 通过，Ruff format check 报告 80 个文件均已格式化；migration 漂移检查、Django system check 和 warning-level Production deploy check 均无问题。
- 在干净 PostgreSQL test database 上运行 184 个测试，全部通过；branch coverage 保持 93%。
- Production manifest `collectstatic` 成功；本机 Django Development server 的 desktop/mobile Playwright smoke test 通过。
- 项目负责人随后确认 README 人工走查成功。
- 仓库复查未发现可提交的 `.env`、数据库文件、真实会员资料、用户上传文件或 Secret；`git diff --check` 无格式错误，仅保留既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次 Step 20 针对性测试为 8 个通过、1 个失败；失败来自 README 内容测试将 `Email verification` 的首字母大小写当作语义要求，而文档已包含对应流程。关键词检查改为 Unicode-aware 大小写不敏感比较后，9 个针对性测试全部通过；README 内容和产品行为未改变。
- 完整端到端验收首次运行即通过，没有生产代码、认证规则、权限或数据模型修补。

### Phase 1 退出门槛结论

- 空或现有 PostgreSQL 数据库均可执行全部 migrations，且 model/migration 无漂移。
- 注册、Email verification、Password login、Magic Code、Account update、POST logout 和 USU ID Admin review 已通过服务端、浏览器和人工验收。
- USYD/USU ID 状态、专用审核权限、审核人和审核时间、默认隐藏 Profile 与公开数据边界均受自动化测试保护。
- Tailwind production build、本地静态资产、Ruff、Django checks、Production deploy check、pytest、Playwright 和 README 新环境指引全部通过。
- 仓库 Secret、真实数据、上传内容和未经批准 University Branding 边界通过检查。

### 当前边界与后续门槛

- Phase 1 已完成。Phase 2 仍为 `Not started`，本步骤没有实现 Home 正式内容、About、Beginners & Safety、Risk Notice、error pages、metadata、sitemap 或其他 Phase 2 功能。
- Risk Notice、University Branding、Logo、地点、正式 hosting/SMTP/media/monitoring/map provider、数据保留和中文版本等外部事项仍按 Roadmap 保持待确认，不因 Phase 1 完成而被隐式决定。
- `implementation.md` 只保留 Phase 2 概要；必须由项目负责人明确授权后，才能基于真实 Phase 1 架构展开 Phase 2 微步骤并开始实施。

## Step 21 — 建立公开页面基础与品牌命名

### 已完成

- 扩展全局 `base.html`，增加每页可覆盖的 description、robots、Open Graph title、Open Graph description 和额外 head 内容区块，并输出环境派生的当前页面 Open Graph URL。
- 将全局默认标题、Home、Account 和全部项目认证页面标题中的对外品牌统一为 `NULDL Armwrestling Club`；Home 占位说明与 Footer 同步使用完整品牌名称。
- 将 Header 文字品牌改为 `NULDL Armwrestling Club`，保留 Home、Anonymous 的 Login/Signup 及 Member 的 Account 行为和当前页标识。
- 使用原生 `details` 与 `summary` 建立移动导航；桌面和禁用 JavaScript 时默认提供全部有效链接，Alpine.js 只在手机宽度初始化时收起菜单，后续展开与关闭继续使用浏览器原生键盘行为。
- Header 继续只链接已经存在的 Home、认证和 Account 路由，没有提前加入 About、Events、Members 或 Locations。
- 在 Tailwind source 中建立可复用的 public page、section、card、CTA 和 status 样式，并增加 desktop/mobile 导航、Focus、菜单开关和布局规则；重新生成 minified `static/css/site.css`。
- 扩展 `tests/test_global_templates.py`，覆盖 metadata、唯一 title、完整品牌名称、导航 disclosure、Anonymous/Member 差异、当前页状态和不存在失效链接。
- 新建 `tests/test_public_foundation_browser.py` 与 `tests/browser/public-foundation.mjs`，以真实 Django live server 和 Chromium 覆盖 desktop/mobile 导航、键盘 Focus、菜单展开关闭、无水平溢出、禁用 JavaScript、page error 与外部网络边界。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor hash 检查和 Tailwind production build 均通过，并再次重复运行确认结果可复现。
- 项目负责人运行全局模板、公开页面浏览器、认证模板和认证浏览器专项测试，共 22 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 186 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 73 个文件均已格式化。
- `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次浏览器专项测试发现关闭状态的原生 `details` 在 desktop 会由浏览器隐藏导航子项。Header 改为标记默认 `open`，并只在 Alpine.js 已加载且处于手机宽度时移除 `open`；desktop 与无 JavaScript 场景因此始终保留基础链接，手机增强场景仍默认收起且可以原生键盘切换。
- 第二次浏览器专项测试确认导航显示已正常，剩余失败来自 `Join the Club` 同时匹配 Header 与 Home 占位 CTA。测试 locator 限定到 `Primary navigation` 后通过，没有修改产品行为或放宽断言。

### 当前边界与下一步门槛

- Step 21 只建立公开页面共享基础、品牌命名和响应式导航；Home 仍为占位内容，未加入 Logo、正式 Hero、训练内容或静态日程。
- About、Beginners & Safety、Draft Risk Notice、error pages、sitemap 和 Instagram Footer 尚未实施，仍属于 Step 22–26。
- 当前 metadata 提供安全的全局默认值与覆盖边界；Home、About 和 Beginners & Safety 的最终已确认 title、description 和完整 Open Graph 值在对应页面及 Step 26 实施。
- Step 21 已通过项目负责人验证。不得开始 Step 22，直至项目负责人明确授权。

## Step 22 — 完成 Home、Logo 与静态日程

### 已完成

- 将 Home 占位页替换为 `design_document.md` 已确认的正式英文内容，完成 Metadata、Hero、新手说明、四项训练内容、参与资格和 Upcoming Session。
- Hero 的 Anonymous 主要操作为 `Join the Club` 并进入 Signup；authenticated member 显示 `Account` 并进入本人账户页；两类用户均可通过普通页内链接进入 `New to Armwrestling?`。
- Upcoming Session 只展示 `1 December 2026`、`3:00–7:00 pm`、`Training Session` 和 `Venue details to be confirmed`，附已确认的后续信息说明；没有新增 Event model、报名状态、报名操作或 Events 链接。
- 将仓库外已批准的 `Logo_without_USYD.png` 按原始字节纳入 `static_src/images/brand/`；保留 1254 × 1254 RGB PNG、1,776,890 bytes 和 SHA-256 `1bc738b3a7af5719a296bc0aecc67f2ea943d1acf7eadb499c3dd28592308944`，未重新设计图形内容。
- 新增 `scripts/build_home_images.py`，使用锁定版 Pillow 确定性生成 480、800 和 1200px 方形 WebP；脚本在 build/check 时校验源图 hash、格式、尺寸与模式，并逐字节检查生成物是否过期。
- 将图片 build/check 接入 `package.json` 的 `static:build` 与 `static:check`；生成文件大小分别为 32,364、69,400 和 125,860 bytes，均显著小于原始 PNG。
- Home 使用 `<picture>`、响应式 `srcset`/`sizes`、明确宽高、方形比例和替代文本加载 Logo；Header 继续使用文字品牌，没有加入 University Branding。
- 扩展 Home、图片资产和全局模板测试，并新增 Playwright Home scenario，覆盖 desktop、mobile、无 JavaScript、Logo 加载及比例、无水平溢出、文字/CTA 可见性、CTA 目标、内容完整性和同源网络边界。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor assets、Home 图片逐字节可重复性检查和 Tailwind production build 全部通过。
- Step 22 Home、图片、浏览器、公开页面基础及全局模板专项测试共 17 个，全部通过。
- 完整 pytest 套件共 195 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 77 个文件均已格式化。
- `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- Step 22 浏览器测试、Home 内容测试和图片构建测试首次运行均通过。
- 相关回归测试最初有 1 个失败：Step 21 的全局模板测试仍固定断言旧 Home title。将该断言更新为已批准的 `NULDL Armwrestling Club | Training and Community` 及对应 Open Graph title 后，17 个专项及相关回归测试全部通过；生产页面和业务行为未因此修改。
- Ruff 首次检查只发现两个新 Python 文件的 import 排序，以及四个文件的格式差异；使用锁定 Ruff 机械修复后 lint 与 format check 全部通过，没有业务逻辑变化。

### 当前边界与下一步门槛

- Home 日程仍是明确的静态宣传内容，不代表活动报名开放，也不建立 Phase 4 Event 领域能力。
- Header 保持文字品牌；源 Logo 只用于 Home 大尺寸展示，公开响应及生成文件名不包含受限 University Branding。
- About、Beginners & Safety、Draft Risk Notice、error pages、sitemap 和 Instagram Footer 仍未实施，属于 Step 23–26。
- Step 22 已通过项目负责人验证。不得开始 Step 23，直至项目负责人明确授权。

## Step 23 — 完成 About 与 Beginners & Safety

### 已完成

- 在 `apps.core` 中新增 `/about/` 与 `/beginners-safety/` 两个具名公开路由、对应 views 和独立模板，不新增 Model、migration 或业务 API。
- About 使用已批准的英文 Metadata、介绍、`Our Purpose`、`What We Do`、`Who Can Participate` 与 `How We Train` 内容，明确区分 student-led club 与未声明的 University affiliation。
- Beginners & Safety 使用已批准的英文内容，覆盖 induction、supervised practice、dedicated armwrestling equipment、主要风险及停止训练条件；没有提前加入 Step 24 Draft Risk Notice 页面或链接。
- 两个页面均按认证状态在服务端提供 CTA：Anonymous 进入 Signup，authenticated member 进入 Account；普通链接和页面内容在禁用 JavaScript 时仍可用。
- Header 加入 About 与 Beginners & Safety 导航，并使用既有 URL name 机制输出 `aria-current="page"`；未加入 Events、Members、Locations 或 Risk Notice 等尚未实施的入口。
- 扩展公开内容页面样式，支持正文宽度、内容卡片、步骤列表、安全提示与 CTA，并重新生成提交的 minified CSS。
- 新增 Django 页面测试和 Playwright scenario，覆盖路由、模板、Metadata、获准文案、受限内容、导航、CTA、desktop/mobile、键盘、200% content zoom、无 JavaScript、无横向溢出及同源网络边界。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor assets、Home 图片可重复性检查和 Tailwind production build 全部通过。
- Step 23 与相关公开页面回归专项测试共 26 个，全部通过。
- 完整 pytest 套件共 207 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 79 个文件均已格式化。

### 测试期间的针对性修补

- 首次专项运行有 3 个失败：两个 Django 测试错误读取 `HttpResponse.template_name`，改为从测试客户端记录的 `response.templates` 检查模板；一个 Playwright 可读性 helper 将已折叠移动导航中的隐藏链接误判为裁切，改为跳过 `checkVisibility()` 为 false 的元素。
- 上述修补只修正测试实现，没有改变生产页面、内容或业务行为。
- Ruff format check 首次发现一个新增测试文件存在两处机械格式差异；使用锁定 Ruff 格式化后通过，没有业务逻辑变化。

### 当前边界与下一步门槛

- About 与 Beginners & Safety 是公开宣传信息，不建立活动报名、会员目录、地点地图或 Safety 版本化领域能力。
- 页面不声明 USYD/University affiliation，不公开联系邮箱或具体训练地点；安全内容不构成已确认的正式 Risk Notice。
- Draft Risk Notice、error pages、sitemap 和 Instagram Footer 仍未实施，属于 Step 24–26。
- Step 23 已通过项目负责人验证。不得开始 Step 24，直至项目负责人明确授权。

## Step 24 — 实施 Draft Risk Notice 环境隔离

### 已完成

- 在 `apps.safety` 中新增 `/risk-notice/` 具名 URL、view 和独立 template；路由保持可反向解析，但 view 只在当前环境明确允许时渲染，否则返回 404。
- 在公共 settings 中将 `RISK_NOTICE_DRAFT_VISIBLE` 默认设为关闭；Development 明确开启，Test 默认关闭，Production 强制关闭且不读取同名环境变量。
- 新增 `config.settings.preview`，继承 Production 安全配置并要求显式提供 `RISK_NOTICE_DRAFT_VISIBLE`；未提供开关时拒绝加载，获准 Preview 可通过明确的 `true` 值开启 Draft。
- 在 `.env.example` 中只以注释形式说明 Preview 专用开关，没有改变本地 Development 的既有启动要求，也没有提供 Production 开启路径。
- Draft 页面逐字采用 `design_document.md` 已确认的四段当前正文，包括源文本中重复的 acknowledgement；同时显示 `DRAFT — NOT APPROVED FOR PARTICIPATION USE`、指定说明文字及 `noindex, nofollow`。
- 新增只暴露 Draft 可见性 Boolean 的 template context processor。开启时 Header 显示 `Draft Risk Notice`，Beginners & Safety 显示 `Read the Draft Risk Notice`；关闭时公开页面不输出上述链接。
- 页面没有 POST、checkbox、确认、报名、Event、RiskNoticeVersion、Model 或数据库访问；本步没有创建 migration，也没有改动责任限制文本。
- 新增 Django 环境及页面测试和 Playwright scenario，覆盖 Development、Preview、Production、默认关闭、直接 URL、逐字正文、重复 acknowledgement、banner、robots、条件导航、Beginners CTA、无数据查询、无表单，以及 desktop/mobile、键盘、无 JavaScript、布局和同源网络边界。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor assets、Home 图片可重复性检查和 Tailwind production build 全部通过。
- Step 24 与相关公开页面回归专项测试共 27 个，全部通过。
- 完整 pytest 套件共 216 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 85 个文件均已格式化。
- `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次本地专项运行有 1 个失败：零查询断言使用查询捕获器，但测试没有声明 pytest database fixture。为该测试补充 `django_db` 标记后，零查询断言和全部专项测试通过；生产 view、template 和 settings 行为未修改。
- Ruff 首次检查只发现新增测试文件的 import 排序与一处机械格式差异；使用锁定 Ruff 整理后 lint 与 format check 全部通过，没有业务逻辑变化。

### 当前边界与下一步门槛

- 当前 Risk Notice 仍是只供 Development 和获准 Preview 审阅的静态 Draft，不是最终参与条款，也不建立 Phase 4 的版本管理或报名确认能力。
- 项目尚未建立 sitemap；关闭 Draft 时直接 URL 返回 404，Header 与页面 CTA 均不产生可发现链接。Step 26 建立 sitemap 时仍必须排除 Draft Risk Notice。
- Production 强制关闭 Draft，无法通过 `RISK_NOTICE_DRAFT_VISIBLE` 环境变量公开正文。
- 403、404、500 页面、正式 sitemap 和 Instagram Footer 仍未实施，属于 Step 25–26。
- Step 24 已通过项目负责人验证。不得开始 Step 25，直至项目负责人明确授权。

## Step 25 — 建立 403、404 与 500 页面

### 已完成

- 在 `apps.core.views` 中新增 403、404 与 500 handlers，并在项目根 URLConf 显式注册 `handler403`、`handler404` 和 `handler500`。
- 新增三个继承全局页面壳的英文错误模板，分别使用 `Access Denied`、`Page Not Found` 和 `Something Went Wrong`，保持唯一 H1、项目 Header/Footer、现有 CSS 及明确的 `Return Home` 操作。
- handlers 保持正确的 403、404 与 500 HTTP 状态码，不将接收到的 exception 内容传入 template context，也不输出 traceback、异常类型、内部路径、Secret、技术细节或虚构联系方式。
- 错误页面全部使用普通 HTML link；返回 Home、Header 和 Footer 在 JavaScript 关闭时仍可使用，没有增加错误监控 Provider、外部资源或客户端路由。
- 新增隔离的测试 URLConf，以真实 `PermissionDenied`、缺失路由和未处理异常触发三个 Django handlers，不向生产 URL 暴露合成错误入口。
- 新增 Django handler 测试和 Playwright scenario，覆盖状态码、模板、页面标题、唯一 H1、Home link、CSS、敏感内容隔离、desktop/mobile、键盘 Focus、无 JavaScript、无水平溢出及同源网络边界。
- 本步没有新增 Model、migration 或配置变量，也没有修改 Step 24 Draft Risk Notice 或实现 Step 26 sitemap、最终 Metadata 与 Footer 内容。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor assets、Home 图片可重复性检查和 Tailwind production build 全部通过。
- Step 25 错误页面与既有 Admin/Account 权限回归测试共 31 个，全部通过。
- 完整 pytest 套件共 221 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 88 个文件均已格式化。
- `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次专项运行中 403、404、三个既有 Admin 权限测试及浏览器 403 场景失败。根因是 Django 通过关键字 `exception=` 调用 403/404 handler，而初始 handler 将该参数命名为 `_exception`，触发 `TypeError` 并转为 500。
- 将两个 handler 的参数名改为 Django 要求的 `exception`，并在函数内明确丢弃，不将异常对象传入页面。修补后错误页面及权限回归共 31 个测试全部通过；既有权限规则没有改变。
- Ruff 首次检查只发现新增测试文件的 import 排序和 handler 的机械格式差异；使用锁定 Ruff 整理后通过，没有业务逻辑变化。

### 当前边界与下一步门槛

- 错误页面提供一致、安全的公开恢复界面，但不建立错误监控、事件上报或用户支持联系方式；相关 Provider 仍由 Phase 6 决定。
- Step 25 只建立错误 handlers 与页面，不实施 sitemap、Instagram Footer 或 Phase 2 最终 metadata 收尾。
- Step 25 已通过项目负责人验证。不得开始 Step 26，直至项目负责人明确授权。

## Step 26 — 完成 Metadata、Open Graph、Sitemap 与 Footer

### 已完成

- 为 Home、About 和 Beginners & Safety 固定已确认的英文 title、description，以及通用 Open Graph type、site name、页面 title、description 和 URL。
- Open Graph URL 由当前 request 构造；最终域名尚未确认，因此没有加入 canonical link，也没有硬编码候选域名或测试 host。
- 在 `apps.core` 建立 `/sitemap.xml`，使用显式 URL name allowlist，只输出 Home、About 和 Beginners & Safety 三个 Production 公开页面的绝对 URL。
- Draft Risk Notice 无论环境开关是否开启都不进入 sitemap；认证、Account、Admin、错误页面及后续 Phase 路由同样不在 sitemap 中。
- Footer 加入已确认的 Instagram `@nuldl_armwrestlingclub` 及 HTTPS 目标，不公开联系邮箱，也不加入未经批准的 University Branding。
- 新增 `tests/test_public_metadata_sitemap_footer.py`，覆盖准确 metadata、环境派生 Open Graph URL、canonical host 边界、sitemap XML 与 allowlist、Draft 排除、Footer 文本和目标，以及敏感 Branding/联系信息边界。
- 本步没有新增 Model、migration、配置变量、外部资源或后续 Phase 功能。

### 验证结果

- 项目负责人运行 `npm.cmd run static:check`，vendor assets、Home 图片可重复性检查和 Tailwind production build 全部通过。
- Step 26 专项及相关页面回归测试共 44 个，全部通过。
- 完整 pytest 套件共 230 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 89 个文件均已格式化。
- `git diff --check` 未发现格式错误，仅报告 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次专项测试即 44 个全部通过，完整测试即 230 个全部通过，没有功能性测试失败。
- Ruff 首次检查只发现新增和调整文件的 import 排序与机械换行差异；使用锁定 Ruff 整理后通过，没有业务逻辑变化。

### 当前边界与下一步门槛

- sitemap 使用明确 allowlist，不从全部 URLConf 自动发现页面；后续新增公开页面必须经过对应阶段确认后显式加入。
- 正式 canonical host 仍待最终域名确认；当前 Open Graph URL 安全地跟随部署环境 request。
- Step 26 已通过项目负责人验证。不得开始 Step 27，直至项目负责人明确授权。

## Step 27 — 完成响应式与 Accessibility 验证

### 已完成

- 新增统一 Phase 2 Playwright accessibility 场景，覆盖 Home、About、Beginners & Safety、Draft Risk Notice，以及真实 403、404 和 500 页面。
- 在 desktop、mobile、200% 内容放大、JavaScript disabled 和 `prefers-reduced-motion` 场景下检查全部目标页面。
- 统一检查 Header、移动菜单、Hero、Logo、CTA、长文、安全列表、Draft banner、Footer 和错误页面的可用性。
- 检查语义 landmarks、唯一 H1、Heading 顺序、link name、图片替代文本、键盘顺序、可见 Focus、Focus 位置和移动菜单键盘操作。
- 检查至少 24px 的可见交互目标、文本重排、内容裁切、水平溢出、Logo 加载、关键文字与 Focus 对比度，以及 reduced-motion 时长限制。
- 复用既有 `browser-support.mjs` 同源网络隔离，统一确认浏览器没有 page error 或外部 HTTP(S) 请求。
- 新增 `tests/test_phase2_accessibility_browser.py`，通过开启 Draft、关闭 Debug 并复用隔离 error URLConf 的 `StaticLiveServerTestCase` 启动统一场景。
- 本步没有修改生产 template、CSS、Model、migration、依赖或环境配置，也没有引入新测试框架或外部 accessibility 服务。

### 验证结果

- 项目负责人运行 Step 27 专项测试，共 1 个测试，全部通过。
- Phase 2 accessibility、既有公开页面及认证浏览器回归共 7 个测试，全部通过。
- 完整 pytest 套件共 231 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过。
- 开发者侧另行确认静态资产检查、Node.js 语法、差异格式检查及同源 Playwright 场景通过。

### 测试期间的针对性修补

- 新增 Playwright 场景首次直接运行即通过，没有发现需要修补的生产 accessibility 阻塞。
- 开发者首次启动正式 pytest 时，Docker Desktop daemon 未运行，PostgreSQL 连接在测试建立阶段超时；该环境问题未进入测试主体。项目负责人启动环境后，专项、浏览器回归和完整测试均通过。

### 当前边界与下一步门槛

- 本步提供针对已实施 Phase 2 页面和当前组件的自动化 WCAG 2.2 AA 风险检查，不构成对全部 WCAG 成功标准的形式化认证。
- Draft Risk Notice 继续只在明确允许的非正式环境可见；统一场景通过测试设置开启 Draft，不改变 Production 强制关闭边界。
- Step 27 已通过项目负责人验证。不得开始 Step 28，直至项目负责人明确授权。

## Step 28 — 完成 Phase 2 质量门禁与阶段验收

### 已完成

- 新增 `scripts/verify_project.py` 作为跨阶段共享项目门禁，统一执行锁定前端依赖与 Chromium 准备、静态资源构建及检查、watch smoke、Ruff lint/format、migration drift、Django system check、干净 PostgreSQL branch coverage 测试、Production deploy check 和 manifest `collectstatic`。
- 将 `scripts/verify_phase_1.py` 保留为调用共享门禁的兼容入口，避免既有本地与 CI 调用失效。
- 新增 `scripts/accept_phase_2.py`，在 OS 临时目录创建全新锁定 uv environment，等待 Docker PostgreSQL、执行 migration 与共享门禁，再启动真实 Development server 并运行 Phase 2 desktop/mobile browser smoke；脚本在成功或失败后均清理 server 和临时 environment。
- 新增 `tests/browser/phase2-development-smoke.mjs` 与 `tests/test_phase2_acceptance.py`，覆盖公开页面、Draft 环境分支、错误页、认证入口、静态资源、同源网络边界、失败传播和清理行为。
- 更新 `tests/test_quality_gate.py` 与 `README.md`，使共享门禁、Phase 2 自动验收及人工走查成为后续开发者的明确入口。
- 根据阶段人工走查完成 Home、About 与 Beginners & Safety 的获准文案、CTA 显示条件和版式收尾，并同步 `design_document.md`。About 匿名 `Join` 按钮最终占内容宽度 90%，高度较上一版降低 15%；登录后不显示该 CTA。

### 验证结果

- 项目负责人首次在全新环境运行 Phase 2 端到端验收：锁定安装、PostgreSQL migration、静态资源 build/check/watch、Ruff lint/format、migration drift、Django check、Production deploy check、collectstatic、共享项目门禁和 Development browser smoke 全部通过。
- 该次完整 pytest 共 234 个测试全部通过，branch coverage 为 94%，终端最终报告 `Phase 2 end-to-end acceptance passed.`。
- 人工反馈修改后，开发者侧专项 Django 页面测试 24 个和相关 Playwright 浏览器测试 4 个全部通过；`static:check`、Ruff lint/format 与差异格式检查通过。
- 浏览器实测 About `Join` 按钮字体为 32px、高度约 74.80px、宽度约为内容区的 90%，水平偏移约 0.01px，外层边框为 0；项目负责人随后确认最终人工验收完成。

### 验收期间的针对性修补

- 初始 Step 28 全新环境门禁直接通过，没有自动化验收阻塞。
- 人工走查后按获准范围调整公开页面内容与 CTA；没有扩展 Model、migration、认证规则、Provider 或后续 Phase 功能。
- About 按钮居中断言最初以包含左侧提示边框的父容器测量，几何中心受到装饰边框影响；断言改为测量实际 action wrapper 后通过，生产布局规则未因此扩大。

### Phase 2 结论与边界

- Phase 2 的页面内容、响应式、Accessibility、错误处理、Metadata、Sitemap、Footer、共享门禁、全新环境验收及人工走查均已完成，阶段状态更新为 `Complete`。
- Risk Notice 最终文本、University Branding 批准、地点详情、Production 域名与 Provider、数据保留规则及中文版本仍属于已记录的外部依赖或后续阶段事项，不影响本阶段已定义退出门槛。
- Phase 3 尚未开始；本步未实施或展开 Phase 3 功能。

## Step 29 — 建立本人 Profile 编辑入口与所有权边界

### 已完成

- 在 `apps.members` 新增 `/profile/edit/` 命名路由、登录保护的编辑 view 和独立 Profile 编辑模板，并从项目根 URLConf 接入。
- 编辑 view 只通过 `request.user` 读取当前会员的一对一 MemberProfile，不接受 URL、POST 或表单中的目标 User/Profile 标识；Profile 不存在时返回 404。
- Anonymous 访问会进入既有登录流程；已认证但邮箱未验证的账户返回 403；停用账户不能进入编辑页面。
- `MemberProfileForm` 只包含 Display name、Avatar、Bio、Experience level、Preferred arm、Instagram Username 和一个 HTTPS social URL；移除 `is_published`，并继续排除 User、管理员隐藏状态、Executive role 和时间戳。
- 保存成功采用 redirect-after-POST 并显示英文成功消息；普通编辑不会改变 `is_published`、`is_hidden_by_admin` 或 `executive_role`，也不依赖 JavaScript。
- 增加 Display name 忽略大小写的表单级重复检查，使错误与字段关联，同时保留现有 PostgreSQL 唯一约束作为最终保护；Instagram 输入允许并清理开头的 `@`。
- Account 页面新增 `Edit profile` 入口；编辑模板使用现有全局页面壳、表单字段组件、CSRF 和 multipart form，为 Step 30 的 Avatar 生命周期工作保留同一入口。
- 新增 `tests/test_profile_edit.py`，并更新既有 MemberProfile form 测试，覆盖访问资格、本人对象绑定、允许字段、验证错误、伪造字段、状态保持、Account 入口和无 JavaScript POST。

### 验证结果

- 项目负责人运行 Step 29、MemberProfile 与 Account 专项回归共 46 个测试，全部通过。
- 项目负责人运行完整 pytest 套件共 245 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 对 `manage.py`、`config`、`apps`、`tests` 和 `scripts` 全部通过；Ruff format check 报告 96 个文件均已格式化。
- 开发者侧 `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次专项运行因 Docker Desktop 未启动而无法连接；启动后确认 Windows 将 `5432` 纳入动态保留端口范围。仅在验证环境中将主机映射临时改为 `15432`，容器内端口和 named volume 未改变；项目文件及 `.env` 未被自动改写。
- 数据库连接恢复后的首次运行为 35 个通过、11 个失败：10 个新增测试遗漏 `django_db` 标记，另 1 个失败来自 Instagram 清理函数未处理空值。补充测试标记并将空值安全规范化后，剩余 2 个行为差异继续检查。
- 第二次运行为 44 个通过、2 个失败：Display name 冲突由数据库约束生成通用错误，HTTPS URL 已正确拒绝但错误文案由 Django validator 决定。为 Display name 增加表单级字段错误，并将 URL 测试保持为行为断言；最终 46 个专项与 245 个完整测试全部通过。

### 当前边界与下一步门槛

- Step 29 只建立本人 Profile 编辑和所有权边界。Avatar 替换/删除后的文件清理、metadata 提示、方形展示及 Development media serving 仍属于 Step 30。
- Preview、Publish、Unpublish、公开 Members 列表、Member detail 和 Admin hide/unhide 尚未实施；编辑保存不会直接改变公开状态。
- Step 29 已通过项目负责人验证。不得开始 Step 30，直至项目负责人明确授权。

## Step 30 — 完成 Avatar 上传、删除与文件清理

### 已完成

- 在既有 MemberProfile 编辑流程中增加明确的 `Remove current avatar` 控制；上传新文件与主动删除不能在同一次提交中同时选择。
- 保留 JPG、PNG、WebP、5 MB、声明 MIME 和 Pillow 真实内容验证，并补充扩展名必须与实际图片格式匹配的检查。
- 上传验证成功后直接保存原始字节，不执行 EXIF 转向、metadata 删除、缩放或格式转换。
- 新增受控保存 service：替换或主动删除成功后才删除旧 Avatar；数据库保存失败时回收已经写入的新文件并保留当前有效 Avatar。
- 对已保存 Avatar 执行验证后显式关闭 Django `FieldFile`，保证 Windows 可以立即替换或删除文件；新上传对象在保存前保持可读。
- Profile 编辑页展示当前 Avatar、方形 `object-fit: cover` 图片、删除控件，以及已确认的 metadata 隐私提示；页面继续使用普通 multipart POST。
- Development 使用 `/media/` 和 Django local media helper 提供本地文件；`DEBUG=False` 时不注册该 helper，Production persistent media storage 仍留待 Phase 6 决定。
- 将仓库根 `media/` 加入 `.gitignore`；全部 Avatar 测试使用隔离临时目录，不提交上传文件。
- 新增 Avatar 生命周期 Django 测试、测试专用 media URLConf 和 Playwright desktop/mobile 场景，覆盖原始字节、大小边界、伪装扩展名、错误 MIME、损坏图片、替换、删除、失败保护、文件清理、隐私提示及方形展示。

### 验证结果

- 项目负责人运行 Step 30、Profile 编辑与 MemberProfile 专项回归共 45 个测试，全部通过。
- 项目负责人运行完整 pytest 套件共 256 个测试，全部通过，其中包含 Avatar Playwright 浏览器场景。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 全部通过，Ruff format check 报告 99 个文件均已格式化。
- `npm.cmd run static:check` 完成 vendor、Home images 和 Tailwind production build 检查。
- 开发者侧 `git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次真实专项回归为 44 个通过、1 个失败：表单把已存在的 Avatar 当作本次新上传，错误阻止单独删除。冲突判断改为只检查 `request.FILES` 对应的实际新文件后，删除流程进入保存阶段。
- 第二次回归暴露 Windows 对已打开文件的删除限制。Pillow 图片对象关闭后，持久化 Django `FieldFile` 仍保持打开；validator 现只对 `_committed` 的已保存文件在验证后关闭 `FieldFile`，同时保持新上传文件可供后续保存。修补后 45 个专项及 256 个完整测试全部通过。
- 初次开发者测试在沙箱内因 Docker API 与本机 PostgreSQL 端口访问受限而未进入测试主体；在获准的本地数据库权限下重跑后得到上述有效测试结果。

### 当前边界与下一步门槛

- Step 30 只完成 Avatar 验证、原文件保存、替换/删除清理、编辑页展示及 Development media serving；没有选择或实现 Production media provider。
- Preview、Publish、Unpublish、公开 Members 列表、Member detail 和 Admin hide/unhide 仍未实施。
- Step 30 已通过项目负责人验证。Step 31 尚未开始，必须等待项目负责人明确授权。

## Step 31 — 建立 Preview、Publish 与 Unpublish 流程

### 已完成

- 新增仅限当前有效会员访问的 `/profile/preview/`，继续按 authenticated User 查询一对一 MemberProfile，不接受客户端提供的 User 或 Profile 标识。
- Preview 对未发布资料同样可用且不会改变状态；页面使用可复用公开字段组件，按未来 Member detail 的字段顺序展示公开名称、Username、Avatar、Experience level、Preferred arm、Bio 和社交链接。
- 新增独立 `/profile/publish/` 与 `/profile/unpublish/` confirmation 页面；GET 只展示确认信息，状态转换仅由带 CSRF 的 POST 执行。
- 新增事务化 `set_profile_publication` service，通过 row lock 更新当前会员的 `is_published`，重复 Publish 或 Unpublish 保持幂等，并使用固定站内 redirect 忽略外部 `next`。
- Publish confirmation 明确列出将公开的字段、未来 `/members/<username>/` URL、Display name 为空时的 Username 回退，以及原始 Avatar metadata 可能公开的风险。
- 管理员隐藏状态始终优先：会员 Publish 不会修改 `is_hidden_by_admin`，隐藏资料仍不进入公开 queryset；本人页面只显示不泄露管理员身份或后台记录的中性提示。
- Profile 编辑页新增 `Preview profile` 入口；普通编辑保存继续不改变发布或管理员状态。
- 新增 `tests/test_profile_publication.py`，覆盖 Anonymous、未验证及停用账户、本人所有权、未发布 Preview、GET 无副作用、Publish/Unpublish、重复 POST、CSRF、开放 redirect、管理员隐藏、敏感字段隔离和编辑入口。
- 本步没有新增 Model、migration、公开 Members 列表、公开 Member detail 或 Header Members 导航。

### 验证结果

- 项目负责人运行 Step 31、Profile 编辑与 Avatar 生命周期专项回归共 41 个测试，全部通过。
- 项目负责人运行完整 pytest 套件共 276 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`。
- Django system check 通过，无问题。
- Ruff lint 全部通过，Ruff format check 报告 100 个文件均已格式化。
- `npm.cmd run static:check` 完成 vendor、Home images 和 Tailwind production build 检查。
- 开发者侧同样通过 41 个专项、276 个完整测试及全部质量检查；`git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 当前边界与下一步门槛

- Preview 使用可复用展示组件，但本步没有建立公开 `/members/` 或 `/members/<username>/` 路由；confirmation 中的 Username URL 仅用于发布前告知。
- 公开 Members 目录、Header Members 导航、empty state 和卡片字段边界属于 Step 32，尚未开始。
- Member detail、Admin hide/unhide、Phase 3 统一 accessibility 与质量验收仍属于后续步骤。
- Step 31 已通过项目负责人验证。Step 32 尚未开始，必须等待项目负责人明确授权。

## Step 32 — 建立 Members 公开目录

### 已完成

- 新增公开 `/members/` 目录和命名路由 `members:list`；页面不要求登录，Anonymous 与 authenticated member 使用同一公开数据边界。
- 列表数据只从 `MemberProfile.objects.public()` 获取，并通过 `select_related("user")` 读取公开名称回退所需的 User；未发布、管理员隐藏、停用及邮箱未验证账户均被统一排除。
- 排序使用 Display name 或 Username 回退后的公开名称执行不区分大小写排序，并以不区分大小写的 Username、原始 Username 和主键作为稳定次序。
- Member 卡片只展示 Avatar 或非敏感首字母 fallback、Display name 或 Username、已填写的 Experience level 与 Preferred arm；`Not specified` 不输出。
- 页面提供明确 empty state；没有加入搜索、HTMX 筛选、分页、Member detail 链接或 sitemap 变更。
- Header 对 Anonymous 与 authenticated member 均加入 `Members` 导航，并在目录页面使用 `aria-current="page"` 标记当前项；普通链接在无 JavaScript 场景继续可用。
- 新增目录响应式 cards、方形 Avatar/fallback 和 empty-state 样式，并由 Tailwind CLI 重新生成提交的 minified CSS。
- 新增 `tests/test_member_directory.py`、`tests/test_member_directory_browser.py` 与 `tests/browser/member-directory.mjs`，覆盖公开 queryset、稳定排序、名称回退、字段白名单、empty state、导航、desktop/mobile、键盘、无 JavaScript、无横向溢出、浏览器错误及同源网络边界。

### 验证结果

- 项目负责人运行 Step 32 与相关 MemberProfile、发布、全局模板和公开页面回归共 70 个测试，全部通过。
- 项目负责人运行完整 pytest 套件共 285 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 全部通过，Ruff format check 报告 102 个文件均已格式化。
- `npm.cmd run static:check` 完成 vendor、Home images 和 Tailwind production build 检查。
- 开发者侧同样通过 70 个专项、285 个完整测试及全部质量检查；`git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次完整回归在既有 Phase 2 accessibility 浏览器门禁失败：Header 新增 `Members` 后，固定键盘 Tab 顺序仍预期直接聚焦 `Draft Risk Notice`，实际正确聚焦新增的 `Members`。
- 只在既有 accessibility 场景的预期导航顺序中加入 `Members`，没有放宽 Focus、可见性、触控目标或网络断言；随后 accessibility 与目录浏览器测试 2 个全部通过，完整 285 个测试全部通过。

### 当前边界与下一步门槛

- Step 32 只建立公开目录和摘要卡片，不提供 `/members/<username>/` 详情 URL；卡片当前不包含尚未存在的 detail link。
- Members 列表仍未加入 sitemap；按实施顺序，该列表与个人详情的搜索边界在 Step 33 统一处理。
- Member detail、Admin hide/unhide、Phase 3 统一 accessibility 与阶段质量验收仍属于后续步骤。
- Step 32 已通过项目负责人验证。Step 33 尚未开始，必须等待项目负责人明确授权。

## Step 33 — 建立 Member detail 与搜索边界

### 已完成

- 新增公开 `/members/<username>/` 详情路由和命名路由 `members:detail`；URL 使用保存的 Username，并执行区分大小写的精确匹配。
- 详情 view 只从 `MemberProfile.objects.public()` 查询，并通过 `select_related("user")` 取得公开 Username；未发布、管理员隐藏、账户停用、邮箱未验证、大小写不匹配及不存在的 Username 均进入相同 404 handler。
- 新增 Member detail template，并复用 Preview 的公开字段组件；详情页使用公开名称作为唯一 H1，展示 Username、Avatar/fallback、Bio、已填写的 Experience level 与 Preferred arm、Instagram Username 和一个 HTTPS social URL。
- `Not specified`、Email、USYD 声明、USU ID、审核信息、Executive role、时间戳和后台状态不进入公开详情输出；Bio 继续通过 Django 默认 escaping 与 `linebreaksbr` 作为纯文本呈现。
- Instagram 与其他社交链接使用 `target="_blank"` 和 `rel="noopener noreferrer"`；其他 social URL 继续受既有 HTTPS model/database 边界保护。
- Members 卡片的公开名称现在链接到稳定 Username detail URL；详情页提供返回 Members 的普通链接，Header 在目录和详情页均将 `Members` 标记为当前导航。
- 详情页沿用全局普通公开 `index, follow` robots 规则。显式 sitemap allowlist 新增 Members 列表，继续不枚举个人详情 URL。
- 新增 `tests/test_member_detail.py`，并扩展目录、sitemap 及 Playwright 测试，覆盖 URL 大小写、字段白名单、HTML escaping、安全外链、统一 404、卡片导航、直接 URL、mobile、无 JavaScript 和搜索边界。

### 验证结果

- 项目负责人运行 Step 33、目录、发布、sitemap 及浏览器专项回归共 43 个测试，全部通过。
- 项目负责人运行完整 pytest 套件共 290 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 全部通过，Ruff format check 报告 103 个文件均已格式化。
- `npm.cmd run static:check` 完成 vendor、Home images 和 Tailwind production build 检查。
- 开发者侧同样通过 43 个专项、290 个完整测试及全部质量检查；`git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 统一 404 测试最初按完整 HTML 字节比较响应；全局 Open Graph URL 会正常反映访问者已经请求的路径，因此不同 URL 的 `<head>` 不相同。断言收窄为比较 HTTP 404 与实际 `<main>` 正文，继续保证不同不可见原因不会通过状态码或正文泄露。
- 浏览器夹具最初生成包含连字符的 Instagram Username，违反既有 Username validator；测试数据改为合法下划线形式，生产验证规则未放宽。
- Member 卡片标题增加链接后，Playwright 的原始文本包含模板缩进空白；排序断言只对读取结果执行 `trim()`，仍严格验证两张卡片的显示顺序和名称。

### 当前边界与下一步门槛

- Step 33 只完成公开 Member detail 与 sitemap/search 边界，没有修改 Profile schema、发布规则或管理员权限。
- Admin hide/unhide、Phase 3 统一 accessibility 与阶段质量验收仍属于 Step 34–36。
- Step 33 已通过项目负责人验证。Step 34 尚未开始，必须等待项目负责人明确授权。

## Step 34 — 完成 Django Admin Hide/Unhide

### 已完成

- 收紧 `MemberProfileAdmin` change form：User、会员自述字段、`is_published`、创建时间和更新时间均为只读，只允许维护 `is_hidden_by_admin` 与 `executive_role`。
- 继续使用 Django 自动生成的标准 `members.change_memberprofile` 权限；没有增加专用 permission、自定义 action、隐藏原因字段、历史 model 或 migration。
- 禁用 MemberProfile Admin 的新增和删除入口，使后台职责限定为维护现有 Profile 的隐藏状态与 Executive role。
- Hide/Unhide 继续通过标准 Admin change form 保存，并由 Django `LogEntry` 记录字段修改。
- 隐藏操作不修改 `is_published`、会员自述内容、Profile 所属 User 或账户启用状态；公开 queryset 使隐藏资料从 Members 列表和 detail 同时消失。
- 被隐藏会员仍可登录、进入本人 Profile 编辑流程并执行 Unpublish；本人页面继续使用既有中性隐藏提示。
- 新增 `tests/test_member_profile_admin.py`，覆盖普通会员、无 change 权限 Staff、有标准 change 权限 Staff、Superuser、字段防伪造、Hide/Unhide、Executive role、Admin 日志和前后台状态边界。
- 更新既有 MemberProfile Admin 配置测试，使其固定仅有两个可编辑字段。

### 验证结果

- 项目负责人运行 Step 34 专项测试，共 9 个测试，全部通过。
- 项目负责人运行完整 pytest 套件，共 299 个测试，全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 全部通过；Ruff format check 报告 104 个文件均已格式化。
- 开发者侧相关 Admin、Profile 编辑、发布、目录与详情回归共 76 个测试全部通过；`git diff --check` 未发现格式错误，仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 初次专项回归为 73 个通过、3 个失败，均来自测试断言与 Django 标准表现不一致，生产权限和隐藏行为已生效。
- 无自定义 Model permission 在 Django metadata 中表现为空列表，测试由固定 tuple 类型比较改为验证其为空。
- Django Admin `LogEntry.get_change_message()` 返回可读字段名 `Is hidden by admin`，日志断言调整为验证实际标准消息，没有修改日志实现。
- Admin 保存成功消息会在同一 Staff session 的下一次页面响应中显示 Profile 名称；公开隐藏断言改用独立 Anonymous client，并同时直接验证公开 queryset，避免把后台 flash message 误判为公开目录数据泄露。

### 当前边界与下一步门槛

- Step 34 只完成 Django Admin Hide/Unhide、Executive role 维护、标准权限和日志边界，没有增加 schema、专用权限、action 或隐藏原因记录。
- Executive role 仍不在公开页面展示；Production media provider、年龄逻辑、筛选和排行榜均未进入本步。
- Step 34 已通过项目负责人验证。Step 35 尚未开始，必须等待项目负责人明确授权。

## Step 35 — 完成 Phase 3 响应式、Accessibility 与隐私门禁

### 已完成

- 新增 `tests/browser/phase3-accessibility.mjs`，统一覆盖 Profile Edit、Avatar、Preview、Publish、Unpublish、Members 列表、Member detail、empty state 和管理员隐藏提示。
- 新增 `tests/test_phase3_accessibility_browser.py`，使用 `StaticLiveServerTestCase`、合成已验证账户和隔离临时 media 运行完整与 empty-state 场景，并在结束后确认临时目录已清理。
- 浏览器门禁覆盖 desktop、mobile、200% content zoom、禁用 JavaScript 和 `prefers-reduced-motion`；验证 landmarks、唯一 H1、Label、错误关联、键盘 Focus、24px 触控目标、图片 alt/解码、长 Username、长 Bio、安全社交链接、横向溢出、page error 和同源网络边界。
- 禁用 JavaScript 场景实际提交 Profile 编辑、Unpublish 和 Publish，确认普通 POST、状态转换及管理员隐藏提示继续可用。
- 扩展 `tests/test_quality_security.py`，扫描 Members 列表和 detail，确认 Email、USYD/USU ID、审核状态、Executive role、未发布 Profile 及其他私有值不进入公开响应；同时固定 User、MemberProfile 和会员表单不收集年龄、出生日期、监护人或紧急联系人。
- 为动态公开名称、Username path 和长标题增加安全断行；将 Profile 表单 checkbox/radio 及公开社交链接触控目标提升至至少 24px，并重新生成 minified CSS。
- 修复保留现有 Avatar 保存 Profile 时的重复验证：已提交 `FieldFile` 在每次内容校验前重新打开，校验后继续关闭，避免表单校验关闭文件后 model `save()` 二次校验产生 500；新增生命周期回归测试确认原文件和字节保持不变。

### 验证结果

- 项目负责人运行 Step 35、Avatar 生命周期和安全专项测试，共 20 个测试全部通过。
- 项目负责人运行完整 pytest 套件，共 304 个测试全部通过。
- `npm.cmd run static:check` 完成 vendor、Home images 和 Tailwind production build 检查。
- `makemigrations --check --dry-run` 报告 `No changes detected`，本步没有 Model、schema 或 migration 变更。
- Django system check 通过，无问题。
- Ruff lint 全部通过；Ruff format check 报告 105 个文件均已格式化。
- 开发者侧 Phase 3 功能与浏览器回归共 66 个测试全部通过；`node --check` 和 `git diff --check` 通过，后者仅报告既有 LF/CRLF 转换提示。

### 测试期间的针对性修补

- 首次统一场景发现超长 Username 在 Profile Preview 和移动端 Publish confirmation 产生横向溢出；只对 Profile 动态标题、`code` 与强调名称增加 `overflow-wrap: anywhere`，没有缩短或改写用户数据。
- 移动场景发现 Avatar 删除 checkbox 和公开社交链接高度为 20px；将对应控件最小尺寸提升至 24px，没有扩大其他页面组件范围。
- 无 JavaScript 编辑提交发现持久化 Avatar 在 ModelForm 校验后已关闭，随后 `MemberProfile.save()` 的重复 `full_clean()` 读取关闭文件并返回 500；validator 现重新打开已提交文件，并由新增回归测试固定该行为。
- URL 错误检查最初写死自定义 validator 文案，但 Django URL validator 可以先返回自身错误；断言改为验证 `aria-invalid`、`aria-describedby` 和实际关联的非空错误说明，未放宽 HTTPS 规则。
- Chromium 可以把多个 reduced-motion transition duration 返回为逗号分隔或科学计数格式；测试改为解析全部时长并逐项验证不超过 0.01ms，生产 reduced-motion 规则未改变。

### 当前边界与下一步门槛

- Step 35 只完成 Phase 3 已实施页面的统一响应式、Accessibility、隐私、媒体和 no-JavaScript 门禁，没有增加年龄逻辑、筛选、排行榜、Production media provider 或新 migration。
- Phase 3 全新环境质量门禁、README/验收入口和最终人工阶段验收属于 Step 36，尚未开始。
- Step 35 已通过项目负责人验证。Step 36 尚未开始，必须等待项目负责人明确授权。

## Step 36 — Phase 3 质量门禁与阶段验收

### 已完成

- 新增 `scripts/accept_phase_3.py`，通过 OS 临时目录建立独立 uv environment，启动并等待 PostgreSQL、应用 Development migrations、执行共享项目门禁，并在动态 loopback port 启动真实 Development server。
- Phase 3 验收入口在共享门禁完成后依次运行既有 Phase 2 Development smoke 和新增 Phase 3 Development smoke；异常路径输出 server log，并始终终止 server 和清理临时环境。
- 新增 `tests/browser/phase3-development-smoke.mjs`，在 desktop/mobile 下验证 Members、Anonymous Profile 登录重定向、不可见 Member 的 404、Development media serving、CSS、横向布局、page error 和同源网络边界。
- 新增 `tests/test_phase3_acceptance.py`，固定命令失败传播、server 清理、锁定安装、migration、共享门禁、两组 Development smoke 及 README 验收说明。
- 共享 `scripts/verify_project.py` 的 Production deploy-check 合成 Secret 名称改为跨阶段中性名称，不改变 Production Secret 来源或安全设置。
- 更新 README，将 Phase 3 全新环境验收设为当前入口，并记录合成账户、临时 media、Profile 编辑、Avatar、Preview、Publish/Unpublish、Members、Admin hide/unhide 和隐私人工走查流程；保留 Phase 1/2 历史兼容命令。

### 首次全新环境验收

- 项目负责人运行 `python -m uv run --env-file .env python scripts\accept_phase_3.py`，临时 uv environment 从锁文件成功安装 Python 3.13.17 与 17 个依赖，npm clean install 完成且报告 `0 vulnerabilities`。
- Development migrations 成功执行且没有待应用 migration；共享门禁完成 static build/check/watch、Ruff、format、migration drift、Django checks、完整 coverage pytest、Production deploy check 和 manifest collectstatic。
- 完整测试共 `308 passed`，branch coverage 报告总计 `95%`；`makemigrations --check --dry-run` 报告 `No changes detected`，Production `check --deploy --fail-level WARNING` 无问题。
- Phase 2 与 Phase 3 Development desktop/mobile smoke 均通过，验收入口最终报告 `Phase 3 end-to-end acceptance passed.`。

### 人工走查发现及针对性修补

- 人工 Preview 发现连续无空格的长 Bio 会撑宽页面；为公开 Profile Bio 增加 `overflow-wrap: anywhere`，并将测试资料改为包含连续字符，统一门禁现同时固定本人 Preview 和公开 detail 的无溢出行为。
- Profile 的 Experience level 与 Preferred arm 在宽卡片中因比例列产生过大间距；Profile 专属定义列表改为按标签实际宽度排列，并在窄屏继续堆叠。
- Members 目录的 Avatar 原先占满卡片宽度，较大原图形成过度突出的纵向卡片；目录卡片改为 desktop/mobile 均使用左侧固定紧凑 Avatar、右侧会员摘要，并由浏览器测试检查两列相对位置和最大显示宽度。原文件保存策略、5 MB 上限和 Production media 边界没有改变。
- Account 原先使用独立 Member profile 卡片且只提供 Edit 入口。页面现保留 Account details、USYD and USU details、Security 三个主卡片，并在 Account details 内展示 Public member profile 摘要、当前公开状态和 Edit、Preview、Publish/Unpublish 操作。
- Account 的公开说明明确：Username 始终属于公开 Profile URL；其他资料只在提供时显示；不希望公开的可选文本应留空，choice 选择 `Not specified`，Avatar 使用删除操作。没有引入逐字段 Publish checkbox、字段或 migration。
- Account 的 Profile 操作按钮增加上方间距，Public member profile 标题调整为清晰的次级层级；Profile 保存成功后返回 Account，Preview 增加 `Back to Account` 入口。
- 人工 Avatar 替换、无效文件保护、删除及 Admin hide/unhide 其余路径均正常。本地只读核对确认 `media/member_avatars/` 只存在数据库当前引用的一个文件；人工仍能看到旧 URL 的现象判断为浏览器缓存，没有发现 storage 中的旧文件残留。

### 修补后验证结果

- 长 Bio 与公开字段布局修补通过 Profile browser、publication 和 detail 专项回归，共 `27 passed`；static check 与 `git diff --check` 通过。
- Members 横向卡片与 Account 三卡片整合通过 Account、目录、发布、全局模板及 Phase 3 browser 回归，共 `54 passed`。
- 上述整合后的完整 pytest 共 `312 passed`；static check、migration drift、Django check、Ruff lint/format 和 `git diff --check` 均通过，没有新增 migration。
- 最后一组 Account 按钮间距、标题层级、保存 redirect 和 Preview 返回入口通过相关 Django 与 Phase 3 browser 回归，共 `50 passed`；static check 与 `git diff --check` 通过。

### 当前边界与下一步门槛

### 最终全新环境与人工验收

- 项目负责人在全部人工修补完成后重新运行 `python -m uv run --env-file .env python scripts\accept_phase_3.py`；临时 uv environment、锁定依赖安装、PostgreSQL、migrations、npm clean install、static build/check/watch、Ruff lint/format、migration drift、Django check、Production deploy check 和 collectstatic 全部通过。
- 最终完整测试共 `313 passed`，branch coverage 为 `95%`；npm audit 报告 `0 vulnerabilities`，没有新增 migration。
- Phase 2 与 Phase 3 Development desktop/mobile smoke 均通过，最终入口报告 `Phase 3 end-to-end acceptance passed.`。
- 项目负责人确认 Members 横向卡片、Account 三卡片与 Profile 摘要、按钮间距、标题层级、Profile 保存返回 Account、Preview 返回入口、Avatar 生命周期及 Admin hide/unhide 全部符合预期。
- Phase 3 Roadmap 退出门槛全部满足，项目负责人批准更新产品、实施、进度与架构文档，并将 Phase 3 标记为 `Complete`。

### 当前边界与下一步门槛

- Phase 3 已完成；Phase 4 尚未开始，不得在未重新阅读当前文档与获得明确授权前实施。
- Production persistent media storage 仍由 Phase 6 决定；Risk Notice 最终文本仍是 Phase 4 正式报名启用前的外部依赖。
- Phase 3 没有新增年龄逻辑、目录筛选、专用隐藏权限、排行榜或 Production media provider。

## Step 37 — Risk Notice 版本管理

### 已完成

- 新增 `RiskNoticeVersion` 和 `safety.0001_initial`。PostgreSQL 条件唯一约束保证最多一个当前版本。
- 授权管理员可创建明确标记为 `SYNTHETIC TEST ONLY` 的测试版本，并通过独立 Admin 操作切换当前版本。版本标识及正文创建后在 Admin 中只读，删除入口关闭。
- 激活服务通过事务和行锁切换版本，保留旧版本正文。重复激活当前版本不更新时间。后台切换由 Admin 日志记录。
- 版本后台及激活服务沿用环境开关，Production 强制关闭。公开 Draft 页面继续读取现有静态模板。

### 验证结果

- 项目负责人验证 PostgreSQL 健康，`migrate` 报告无待应用迁移，migration drift 和 Django 系统检查均通过。
- Risk Notice 版本及 Draft 专项测试 `14 passed`，完整 pytest `319 passed`。
- 开发者侧 Ruff lint、格式检查及 `git diff --check` 通过。

### 下一步门槛

- Step 37 已通过验收。Step 38 尚未开始。
- 正式 Risk Notice 文本仍待批准，正式报名保持关闭。

## Step 38 — Event 模型与后台管理

### 已完成

- 新增 Event 模型与 `events.0001_initial`，包含标题、唯一 slug、说明、起止时间、地点文字、可选 HTTPS 地图链接、公开状态、报名开关及时间戳。公开和报名状态默认关闭，地点默认显示待确认文字。
- 新增公开活动 queryset，以及按当前 Django 时区的本地日期判断 Upcoming/Past 的方法。数据库约束要求结束时间晚于开始时间，并要求非空地图链接以 HTTPS 开头。
- 新增 Django Admin 活动管理，使用标准模型权限，支持列表、筛选、搜索和 slug 生成。新增专项测试覆盖模型规则、约束与后台权限。

### 验证结果

- 项目负责人成功应用 `events.0001_initial`。Event 与 Risk Notice 专项测试 `17 passed`，完整 pytest `330 passed`。
- migration drift、Django check 与 Ruff 检查均通过。开发者侧专项测试及格式检查也通过。

### 测试期间的针对性修补

- 首次开发者专项测试有 3 项失败。将 URL 去空格提前到模型字段校验前，修正 Admin 测试提交的日期字段，并将缺失模型断言改为捕获 Django 的 `LookupError`；重跑后通过。
- 为 Admin URL 输入明确默认 HTTPS scheme，消除 Django 6.0 默认值变更警告。

### 当前边界与下一步门槛

- Step 38 已通过验收，Step 39 尚未开始。活动模型的报名开关仅保存状态，报名流程仍待后续步骤实施。

## Step 39 — EventRegistration 与事务服务

### 已完成

- 新增 `EventRegistration` 和 `events.0002_eventregistration`，记录活动、会员、报名状态、Risk Notice 版本、报名及确认时间和可空取消时间。数据库条件唯一约束限制同一会员和活动最多一条有效报名；状态与取消时间组合由数据库约束保护。
- 新增报名事务服务，检查环境开关、有效会员、公开活动、报名开关、本地日期、主动确认及当前合成 Risk Notice；通过行锁协调重复提交与版本切换。有效重复提交返回已有记录。
- 已取消记录可保留原有版本与时间，后续报名可产生新记录。当前只建立数据结构与报名服务，取消服务、前台流程及 Admin 名单尚未实施。
- 新增专项测试，覆盖唯一约束、确认信息、历史记录、资格及关闭条件，并在 PostgreSQL 上验证并发重复报名和版本切换。

### 验证结果

- 项目负责人成功应用 `events.0002_eventregistration`；报名、Event 和 Risk Notice 专项测试 `27 passed`，完整 pytest `340 passed`。
- migration drift、Django system check、Ruff lint 和 format check 均通过。开发者侧针对修改文件的 Ruff 检查及 `git diff --check` 通过。
- 生成 migration 时开发者侧数据库连接受限；项目负责人已在本机成功应用并验证该 migration。未发现需要针对性修补的测试失败。

### 当前边界与下一步门槛

- Step 39 已通过验收。Production 报名保持关闭，开发和测试只使用明确标记的合成 Risk Notice。
- Step 40 尚未开始，需等待项目负责人授权。

## Step 40 — 公开活动页面与首页集成

### 已完成

- 新增公开 `/events/` 列表和 `/events/<slug>/` 详情路由，只查询 `is_published=True` 的 Event；未发布或不存在的 slug 统一返回 404。
- Events 列表仅保留 `Upcoming` 与 `Past` 筛选。未知参数（包括已取消的 `view=all`）回退到 Upcoming，不在公开页面输出 `All` 入口。
- Upcoming/Past 以 `Australia/Sydney` 当地日历日的零点为分界：活动结束日当天仍属 Upcoming，到下一个当地日历日才进入 Past，不受请求或进程当前时区影响。
- Home 从同一公开 Upcoming queryset 按时间顺序展示最多 3 条活动，提供详情链接、`View all events` 入口及无数据状态，取代 Phase 2 的静态 Upcoming Session。
- 列表与详情页共用 Event card，显示 Sydney 日期时间、地点文字和活动状态；详情页输出说明和可选的 HTTPS `View location in map` 外链。
- Production 报名保持关闭。Upcoming 详情显示 `Registration unavailable`，Past 详情显示 `Past event`；公开页面没有报名、取消或 Risk Notice 确认表单。
- 调整 Event card 的自然高度、H3 标题字号、筛选器与卡片的间距，以及详情卡片与 `Back to events` 的间距；编译后 CSS 已重新生成。
- 新增 Django 页面测试、真实 Playwright desktop/mobile/no-JavaScript 场景，并更新 Home 及 Development smoke 的活动预览断言。

### 验证结果

- 项目负责人运行 Event Django 与浏览器专项测试，共 `5 passed`。
- 完整 pytest 套件共 `345 passed`。
- `npm.cmd run static:check` 的 vendor assets、Home images 和 Tailwind CSS build 全部通过。
- Step 40 实施期间的 migration drift、Django system check、Ruff lint 与 format check 均通过；本步没有新增 Model 或 migration。
- 项目负责人通过 Django Admin 创建并发布已确认的合成测试活动，完成 Home、Upcoming/Past 列表、活动详情、无报名入口和视觉间距人工走查，并确认符合预期。

### 测试与人工走查期间的针对性修补

- 首次真实浏览器测试发现共享 `.content-card { height: 100% }` 使单独 Event card 占据过高空间，从而遮挡首页 `View all events` 链接。仅为 `.event-card` 设置自然高度后，Home 与 Events 浏览器回归通过。
- 人工走查后按批准范围取消价值较低的 `All` 筛选，并局部增加列表、标题和返回按钮的视觉层级。
- 取消 `All` 后的首次针对性测试为 `3 passed, 1 failed`。失败源于测试将请求 canonical URL 中保留的 `?view=all` 误当作页面导航入口；断言改为检查实际 `All` 链接不存在后，生产回退逻辑无需放宽，最终 `4 passed`。

### 当前边界与下一步门槛

- Step 40 只建立公开活动浏览和 Home 预览，没有开放 EventRegistration 前台入口、取消报名、名单管理、活动地图组件或 Events sitemap 收录。
- 地点继续由 Admin 输入文字与可选 HTTPS 地图链接；MapLibre 资产仍未接入业务。
- Step 40 已通过自动化与人工验收。Step 41 尚未开始，必须等待项目负责人明确授权。

## Step 41 — 会员报名与 Risk Notice 确认

### 已完成

- 在已发布且仍属 Upcoming、报名开放的 Event detail 中，为启用账户且具有已验证 Email 的会员提供 `Register` 入口；Anonymous 显示登录入口，不符合条件或不可报名时不显示报名按钮。
- 使用 Alpine 原生 `<dialog>` 呈现当前合成 Risk Notice，并由确认按钮通过普通 POST 提交明确同意；HTMX 仅渐进增强报名区域，无 JavaScript 时沿独立确认页面完成同一服务端流程。
- 报名成功后详情页显示 `Registered`。本步未加入取消入口或取消服务，相关行为保留给 Step 42。
- 报名继续复用 Step 39 的事务服务和 EventRegistration 外键，不重复存储姓名、Email 或 USU ID；后续名单可由关联 User 读取当前账户资料。
- 旧 Risk Notice 版本提交会被拒绝，并重新呈现最新版本要求再次确认。报名关闭、Past、未发布及 Production 环境同时由界面可见性和服务端校验保护。
- Risk Notice 正文取自项目负责人指定的 `Armwrestling_Risk_Notice_EN.docx`：排除签名、版本和 Event 待填字段，将纸质签名表述改为线上报名确认表述，并保留首行 `SYNTHETIC TEST ONLY`。开发数据库已创建并激活 `synthetic-en-v1`；Production 仍不开放报名。
- 新增 Django 页面测试和真实 Playwright 场景，覆盖普通 POST、HTMX、无 JavaScript、重复提交、旧版本重试、资格及关闭边界。

### 验证结果

- 项目负责人运行 Step 41 服务、页面与浏览器专项测试，共 `20 passed`。
- 完整 pytest 套件共 `354 passed`。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 与 Ruff 均通过。
- `npm.cmd run static:check` 的 vendor assets、Home images 和 Tailwind CSS build 全部通过。
- 本步没有新增 Model 或 migration；`git diff --check` 仅报告既有 Windows 行尾提示，没有空白错误。

### 当前边界与下一步门槛

- Step 41 只实现首次报名及当前 Risk Notice 确认。取消报名、取消后重新报名及其界面属于 Step 42，尚未开始。
- 当前 Risk Notice 和活动数据均为明确合成开发数据；Production 继续由 settings 强制关闭 Draft Risk Notice 与报名能力。
- Step 41 已通过项目负责人自动化验收。Step 42 必须等待项目负责人明确授权。

## Step 42 — 取消报名与重新报名

### 已完成

- 新增事务化取消服务，在锁定 Event、User 与报名记录后，将当前有效报名改为 `cancelled` 并记录 `cancelled_at`；重复取消返回既有取消记录，保持幂等。
- 取消不会删除原 EventRegistration，原报名时间、Risk Notice 版本与确认时间继续保留。取消后重新报名会创建新的有效记录，并再次确认服务器当前 Risk Notice。
- 已报名会员在开放且仍属 Upcoming 的活动详情中看到 `Cancel registration`；JavaScript 模式使用 Alpine 原生确认 dialog，禁用 JavaScript 时进入独立确认页。
- 取消操作同时支持普通 POST 与 HTMX 局部更新；成功后报名区域恢复 `Register`，会员可重新阅读并确认当前 Risk Notice。
- 报名关闭、活动进入 Past 或 Production Draft 开关关闭时，页面不提供取消入口，直接请求也由服务端拒绝。
- 新增取消确认 form、`/events/<slug>/cancel/` 路由、完整确认页及共享 cancellation partial；未新增或修改 Model、字段与 migration。
- 扩展 Django 与 Playwright 测试，覆盖正常取消、重复取消、历史保留、关闭/Past/Production 拒绝、HTMX、无 JavaScript，以及 Risk Notice 更新后的重新报名。

### 验证结果

- 项目负责人运行 Step 42 报名服务、页面与浏览器专项测试，共 `30 passed`。
- 完整 pytest 套件共 `364 passed`。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 无问题。
- Ruff lint 报告 `All checks passed!`，format check 报告 `126 files already formatted`。
- `npm.cmd run static:check` 的 vendor assets、Home images 与 Tailwind CSS build 全部通过。
- 开发者侧得到相同专项与完整回归结果；`git diff --check` 仅报告既有 Windows 行尾提示。

### 当前边界与下一步门槛

- Step 42 已完成取消、历史保留及重新报名；没有增加容量、候补、截止时间、付款或 My registrations 页面。
- Admin 报名名单与最小权限属于 Step 43，尚未开始。
- Step 42 已通过项目负责人自动化验收。Step 43 必须等待项目负责人明确授权。

## Step 43 — Admin 报名名单

### 已完成

- 在 Django Admin 注册只读 `EventRegistration` 名单，使用 Django 自动生成的 `events.view_eventregistration` 权限作为最小访问边界；普通会员、无权限 Staff 及仅有 Event 编辑权限的 Staff 均不能访问。
- 名单展示 Event、会员姓名或 Username 回退、Username、Email、USU ID、报名状态、Risk Notice 版本、报名时间、确认时间和取消时间，并支持按 Event、状态及 Risk Notice 筛选和按相关识别信息搜索。
- 报名名单同时保留有效、已取消和重新报名记录；每条历史继续引用当时确认的 Risk Notice 版本。
- 获授权 Staff 与 Superuser 只能查看名单和单条详情；新增、修改、删除及 Admin actions 均被关闭。
- 新增专项测试，覆盖角色隔离、只读防伪造、历史与版本可见性，以及公开 Event 页面不泄露名单、Email、USU ID 或历史版本。

### 验证结果

- 项目负责人运行 EventRegistration Admin 与 Event Admin 专项测试，共 `18 passed`。
- 完整 pytest 套件共 `372 passed`。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 无问题。
- Ruff lint 报告 `All checks passed!`，format check 报告 `127 files already formatted`。
- 开发者侧得到相同专项与完整回归结果。

### 当前边界与下一步门槛

- Step 43 只建立最小权限只读名单，没有新增报名编辑、名单导出、容量、候补、付款、会员本人报名历史页面或前台名单入口。
- Step 43 已通过项目负责人自动化验收。Step 44 尚未开始，必须等待项目负责人明确授权。

## Step 44 — Phase 4 并发、隐私与浏览器门禁

### 已完成

- 扩展报名事务测试，以两个并发取消请求验证行锁与幂等行为：两个请求返回同一 EventRegistration，最终只保留一条已取消历史，状态与取消时间保持一致。
- 扩展前台隐私测试，验证 Home、Events 列表与 Event detail 不向 Anonymous 或其他会员公开报名人的姓名、Username、Email、USU ID、取消历史或旧 Risk Notice 版本。
- 验证其他会员只看到本人的报名入口与状态，直接尝试取消他人的报名不会修改原报名记录。
- 扩展 Events Playwright 场景，在 desktop、mobile、200% 内容放大和禁用 JavaScript 环境检查列表、筛选、详情、地图链接、语义 landmarks、唯一 H1、键盘 Focus、24px 触控目标、文本裁切及横向溢出。
- 扩展报名 Playwright 场景，覆盖报名、取消、重新报名、HTMX dialog、普通确认页、mobile dialog、200% 内容放大、无 JavaScript POST、可见 Focus、触控目标、page error 和同源网络边界。
- 新增检查全部通过，没有发现需要修改的生产 template、CSS、Model、service 或 migration。

### 验证结果

- 项目负责人运行 Step 44 并发、隐私与浏览器专项测试，共 `33 passed`。
- 完整 pytest 套件共 `374 passed`。
- `npm.cmd run static:check` 的 vendor assets、Home images 与 Tailwind CSS build 全部通过。
- `makemigrations --check --dry-run` 报告 `No changes detected`；Django system check 无问题。
- Ruff lint 报告 `All checks passed!`，format check 报告 `127 files already formatted`。
- 开发者侧得到相同专项与完整回归结果；`git diff --check` 仅报告既有 Windows 行尾提示。

### 当前边界与下一步门槛

- Step 44 只加强 Phase 4 已实施功能的并发、隐私、响应式、Accessibility、无 JavaScript 与浏览器回归，没有增加产品功能、生产配置、数据字段或 migration。
- Step 44 已通过项目负责人自动化验收。Step 45 尚未开始，必须等待项目负责人明确授权。

## Step 45 — Phase 4 质量门禁与阶段验收

### 已完成

- 新增 `scripts/accept_phase_4.py`，在临时全新 uv environment 中执行锁定安装、PostgreSQL migrations、共享项目门禁，并在真实 Development server 上依次运行 Phase 2、Phase 3 与 Phase 4 desktop/mobile smoke。
- 新增 `tests/test_phase4_acceptance.py` 和 `tests/browser/phase4-development-smoke.mjs`，固定命令失败传播、server 清理、活动页面、导航、报名状态及同源网络边界。
- 更新 README，将 Phase 4 自动验收和合成数据人工走查作为当前入口；Production 继续不开放报名。
- Header 增加 Events 导航并调整响应式断点；修正 Home/Events 卡片与按钮间距、活动标题和状态文字层级，报名与取消 dialogs 在视口中居中。
- 将当前 Risk Notice 查询集中到 `apps.safety.services.current_risk_notice`。Home、Events 列表和详情页共用同一当前版本存在性判断，避免卡片与详情状态不一致。
- 报名表单直接显示当前 Notice 的完整正文，不再添加重复的固定 banner，也不解析或剥离正文首行。提交时以隐藏的 Notice ID 与事务中锁定的当前版本比较；旧版本提交返回最新版本并要求重新确认。
- 保留报名关闭、Past 自动归类、跨会员隐私、最小权限只读名单、HTMX 渐进增强及无 JavaScript 完整确认页。

### 自动化验收结果

- 项目负责人运行 `python -m uv run --env-file .env python scripts\accept_phase_4.py`；临时环境锁定安装、PostgreSQL、migrations、npm clean install、静态资源、Ruff、migration drift、Django checks、Production deploy check 和 collectstatic 全部通过。
- 完整测试共 `378 passed`，branch coverage 为 `94%`；npm audit 报告 `0 vulnerabilities`，没有新增待生成 migration。
- Phase 2、Phase 3 与 Phase 4 Development desktop/mobile smoke 全部通过。
- Risk Notice 状态一致性、CRLF 正文、旧版本刷新和完整正文单次显示的最终针对性回归共 `43 passed`，Ruff lint 与 format check 通过。

### 人工验收结果

- 项目负责人确认 Home、Events 列表与详情页的报名状态一致，Events 导航、视觉间距、状态强调和居中 dialogs 符合预期。
- 旧版本 Notice 提交会拒绝原确认、在同一流程中显示当前版本并允许重新确认；正文中的 `SYNTHETIC TEST ONLY` 只显示一次。
- 报名关闭后全部入口消失且服务端拒绝请求；活动日期结束后按 Sydney 当地日期自动进入 Past，并移除报名与取消操作。
- Anonymous 与其他会员无法读取报名人的姓名、Email、USU ID、Notice 版本或报名历史；Admin 名单维持最小权限只读边界。
- JavaScript 禁用时，报名、确认、取消和重新报名均可通过普通页面与 POST 完成。

### 当前边界与下一步门槛

- Phase 4 Roadmap 退出门槛已全部满足，状态为 `Complete`。
- 当前 Risk Notice 与活动资料仍属于明确的合成 Development/Test 数据；正式文本获批前，Production 不开放报名。

## Phase 5 范围变更

- 项目负责人确认取消原定的地点与地图阶段，保留编号，状态为 `Cancelled`。活动地点继续由管理员在 Event 中录入，在详情页显示地点文字和可选 Google Maps 链接。
- Phase 6 衔接已验收的 Phase 4，移除独立地点模型、站内地图、地点坐标和地图瓦片供应商相关的阶段依赖。仓库仍保留既有的 `locations` App 骨架及未加载的 MapLibre 资产。

## Visual Refresh Step V1 — 视觉 Tokens 与资产管线

### 前置条件检查

- Phase 1–4 为 `Complete`，代码清理第 1–6 批已提交（`e156ce3`），Phase 5 已取消；`implementation.md` 九点五节 V1 的展开条件满足。
- `AGENTS.md`、`architecture.md`、`design_document.md`（7.4、7.7、9.2–9.6）与 `implementation.md` 九点五节已完整阅读，彼此不冲突。
- 两张源图存在且可读：`static_src/images/brand/gold-texture-source.png`（1600 × 640 RGB PNG）与 `static_src/images/home/hero-specimen-source.png`（1122 × 1402 RGBA PNG，含透明通道）；两者都不含 EXIF、XMP 或文本 metadata。
- Docker PostgreSQL healthy；Token 取值以 Design canvas `NULDL Home hero concepts` 的 `E · Aligned · three-line title` 与 `design_document.md` 9.2 为准。

### 已完成

- `static_src/css/site.css` 的 `@theme`：
  - 页面底色 `--color-ink` 改为暖黑 `#0a0908`，正文 `--color-cream` 改为 `#ece4d3`，次要文字 `--color-muted` 改为 `#c9c0ae`（均取自设计稿）；这三项是全站生效的唯一可见变化。
  - 新增金色材质色阶 `--color-gold-shadow: #7e5015`、`--color-gold-metal: #bf8933`、`--color-gold-highlight: #f2bf5a`（9.2 规定值），网格线色 `--color-grid: rgb(226 176 74 / 4.5%)`，以及等宽字体族 `--font-mono`。
  - 平面金色 `--color-gold` / `--color-gold-bright` 保持不变，继续用于链接、Focus 与现有主要按钮。
- 以 `--save-exact` 加入 `@fontsource/jetbrains-mono@5.3.0`（2026-07-19 发布，OFL-1.1，无传递依赖）；`build-static-assets.mjs` 复制 Latin 400/500 两个字重与 license，并写入 vendor manifest；`site.css` 增加对应 `@font-face`。
- `scripts/build_home_images.py` 改为按源图清单构建，每个源图都校验 SHA-256、格式、尺寸、mode 与透明通道，并以 method 6、去除 EXIF/XMP 的固定参数确定性生成 WebP：
  - Logo：参数与输出不变（480/800/1200，字节一致）。
  - 金色材质：`static/images/brand/gold-texture-800.webp`（29,098 bytes）与 `-1600.webp`（92,904 bytes），quality 80。
  - Hero 背景照片：`static/images/home/hero-specimen-560.webp`（75,100 bytes）与 `-1120.webp`（224,692 bytes），保留透明度，quality 78、alpha_quality 80。
  - 新资产已由 `images:build` / `images:check` 覆盖；脚本名与 npm scripts 保持不变。
- 测试：
  - `tests/test_home_images.py` 参数化覆盖三张源图的完整性，以及全部变体的尺寸、格式、mode、透明度和无 metadata。
  - `tests/test_static_assets.py` 新增 JetBrains Mono 构建检查、四组 token 对比度（muted/surface-raised、ink/gold-metal、ink/gold-highlight、gold-metal/ink），以及金色材质图作为大号展示文字时最暗 1% 像素对页面底色 ≥ 3:1 的检查。

### 验证结果

- `npm run static:check`（vendor assets、images、Tailwind build）通过。
- `tests/test_static_assets.py` 与 `tests/test_home_images.py` 共 `21 passed`。
- 完整 pytest（含全部 Playwright 浏览器与 Accessibility 门禁）在全新 test database 上 `394 passed`。
- Ruff lint `All checks passed!`，format check `138 files already formatted`；Django system check 无问题；`makemigrations --check --dry-run` 报告 `No changes detected`；`git diff --check` 无问题。
- 对比度实测（WCAG）：cream/ink 15.7、muted/ink 11.0、muted/surface 9.9、ink/gold-metal 6.5、ink/gold-highlight 11.7、gold-metal/ink 6.5、gold-bright/ink 13.8。

### 遗留与需要项目负责人决定的事项

- **材质按钮小字对比度（V2 前需决定）：** 金色材质图深色斑块较多。按像素统计，深色文字（`#1a1000`）对材质图的对比度在 5% 分位约 4.0、1% 分位约 3.3，低于正常字号所需的 4.5:1；设计稿的底部暗化叠层还会进一步降低该值。22px、字重 600 的按钮文字不属于 WCAG 大号文字。可选方案：V2 生成提亮暗部的按钮专用材质变体，或减小材质对按钮底色的贡献（以 `--color-gold-metal` 为主、叠加低透明度纹理）。主标题等大号金色文字（≥ 3:1）不受影响，已由测试固定。
- **平面金色取值：** 设计稿链接与标签文字使用 `#e2b04a`，当前平面金色 token 仍为 `#d9ad50` / `#ffd166`。V1 未改动，是否统一由 V2 决定。
- **Tailwind 输出：** Tailwind v4 只输出被使用的 theme 变量，新增材质与网格颜色要到 V2 组件引用后才出现在 `static/css/site.css`；构建产物目前只增加 JetBrains Mono `@font-face` 与新色值（21,469 → 21,847 bytes）。
- **npm audit：** 报告 2 个 high（`picomatch` ReDoS，经 Tailwind CLI 的 `@parcel/watcher` 引入，仅开发工具链）。本步 lockfile 只新增 `@fontsource/jetbrains-mono`，该告警为既有依赖的新公告，本步未处理。
- 本步没有修改模板、业务逻辑、URL、表单或 migration。

### 验收与文档

- 项目负责人已确认 V1，并批准更新 `architecture.md`：新增 3.49 节，补充新 token、JetBrains Mono、图片构建清单及相关文件职责。
- 上述两项 V2 前决策（材质按钮小字对比度、平面金色取值）仍待项目负责人决定。V2 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V2 — 全站共用组件、Header 与 Footer

### 项目负责人决定

- 材质按钮小字对比度：采用提亮暗部的按钮专用材质贴图。
- 平面金色：链接、标签与小号金色文字改用设计稿 `#e2b04a`，悬停 `#f3d58a`；Focus 指示继续使用更亮的 `#ffd166`。两项决定已写入 `design_document.md` 9.2。

### 已完成

- 图片构建清单新增 `static/images/brand/gold-texture-button-800.webp`（16,372 bytes）：从同一材质源图按像素暗度向 `--color-gold-highlight` 混合（强度 0.7），实测最暗像素对 `--color-on-gold` 为 5.3:1，纹理保持可见。
- 新增 token：`--color-gold-pale`、`--color-gold-glint`、`--color-gold-sheen`、`--color-gold-edge`、`--color-gold-depth`、`--color-on-gold`、`--color-gold-wash`；`--color-gold` 改为 `#e2b04a`，Header 背景改为 88% 暖黑，删除不再使用的 `--color-divider`。组件规则继续只引用 `var(--color-*)`，半透明效果使用 `color-mix()`。
- 共用组件（`static_src/css/site.css`）：
  - `.button`：金色材质填充、切角、顶部内高光与底部内暗边、近黑文字；悬停时一次性扫过高光（不循环，reduced motion 下即时完成），按下轻微下移。填充与高光画在带 `clip-path` 的 `::before`/`::after` 上，切角不会裁掉元素自身的 Focus outline。
  - `.button--secondary`：金色渐变描边切角按钮，内部底色读取所在表面的 `--button-ground`（页面、卡片、dialog、安全提示与 CTA 面板各自声明），悬停与 `aria-current` 使用 `--color-gold-wash`；当前项另以下划线标识，不只依赖颜色。
  - `.button--quiet` 关闭材质层；`.button--compact` 供 Header 使用较小切角。
  - `.gold-text`：材质贴图裁切到文字，每个行片段上亮下暗，顶部亮边、底部暗边与柔和投影；只用于大号展示文字，forced colors 与不支持 `background-clip: text` 时回退为普通文字。
  - `.gold-rule` 金色分隔线、`.label-mono` 等宽金色标签、`.gold-tag` 材质等宽标签。
  - `body` 使用暖黑底色叠加 2.5rem 极淡金色坐标网格。
- Header：品牌改为大写 Barlow Condensed；导航链接为次要文字色，悬停浅金，当前页金色文字加 2px 金色下划线；`Join the Club` 改用 `.button .button--compact`；底部使用金色分隔线。
- Footer：顶部金色分隔线，版权行使用等宽大写小字，Instagram 链接使用平面金色；宽屏左右分布，窄屏换行。
- `.gold-text`、`.label-mono`、`.gold-tag` 已定义但尚无页面使用，由 V3 Hero 首先使用；本步用临时注入的样例截图确认渲染。
- 测试：
  - 静态资产测试新增按钮材质每个像素对 `--color-on-gold` ≥ 4.5:1、七组平面金色/浅金/近黑文字对比度，以及构建 CSS 引用的图片均存在。
  - 图片测试加入按钮材质变体。
  - `phase2-accessibility.mjs` 的对比度计算在元素自身背景透明时读取其 `::after`/`::before` 背景，并增加 `main .button--secondary` 与 `.site-header .button`；必需内容检查与 `home-page.mjs` 的裁切检查限定在 `main`，避免把 mobile 收起菜单中的 Header 按钮当作页面内容。

### 验证结果

- 完整 pytest（含全部 Playwright、Phase 2–4 Accessibility 门禁：对比度、Focus、24px 触控目标、200% 重排、无 JavaScript、reduced motion）在全新 test database 上 `405 passed`。
- `npm run static:check`、Ruff lint/format（`138 files already formatted`）、Django check、`makemigrations --check`（`No changes detected`）、`git diff --check` 均通过。
- Production settings 下 `collectstatic` 通过，manifest CSS 中三处材质图片 URL 均被替换为带 hash 的文件名。
- 人工截图走查：在 Development server 上以 1440×900 与 390×844 截取 Home、About、Beginners & Safety、Events、Members、Log in、Sign up、Draft Risk Notice、404 的全页截图，以及组件样例、悬停、Focus 和 mobile 展开菜单。按钮、描边按钮、卡片内按钮、安全提示内按钮、Header、Footer 与网格背景均正常，无重叠或溢出；悬停高光按预期单次扫过。走查发现 Events 的 Upcoming/Past 筛选没有当前项样式（V2 之前即如此），已补充当前项底色与下划线。

### 当前边界与下一步门槛

- 本步没有修改业务逻辑、权限、URL、表单字段或 migration；模板变更只限 Header 的 `Join the Club` class 与 Footer 版权行 class。
- `architecture.md` 尚未更新，需要项目负责人批准。V3 尚未开始，需要项目负责人明确授权。

### V2 修订（项目负责人参考截图）

- 项目负责人提供最终 Home 视觉截图后，Header 改为截图布局：页面导航紧跟品牌（不再推到右侧），`Log in` 与 `Join the Club` 位于最右；导航文字 0.875rem、字重 400，当前页下划线与文字等宽；品牌 1.25rem。
- Header、messages、页面主体与 Footer 共用 `min(80rem, 100% - 4rem)` 内容宽度（窄于 `--breakpoint-nav` 时为 `100% - 2rem`），原为 88rem；`home-page.mjs` 的宽度断言相应改为 80rem。
- 按钮字重按设计稿调整：主要按钮 600、描边按钮 500；Header 的 `Join the Club` 为 0.875rem。
- 截图中的 Hero（三行金色标题、等宽按钮、信息表、背景照片、Logo 布局）属于 V3–V5，本修订未实施。
- 验证：完整 pytest `405 passed`，`static:check`、Ruff lint/format、`git diff --check` 通过；desktop 1440×900 与 mobile 390×844 截图走查 Header、mobile 展开菜单、Beginners & Safety 与组件样例均正常。

### 文档补充（项目负责人提供）

- 另一个 Claude 桌面会话对 memory-bank 的补充修改未写入本仓库文件夹（排查：无 OneDrive 覆盖、无 git worktree/reset、无其他副本；02:22 之后 memory-bank 的磁盘写入只来自本会话）。项目负责人改为直接提供文本，已逐字写入 `design_document.md`：7.4 背景彩蛋参数与 Logo 外发光、7.7 彩蛋标注文案、9.2 表面与文字基准值及 Header 金色分隔线、9.3 等宽字体用途与 Hero 字号、9.4 切角尺寸、导航当前页、次要按钮与信息表样式。
- 已实施的 V2 与新增规则逐项核对一致（网格 2.5rem/4.5%、Header 半透明暖黑与金色渐变线、导航当前页 2px 下划线、主/次按钮切角 10px 与 Header 8px、次要按钮 1px 渐变描边与深金褐悬停）。
- 按 9.2 新增 token：`--color-subtle: #9c9483`（表格标签与低优先级文字，对页面底色 6.9:1）与 `--color-gold-line`（30% `#e2b04a` 细边框），供 V3/V4 使用；静态资产测试新增 subtle 对页面底色与卡片表面的 4.5:1 检查。`static:check`、Ruff 与静态/图片测试（`34 passed`）通过。

### 验收与文档

- 项目负责人已确认 V2（含 Header 修订与文档补充），并批准更新 `architecture.md`：新增 3.50 节，更新按钮层结构、共享内容宽度、新 token、按钮材质贴图及相关文件职责。V3 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V3 — Home Hero 布局

### 前置条件检查

- V1、V2 已由项目负责人确认，`architecture.md` 已记录至 3.50；`design_document.md` 7.4、7.7、9.2–9.4 已包含项目负责人补充的 Hero 参数。V3 不包含信息表（V4）与背景彩蛋（V5）。

### 已完成

- `apps/core/templates/core/home.html` 重建 Hero：
  - `Research Field` 材质标签 + 等宽金色 eyebrow；
  - 唯一 H1 由三个行块组成（`Nonlinear` / `Upper Limb Dynamics` / `Laboratory`），每行内是 `.gold-text`，可访问名称仍为 `Nonlinear Upper Limb Dynamics Laboratory`；
  - 介绍文字、操作按钮（`Join the Club` 仅 Anonymous、`Join on USU`、`New to Armwrestling?`，顺序与 href 不变）；
  - 右侧响应式 Logo（`sizes` 改为桌面 31.25rem、窄屏 34rem）；
  - Hero 底部图纸标题栏：`Specimen 001 is kept in the dark. Bring a light.` 与 `<dl>` 形式的 `Dwg no. NULDL-001`、`Scale 1:1`、`Est. 2026`，对辅助技术可读。
- `static_src/css/site.css`：
  - 宽于 `--breakpoint-hero`（54rem）时，文字栏与 Logo 作为一组 flex 居中，栏间距 3.5rem；文字栏 `width: min-content`，标题行 `nowrap`，因此由第二行决定栏宽，标签、介绍、按钮行全部对齐该栏宽；主标题 `clamp(3rem, 6vw, 5.5rem)`、行高 0.92。
  - 按钮在一行内等宽等高（`grid-auto-flow: column` + `align-self: stretch`），文字 `clamp(1rem, 1.5vw, 1.375rem)`（1440px 时约 22px）；会员只有两个按钮时同样平分一行。窄于 54rem 时为两列、奇数最后一个占满整行。
  - Logo 在 18.75–31.25rem（300–500px）之间随剩余空间伸缩，带 12% 金色 40px 外发光；窄屏移到标题下方。
  - 窄屏标题行允许换行，避免 320–390px 视口溢出。
  - 原 `.home-hero__content h1` 的任意断行规则删除（标题改由行块控制换行）。
- 测试：
  - `tests/test_home_page.py` 以去除标签后的文本校验 H1、三行标题、标签与 eyebrow、图纸标题栏文字，并确认标题栏未对辅助技术隐藏。
  - `tests/browser/home-page.mjs` 新增：desktop 三个按钮同一行等宽等高、标题三行互不重叠、第二行宽度等于文字栏宽度、Logo 位于文字右侧且 300–500px、标题栏可见；mobile Logo 位于标题下方。
  - `phase2-accessibility.mjs` 的对比度检查由已不存在的 `.lede` 改为 `.home-hero__intro`，并新增材质标签、eyebrow、标题栏说明、`dt`、`dd`。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `408 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过。
- Development server 截图走查 1920、1440、1100、900、800 与 390px：均无横向溢出；≥ 900px 时标题三行、按钮等宽、Logo 在右侧（1440px：文字栏 702px、Logo 500px；900px：Logo 373px）；800 与 390px 时 Logo 移至标题下方，按钮两列、第三个占满整行。

### 当前边界与下一步门槛

- 未实施 V4 信息表与 V5 背景彩蛋；Hero 内容宽度沿用 V2 的 80rem 共享宽度（设计稿约 1360px）。会员视图的两按钮布局由 Django 测试校验顺序，未做浏览器截图。
- 没有修改 view、URL、业务逻辑或 migration。`architecture.md` 尚未更新，需要项目负责人批准；V4 尚未开始。

### 项目负责人确认

- 项目负责人已确认 V3，并批准更新 `architecture.md`：新增 3.51 节，更新 Home 模板、样式源及 Home/Accessibility 测试的文件职责。V4 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V4 — 已取消

- 项目负责人决定取消 V4（Hero 近期活动信息表）：它只显示最近一场 Upcoming Event 的日期、时间与地点，与 Home 下方 `Upcoming Events` 区第一张活动卡片重复，且会增加已经较满的 Hero 的内容。
- 原信息表的等宽信息行风格（等宽标签、`--color-subtle` 标签与 `--color-cream` 数值、`--color-gold-line` 细边框）并入 V6 活动卡片，具体样式在 V6 设计确认时定稿。
- 文档更新：`design_document.md` 7.4 删除 Hero 信息表并说明近期活动只在 `Upcoming Events` 区展示，7.7 删除信息表文案，9.3 与 9.4 改为活动卡片信息行；`implementation.md` 将 V4 标为已取消（保留编号），V6 加入原信息表风格。
- 本次只修改文档，没有修改代码、view 或测试。`architecture.md` 3.51 与 JetBrains Mono 文件说明中仍提到信息表，待下一次批准更新 `architecture.md` 时一并修正。V5 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V5 — Hero 背景彩蛋

### 前置条件检查

- V3 已确认，V4 已取消（见上节）；`design_document.md` 7.4、7.7、9.5 已包含彩蛋参数与标注文案；`hero-specimen-{560,1120}.webp` 由 V1 图片管线生成。
- 开始时发现工作区已有未提交的照片替换：`static_src/images/home/hero-specimen-source.png`（仍为 1122 × 1402 RGBA，新 SHA-256 `94b50484…f2ed`）、`scripts/build_home_images.py` 中对应 hash 与两张重新生成的 WebP（560：40,286 bytes；1120：112,340 bytes）。视为项目负责人更新的照片，`images:check` 通过；`tests/test_home_images.py` 的固定 hash 随之更新。

### 已完成

- 按项目负责人要求删除 Hero 底部装饰文字 `Specimen 001 is kept in the dark. Bring a light.`（模板、`.home-hero__note` 样式、Home 页面测试与对比度检查）；图纸标题栏保留并靠右对齐。`design_document.md` 7.7 与 9.3 同步更新。
- `apps/core/templates/core/home.html`：Hero 内新增 `aria-hidden="true"` 的 `.hero-specimen` 层，包含常态暗照片、光照下的照片，以及光照下的受力标注 SVG（握点金色虚线圆与圆点、一条直线与一条弯曲的带箭头发力线、两条细引线、`Fig. 01` / `Contact point` 与 `F = ?` / `Direction: nonlinear` 等宽标签）。
- 指针交互使用 Hero 上的 Alpine 行内处理：`pointermove`（忽略 touch）只把指针相对 Hero 的坐标写入 `--light-x` / `--light-y` 并设置 `data-lit`，`pointerleave` 移除 `data-lit`；没有持续动画或定时器。
- `static_src/css/site.css`：
  - `.hero-specimen` 默认 `display: none`；只在 `@variant hero`（≥ 54rem，Logo 位于标题右侧）内的 `@media (hover: hover)` 中显示，照片 `image-set` 背景也只在该条件内声明，因此窄屏和不能悬停的设备不下载照片。
  - 照片框位于 Hero 横向 36%、底边对齐、高 80%；常态不透明度 7%，光照下 85%。
  - 光照层以 `radial-gradient(circle 12.5rem …)` 遮罩（0–55% 实心、至 200px 渐隐），`data-lit` 时不透明度 0 → 1（200ms，reduced motion 下即时）。
  - 照片层位于文字与 Logo 之后（可被遮挡）；标注层在同一遮罩下位于内容之上，标签以暗色描边保持在文字或 Logo 上可读。整层 `pointer-events: none`。
  - 标签字号约 11.6px（1440px 时）、字距 0.1em、大写，居中于握点上下，使完整标注落在 200px 光照内。
- 测试：
  - `tests/test_home_page.py`：彩蛋层对辅助技术隐藏并包含四条标注文案；HTML 不引用照片（只由 CSS 加载）；装饰文字已删除。
  - `tests/browser/home-page.mjs`：desktop 下彩蛋层显示且不接收指针、照片已请求、光照默认熄灭、指针进入后两层光照点亮且坐标跟随指针、光照下三个 Hero 按钮中心仍命中按钮本身、指针离开后熄灭；mobile（390px）与 1280px 触屏（`hover: none`）均不显示该层且没有照片网络请求。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`；`static:check`、Ruff lint/format、Django check、`makemigrations --check`、`git diff --check` 通过。
- Development server 截图走查 1440、1920 与 900px：常态只见极淡轮廓；指针位于握点时照片、虚线圆、两条发力线、引线与两组标签完整出现在光照内；1440px 时标注位于文字栏与 Logo 之间，900px 时部分标签叠在 Logo 上，依靠暗色描边仍可读。

### 当前边界与下一步门槛

- 光照会暂时降低其下方 Hero 介绍文字的对比度（只在指针悬停期间）；对比度门禁在未点亮状态下检查。
- 没有修改 view、URL、业务逻辑或 migration；未新增 JavaScript 文件或依赖。`architecture.md` 尚未更新（3.51 与字体说明中的信息表措辞也待一并修正），需要项目负责人批准；V6 尚未开始。

### V5 修订：删除受力标注

- 项目负责人走查后认为照片上叠加的受力标注不合适，要求全部删除：金色虚线圆与圆点、两条发力箭头、两条引线，以及 `Fig. 01` / `Contact point`、`F = ?` / `Direction: nonlinear` 标签。光照现在只显现照片本身。
- 删除模板中的标注 SVG 与第二个光照层，以及对应 CSS（标注层、描边标签、`--marks` 修饰类）；照片、7% 常态、200px 柔边光照、指针跟随与熄灭、媒体条件和不下载规则不变。
- 测试：Home 页面测试改为断言彩蛋层不含标注文案与 SVG；浏览器测试改为只有一个光照层。
- 文档：`design_document.md` 7.4 删除受力标注描述并记录该决定，7.7 删除标注文案，9.3 等宽字体用途去掉彩蛋标注；`implementation.md` V5 行注明不叠加受力标注。
- 同时确认：页面使用的两张 WebP 与当前磁盘上无粒子效果的照片源图一致；开发服务器下照片 URL 不带 hash，浏览器可能缓存旧版，强制刷新即可。

### V5 修订：更换背景照片

- 项目负责人再次替换 `static_src/images/home/hero-specimen-source.png`：新图为多名成员对抗场景的拼贴，1448 × 1086 横版，RGBA 但完全不透明（黑色底），SHA-256 `95bf86e1…63ec8`，2,153,981 bytes。
- `scripts/build_home_images.py`：照片源图更新 hash 与尺寸，新增 `opaque` 标记——源图须保持完全不透明（不再要求透明通道），编码前转为 RGB；输出宽度改为 720 与 1440（适配约 640px 的显示宽度及 2x），生成 `hero-specimen-720.webp`（720 × 540，34,628 bytes）与 `hero-specimen-1440.webp`（1440 × 1080，88,894 bytes），删除旧的 560/1120 文件。`images:check` 通过。
- `static_src/css/site.css`：照片框比例改为 1448 / 1086，仍按 36% 横向、底边对齐、高 80% 放置；照片四边各 12% 以遮罩渐隐，避免黑色底形成矩形边；`.hero-specimen` 增加 `overflow: hidden`，横版照片在较窄宽屏下超出 Hero 的部分被裁去，不产生横向滚动。
- 测试：`tests/test_home_images.py` 更新照片 hash、尺寸与输出宽度，并以 `OPAQUE_SOURCES` 声明该源图不透明、生成物为 RGB；Home 页面测试改为检查 HTML 不引用 720/1440 照片。
- `design_document.md` 7.4 与 9.6 改为描述当前照片拼贴；9.6 记录画面包含多名成员，按既有规则公开上线前需取得其同意（待项目负责人确认）。
- 完整 pytest `409 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过；1440/1920/900px 截图确认常态极淡、光照显现照片、边缘无矩形痕迹。

### V5 修订：照片铺满 Hero

- 项目负责人指出横版照片被限制在 Hero 中间偏右下（原参数：横向 36%、底边对齐、高 80%），选择让照片铺满整个 Hero。
- `static_src/css/site.css`：照片框改为 `inset: 0`，背景 `cover`、定位 `center 20%`（超出部分主要裁去照片底部的桌腿与地面）；四边 12% 渐隐、7% 常态、85% 光照下不透明度和 200px 光圈不变；不再需要 `.hero-specimen` 的 `overflow: hidden`。
- 照片铺满约 1280 × 600px 时显示宽度约 1280px，720px 版本会被放大，因此改为只生成接近源图宽度的 `hero-specimen-1440.webp`（源图只有 1448px 宽，无法提供 2x），删除 720 版本；构建脚本与图片测试的输出宽度改为 `(1440,)`。
- `design_document.md` 7.4 改为铺满 Hero 并记录该决定。
- 1440/1920/900px 截图确认照片覆盖整个 Hero，光圈在标题、介绍文字、Logo 下都能显现照片，四边无矩形痕迹。

### 项目负责人确认

- 项目负责人已确认 V5（含删除装饰文字、删除受力标注、更换照片与铺满 Hero 的修订），并批准更新 `architecture.md`：新增 3.52 节（含 V4 取消），修正 3.49、3.51 中已过时的照片、装饰说明与信息表描述，更新照片源图与生成物、构建脚本、字体、Home 模板与样式及相关测试的文件职责。V6 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V6 — Home 其余区块与共享活动卡片

### 前置条件检查

- V5 已确认并提交；V4 取消后其信息行风格并入 V6（见 `implementation.md`）。
- V6 要求先在设计画布确认样式；本会话无法访问 Design canvas，因此以 `design_document.md` 7.5、9.3、9.4 与 V2 组件制作临时 HTML mockup（1440/390px 截图，只在 scratchpad 中），项目负责人确认后实施。

### 已完成

- `apps/core/templates/core/home.html`：
  - `New to Armwrestling?`：新的 `.section-heading` 标题区（等宽金色小标签 `Start with the fundamentals`、两行 H2，`Join Us !` 使用 `.gold-text`）；四张 `.feature-card` 带装饰性编号 `01–04`（`aria-hidden`），文案不变。
  - `Upcoming Events`：去掉整块 `.session-card` 面板，`View all events` 移到标题区右侧（紧凑次要按钮）；卡片放在 `.event-stack` 中；空状态改为 `.events-empty`。
- `apps/events/templates/events/includes/event_card.html` 重写（Home 与 Events 列表共用）：日期块（星期/日/月年，`aria-hidden`）、标题链接、`<dl class="event-facts">`（同一天显示 `Date` 与 `Time`，跨天显示 `Starts`/`Ends`，均含 `<time datetime>`；`Location`）、状态标签与 `View details` 次要按钮（可访问名称 `View details for <title>`，使用 Tailwind `sr-only`）。状态分支与文案不变，`event-status` class 保留，开放状态另加 `.gold-tag`。整个卡片在 `Australia/Sydney` 时区下渲染。
- `apps/events/templates/events/event_list.html`：列表容器改为 `.event-stack`，空状态使用 `.events-empty`。
- `apps/events/templates/events/event_detail.html`：详情信息卡去掉不再适用的 `event-card` class（V6 前该 class 在详情页没有任何样式作用），以免继承新的列表卡片布局；详情页其余不变。
- `static_src/css/site.css`：新增 `.section-heading`、`.feature-grid`/`.feature-card`、`.event-stack`/`.event-card` 网格布局、`.event-facts`、`.status-tag`、`.events-empty`；窄于 `--breakpoint-hero` 时活动卡片改为“日期块 + 标题 / 信息行 / 状态与按钮”三行，信息行纵向排列。删除 `.session-card`、`.home-events-action`、`.home-page .content-card h3` 与旧 `.event-card h3` 规则。Home 卡片标题由 19px 改为 mockup 中确认的 22px（1.375rem）。

### 测试

- `tests/test_event_pages.py`：状态标签断言改为新 class（`event-status status-tag gold-tag` / `event-status status-tag`），测试名改为 `test_event_cards_show_registration_status_labels`。
- `tests/browser/event-pages.mjs`：`View all events` 改为位于活动卡片上方（≥ 16px 间距）；点击标题链接时使用精确名称，避免与 `View details for …` 混淆。
- `tests/browser/home-page.mjs`：卡片标题选择器改为 `.feature-card h3`，字号 22px。
- `tests/browser/phase2-accessibility.mjs`：新增 `.feature-card__index`、`.feature-card p`、`.events-empty` 对比度检查。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过；最后一次 CSS 调整（日期块居中不换行、窄屏宽 5.5rem）后重跑 Home、Events、报名浏览器与 Accessibility 测试 `29 passed`。
- Development server 截图走查 Home 两个区块与 Events 列表的 1440 与 390px：无横向溢出；走查中修正窄屏日期块月份换行与左对齐。

### 当前边界与下一步门槛

- 没有修改 view、URL、业务逻辑或 migration；活动详情页的视觉重做属于后续 Events 页面轮次。
- `architecture.md` 尚未更新，需要项目负责人批准；V7 尚未开始。

### V6 修订：状态标签与按钮

- 项目负责人指出 `Registration open` 的金色材质底容易被误认为按钮，并要求它与 `View details` 等宽。
- 状态标签改为不填充的细描边文字框：开放状态用 `.status-tag--open`（金色文字，取代 `.gold-tag`），其余状态保持次要文字色；文字居中。
- `.event-card__aside` 改为 `justify-items: stretch`，桌面端两者等于较宽一方的宽度；窄屏时改为两等分列并等高。
- `View details` 保持描边次要按钮：金色材质填充只用于主要操作，列表中每张卡片各一个材质按钮会与 Hero 的 `Join the Club` 争夺注意力。
- 测试：`test_event_pages.py` 改为 `status-tag status-tag--open`；`event-pages.mjs` 新增断言——状态标签与按钮等宽、标签没有背景图。`design_document.md` 7.5 同步更新。

### 项目负责人确认

- 项目负责人已确认 V6（含状态标签与按钮修订），并批准更新 `architecture.md`：新增 3.53 节，注明 3.38 中 `.event-card` 的变化，并更新样式源、Home 与 Events 模板及相关测试的文件职责。V7（第一轮质量门禁）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V7 — 第一轮质量门禁

### 前置条件检查

- V1–V3、V5–V6 已由项目负责人确认并提交推送（V4 已取消）；工作区干净，Docker PostgreSQL healthy。

### 验证结果

- `scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中完整通过（`Phase 4 end-to-end acceptance passed.`）：
  - 共享门禁 `scripts/verify_project.py`：`npm ci`、Chromium 安装、`static:build`、`static:check`、`css:watch:smoke`、Ruff lint/format、`makemigrations --check`（No changes detected）、Django check、干净 PostgreSQL 上的完整 pytest（`409 passed`，含全部 Phase 1–4 Playwright 与 Accessibility 门禁）、branch coverage `95%`、Production `check --deploy --fail-level WARNING`（无问题）与 manifest `collectstatic`。
  - 真实 Development server 上的 Phase 2、Phase 3、Phase 4 desktop/mobile smoke 全部通过。
- 验收后工作区仍然干净（门禁没有改动任何已跟踪文件）。
- 走查截图：Development server 上 1440 × 900 与 390 × 844 的全页截图，覆盖 Home、About、Beginners & Safety、Events 列表、Event detail、Members、Log in、Sign up，共 16 张；均无横向溢出与 page error。截图保存在临时目录，不进入仓库，已提交项目负责人走查。

### 当前边界与下一步门槛

- Visual Refresh 第一轮只改了全站共用组件（Header、Footer、按钮、颜色、字体）、Home 与 Events 列表卡片；About、Beginners & Safety、Event detail、Members、认证与 Account、错误页仍是原有布局，只继承了新的颜色、字体与按钮。按 `implementation.md` 九点五，后续按 Events 列表与详情 → About、Beginners & Safety → Members → 认证与 Account → 403/404/500 的顺序逐页设计确认后再展开步骤。
- 截图中 Members 的会员与 Events 的活动来自 Development database 中既有的合成数据。
- 本步没有修改代码。`architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V7 截图并确认第一轮 Visual Refresh 完成，批准更新 `architecture.md`：新增 3.54 节并更新页头状态。后续页面（Events 列表与详情 → About、Beginners & Safety → Members → 认证与 Account → 403/404/500）需要项目负责人先确认设计，再展开为具体步骤。

## Visual Refresh 第二轮 — Events 设计确认

- 以 mockup（1440 与 390px，临时目录，不进入仓库）提出 Events 列表与详情设计：列表页标签页式筛选、Past 卡片日期弱化、虚线框空状态；详情页顶部返回链接、页头状态标签、两栏布局与信息面板、报名区各状态（`Registered` 改为状态标签）、带 `Risk Notice` 小标签的确认 dialog。
- 项目负责人已确认该设计。规则写入 `design_document.md` 7.5；`implementation.md` 新增第二轮步骤 V8（Events 列表）、V9（活动详情与报名区）、V10（第二轮质量门禁）。
- 本次只修改文档，没有修改代码。V8 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V8 — Events 列表页

### 前置条件检查

- 项目负责人已确认第二轮 Events 设计（`design_document.md` 7.5）并授权 V8；V1–V7 已提交。

### 已完成

- `apps/events/templates/events/event_list.html`：页头改为 `.page-heading`（等宽金色小标签 `Club activities` 与大标题 `Events`）；`Upcoming`/`Past` 由两个描边按钮改为 `<nav class="filter-tabs" aria-label="Event filters">` 中的两个普通链接，`?view=` 参数与 `aria-current="page"` 不变。
- `apps/events/templates/events/includes/event_card.html`：Past 活动的卡片加 `event-card--past`。
- `static_src/css/site.css`：新增 `.page-heading`、`.filter-tabs`（等宽大写文字、半透明金色底线，当前项金色文字加 2px 金色下划线，悬停为浅金）与 `.event-card--past .event-card__day`（低优先级文字色）；删除 `.event-list` 的上边距（标签页已提供间距）。
- 测试：`tests/test_event_pages.py` 新增断言——Past 视图卡片带 `event-card--past` 而 Upcoming 不带；两个视图都渲染 `filter-tabs` 导航，且只有当前视图带 `aria-current="page"`。既有浏览器测试按链接名称与 `aria-current` 定位筛选，无需修改。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过。
- Development server 截图走查 Upcoming 与 Past 的 1440 与 390px：均无横向溢出，标签高度 47px（满足 24px 触控目标），与确认的 mockup 一致。

### 当前边界与下一步门槛

- 没有修改 view、URL、业务逻辑或 migration；活动详情页属于 V9。
- `architecture.md` 尚未更新，需要项目负责人批准；V9 尚未开始。

### 项目负责人确认

- 项目负责人已确认 V8，并批准更新 `architecture.md`：新增 3.55 节，更新样式源、Events 列表模板、共享活动卡片与 Events 页面测试的文件职责。V9 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V9 — 活动详情页与报名区

### 前置条件检查

- V8 已确认并提交；设计规则见 `design_document.md` 7.5。

### 已完成

- `apps/events/templates/events/event_detail.html` 重写：
  - 顶部 `.back-link`「← Back to events」（箭头 `aria-hidden`），取代底部按钮；
  - `.page-heading`：等宽金色小标签 `Club activity`、H1 与状态标签（Past / `registration_available` / 其余为 Registration unavailable，与列表卡片同一判断）；
  - `.event-detail` 两栏：`<aside class="event-panel" aria-label="Event details and registration">` 在源码中位于说明之前（窄屏自然在前），宽于 `--breakpoint-hero` 时以 grid 放到右栏；面板内为 Sydney 时区的 `event-facts`（同日 `Date` 含星期与 `Time`，跨天 `Starts`/`Ends`，均含 `<time datetime>`）、可选 `View location in map`（新窗口安全属性不变）与报名区。
- `registration_panel.html`：Past、Registration unavailable 与 `Registered` 改为 `event-status status-tag`（`Registered` 另加 `status-tag--open`，取代 `status-banner`），`role="status"`、`tabindex="-1"`、`x-ref="status"` 与 HTMX/Alpine 契约不变；报名 dialog 标题上方加等宽小标签 `Risk Notice`。
- `registration_form.html`：版本行改为 `.notice-version`（等宽小字 `Notice version` + 版本号）；`confirm_page.html`（无 JavaScript 确认页）改用 `.page-heading` 与单行 `event-facts`（`Event`）。
- `static_src/css/site.css`：新增 `.back-link`（含 24px 以上触控目标的上下内边距）、`.event-detail-heading`、`.event-detail`/`__body`、`.event-panel`（顶部金色渐变线、纵向信息行）、`.event-panel__map`、报名区网格（按钮与状态占满面板宽度）、dialog 金色细边框与阴影、`.risk-notice-copy`（暖黑底细边框）、`.notice-version`、`.confirm-page__event`；`event-facts` 的网格位置改为只作用于 `.event-card`，以便在面板与确认页中复用。
- 测试：`test_event_pages.py` 改为新的状态 class，并新增顶部返回链接、页头状态、信息面板与“面板先于说明”的源码顺序断言；`test_event_registration_pages.py` 断言 `Registered` 为带 `role="status"` 的状态标签且不再使用 `status-banner`。
- 走查中修正：返回链接最初只有 19px 高，未通过 24px 触控目标门禁，增加上下内边距后通过。
- `design_document.md` 7.5 澄清：`Risk Notice` 小标签只用于报名 dialog（取消 dialog 不含 Risk Notice 正文）。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`（之后新增的 Events 断言另跑 `21 passed`）；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过。
- 截图走查使用一个临时测试（在 test database 中建立合成活动、合成 Risk Notice 与两名合成会员，截图后已删除，不进入仓库），覆盖 1440 与 390px 下的 Anonymous、会员可报名、已报名、报名关闭、Past、报名 dialog、取消 dialog 与无 JavaScript 确认页：均无横向溢出。

### 当前边界与下一步门槛

- 没有修改 view、URL、业务逻辑、表单字段或 migration；Development database 未写入任何数据。
- `architecture.md` 尚未更新，需要项目负责人批准；V10 尚未开始。

### V9 修订：详情页布局与报名 dialog 标题

- 项目负责人走查指出：宽屏两栏中标题与信息面板错层，左侧说明很短时中间留下大片空白；报名 dialog 的大标题应为 `Risk Notice`，`Confirm registration` 可作小字但需约为原先等宽小标签的两倍大。
- 详情页改为单栏：页头 → 通栏信息面板 → 说明。面板在宽于 `--breakpoint-hero` 时分为左右两列（左：横排信息行与地图链接，包在 `.event-panel__facts` 中；右：报名区），窄屏时纵向排列。面板顶部金色细线以 `align-self: start` 固定在边框处（垂直居中曾让它下移约 12px）。
- 报名 dialog：H2 改为 `Risk Notice`（`clamp(2.25rem, 6vw, 2.75rem)`），上方 `.event-registration-dialog__action` 显示 `Confirm registration`（等宽金色大写，1.375rem，约为原 0.75rem 小标签的两倍）；`aria-labelledby` 同时引用两者，可访问名称为 `Confirm registration Risk Notice`。取消 dialog 不变。
- 测试：`event-registration.mjs` 以精确名称 `Confirm registration Risk Notice` 定位 dialog，并断言其 H2 为 `Risk Notice`。`design_document.md` 7.5 同步更新。
- 以同一临时测试重新截取 1440/390px 下全部报名状态、两个 dialog 与无 JavaScript 确认页（截图后删除），均无横向溢出。

### V9 修订：详情页信息行换行、居中与地图链接

- 项目负责人用真实长度的数据走查后指出：信息行提前换行，按钮被挤成单独一列，结构突兀；建议标题与说明居中；地图链接改为在 `Location` 行内显示 `(View in Map)`。
- 信息面板改为两行：第一行为占满面板宽度的信息格（`flex: 1 1 16rem` 换行，1px 间隙配金色底绘制分隔线，单独成行的格子拉伸填满，不再出现空格子）；第二行为居中、宽 `min(100%, 20rem)` 的报名区。删除宽屏左右分列规则与 `.event-panel__facts`、`.event-panel__map`。
- 页头加 `.page-heading--center`（小标签、标题与状态标签居中）；说明栏宽 `min(100%, 48rem)` 居中，段落文字保持左对齐（多行居中文字难读；项目负责人如需文字本身居中可再调整）。
- 地图链接移入 `Location` 的 `<dd>`，文字改为 `(View in Map)`，仍为新窗口与 `noopener noreferrer`；`design_document.md` 7.5、7.6 同步改为该文案。
- 测试：`test_event_pages.py` 断言链接位于 `Location` 行内、文字为 `(View in Map)`，无地图链接时不出现；`event-pages.mjs` 按 `(View in Map)` 精确定位链接。
- 以临时测试（6 段长说明、合成地点与地图链接）截取 1440、820 与 390px：信息行在 1440px 一行、820px 两行（Location 独占并拉伸）、390px 逐行，均无横向溢出；临时测试已删除。

### V9 修订：状态标签移到小标签旁

- 项目负责人要求把状态标签放到 `Club activity` 旁边：页头改为 `.event-detail-kicker` 一行（`Club activity` · 状态标签，间隔点 `aria-hidden`），H1 单独一行；状态标签的描边样式不变。`.event-detail-heading` 删除。`design_document.md` 7.5 同步更新。
- 1440 与 390px 截图确认居中且无横向溢出（临时测试已删除）。

### 项目负责人确认

- 项目负责人已确认 V9（含全部走查修订），并批准更新 `architecture.md`：新增 3.56 节，更新样式源、活动详情、报名区、Risk Notice 表单与无 JavaScript 确认页模板及相关测试的文件职责。V10（第二轮质量门禁）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V10 — 第二轮质量门禁

### 前置条件检查

- V8、V9 已由项目负责人确认并提交推送（`a54795d`）；工作区干净，Docker PostgreSQL healthy。

### 验证结果

- `scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中完整通过（`Phase 4 end-to-end acceptance passed.`）：
  - 共享门禁 `scripts/verify_project.py`：`npm ci`、Chromium 安装、静态资源 build/check/watch smoke、Ruff lint/format（`All checks passed!`）、`makemigrations --check`、Django check（无问题）、干净 PostgreSQL 上的完整 pytest（`409 passed`，含全部 Phase 1–4 Playwright 与 Accessibility 门禁）、branch coverage `95%`、Production `check --deploy --fail-level WARNING`（无问题）与 manifest `collectstatic`。
  - 真实 Development server 上的 Phase 2、Phase 3、Phase 4 desktop/mobile smoke 全部通过。
- 验收后工作区仍然干净。
- 走查截图使用一个只在本地临时存在的测试（在 test database 中建立合成的开放、关闭与 Past 活动、合成 Risk Notice 与两名合成会员，截图后删除，不进入仓库），在 1440 × 900 与 390 × 844 下各 11 张，共 22 张：
  - Events 列表 Upcoming 与 Past；
  - 详情页 Anonymous（`Log in to register`）、会员可报名（`Register`）、已报名（`Registered` + `Cancel registration`）、报名关闭（Registration unavailable）、Past；
  - 报名 dialog（`Confirm registration` / `Risk Notice`）与取消 dialog；
  - 禁用 JavaScript 的报名确认页与取消确认页。
- 全部截图无横向溢出、无 page error；与项目负责人确认的 V8、V9 设计一致，走查中未发现需要修改的问题。截图保存在临时目录，已提交项目负责人走查；Development database 未写入数据。

### 当前边界与下一步门槛

- 走查问答：禁用 JavaScript 的完整报名确认页标题仍为 `Event registration` / `Confirm registration`（V9 只把 dialog 大标题改为 `Risk Notice`），Risk Notice 正文区沿用 dialog 的最大高度、需在框内滚动；项目负责人决定保持现状。
- 本步没有修改代码。`architecture.md` 尚未更新，需要项目负责人走查截图并批准。
- 后续页面按 About、Beginners & Safety → Members → 认证与 Account → 403/404/500 的顺序，逐页先确认设计再展开步骤。

### 项目负责人确认

- 项目负责人已走查 V10 截图并确认第二轮 Visual Refresh（Events）完成，批准更新 `architecture.md`：新增 3.57 节并更新页头状态。下一轮（About、Beginners & Safety）需要项目负责人先确认设计，再展开为具体步骤。

## Visual Refresh 第三轮 — About 与 Beginners & Safety 设计确认

- 以 mockup（1440 与 390px，临时目录，不进入仓库）提出两页设计：左对齐页头（新增等宽小标签 `About the club` / `Beginners & Safety`）、带编号的报告分节、补充说明段落、About 的编号功能卡片与 `Join`、Beginners & Safety 的编号流程、风险面板与单框规则列表。
- 走查修订：`Join` 改为在页面末尾居中；宽屏右侧空白较大，提出“正文延伸到右边缘”（B）与“整页收窄居中”（A）两个方案，项目负责人选择 B（左右 1 : 2 分宽）。
- 项目负责人已确认该设计。规则写入 `design_document.md` 7.9，页头小标签、`Join` 位置与 Draft Risk Notice 入口左对齐同步写入 7.7；`implementation.md` 新增第三轮步骤 V11（About 与共用报告分节）、V12（Beginners & Safety）、V13（第三轮质量门禁）。
- 本次只修改文档，没有修改代码。V11 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V11 — About 页与共用报告分节

### 前置条件检查

- 项目负责人已确认第三轮设计（`design_document.md` 7.7、7.9）并授权开始 V11；已重新阅读 `architecture.md` 与 `design_document.md`。

### 实施内容

- `about.html`：
  - 页头改为 `.page-heading`（等宽小标签 `About the club`、H1、`.lede`），左对齐并占满共享内容宽度（`public-page--report`，取代 `public-page--content` 窄栏）；
  - 四个区块改为 `.report-section`：金色细线、`aria-hidden` 的 `01–04` 编号与 H2 在 `.report-section__label`，正文在 `.report-section__body`；
  - `What We Do` 改用 Home 的 `.feature-grid` / `.feature-card`（`aria-hidden` 编号 `01–04`，项目名为 H3）；
  - 投票权说明段落加 `.report-note`；
  - Anonymous 的 `Join` 放在 `.report-action` 中居中（`data-public-primary` 与 Signup 链接不变，会员仍不显示）。
- `static_src/css/site.css`：
  - 新增 `.public-page--report`、`.report-section`（含 `__label`、`__index`、`__body`）、`.report-note`、分节内功能卡片（`minmax(20rem)` 自动列数：宽屏两列、窄屏一列，不新增断点）与 `.report-action`；
  - `@variant hero` 下分节为 `1fr : 2fr` 两列，编号与标题纵向排列；
  - `.button--hero` 改为 Hero 按钮尺寸（`min(100%, 16rem)`、`min-height: 3.5rem`、`1.375rem` 文字），并在 `max-nav` 下保持该宽度（窄屏按钮默认占满整行）；
  - 删除只被旧 About 使用的 `.card-grid`、`.public-card-list .content-card` 与 `.public-page__join-action`。
- 测试：
  - `test_public_information_pages.py`：Heading 顺序加入四个 H3，断言页头小标签、4 张功能卡片与 4 个分节；
  - `public-information.mjs`：
    - 宽屏分节标题列在正文左侧、正文右缘与页面右缘对齐；
    - 功能卡片两列；
    - `Join` 约 22px 文字、至少 56px 高、约 16rem 宽，并在页面中居中（取代旧的“九成宽、32px 文字”断言）；
    - 手机上编号标题在正文之上，`Join` 保持 16rem 宽；
    - About 也加入 200% 放大与无 JavaScript 检查；
    - 可读性检查加入 H3。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过。
- Development server 上 About（Anonymous）1440、820、390px 全页截图，均无横向溢出与 page error。走查中发现 `max-nav` 让 `Join` 在窄屏占满整行，已修正为保持 16rem 并加入断言。

### 当前边界与下一步门槛

- 没有修改 view、URL、Metadata、文案或 migration；Beginners & Safety 仍为旧布局（V12）。
- `architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V11 截图并确认，批准更新 `architecture.md`：新增 3.58 节，更新页头状态以及样式源、About 模板与相关测试的文件职责。V12（Beginners & Safety）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V12 — Beginners & Safety 页

### 前置条件检查

- V11 已由项目负责人确认并提交推送（`0d8560d`）；项目负责人授权开始 V12。

### 实施内容

- `beginners_safety.html`：
  - 页头改为 `.page-heading`（等宽小标签 `Beginners & Safety`、H1、`.lede`），`public-page--report` 占满共享内容宽度；
  - 五个区块改为 V11 的 `.report-section`（`aria-hidden` 编号 `01–05` 与 H2）；
  - `What to Expect` 改为 `<ol class="procedure">`；
  - 风险说明改为分节正文中的 `.risk-panel`，`Read the Draft Risk Notice`（`data-draft-risk-notice`，仍只在 `draft_risk_notice_visible` 时输出）位于面板内正文下方；
  - 不确定身体状况的段落加 `.report-note`；
  - `During Training` 改为 `<ul class="rule-list">`。
- `static_src/css/site.css`：
  - 新增 `.procedure`（等宽编号方块，金色细竖线连接相邻方块的中心）、`.risk-panel`（暖色底、金色细边框与顶部金色渐变细线，按钮左对齐）与 `.rule-list`（单一金色细边框、行间细线、金色小方块标记）；
  - 删除 `.step-list`、`.safety-list`、`.safety-panel`、`.safety-panel__action` 及其在共享卡片表面、末子元素间距与居中操作分组中的条目。`--color-warning` / `--color-warning-surface` 仍由 `.status-banner` 与表单使用。
- 测试：
  - `test_public_information_pages.py`：断言页头小标签、5 个分节、各含 5 项的流程与规则列表；
  - `test_draft_risk_notice.py`：Draft 入口位于 `.risk-panel` 内；
  - `draft-risk-notice.mjs`：入口改为在面板内容左缘对齐且位于正文下方（取代“面板内居中”）；
  - `phase2-accessibility.mjs`：必需元素改为 `.procedure`、`.rule-list`、`.risk-panel`；
  - `public-information.mjs`：宽屏流程方块同列且后四项有 1px 连接线、规则 5 行、风险面板位于分节标题右侧。

### 验证结果

- 完整 pytest（含全部 Playwright 与 Accessibility 门禁）在全新 test database 上 `409 passed`；`static:check`、Ruff lint/format、Django check、`git diff --check` 通过。
- 截图使用一个只在本地临时存在的测试（Test settings 的 live server，Draft 关闭与 `override_settings` 开启两种状态，截图后删除），覆盖 1440、820、390px，共 6 张，均无横向溢出与 page error。

### 当前边界与下一步门槛

- 没有修改 view、URL、Metadata、文案或 migration；Draft 入口的环境开关逻辑不变。
- `architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V12 截图并确认，批准更新 `architecture.md`：新增 3.59 节，更新页头状态以及样式源、Beginners & Safety 模板与相关测试的文件职责。V13（第三轮质量门禁）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V13 — 第三轮质量门禁

### 前置条件检查

- V11、V12 已由项目负责人确认并提交推送（`a92b6ad`）；工作区干净，Docker PostgreSQL healthy；项目负责人授权开始 V13。

### 验证结果

- `scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中完整通过（`Phase 4 end-to-end acceptance passed.`）：
  - 共享门禁 `scripts/verify_project.py`：`npm ci`、Chromium 安装、静态资源 build/check/watch smoke、Ruff lint/format（`All checks passed!`）、`makemigrations --check`、Django check（无问题）、干净 PostgreSQL 上的完整 pytest（`409 passed`）、branch coverage `95%`、Production `check --deploy --fail-level WARNING`（无问题）与 manifest `collectstatic`。
  - 真实 Development server 上的 Phase 2、Phase 3、Phase 4 desktop/mobile smoke 全部通过。
- 验收后工作区仍然干净。
- 走查截图使用一个只在本地临时存在的测试（Test settings 的 live server、一名合成已验证会员，Draft 关闭与 `override_settings` 开启两种状态，截图后删除），在 1440 × 900 与 390 × 844 下覆盖 About 与 Beginners & Safety 的 Anonymous/会员 × Draft 开/关，共 16 张：
  - About：Anonymous 显示居中的 `Join`，会员不显示；
  - Beginners & Safety：Draft 开启时风险面板内显示 `Read the Draft Risk Notice`，关闭时面板只有风险说明；Header 的 `Draft Risk Notice` 导航同步出现或消失。
- 全部截图无横向溢出、无 page error；与项目负责人确认的 V11、V12 一致，走查中未发现需要修改的问题。截图保存在临时目录，已提交项目负责人走查；Development database 未写入数据。

### 当前边界与下一步门槛

- 本步没有修改代码。`architecture.md` 尚未更新，需要项目负责人走查截图并批准。
- 后续页面按 Members → 认证与 Account → 403/404/500 的顺序，逐页先确认设计再展开步骤。

### 项目负责人确认

- 项目负责人已走查 V13 的 16 张截图并确认，批准更新 `architecture.md`：新增 3.60 节并更新页头进度与状态。第三轮（About 与 Beginners & Safety）完成；Members 的设计确认尚未开始，需要项目负责人明确授权。

## Visual Refresh 第四轮 — Members 设计确认

- 项目负责人提出在会员名字或 Avatar 旁加入金色 `Researcher ##` 标签。会员资料原本没有编号字段，因此先请项目负责人决定号码来源：在“首次 Publish 时自动编号”“邮箱验证时自动编号”“管理员手动分配”中选择了管理员手动分配。
- 以 mockup（1440 与 390px，合成会员与程序生成的抽象头像，临时目录，不进入仓库）提出 Members 列表与详情设计：左对齐页头、金色细边框卡片（整卡可点击）、图纸式资料格、详情信息面板、`Bio`/`Links` 报告分节；Researcher 标签给出“名字上方”（A）与“压在头像下沿”（B）两个位置，项目负责人选择 A。
- 规则写入 `design_document.md`：4.4（Researcher 编号的分配、唯一性、显示格式与公开边界，卡片公开字段与 Admin 可维护字段）、3.4、7.8（Publish confirmation 列出编号）、新增 7.10（Members 版式）与 11.1（允许公开）。`implementation.md` 在 Step 8 字段表与 Migration 顺序中加入 `researcher_number` / `members.0002`，并新增第四轮步骤 V14（编号数据与 Admin）、V15（Members 列表）、V16（Member detail 与 Preview）、V17（第四轮质量门禁）。
- 本轮经项目负责人批准新增一个字段与 migration（只在 V14），这是与前几轮“不改 migration”约束的唯一差异。
- 本次只修改文档，没有修改代码。V14 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V14 — Researcher 编号的数据与 Admin

### 前置条件检查

- 项目负责人已确认第四轮 Members 设计（`design_document.md` 4.4、7.10、11.1）并授权开始 V14；已完整阅读 `architecture.md` 与 `design_document.md`。

### 实施内容

- `apps/members/models.py`：
  - 新增 `researcher_number`（`PositiveIntegerField`，可空，`unique=True`，`MinValueValidator(1)`，verbose name `Researcher number`，Admin 帮助文字说明公开格式与留空含义）；
  - 新增数据库约束 `members_profile_researcher_number_positive`（为空或不小于 1）；唯一性由字段级唯一索引保证，多个空值可以共存；
  - 新增 `researcher_label` 属性：未分配时为 `None`，否则为至少两位补零的 `Researcher 07`（100 及以上照常显示）。
- `apps/members/migrations/0002_memberprofile_researcher_number.py`：加入字段与检查约束（已在 Development database 应用）。
- `apps/members/admin.py`：列表增加可排序的 `Researcher number` 列；change form 中 `researcher_number` 与 `is_hidden_by_admin`、`executive_role` 并列为唯一可编辑字段，其余字段仍只读，新增与删除入口仍关闭。
- `profile_publish_confirm.html`：公开字段清单在名称之后加入一项——已分配时为 `Researcher number (Researcher 07)`，未分配时为 `Researcher number, if one has been assigned`。
- 会员可写表单 `MemberProfileForm` 的显式字段白名单没有变化，因此会员无法提交该字段。本步没有修改任何公开页面版式。

### 验证结果

- 新增与更新测试：
  - `test_member_profile.py`：默认无编号无标签；`01`/`07`/`42`/`100` 显示格式；多个空值共存；重复号码在 model 校验中被拒绝、直接写库时被唯一索引拒绝；`0` 在 model 校验中被拒绝、直接写库时被检查约束拒绝；会员表单不含该字段且伪造提交不改变已分配号码；Admin 可编辑字段集合加入该字段。
  - `test_member_profile_admin.py`：获授权 Staff 可分配、修改与清除号码；`0`、`-3`、非数字与重复号码显示字段错误且不写入；列表显示并可按编号排序；可编辑字段集合更新。
  - `test_profile_publication.py`：确认页在未分配与已分配时分别显示对应文字。
- 完整 pytest 在全新 test database 上 `426 passed`（原 409 + 新增 17）；Ruff lint/format、Django check、`makemigrations --check` 与 `git diff --check` 通过。本步没有修改 CSS 或静态资源。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、一名合成 Superuser 与两名合成会员，截图后删除）：Admin 列表、已分配号码的修改页、填写重复号码时的字段错误，以及 Publish 确认页（已分配/未分配）的 1440 与 390px 截图，共 7 张，均无横向溢出与 page error；Development database 未写入合成数据。

### 当前边界与下一步门槛

- Members 列表、详情与 Preview 尚未显示标签（V15、V16）。
- `architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V14 截图并确认，批准更新 `architecture.md`：新增 3.61 节，更新页头进度与状态，在 3.3、3.6、3.32 注明 Researcher 编号为管理员可编辑字段，并更新 MemberProfile model、Admin、Publish confirmation 模板、新 migration 与相关测试的文件职责。V15（Members 列表）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V15 — Members 列表页

### 前置条件检查

- 项目负责人批准 V14 文档后要求直接进入下一步（Members 页面），视为授权开始 V15；V14 的代码、migration 与文档尚未提交（项目负责人未要求提交）。本会话已完整阅读 `architecture.md` 与 `design_document.md`。

### 实施内容

- `member_list.html`：
  - 外层改为 `<section class="members-page">`，页头改为 `.page-heading`（等宽小标签 `Club community`、H1、`.lede`），取代 `eyebrow` 与普通段落；
  - 卡片内容依次为：已分配时的 `gold-tag` Researcher 标签（`Researcher 07`，来自 `researcher_label`）、H2 名称链接、`<dl class="member-facts">` 资料格；未分配号码时不输出标签；
  - 卡片字段白名单、排序、详情链接、Avatar include、`aria-labelledby` 与 empty state 结构不变。
- `static_src/css/site.css`：
  - 新增 `.members-page`（页头与卡片网格间距 `clamp(2rem, 5vw, 3rem)`）；
  - `.member-directory` 改为 `auto-fill` / `minmax(min(100%, 22rem), 1fr)`：1440px 三列、820px 两列、手机一列，不新增断点；
  - `.member-card`：金色细边框与顶部金色渐变细线、`6.5rem` 方形 Avatar（金色细边框、直角、页面底色 fallback），悬停时边框提亮、名称变为浅金；`max-nav` 下 Avatar `5rem`、名称 1.5rem；
  - 名称链接以 `::after` 覆盖整张卡片，整卡可点击；名称自身的 Focus outline 取消，改由 `.member-card:has(:focus-visible)` 在卡片外框绘制同样的金色 Focus 环；
  - 新增 `.member-card__tag`（左对齐、不换行）与共用图纸式资料格 `.member-facts`（等宽大写、标签低优先级色居左、数值主文字色居右，行间金色细线）；
  - 删除 `.member-card__details` 系列规则，断行分组改为 `.member-facts dd`。
- 测试：
  - `test_member_directory.py`：页头小标签与 H1；已分配号码的卡片在 H2 之前输出 `Researcher 07` 金色标签，未分配的卡片没有标签；未发布与被隐藏资料的号码不出现在列表中。
  - `member-directory.mjs`（合成会员 Alpha 分配 7 号）：标签位于名称正上方且左对齐、无号码的卡片没有标签、桌面两张卡片同一行并排、名称获得键盘 Focus 时整张卡片出现 outline、点击卡片右下角即可进入详情。

### 验证结果

- 完整 pytest 在全新 test database 上 `429 passed`；`static:check`、Ruff lint/format、Django check 与 `git diff --check` 通过。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、六名合成会员，头像为程序生成的抽象图，截图后删除）：列表 1440、820、390px，桌面键盘 Focus 与悬停状态，以及空状态 1440、390px，共 6 张，均无横向溢出与 page error。
- 空状态沿用原有的共享卡片样式（H2 + 说明），7.10 没有规定其新样式。

### 当前边界与下一步门槛

- Member detail 与 Preview 仍为旧布局（V16）。
- `architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V15 截图并确认，批准更新 `architecture.md`：新增 3.62 节，更新页头进度与状态，以及样式源、Members 列表模板与相关测试的文件职责。V16（Member detail 与 Preview）尚未开始，需要项目负责人明确授权；空状态样式未另作决定，保持现状。

## Visual Refresh Step V16 — Member detail 与本人 Preview

### 前置条件检查

- V14、V15 已由项目负责人确认并提交推送（`af972b1`）；项目负责人授权开始 V16。本会话已完整阅读 `architecture.md` 与 `design_document.md`。

### 实施内容

- `members/includes/profile_public_fields.html`（详情与 Preview 共用）重写为：
  - `.profile-panel` 信息面板：左侧 Avatar 或首字母 fallback（`public_avatar.html`，block 为 `profile-panel`），右侧依次为 `.profile-kicker`（等宽 `Member profile`，已分配号码时加装饰性间隔点与 `gold-tag` Researcher 标签）、名称、等宽 `@username`、`.member-facts` 资料格；
  - `Bio` 与 `Links` 改为 `.report-section`，没有内容的分节不输出，编号按出现顺序连续（只有 Links 时为 `01`）；
  - 标题层级：详情页名称为 H1、分节为 H2；Preview 名称为 H2、分节为 H3（原先详情页的 H1 之后直接是 H3）。
- `member_detail.html`：外层 `.member-profile`，顶部改为与活动详情一致的 `.back-link`「← Back to members」（取代普通链接 `Back to Members`）。Preview 页面外壳、隐藏提示与操作按钮不变。
- `static_src/css/site.css`：
  - 新增 `.member-profile` / `.profile-public` 纵向间距、`.profile-panel`（金色细边框、顶部金色渐变细线；`@variant hero` 下 `15rem : 1fr` 两列，否则 Avatar 在上；`max-nav` 下 Avatar 11rem）、`.profile-kicker`、`.profile-panel__username`，面板内 `.member-facts` 改为可整格换行的横向格子；Preview 的 H2 名称与公开 H1 使用同一字号、字重与大写；
  - 报告分节的 H3 与 H2 同样式（供 Preview 使用）；
  - 删除 `.profile-public-card` 系列规则及其在共享卡片表面、Avatar、断行分组和 `max-nav` 中的条目，改为 `profile-panel` / `profile-public` 对应项。
- 测试：
  - `test_member_detail.py`：返回链接、标题层级（H1 名称、H2 Bio/Links）、kicker 中的小标签与 `Researcher 07` 位于 H1 之前、分节编号 `01`/`02`；只有 Links 时编号为 `01`、未分配号码时没有标签、什么都没填时没有分节。
  - `test_profile_publication.py`：Preview 使用同一面板、标题层级为 H1 页面标题 → H2 名称 → H3 Bio/Links，并显示 `Researcher 12`。
  - `member-directory.mjs`：桌面详情 Avatar 在身份信息左侧、标签在名称上方、存在 `Back to members` 与 H2 `Bio`；手机详情 Avatar 在身份信息上方，未分配号码时没有标签。

### 验证结果

- 完整 pytest 在全新 test database 上 `432 passed`；之后只调整了 Preview H2 的大写与字重（CSS），重新运行 Members 浏览器、Phase 3 Accessibility 与静态资源测试 `28 passed`。`static:check`、Ruff lint/format、Django check 与 `git diff --check` 通过。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、四名合成会员，头像为程序生成的抽象图，截图后删除）：详情页完整/只有 Links/未填写三种组合、本人 Preview、被管理员隐藏时的 Preview，在 1440 与 390px 下，加上 820px 完整详情，共 11 张，均无横向溢出与 page error。

### 当前边界与下一步门槛

- Preview 页面外壳（窄栏页头、隐藏提示、操作按钮）与 Publish/Unpublish 确认页仍为旧样式，属于认证与 Account 轮次。
- `architecture.md` 尚未更新，需要项目负责人走查截图并批准。

### 项目负责人确认

- 项目负责人已走查 V16 截图并确认，批准更新 `architecture.md`：新增 3.63 节，更新页头进度与状态、3.31 的标题层级说明，以及样式源、详情模板、共享公开字段组件与相关测试的文件职责。V17（第四轮质量门禁）尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V17 — 第四轮质量门禁

### 前置条件检查

- V14–V16 已由项目负责人确认并提交推送（`1553bc4`）；工作区干净，Docker PostgreSQL healthy；项目负责人授权开始 V17。

### 验证结果

- `scripts/accept_phase_4.py` 在 OS 临时目录的全新 uv environment 中完整通过（`Phase 4 end-to-end acceptance passed.`）：
  - 共享门禁 `scripts/verify_project.py`：`npm ci`、Chromium 安装、静态资源 build/check/watch smoke、Ruff lint/format（`All checks passed!`）、`makemigrations --check`（含 V14 的 `members.0002`）、Django check（无问题）、干净 PostgreSQL 上的完整 pytest（`432 passed`）、branch coverage `95%`、Production `check --deploy --fail-level WARNING`（无问题）与 manifest `collectstatic`。
  - 真实 Development server 上的 Phase 2、Phase 3、Phase 4 desktop/mobile smoke 全部通过。
- 验收后工作区仍然干净。
- 走查截图使用一个只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、七名合成会员，头像为程序生成的抽象图，截图后删除），在 1440 × 900 与 390 × 844 下各 7 张，共 14 张：
  - Members 列表（有/无编号、有/无 Avatar、长名称；被管理员隐藏的 3 号资料不出现）与空状态；
  - Member detail 的完整、只有 Links、未填写三种组合；
  - 本人 Preview 与被管理员隐藏时的 Preview（显示中性提示与编号标签）。
- 全部截图无横向溢出、无 page error；与项目负责人确认的 V15、V16 一致，走查中未发现需要修改的问题。Development database 未写入数据。

### 当前边界与下一步门槛

- 本步没有修改代码。`architecture.md` 尚未更新，需要项目负责人走查截图并批准。
- 后续页面按认证与 Account → 403/404/500 的顺序，逐页先确认设计再展开步骤；Preview 页面外壳与 Publish/Unpublish 确认页属于认证与 Account 轮次。

### 项目负责人确认

- 项目负责人已走查 V17 的 14 张截图并确认，批准更新 `architecture.md`：新增 3.64 节并更新页头进度与状态。第四轮（Members）完成；认证与 Account 的设计确认尚未开始，需要项目负责人明确授权。

## Visual Refresh 第五轮 — 认证与 Account 设计确认

- 项目负责人授权开始认证与 Account 的设计确认。以 mockup（1440 与 390px，合成会员与程序生成的抽象头像，临时目录，不进入仓库）提出 Log in、Join the Club、密码重置、Account、Edit Profile、Profile Preview 与 Publish Profile 设计，并附现有页面截图对照：
  - 共用表单字段改为等宽大写 Label、直角金色细边框输入框，Checkbox 放在 Label 前同一行；
  - 认证页面左侧页头、右侧带顶部金色渐变细线的访问面板，窄屏上下排列；
  - Account 改为四个编号报告分节与图纸式表格，资料摘要显示发布状态标签与 Researcher 标签；
  - Edit Profile 一张表单分为三个编号分节，末尾操作栏；Preview 的公开组件放入 `Public view` 虚线框；Publish 确认页分为公开字段规则列表与公开页面表格。
- 项目负责人确认设计，同时确认其中的文案变动：新增 `Member access`、`Membership`、`Member settings`、`Private preview`、`Publication confirmation` 页头小标签，Edit Profile 的 `Name and avatar`、`About you`、`Links` 分节标题，`Public view`、`What becomes public`、`Your public page`、`Public name`、`Profile URL`；Log in 页删除重复的 `Forgot password?` 按钮（保留 allauth 的 `Forgot your password?` 链接）；去掉 Label 末尾冒号；Account 显示发布状态与 Researcher 标签。
- 规则写入 `design_document.md`：新增 7.11（认证与 Account 版式），7.8 的 Account 结构描述改为引用 7.11。`implementation.md` 新增第五轮步骤 V18（共用表单字段与认证页面）、V19（Account）、V20（Edit Profile、Preview 外壳与 Publish/Unpublish）、V21（第五轮质量门禁）。
- 本次只修改文档，没有修改代码。V18 尚未开始，需要项目负责人明确授权。

## Visual Refresh Step V18 — 共用表单字段与认证页面

### 前置条件检查

- 项目负责人已确认第五轮设计（`design_document.md` 7.11）并授权开始 V18；已完整阅读 `architecture.md` 与 `design_document.md`。

### 实施内容

- 字段 Label 去掉末尾冒号：
  - 新增 `apps/core/templatetags/form_labels.py` 的 `plain_label` filter，以 `label_suffix=""` 输出 label 或 legend；
  - `templates/includes/forms/field.html` 改为 Django `django/forms/field.html`（即 `as_field_group` 所用模板）的项目副本，只把 label 换成该 filter，id、`aria-invalid` 与 `aria-describedby` 仍由 BoundField 提供；
  - 用临时脚本比较 Login、Reset、Signup（含错误）与 Profile 表单全部字段：新旧输出除冒号外完全一致；
  - Django Admin 不经过该模板，保留冒号。
- `static_src/css/site.css` 的共用字段样式：
  - Label 为等宽大写小字、次要文字色；
  - 输入框、下拉框与多行文本框为直角、页面底色、新 token `--color-input-border`（`#8a6c30`，不透明金色）细边框，悬停时为金色；错误时的红色边框优先；
  - Checkbox 放在 Label 前同一行，帮助文字与错误整行显示；
  - 7.11 写的是“半透明金色细边框”；为满足 WCAG 1.4.11（输入框边界对背景至少 3:1），输入框改用不透明的较亮金色：对页面底色 4.0:1，对卡片表面 3.6:1。原 30% 金色细线只有约 1.9:1。原 `--color-input` token 不再使用，已删除。
- 访问页面：
  - `templates/account/_page.html` 改为 `.access-page`：`.page-heading`（`label-mono` 小标签、`page-title` H1、intro）加 `.access-panel`（金色细边框、顶部金色渐变细线、卡片表面）；
  - 宽于 `--breakpoint-hero` 时为 `1fr : 30rem` 两列，窄屏上下排列；
  - 面板内主按钮占满宽度；其他入口放在 `.access-panel__alt`（金色细线之下，按钮同样占满宽度）；
  - 面板内的文字链接（密码重置帮助链接、`Join the Club`、`Log in` 等）保证 24px 触控目标。
- 套用到全部 allauth 页面：
  - `panel_form.html` 与 `code_form.html` 去掉旧 `.panel` 包裹；
  - Login 删除重复的 `Forgot password?` 按钮，`Log in by email code` 与 `Need an account?` 移到分隔线下；
  - Signup、Magic Code 请求、Password reset 的返回或切换链接移到分隔线下；
  - 两个验证码页的换邮箱 details 与 Cancel 移到分隔线下；
  - Password change 去掉 `.panel`；
  - 只有单个按钮的页面（Account inactive、Reset done、Reset 链接失效、Reset 完成）把按钮直接放进面板。
- 文案、URL、字段与顺序、allauth 流程、Alpine USYD 条件字段均未改动。Account 与 Edit Profile 只随共用字段样式变化，版式留给 V19、V20。

### 测试

- `test_authentication_templates.py` 新增：
  - 六个公开认证页与两个会员页使用页头加单个访问面板；
  - Login 只保留一个指向 Password reset 的链接（allauth 的 `Forgot your password?`），`Log in by email code` 与注册链接位于分隔线区域；
  - 站点表单 Label 没有冒号；
  - Django Admin Label 保留冒号。
- `test_static_assets.py`：`--color-input-border` 对页面底色与卡片表面至少 3:1。
- `authentication-ui.mjs`：在 1440 与 390px 下检查 Login、Signup、Magic Code 请求与 Password reset：
  - 无溢出，`main` 内触控目标至少 24px；
  - 宽屏面板在页头右侧且不超过 30rem，手机在页头下方；
  - 主按钮与表单同宽；
  - Label 为等宽大写且无冒号；
  - Remember me 的 checkbox 在 Label 前同一行；
  - `Log in by email code` 占满面板宽度。

### 验证结果

- 完整 pytest 在全新 test database 上 `448 passed`。
- `static:check`、Ruff lint/format、Django check、`makemigrations --check`（无变化）与 `git diff --check` 通过。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、一名合成会员，截图后删除），共 25 张，均无横向溢出、无冒号 Label、无 page error：
  - 1440 × 900 下 15 张：Login（含错误）、Signup（含 USU ID 服务端错误）、Verify email、Magic Code 请求与确认、Password reset 及完成页、失效 reset 链接、Account inactive、Logout、Password change、Account、Edit Profile；
  - 390 × 844 下 10 张：除 Verify email、Reset 完成页、失效链接、Account inactive 与 Logout 外的同一组页面。

### 当前边界与下一步门槛

- 项目负责人已走查截图并批准 V18，包括输入框使用不透明金色边框的差异；`design_document.md` 7.11 已同步该写法。
- 走查中发现：新增 templatetags 包后，已在运行的 Development server 会报 `'form_labels' is not a registered tag library`；Django 只在启动时登记模板标签库，重启后正常，代码无需修改。
- 项目负责人确认 Account 页面的 `Log out` 继续直接 POST 登出，不增加确认页。
- `architecture.md` 已新增 3.65 并更新对应文件职责。V19（Account）尚未开始。

## Visual Refresh Step V19 — Account 页面

### 前置条件检查

- 项目负责人已批准 V18 并授权开始 V19；已完整阅读 `architecture.md` 与 `design_document.md`；Account 版式以 7.11 及第五轮确认的 mockup 为准。

### 实施内容

- `apps/accounts/templates/accounts/account.html` 改为报告页结构，取代原先窄栏中的三张 `.panel` 卡片：
  - 页头为 `label-mono` 小标签 `Member settings` 与 H1 `Account`；
  - 四个 `.report-section`：`01 Account details`、`02 Public member profile`、`03 USYD and USU details`、`04 Security`，节标题均为 H2（原 `Public member profile` 为 H3）；
  - 没有 MemberProfile 时第二节不输出，编号按实际顺序连续（`01`–`03`）。
- 新增图纸式表格 `.facts-table`（等宽大写标签列为低优先级文字色，数值为主文字色，行间金色细线）：
  - Account details 列出 Username、Email、Email verification、USU review status；
  - Profile 资料列出 Bio、Experience level、Preferred arm、Instagram Username、Other social URL，空值仍为 `Not provided` / `Not specified`；
  - 窄于 `--breakpoint-hero` 时标签在数值上方。
- 资料摘要 `.account-summary`：
  - 左侧 6rem 方形 Avatar（alt 仍为 `Current avatar for …`），没有 Avatar 时为对辅助技术隐藏的首字母 fallback；
  - 右侧依次为发布状态标签（`Published` 为 `status-tag--open` 金色文字，`Not published` 与 `Unavailable on public pages` 为次要文字色，均不填充）与已分配时的 Researcher `gold-tag`、公开名称（Display name 为空时回退 Username）、等宽公开路径 `/members/<username>/`（由 `members:detail` 反向解析）；
  - 按 mockup，原表格中的 `Publication status`、`Display name` 与 `Avatar` 三行由摘要取代。
- Username/可选资料说明改用 `.report-note`；Edit、Preview、Publish/Unpublish 入口不变。
- USYD/USU 表单与 Security 按钮在宽屏左对齐、保持自身宽度；手机上沿用全站规则占满宽度（与 mockup 一致）。`Log out` 仍为直接 POST。
- CSS：删除只被旧 Account 使用的 `.definition-list` 与 `.account-profile-summary` 规则（含共享 Avatar 与断行分组中的条目），以及因此不再使用的 `--color-separator` token；新增 `.facts-table`、`.account-summary` 系列与报告分节内表单按钮左对齐规则。
- view、URL、form、Alpine 条件字段、隐私边界、文案与 migration 均未改动。

### 测试

- `test_account_page.py`：
  - 页头小标签与 H1、四个编号分节的顺序与标题、两张 facts 表格、不再使用 `.panel`；
  - 没有 Profile 时分节编号 `01`–`03` 连续；
  - 摘要中的 `Published` 金色标签位于 Researcher 标签之前、公开名称、公开路径与首字母 fallback；
  - 未发布与管理员隐藏为普通标签、未分配编号时不输出 Researcher 标签、名称回退 Username；
  - 原有 Profile 摘要测试改为 H2 标题，去掉已不存在的 `Not provided` Avatar 行。
- `phase3-accessibility.mjs`：`Public member profile` 改为 H2；桌面断言表格标签与数值同行、Avatar 在摘要左侧、`Update account` 左对齐且不拉伸、状态标签为等宽字体；手机断言标签在数值上方、Avatar 仍在摘要左侧。
- `phase1-core-flows.mjs`：Username 与 `Pending` 的查找限定在 `Account details` 区域（摘要的名称回退也会显示 Username）。

### 验证结果

- 完整 pytest 在全新 test database 上 `453 passed`。
- `static:check`、Ruff lint/format、Django check、`makemigrations --check`（无变化）与 `git diff --check` 通过。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、四名合成会员与程序生成的抽象头像，截图后删除），共 12 张，均无横向溢出与 page error：
  - 1440 × 900 与 390 × 844 各 5 张：已发布含编号与 Avatar（USU Pending）、未发布无 Avatar 且非 USYD、管理员隐藏含编号（USU Verified）、未发布长名称（USU Rejected）、USU ID 服务端错误；
  - 另有 820px 已发布与 640px 视口 200% 字号已发布各 1 张。
- USU 错误截图中 `Skip to main content` 出现在页面中部：经检查焦点正确落在 USU ID 字段，跳转链接仍位于视口上方隐藏，是全页截图对 fixed 元素的绘制方式，不是页面问题。

### 当前边界与下一步门槛

- 项目负责人已走查截图并批准 V19；`architecture.md` 已新增 3.66 并更新对应文件职责。V20（Edit Profile、Preview 外壳与 Publish/Unpublish）尚未开始。

## Visual Refresh Step V20 — Edit Profile、Preview 外壳与 Publish/Unpublish 确认页

### 前置条件检查

- 项目负责人已批准 V19（已提交并推送）并授权开始 V20；已完整阅读 `architecture.md` 与 `design_document.md`；版式以 7.11 及第五轮确认的 mockup 为准。

### 实施内容

- `profile_edit.html` 改为报告页结构，取代原窄栏 `.panel`：
  - 页头为 `label-mono` 小标签 `Member profile`、H1 `Edit Profile` 与 `.lede`；
  - 同一张 `form.settings-form` 分为三个 `.report-section`：`01 Name and avatar`（Display name 与 Avatar 编辑区）、`02 About you`（Bio；Experience level 与 Preferred arm 放在 `.field-pair` 中，宽度足够时并排）、`03 Links`（Instagram Username、Other social URL）；
  - Avatar 编辑区：有 Avatar 时加 `avatar-editor--current`，宽于 `--breakpoint-hero` 时左侧为 8rem 方形当前 Avatar（金色细边框、直角），右侧 `.avatar-editor__controls` 依次为上传、metadata 提示与删除 Checkbox；窄屏纵向排列；没有 Avatar 时只有上传控件；
  - 末尾操作栏复用 `.report-action`（金色细线之下），新增修饰类 `report-action--start` 使按钮在宽屏左对齐、保持自身宽度，手机仍按全站规则占满宽度。
- `profile_preview.html`：页头为 `Private preview` 与 H1 `Profile Preview`；公开字段组件放进 `.preview-frame`（半透明金色虚线框），框顶 `.preview-frame__label` 为金色等宽 `Public view` 与该资料的公开路径（由 `members:detail` 反向解析）；管理员隐藏提示在框之前、操作按钮在框之后。公开组件与 H1 → H2 → H3 层级不变。
- `profile_publish_confirm.html`：页头为 `Publication confirmation` 与 H1；`01 What becomes public` 的八项公开字段改用 `.rule-list`；`02 Your public page` 为 `.facts-table`（`Public name`、`Profile URL`），其下为 Avatar metadata 警示与 `.report-note` 说明；确认表单（CSRF、`Publish profile`、`Return to preview`）在分节之后，使用 `report-action report-action--start`。
- Username 回退说明：mockup 的 Publish 页没有这句，但 7.11 要求保留，因此放在警示之下的补充说明中：`Your Username is always part of your public profile URL.`，Display name 为空时接 `It is also your public name because no Display name is set.`。原两句（`Your Username will be part of your public profile URL: …` 与 `Your public name will be …, using your Username because …`）由表格与这段说明取代。
- `profile_unpublish_confirm.html`：同样的页头与 lede；`01 Your public page` 为同一张 `Public name` / `Profile URL` 表格；确认表单在分节之后。7.11 只写“相同的页头、分节与表格写法”，没有 mockup，此处只放一个分节。
- 管理员隐藏提示（`profile_hidden_notice.html`）、Publish/Unpublish 入口、view、URL、form、CSRF POST、幂等 service、固定 redirect、文案（除上述 Username 回退说明）与 migration 均未改动。
- CSS：
  - 删除只被这几页使用的 `.content-narrow`、`.panel`、`.profile-flow` 规则及其在共享卡片表面、Avatar 与断行分组中的条目；`.avatar-preview` 移出共享 Avatar 分组，改为金色细边框直角；
  - 新增 `.settings-form`、`.field-pair`、`.avatar-editor--current`（`@variant hero` 两列）、`.avatar-editor__controls`、`.report-action--start`、`.preview-frame`、`.preview-frame__label`（长路径可断行）与 `.facts-table code`；
  - `.eyebrow` 仍被错误页使用，保留。

### 测试

- `test_profile_edit.py`：页头小标签、三个编号分节的标题与顺序、七个字段各在正确分节内、两项下拉在 `.field-pair` 中、无 Avatar 时没有删除控件、保存按钮位于全部字段之后。
- `test_profile_publication.py`：
  - Publish 页两个编号分节、规则列表 8 项、`Public name` 与 `Profile URL` 表格行、设置 Display name 时不输出回退说明、确认按钮位于分节之后；回退说明断言改为新文字；
  - Unpublish 页一个分节与同一表格；
  - Preview 的虚线框含 `Public view`、本人公开路径与公开面板，隐藏提示在框前，`Back to Account` 与 `Unpublish profile` 在框外。
- `test_avatar_lifecycle.py`：有 Avatar 时编辑区带 `avatar-editor--current`。
- `phase3-accessibility.mjs`：桌面断言当前 Avatar 在上传控件左侧、两项下拉并排、`Save changes` 左对齐不拉伸、Preview 框为虚线且标签为 `Public view /members/<owner>/`、框内有公开面板没有按钮；手机断言 Avatar 在上传控件上方、两项下拉上下排列。

### 验证结果

- 完整 pytest 在全新 test database 上 `457 passed`。
- `static:check`、Ruff lint/format、Django check、`makemigrations --check`（无变化）与 `git diff --check` 通过。
- 走查截图使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、四名合成会员与程序生成的抽象头像，截图后删除），共 24 张，均无横向溢出与 page error：
  - 1440 × 900 与 390 × 844 各 10 张：Edit Profile（有 Avatar、空资料、HTTPS 链接服务端错误）、Preview（已发布含编号与 Avatar、未发布无 Avatar、管理员隐藏）、Publish（Display name 为空的回退说明、长名称与长 Username）、Unpublish（普通、管理员隐藏）；
  - 另有 820px 的 Edit 与 Preview，以及 640px 视口 200% 字号的 Edit 与 Publish 各 1 张。
- 手机 Edit 错误截图中 `Skip to main content` 出现在页面中部，与 V19 相同：焦点落在无效字段，属于全页截图对 fixed 元素的绘制方式，不是页面问题。
- 已知现状：这几页上 Header 没有任何导航项标为当前页（mockup 中为 `Account`），这是 V20 之前就存在的导航映射，本步未改动。

### 当前边界与下一步门槛

- 项目负责人已走查截图并批准 V20；`architecture.md` 已新增 3.67 并更新对应文件职责。V21（第五轮质量门禁）尚未开始。

## Visual Refresh Step V21 — 第五轮质量门禁

### 前置条件检查

- 项目负责人已批准 V20（已提交并推送）并授权开始 V21；V18–V20 的代码与文档均已提交，工作区干净。本步不修改代码。

### 自动验收

- 沿用 V7、V10、V13、V17 的门禁方式，没有新增脚本：`python -m uv run --env-file .env python scriptsccept_phase_4.py` 在 OS 临时目录的全新 uv environment 中完整通过（`Phase 4 end-to-end acceptance passed.`）：
  - 锁定 npm/Chromium 安装、静态资源 build/check/watch smoke、Ruff lint/format、migration drift、Django check 均通过；
  - 干净 PostgreSQL 上完整 pytest `457 passed`，branch coverage `95%`；
  - `check --deploy --fail-level WARNING` 无问题，manifest `collectstatic` 通过；
  - 真实 Development server 上 Phase 2、Phase 3、Phase 4 desktop/mobile smoke 全部通过。
- 验收后工作区没有任何已跟踪文件变化。

### 人工走查截图

- 使用只在本地临时存在的测试（Test settings 的 live server、临时 media 目录、四名合成会员与程序生成的抽象头像，截图后删除；Development database 未写入数据），在 1440 × 900 与 390 × 844 下各 13 张，共 26 张：
  - 认证页面：Log in、Join the Club、Verify email（合成注册后进入）、Log in by email code、Password reset、Change password；
  - Account：已发布含编号与 Avatar、未发布无 Avatar；
  - Edit Profile（含 Avatar）；
  - Preview：已发布、管理员隐藏；
  - Publish（Display name 为空，显示 Username 回退说明）与 Unpublish。
- 每张截图均自动检查：无横向溢出、主内容中没有以冒号结尾的 Label、恰好一个 H1、没有 page error，全部通过。

### 当前边界与下一步门槛

- 第五轮（V18 共用表单字段与认证页面、V19 Account、V20 Edit Profile/Preview/Publish/Unpublish）完成后，Home、Events、About、Beginners & Safety、Members、认证与 Account 已按新视觉实施；只剩 403/404/500 错误页沿用原有布局，需先确认设计再展开步骤。
- 项目负责人已走查截图并批准 V21；`architecture.md` 已新增 3.68 并更新页首进度。第五轮完成，下一项为 403/404/500 错误页的设计确认，尚未开始。

## Visual Refresh — 403/404/500 错误页设计决定

- 第五轮完成后，按既定顺序为 403/404/500 制作了三个只在本地临时目录存在的 mockup（A：左侧页头与按钮、右侧带金色顶线的面板放大号金色状态码；B：整页居中的大号金色状态码；C：左对齐报告页，右侧金色描边空心状态码），均以 404 为例在 1440 与 390px 截图，未修改仓库。
- 项目负责人看过现状与三个方案后决定：错误页保持现有布局，不重新设计。现有错误页已继承全站颜色、字体、按钮与页面壳，继续使用 `_error_page.html` 中的 `.eyebrow` 状态码、H1、`.lede` 说明与 `.cta-panel` 中的 `Return Home`；文案、handlers、状态码与隐私边界不变。
- 因此 Visual Refresh 的页面范围（Home、Events、About、Beginners & Safety、Members、认证与 Account、错误页）全部结束，没有 V22。`.eyebrow`、`.cta-panel` 与 `.public-section__header` 仍由错误页使用，需保留。
- 经项目负责人批准，`architecture.md` 3.68 末条、页首状态与 `implementation.md` 的 Visual Refresh 页面顺序说明已改为记录该决定。

## Visual Refresh Step V22 — Home 整页背景照片（补充）

### 决定与前置条件

- 项目负责人指出 Home 背景照片显示不完整。原因是规则本身：照片按比例覆盖约 1280 × 600 的 Hero（`cover`、对齐点 `center 20%`），4:3 原图只显示约 62% 的高度，主要裁去底部，四边另有 12% 渐隐。
- 项目负责人决定：照片改为整个 Home 页的背景，宽度与内容区一致、从导航栏下方开始、到达窗口顶部后固定，内容在其上滑过；窗口越高显示越多；整页都能用光照；手机与触屏仍不显示。照片只用于 Home，其他页面保持网格加纯黑底（分析过的可读性、隐私与语气代价见设计文档 7.4）。
- 项目负责人提供了 1440 × 2200 的竖版拼贴 `static_src/images/home/hero-specimen-tall-source.png`（RGBA、完全不透明）。更正：本步编码前没有按 AGENTS.md 重新完整阅读 `architecture.md` 与 `design_document.md`（最近一次是 V20 开始时），原记录“已完整阅读”不属实。

### 实施内容

- 文档：`design_document.md` 7.4 的背景彩蛋规则改为整页背景（新增各项行为与“只用于 Home”的决定），参数改为竖版源图与左右 12%、顶边 4%、底边 12% 的渐隐；9.5 与 9.6 的措辞同步；`implementation.md` 增加 V22 一行。
- 图片：`scripts/build_home_images.py` 的 Hero 照片条目改用新源图（新 SHA-256、1440 × 2200、不透明、RGB 输出），生成物仍为 `hero-specimen-1440.webp`（1440 × 2200，约 173 KB）。旧源图 `hero-specimen-source.png` 已不再被引用，等项目负责人确认效果后删除。
- `home.html`：照片层 `.hero-specimen` 从 `.home-hero` 移到 `.home-page` 的第一个子元素，内部新增 `.hero-specimen__window`；指针处理器移到 `.home-page`，坐标改为相对光照层计算。
- CSS（仍只在 `@variant hero` 且 `hover: hover` 时生效，照片 URL 也只在其中声明）：
  - `.page-shell` 的上下内边距提取为 `--shell-padding`；
  - `.hero-specimen` 绝对定位于 `.home-page`，顶端向上抵消 `--shell-padding`（从导航栏下方开始），底端向下延伸一个视口高度；
  - `.hero-specimen__window` 为视口高度的 `position: sticky; top: 0` 窗口，照片先随页面上移，到达窗口顶部后固定，一直到 Home 末尾都不移动；
  - Home 的 `.page-shell` 设 `overflow-y: clip`，把多出的高度裁在 Footer 之前，不增加滚动长度，也不在 Footer 显示照片；
  - `.hero-specimen__figure` 宽度为内容区宽度，按 1440 / 2200 比例缩放并顶端对齐；
  - 光照的显示条件改为 `.home-page[data-lit]`；删除 `.home-hero` 上为照片层设置的 `position`/`isolation`。

### 测试

- `test_home_images.py`：照片源图改为新文件、SHA-256 与尺寸。
- `test_home_page.py`：照片层位于 `.home-page` 内、`.home-hero` 之前（整页背景），仍对辅助技术隐藏、HTML 不引用照片文件。
- `home-page.mjs`：桌面断言照片层与内容区等宽对齐、顶端位于导航栏下方、保持原比例；光照在 Hero 内点亮并跟随指针；页面内全部可见链接不被遮挡；滚到底后照片窗口仍在视口顶部、照片没有位移、Footer 底边与视口底边对齐（没有多出的滚动）、Home 的 `.page-shell` 为 `overflow-y: clip`；指针在 `Upcoming Events` 旁也能点亮，移到 Footer 后熄灭。mobile 与宽屏触屏不显示照片层、不下载照片的断言不变。

### 验证结果

- 完整 pytest 在全新 test database 上 `457 passed`。
- `static:check`（含图片生成物检查）、Ruff lint/format、Django check 与 `git diff --check` 通过。
- 在本地 Development server（只读访问 Home，未写入数据）截图，均无横向溢出与 page error：1440 × 900 顶部、中段、底部与在 `Upcoming Events` 旁点亮光照，1920 × 1080，1234 × 1360（项目负责人截图的瘦高比例），1080 × 1920 竖屏，1000 × 800 窄桌面，以及 390px 手机整页（照片层不显示）。

### 当前边界与下一步门槛

- 项目负责人已走查截图并批准 V22；旧源图 `hero-specimen-source.png` 已删除（可从 Git 历史恢复），`architecture.md` 已新增 3.69 并更新页首进度与相关文件职责。照片中成员的公开使用同意仍需项目负责人在上线前取得。

## Home 背景照片成员同意

- 项目负责人确认（2026 年 11 月 22 日）：Home 背景照片拼贴中的成员已同意公开使用。`design_document.md` 9.6 已改为记录该确认；`architecture.md` 3.52 与 3.69 中“仍需取得同意”的说明待项目负责人批准后同步。

## Phase 6 — Provider 决定与步骤规划

- 项目负责人 2026 年 11 月 22 日决定：BinaryLane 悉尼机房入门 VPS（至少 1 GB 内存、带 IPv4），一台服务器以 Docker Compose 运行 PostgreSQL、gunicorn 与 Caddy；Avatar 存在 VPS 磁盘 volume；社团专用 Gmail 作为 SMTP；不使用 Sentry，改用 Django 错误邮件与服务器日志；数据库与 media 每日备份、保留 7 份。比较过的托管平台、AWS 与中国云服务商的价格与取舍记录在本次对话，结论写入 `tech_stack.md` 第十三章。
- `tech_stack.md` 已记录上述决定并更新第三、六、七、九、十二、十三、十五章；`implementation.md` 第十节展开为 Step 46–53；Roadmap 将 Visual Refresh 标为 `Complete`、Phase 6 标为 `In progress`，并加入域名注册这一阻塞项。
- 仍待决定：CI Provider、备份是否另存 VPS 以外、是否单独部署 Preview 环境、`nuldl.com` 注册与 DNS、正式数据保留规则。正式 Risk Notice 由项目负责人在期末后联系 USU 确认。
- 尚未修改任何代码。Step 46 开始前需要项目负责人确认步骤规划。

## Phase 6 Step 46 — 生产运行时设置

### 前置条件检查

- 项目负责人已确认 Phase 6 计划并授权开始 Step 46；更正：本步编码前没有按 AGENTS.md 重新完整阅读 `architecture.md` 与 `design_document.md`（最近一次是 V20 开始时），原记录“已完整阅读”不属实。Provider 决定以 `tech_stack.md` 第十三、十五章为准。本步不涉及服务器、域名或真实邮箱。

### 实施内容

- 依赖：加入运行依赖 `gunicorn==26.2.0` 并更新 `uv.lock`。没有选最新的 27.0.1：它是 2026 年 11 月 12 日发布的新大版本，发布不到两周；26.2.0 已发布约三个月。
- `config/settings/production.py`：
  - `SECURE_PROXY_SSL_HEADER`：信任 Caddy 设置的 `X-Forwarded-Proto`，避免 HTTPS 重定向循环；gunicorn 只能由 Caddy 访问，客户端无法伪造该 header；
  - `SECURE_REDIRECT_EXEMPT`：只豁免 `health/`，供服务器内部以 HTTP 做健康检查；`ALLOWED_HOSTS` 仍然严格；
  - `MEDIA_URL`、`MEDIA_ROOT`：Avatar 存在 `BASE_DIR / "media"`，Step 47 挂载持久 volume；此前 Production 没有设置 `MEDIA_ROOT`，上传会落到进程工作目录；
  - `SERVER_EMAIL`：等于 `DEFAULT_FROM_EMAIL`，因为 Gmail 只能以账号本身发信；`ADMINS` 来自可选的 `DJANGO_ADMINS`（逗号分隔）；
  - `LOGGING`：单行纯文本日志输出到 stdout；只有 `django.request` 的 ERROR 会发错误邮件；`DisallowedHost` 只记日志、不发邮件；
  - 修复既有隐患：原先 `STORAGES["staticfiles"] = …` 会直接修改与 `base.py` 共享的字典，同一进程中只要导入过 Production settings，Test settings 也会变成 Manifest 静态存储。现改为建立新字典。
- `config/settings/base.py`：新增 `optional_csv_env`；所有环境的 `DEFAULT_EXCEPTION_REPORTER_FILTER` 指向新的 `apps/core/error_reporting.py`。
- `PrivateExceptionReporterFilter`（更正：下述效果不属实，该类已在 Step 47 中删除，见该节）：在 DEBUG 关闭时，错误报告只保留 traceback、路径与异常类型；所有 POST 值、所有 cookie（含 session 与 CSRF）、全部局部变量，以及名称含 EMAIL、DATABASE、ADMINS、SESSION、CSRF、COOKIE、KEY、SECRET、PASS、TOKEN 等的 settings 一律替换为占位符。DEBUG 开启时沿用 Django 默认行为，本地调试页不受影响。
- `apps/core/checks.py`：deploy 检查 `core.W001`，`ADMINS` 为空时警告。因此 `check --deploy --fail-level WARNING` 会拦下没有设置错误邮件收件人的部署，而本地 `.env` 与普通测试不受影响。`scripts/verify_project.py` 为其中的 deploy check 注入占位收件人 `deploy-check@example.invalid`；`.env.example` 增加注释说明。
- `/health/`（路由名 `health`；原记录误写为 `core:health`）：只接受 GET，不缓存，执行 `SELECT 1`。数据库可用时返回 `{"status": "ok"}`，否则返回 503 `{"status": "unavailable"}`，日志只记一句不含异常原文的错误；不进入 sitemap。

### 测试

- 新增 `tests/test_production_runtime.py`（13 项）：
  - 代理 header、重定向豁免、media 与 static 路径、`SERVER_EMAIL`；
  - 导入 Production 后 base 的 `STORAGES` 不变（回归）；
  - `DJANGO_ADMINS` 解析（去空格、跳过空项）；
  - `LOGGING` 能被 `dictConfig` 加载，且只有 `django.request` 发错误邮件、`DisallowedHost` 不发；
  - 私有报告过滤器在所有环境生效；`core.W001` 在有、无收件人时的结果；
  - health check 的正常、只接受 GET、数据库不可用时 503 且响应与日志不含异常原文、不在 sitemap；
  - 在 Production 重定向设置下 health 以 HTTP 返回 200、普通页面 301、带 `X-Forwarded-Proto: https` 时返回 200 不循环；
  - 合成会员 POST 触发 500 后，错误邮件含 `RuntimeError` 与路径，但不含 Email、验证码、Password、USU ID 与 session key。

### 验证结果

- 完整 pytest 在全新 test database 上 `470 passed`。
- Ruff lint/format、Django check 与 `makemigrations --check`（无变化）通过。
- Production `check --deploy --fail-level WARNING`：设置 `DJANGO_ADMINS` 时无问题；不设置时只报 `core.W001`。
- `git diff --check` 通过。

### 当前边界与下一步门槛

- 项目负责人已批准 Step 46；`architecture.md` 已新增 3.70，更新页首进度、环境与 App 边界表和相关文件职责，并同步 3.52、3.69 中的照片同意说明。Step 47（Dockerfile、生产 Compose、Caddyfile）尚未开始。
- 已知且接受的边界（更正：基于不完整的测试，已由 Step 47 的白名单摘要取代）：错误邮件仍包含请求路径、登录用户的 Username、IP 与 User-Agent，便于排查；路径中可能出现一次性的密码重置链接 key，它在使用或过期后即失效。

## Phase 6 Step 47 — 开始前检查（暂停，等待项目负责人决定）

- 已完整阅读 `architecture.md` 与 `design_document.md`。尚未修改任何代码，也未建立 Dockerfile、生产 Compose 或 Caddyfile。
- Step 46（`370167d`，已推送、未部署）的更正：
  - 错误邮件隐私缺陷：以合成异常直接调用 `AdminEmailHandler` 实测，异常消息、串联异常消息、查询参数、Referer 与密码重置 key 全部进入邮件。原记录“只保留 traceback、路径与异常类型”不属实；原测试使用固定异常文字，没有覆盖这些位置。
  - 日志隐私缺陷：按 Production 日志格式实测，异常消息、串联异常消息与路径中的重置 key 会进入日志。
  - 路由名记录错误：实际名称是 `health`，`core:health` 不存在（本文 Step 46 与 `architecture.md` 3.70）。
  - “私有报告过滤器在所有环境生效”的测试实际只检查了 Production settings。
- Step 47 需要处理：从 allauth 源码确认，未设置可信代理时客户端 IP 取 `REMOTE_ADDR`；经过 Caddy 后全部访客会共用按 IP 的限流额度（尚未做端到端复现）。
- 文档矛盾，按 AGENTS.md 暂停并请项目负责人决定：
  - Home 照片末尾行为：设计 7.4 与 V22 计划写“随内容离开”，实现与架构 3.69 为“固定且无位移，在 Footer 前裁切”；
  - 报名关闭文字：设计第八章为 `Closed`，设计 7.5 与实现为 `Registration unavailable`；
  - 注册确认密码 Label：设计 7.2 与架构 3.8 为 `Confirm password`，实现为 `Password (again)`；
  - 资料表单 Label：设计 7.8、7.11 为 `Instagram Username`，实现为 `Instagram handle`；
  - 停用账户：设计第八章要求“联系入口”，实现只有不含联系方式的说明；
  - 重复邮箱：设计 6.1 要求明确提示，架构 3.8 与实现为防枚举的通用流程；
  - 过期描述：设计 6.5.1 的 media 待定、架构 3.2 的 SMTP 待定、架构 2.1 缺少 gunicorn。

### 项目负责人的决定（2026 年 11 月 23 日）

- 按建议修复 Step 46 的缺陷并解决上列文档矛盾。
- Avatar 只用随机文件名、由 Caddy 直接公开，不做鉴权；设计 11.2 相应放宽，接受旧链接在取消发布、隐藏或停用后仍可打开。普通社团网站不做过细的安全设计。
- 镜像与构建依赖的下载尚未得到答复，因此本次没有拉取镜像、没有构建应用镜像。

### 已实施

- 先写 8 项失败测试复现问题，再修复：
  - Production 日志与错误邮件改用同一白名单摘要（异常类型、文件与行号、路由名、状态码），删除原过滤器；同一错误每进程每小时最多一封；SMTP 超时 10 秒。
  - `ALLAUTH_TRUSTED_PROXY_COUNT = 1`，按 Caddy 转发的客户端 IP 限流。
  - 新 Avatar 在 model 保存时改为随机文件名，没有 migration；已有本地开发文件保持原名。
  - Label 改为 `Confirm password` 与 `Instagram Username`。
- 新增 `Dockerfile`、`.dockerignore`（白名单）、`compose.production.yaml`、`Caddyfile`、`config/gunicorn.conf.py`、`.env.production.example`（`.gitignore` 放行该示例）。
  - 与计划的差异：除数据库、media、static 三个 volume 外，另有 Caddy 证书与配置两个 volume；一次性 `static` service 在每次部署时复制新静态文件；gunicorn 为 2 workers、每个 2 threads；端口只绑定 IPv4。
- Tailwind 会把 `.dockerignore` 中的 `!static` 识别为 class，已用 `@source not` 排除该文件；生成的 CSS 与 HEAD 相同。
- 按决定更正设计文档、`tech_stack.md`、`implementation.md` 与 `architecture.md` 的相应内容及 3.70。

### 已验证（均未下载）

- 完整 pytest `475 passed`，branch coverage 95%；Ruff、Django check、`makemigrations --check`、`static:check`、`git diff --check` 通过。
- Compose 能解析，缺少必填变量时拒绝。
- 以 `FROM scratch` 导出真实构建上下文：不含 `.env`、测试、Node 依赖、media、memory-bank 与照片源文件。
- 在该上下文中以 Production settings 与一次性 PostgreSQL 18.6 容器（合成值，用后删除）执行 collectstatic、migrate、`check --deploy` 均通过；主要页面与 health 为 200，Draft Risk Notice 为 404，普通 HTTP 页面为 301；数据库日志不含违反约束的行值。
- 在 Windows 上加载真实 gunicorn 配置与 Logger（补齐与日志无关的 POSIX 函数）：配置项均被识别，日志不含探针中的私有值。

### 尚未验证，Step 47 未完成

- 应用镜像构建、非 root 运行、镜像内容与体积。
- gunicorn 在 Linux 中启动、容器 health check、1 GB 下的内存占用。
- Caddyfile 的语法与实际行为：HTTPS、日志过滤、静态与 media、上传大小限制、转发 IP 下两个客户端分别限流。
- `scripts/verify_project.py` 整体未运行（其中 `npm ci` 与浏览器准备会下载）；除这两项准备和 CSS watch smoke 外，各检查已单独运行。
- 以上完成并经项目负责人批准后，再在 `architecture.md` 增加 Step 47 一节与文件职责。

### 上线前待处理（已发现、未改）

- 全新数据库的 Site 名称是 `example.com`，会出现在邮件标题中；已加入 Step 49 的管理员操作清单。
- allauth 的登录限流不覆盖 Django Admin 登录页；最简做法是管理员使用长随机密码，在 Step 49 文档中说明。

## 正式 Risk Notice 获批（2026 年 11 月 25 日，仅记录决定，未改代码）

- 项目负责人告知：社团资料目录中的中英文 Risk Notice（`Armwrestling_Risk_Notice_EN/CN`，2026 年 11 月 24 日定稿）已获 USU 批准，可直接使用。
- 已读取两份 PDF：均为活动现场纸质签字表，包含三段风险告知、`Event sign-off record`、以 “By signing below before taking part in this event” 开头的参与确认和签名栏；`Notice version` 为空白。
- 项目负责人的决定：
  - 网站只逐字展示三段风险告知；在线 `Confirm registration` 只记录已阅读的版本与时间，参与确认和签名仍在现场纸质完成，不改写获批措辞；
  - 版本号 `2026-11-24`，纸质表填写相同版本号；
  - 中文版只用于现场纸质签字，网站保持英文。
- 已更新 `design_document.md`（4.6、Risk Notice 正式版本小节、待确认事项 1 与 6）与 `implementation.md`（Phase 6 展开条件、关键约束、Step 53）。
- 网站正文后提示句 `You will also be asked to sign the participant acknowledgement on site before taking part.` 是新增措辞，待 Step 53 审批时确认。
- 没有修改代码、设置或数据库；Production 报名仍关闭，直至 Step 53 实施并验收。Step 47 的状态不变。

## Phase 6 Step 47 — 本机试装（2026 年 11 月 25 日）

- 项目负责人回复“可以下载”。开始前已完整重读 `architecture.md` 与 `design_document.md`（设计文档含当天写入的正式 Risk Notice 决定）；与 Step 47 无矛盾。
- 下载：`caddy:2.11.9-alpine`（按 digest）、`python:3.13.17-slim-trixie`（按 digest，构建时拉取）、uv 0.13.5 与 `uv.lock` 锁定的运行依赖。没有运行 `npm ci` 或 Playwright 安装。
- 全程只用合成值，单独的 Compose 项目名 `nuldl-s47`，域名 `nuldl.internal`（Caddy 本地 CA 签发证书），主机端口改为 `127.0.0.1:18080/18443`，`EMAIL_HOST` 改为 `smtp.invalid`，不连接 Gmail；没有碰开发数据库、服务器、域名或邮箱。测试结束后已删除该项目的容器、网络、全部 volume 与测试镜像；拉取的基础镜像保留在本机供以后构建。
- 本步没有修改代码或配置；本节以下结果取代上一节“尚未验证”中的对应项。

### 已验证

- 镜像：构建成功（磁盘占用约 329 MB，其中依赖 111 MB、收集后的静态文件 5.9 MB）；运行用户 `app`（uid 10001），PID 1 也是该用户；镜像内只有 `.venv`、`apps`、`config`、`templates`、`static`、`staticfiles`、`media`、`manage.py`，没有 `.env`、测试或开发依赖（无 pytest）；`staticfiles.json` manifest 存在；镜像历史中只有构建用的占位值；gunicorn 26.2.0、Django 5.2.18。
- 启动：`up` 后 db、web 均为 healthy；一次性 `static` 在 `pull_policy: never` 下运行并以 0 退出；Caddy 在其完成后启动。容器内 `migrate` 与 `check --deploy --fail-level WARNING` 通过。
- 经 Caddy 的 HTTPS：Home、About、Events、Members、Log in、Sign up、Admin login、sitemap、`/health/` 均 200；`/risk-notice/` 404；HTTP 308 到 HTTPS；未知域名不提供证书。页面带 HSTS、`nosniff`、`X-Frame-Options: DENY`、COOP、Referrer-Policy，并以 zstd 压缩。
- 静态文件：带 hash 的 CSS 返回一年 `immutable` 缓存、`nosniff` 与压缩；不带 hash 的文件不加长缓存；不存在的文件 404。
- Avatar：写入 media volume 的文件由 Caddy 直接提供（正确 Content-Type 与 `nosniff`），目录不可列出；`down` 后再 `up`，文件、数据库与 Caddy 证书都保留。
- 上传上限：11 MB 请求体返回 413。
- 按客户端 IP 限流：两个同时运行、IP 不同的客户端容器经 Caddy 提交失败登录，A 在第 31 次起收到 429，B 同时段的 3 次都正常；`ALLAUTH_TRUSTED_PROXY_COUNT = 1` 按预期取到真实客户端 IP。（第一次试验 B 也被限流，原因是两个客户端先后运行、B 复用了 A 释放的 IP；改为同时运行后确认是测试方法问题。）
- SMTP 不可达：为不存在的邮箱申请密码重置时，访问者看到通用 500 页面，没有 traceback；日志只有异常类型与文件行号。
- 日志：web、db、Caddy 全部日志中，探针用的邮箱、查询参数、用户名、密码、客户端 IP、数据库密码与 Secret 出现 0 次；Caddy 日志没有请求内容；数据库日志没有 ERROR 行。
- 内存（60 次页面请求后）：web 约 115 MiB / 400、db 约 21–43 MiB / 256、Caddy 约 19 MiB / 128，合计不到 200 MiB，1 GB VPS 足够。
- 仓库检查：Ruff lint 与 format、Django check、`makemigrations --check`、`static:check` 通过。代码自上次完整 pytest（`475 passed`，branch coverage 95%）后未改动，本次没有重跑。

### 仍未验证

- 真实公网证书签发（Let's Encrypt）与续期、真实 Gmail 发信，以及错误邮件发送失败时那一条警告日志在容器内的实际输出（目前只有单元测试覆盖）：留到 Step 51–52。
- `scripts/verify_project.py` 整体运行（需要 `npm ci` 与 Playwright 下载，本次未申请）。

### 上线前需要项目负责人知道或决定的事（已发现、未改）

- 全新数据库的 Site 名称是 `example.com`，会出现在邮件标题中；Admin 登录页不受 allauth 限流（管理员用长随机密码）。均已列入 Step 49 文档。
- HSTS 目前带 `includeSubDomains; preload`：浏览器会记住一年只用 HTTPS 访问该域名及其所有子域名，`preload` 一旦提交到浏览器列表很难撤回。若以后子域名可能用于别的服务，建议去掉 `preload`，在 Step 52 前决定。
- allauth 的限流计数存在每个 gunicorn 进程自己的内存里：重启后清零，两个进程理论上最多各算一份。对几十人的社团可接受，不打算改。
- 页面 `og:url` 会把访问者当前网址（含查询参数）原样写回给访问者本人；这是 Phase 2 起的行为，不进日志或邮件，不打算改。
- 响应带 `Server: gunicorn`，只暴露软件名，不打算改。
- 设计 7.5 写首场 Training Session 为悉尼时间 3:00–7:00 pm，开发数据库中的活动是 3:00–6:00 pm；正式录入活动时以项目负责人确认的时间为准。
- Edit Profile 的字段 Label 显示 `Other social url`，设计写作 `Other social URL`，属于小的文案差异，待项目负责人决定是否改。
- `architecture.md` 第五章末尾关于 `implementation.md` 未提交修改的说明已过时，随 Step 47 的 architecture 更新一并删除。

### 项目负责人批准（2026 年 11 月 25 日）

- 项目负责人批准 Step 47。`architecture.md` 已更新：页首日期、进度与状态；3.2 Production 行补充按转发 IP 限流与白名单错误邮件；3.28 补充随机 Avatar 文件名；3.70 的测试数量改为“本步 13 项，Step 47 后 16 项”；新增 3.71（生产镜像、Compose 与 Caddy）；文件职责表新增 `Dockerfile`、`.dockerignore`、`compose.production.yaml`、`Caddyfile`、`.env.production.example`、`config/gunicorn.conf.py`，并更新 `.gitignore`、`production.py`、members models/forms 与相关测试行；删除第五章末尾已过时的 `implementation.md` 说明。
- 尚未提交或推送。HSTS `preload` 的去留仍待 Step 52 前决定。下一步是 Step 48。
