# NULDL 开发进度

**最后更新：** 2026 年 10 月 25 日
**当前阶段：** Phase 1
**当前步骤：** Step 20 — Phase 1 端到端验收
**状态：** Phase 1 已通过自动化与人工验收并完成；Phase 2 尚未开始

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
