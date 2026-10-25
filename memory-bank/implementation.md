# NULDL 网站 Implementation Plan

**项目名称：** Nonlinear Upper Limb Dynamics Laboratory Website  
**文档职责：** 为 AI 开发者提供可验证、可逐步执行的开发指令  
**实施根目录：** `../`  
**文档状态：** Progressive  
**最后更新：** 2026 年 10 月 22 日

## 一、输入与优先级

执行任何代码任务前，必须完整阅读：

1. [architecture.md](architecture.md)；
2. [design_document.md](design_document.md)；
3. [tech_stack.md](tech_stack.md)；
4. 本文件中当前已展开的实施阶段；
5. [项目开发_Roadmap.md](项目开发_Roadmap.md) 中对应阶段的范围与退出门槛。

发生冲突时：

- 产品行为以 `design_document.md` 为准；
- 技术选型以 `tech_stack.md` 为准；
- 已实施架构及其理由以 `architecture.md` 为准；
- 阶段顺序和外部依赖以 `项目开发_Roadmap.md` 为准；
- 无法消除的冲突必须停止实施并请求决定。

## 二、维护策略

### 2.1 渐进式展开

- 始终保留 Phase 1–6 的完整范围、依赖和验收门槛；
- 只将当前阶段展开为可直接执行的微步骤；
- 当前阶段全部通过后，根据真实代码、测试和依赖版本展开下一阶段；
- 不根据尚未验证的假设提前写完后续阶段的实现细节；
- 每完成一个步骤，在 `progress.md` 记录结果、测试和遗留问题；
- 每完成重大功能或里程碑，先申请更新 `architecture.md`，获得同意后再记录架构变化。

### 2.2 无代码原则

本文档不得包含 Python、HTML、JavaScript、CSS、SQL、配置文件代码或可直接复制的伪代码。可以使用内联标识符说明文件、model、field、setting、URL name、命令名称和状态值。真实实现只存在于代码仓库中。

### 2.3 单步执行规则

AI 开发者一次只执行一个步骤。每一步必须：

- 在开始前检查前置条件；
- 只修改该步骤列出的范围；
- 同时添加或更新对应自动化测试；
- 执行该步骤列出的验证；
- 验证失败时停止，不得通过扩大范围掩盖问题；
- 达到完成条件后才进入下一步。

## 三、固定技术边界

- 使用 Python 3.13、Django 5.2 LTS 和 PostgreSQL；
- 使用 `uv` 管理 Python 虚拟环境与依赖，提交 `pyproject.toml` 和 `uv.lock`；
- 本地开发在主机环境运行 Django，PostgreSQL 通过 Docker Compose 运行；
- 采用 Django 单体架构，不建立独立 SPA 或 REST API；
- 页面使用 Django Templates，局部增强使用 HTMX 和 Alpine.js；
- 样式使用 Tailwind CSS v4 与 Tailwind CLI；
- 地图使用 MapLibre GL JS；
- 使用 npm 管理并锁定前端依赖；HTMX、Alpine.js 和 MapLibre GL JS 作为本地静态资源提供，Production 不依赖第三方 CDN；
- 浏览器端到端测试使用 Playwright；
- 认证使用 django-allauth；
- 开发、测试和生产均以 PostgreSQL 行为为准；
- 核心流程必须在 JavaScript 失效时保留普通 HTTP 回退；
- 业务规则必须由服务端校验，关键一致性同时使用数据库约束；
- 不提前实现付款、容量、候补、报名截止时间、排名或 Social login。

## 四、目标目录职责

| 路径 | 职责 |
| --- | --- |
| `config/` | URL、WSGI 与分环境 settings |
| `apps/core/` | Home、About、全局页面框架和 error pages |
| `apps/accounts/` | User、认证、USYD 声明、USU ID 与账户设置 |
| `apps/members/` | MemberProfile、公开资料与资料管理 |
| `apps/events/` | Event、报名、取消及历史记录 |
| `apps/locations/` | Location、地点页面与地图数据 |
| `apps/safety/` | Risk Notice 版本及当前版本管理 |
| `templates/` | 页面、组件、account templates 与 HTMX partials |
| `static_src/` | Tailwind 输入和源码级前端资产 |
| `static/` | 构建后的静态资产 |
| `tests/` | 跨 App、集成、浏览器与 accessibility 测试 |
| `docker/`、`compose.yaml` | 本地服务和生产构建定义 |

## 五、Phase 1：基础设施、账户与认证

### Step 1 — 建立执行基线

**目标：** 确认输入文档、仓库状态和未决事项均可识别。

**指令：** 完整阅读必读文档；检查当前工作树；列出现有文件、未提交修改和阻塞项；不得改动与本步骤无关的文件。

**验证：** 确认所有必读文档可访问；确认 `architecture.md` 与 `progress.md` 的当前状态；确认未决事项不会被隐式实现。

**完成条件：** `progress.md` 留下本次执行的基线记录，且没有未处理的文档冲突。

### Step 2 — 建立 Python 与前端依赖元数据

**目标：** 建立可重现的 Python 和 Tailwind 工具环境。

**指令：** 使用 `uv` 创建 `pyproject.toml` 和 `uv.lock`，使用 npm 创建 `package.json` 和对应锁文件；Python 依赖加入 Django、django-allauth、PostgreSQL driver、Pillow、pytest、pytest-django、coverage 与 Ruff；前端依赖加入 Tailwind CSS、Tailwind CLI、HTMX、Alpine.js、MapLibre GL JS 与 Playwright；版本必须符合 `tech_stack.md`。

**验证：** 在全新环境分别通过 `uv` 和 npm 安装锁定依赖；确认 Python、Django、pytest、Ruff、Tailwind CLI 和 Playwright 可调用；确认前端库能够从本地依赖解析；检查锁文件未引用未经批准的主要版本。

**完成条件：** 后端和前端依赖均可从空环境重复安装。

### Step 3 — 创建 Django 项目骨架

**目标：** 建立约定的 project 与 App 边界。

**指令：** 创建 `manage.py`、`config/` 以及 `core`、`accounts`、`members`、`events`、`locations`、`safety` Apps；将 Apps 放入 `apps/` Python package；暂不实现业务模型。

**验证：** 导入所有 App config；运行 Django system check；确认目录名称与本文件一致且没有额外业务 App。

**完成条件：** Django 能加载项目和全部 Apps，system check 无错误。

### Step 4 — 配置 PostgreSQL 本地环境

**目标：** 让开发和测试从开始即使用 PostgreSQL。

**指令：** 创建 Docker Compose PostgreSQL service、持久化 volume、健康检查和安全的开发变量示例；本机 `uv` 环境运行 Django，并通过映射端口连接容器中的 PostgreSQL；更新 `.gitignore`；不得加入真实凭据或 SQLite 回退。

**验证：** 启动数据库并等待健康状态；从本机 Django 环境建立连接；重启 PostgreSQL 容器后确认开发数据仍由 volume 保留；确认停止数据库后连接会明确失败；扫描仓库确认 `.env`、数据库文件和凭据未被跟踪。

**完成条件：** 本地 PostgreSQL 可重复启动，Django 使用环境变量连接。

### Step 5 — 拆分环境 Settings

**目标：** 建立 `base`、`development`、`test` 和 `production` 配置。

**指令：** 公共配置进入 `base`；Development 使用 Debug、Console Email 和本地资源；Test 使用独立 PostgreSQL test database、测试邮件 backend 和快速 hasher；Production 从环境变量读取 Secret、hosts、database 和 email，并启用安全设置。

**验证：** 分别运行 Development 与 Test system check；验证 Production 缺少必填 Secret 时安全失败；提供完整测试变量后确认 `DEBUG` 关闭且安全检查可运行。

**完成条件：** 四个环境职责清晰，测试环境无外部网络依赖，Production 无硬编码 Secret。

### Step 6 — 创建 Custom User 初始模型

**目标：** 在第一次业务 migration 前确定 `AUTH_USER_MODEL`。

**指令：** 让 `accounts.User` 继承 Django `AbstractUser`；保留标准权限字段；增加必填且唯一的 Email、USYD 学生声明、可空 USU ID、审核状态、审核时间和审核人；审核人使用可空 Self ForeignKey。

**验证：** 测试默认值、Email 必填和唯一性、审核字段可空性及 User 创建；在空数据库生成并检查第一条 migration；运行 migrate 和 system check。

**完成条件：** 空 PostgreSQL 数据库可直接建立 Custom User，且未创建默认 Django User 业务表。

### Step 7 — 实施 USYD 与 USU ID 领域规则

**目标：** 在 model、form/service 与数据库层保持身份字段一致。

**指令：** 规范化 Email 和 USU ID；禁止非 USYD 用户保存 USU ID；空 USU ID 对应 `not_submitted`；新增或修改 ID 后进入 `pending` 并清除旧审核信息；`verified` 与 `rejected` 只允许受控管理员流程写入。

**验证：** 测试非 USYD 提交 ID 被拒绝、USYD 用户可留空、首次提交进入 `pending`、修改已验证 ID 会撤销审核、取消 USYD 声明会清除 ID 和审核信息；验证数据库约束不能被直接写入绕过。

**完成条件：** 所有状态转换具有行为测试，应用层与数据库结果一致。

### Step 8 — 创建完整 MemberProfile 数据结构

**目标：** 为邮箱验证后建立默认隐藏的会员资料。

**指令：** 创建与 User 一对一的 MemberProfile，并一次建立下列完整字段和规则；建立幂等创建 service；Phase 1 只提供数据结构、验证、自动创建和后台管理，会员编辑界面、预览、发布操作及公开页面留到 Phase 3。

| 字段 | 类型与规则 |
| --- | --- |
| `user` | 必填 One-to-one relation；每个账户只能关联一个 Profile；账户删除时同步删除 |
| `display_name` | 可空 String，最长 80 字符；去除首尾空格；非空值忽略大小写后唯一；空值统一保存为 `NULL`；显示时为空则回退到 Username |
| `avatar` | 可空 Image；仅接受真实 JPG、PNG 或 WebP 文件；最大 5 MB；Development 使用本地 media 目录，Production storage 留待确认 |
| `bio` | 可空 Text，最长 500 字符；只保存和输出纯文本，不允许 HTML |
| `experience_level` | Choice；默认 `not_spec`；允许 `not_spec`、`under_one`、`one_to_three`、`over_three`，界面分别显示 `Not specified`、`< 1 year`、`1–3 years`、`> 3 years` |
| `preferred_arm` | Choice；默认 `Not specified`；允许 `Not specified`、`Left`、`Right`、`Both` 对应的稳定内部值 |
| `instagram_handle` | 可空 String，最长 30 字符；只保存 Instagram Username；保存前去除开头的 `@` |
| `other_social_url` | 可空 URL；最多一个；仅允许 `https` |
| `is_published` | 必填 Boolean；默认 `False`；会员可在 Phase 3 自行开启或关闭 |
| `is_hidden_by_admin` | 必填 Boolean；默认 `False`；仅授权管理员可以修改 |
| `executive_role` | 可空 String，最长 100 字符；自由文本；仅授权管理员可以修改；Phase 1 不公开展示 |
| `created_at` | 必填 DateTime；创建时自动记录；用户不可修改 |
| `updated_at` | 必填 DateTime；每次保存时自动更新；用户不可修改 |

公开查询必须至少满足 `is_published` 为 `True` 且 `is_hidden_by_admin` 为 `False`，并同时排除账户未启用或邮箱未验证的 Profile。管理员专属字段不得出现在会员可写 form 中。

**验证：** 测试一对一关系与级联删除；测试资料默认值、时间戳和创建 service 幂等性；测试 `display_name` 的清理、空值共存及忽略大小写唯一性；测试头像格式、真实图像内容和 5 MB 限制；测试 Bio 纯文本、Experience 与 Preferred arm choices、Instagram `@` 清理和仅限 `https` 的其他链接；测试公开查询排除未发布、被隐藏、停用或未验证用户；检查普通会员不能修改管理员字段。

**完成条件：** Profile schema、创建 service 和公开边界均有测试保护。

### Step 9 — 接入 django-allauth

**目标：** 建立认证基础设施和项目 URL 集成。

**指令：** 配置 username/password 登录、强制邮箱验证、Email verification by code、可选 Email Magic Code、Password reset、唯一 Email、enumeration prevention 和默认 rate limits；未验证账户不得通过密码或 Magic Code 进入会员区域，只能继续验证或请求重发验证码；禁用 Social login、Phone login、MFA 及强制登录验证码；配置 Sites framework、authentication backend 和 redirects。

**验证：** 依据锁定版本的官方文档核对 setting 名称；运行 system check；验证 signup、login、logout、verification、login code 和 password reset 的 URL name 可反向解析；确认禁用功能没有公开入口。

**完成条件：** allauth 配置通过 system check，所需流程均可路由且未启用排除功能。

### Step 10 — 实施单页注册表单

**目标：** 收集 Username、Email、Password、USYD 声明和可选 USU ID。

**指令：** 扩展 signup form；字段顺序与 `design_document.md` 一致；USU ID 仅在选择 USYD 后显示，但服务端始终执行同一规则；注册提交后进入独立邮箱验证码页面。

**验证：** 测试所有必填字段、任意有效邮箱、重复 Username、重复 Email 的 enumeration 行为、USYD 条件字段、非 USYD 绕过提交、USYD 留空 ID 和填写 ID；执行无 JavaScript 提交测试。

**完成条件：** 注册表单的正常、错误和绕过路径均有自动化测试。

### Step 11 — 完成注册邮箱验证码流程

**目标：** 只有完成邮箱验证的账户才能成为有效会员。

**指令：** 建立验证码输入、重发、过期和成功后的 redirect；验证成功后通过幂等 service 建立隐藏 Profile；验证码和完整 Email 不得写入日志。

**验证：** 测试正确、错误、过期和重复使用验证码；测试重发频率限制；测试验证前不能获得会员权限，验证后 Profile 只建立一次；检查测试日志不包含验证码。

**完成条件：** 邮箱验证及重发边界全部通过，会员状态与 Profile 创建一致。

### Step 12 — 完成密码登录、重置与登出

**目标：** 提供安全的 Username/Password 账户入口。

**指令：** 使用通用凭据错误信息；邮箱未验证账户不得建立可访问会员区域的登录状态，并应进入验证或验证码重发流程；验证成功后返回原目标页面或 Account；Password reset 使用 allauth；登出只接受 POST。

**验证：** 测试正确登录、错误 Username、错误 Password、未验证账户、停用账户、开放 redirect 防护、Password reset 和 GET logout 被拒绝；确认错误信息不泄露账户存在性。

**完成条件：** 密码认证相关正常、失败和安全路径全部通过。

### Step 13 — 完成 Email Magic Code 登录

**目标：** 提供可选的邮箱验证码登录方式。

**指令：** 建立请求、确认和重发页面；保持密码登录为独立入口；未验证账户不得通过 Magic Code 进入会员区域，应引导完成注册邮箱验证；对请求、尝试和重发应用 allauth rate limits；不得记录登录码。

**验证：** 测试有效、错误、过期和重复使用 code；测试未验证 Email、停用账户、频率限制和 enumeration prevention；检查密码登录没有被强制追加 code。

**完成条件：** Magic Code 流程可独立完成且不降低账户枚举保护。

### Step 14 — 建立 Account 页面与 USU 信息更新

**目标：** 让会员管理本人账户和身份声明。

**指令：** 展示只读 Username、只读 Email、Email 验证状态、USYD 声明、条件 USU ID 和本人审核状态；Phase 1 不提供 Email 修改入口；提供 Password change 与 POST logout；所有更新通过受控 form/service 完成。

**验证：** 测试 Anonymous 被重定向、会员只能查看和修改本人信息、Username 与 Email 无法通过页面或伪造请求修改、非 USYD 不能提交 ID、修改 ID 回到 `pending`、取消 USYD 清除审核信息、普通会员不能写入审核字段。

**完成条件：** Account 的访问控制与状态转换测试全部通过。

### Step 15 — 建立 USU ID 管理后台

**目标：** 让获授权管理员执行人工审核并留下审计信息。

**指令：** 扩展 UserAdmin 的列表、筛选、搜索和字段分组；审核必须使用专用 form 或 action；通过和拒绝均记录当前管理员与时间；限制非授权 Staff 的查看与编辑能力。

**验证：** 测试普通会员、未授权 Staff、授权 Staff 和 Superuser 的权限差异；测试通过、拒绝、重新提交和审核人停用后的数据行为；确认公开响应不包含审核人或完整 USU ID。

**完成条件：** 审核操作、最小权限和审计字段具有自动化测试。

### Step 16 — 建立全局模板与消息框架

**目标：** 提供一致、可访问且可扩展的页面外壳。

**指令：** 创建 base、Header、Footer、messages 和首页占位模板；Header 根据登录状态显示 `Join the Club`、`Log in` 或 Account；首期用户文案使用英文；不得公开未经批准的 USYD Branding。

**验证：** 对 Anonymous 与 Member 渲染页面；检查 Heading、landmark、当前导航、键盘 Focus、live region 和手机宽度；验证模板无 JavaScript 时仍可导航和提交核心表单。

**完成条件：** 全局页面结构通过模板测试、键盘检查和窄屏 smoke test。

### Step 17 — 完成认证与 Account 页面表现

**目标：** 将注册、验证、两种登录和 Account 流程接入统一界面。

**指令：** 建立所需 account templates；错误靠近字段显示；验证码输入支持粘贴和移动端数字键盘；使用 Alpine.js 控制 USU ID 的条件显示，但服务端不依赖 Alpine.js。

**验证：** 执行各表单的成功与错误渲染测试；验证 Label 与错误关联、Focus 移动、验证码粘贴、窄屏布局和关闭 JavaScript 后的提交；检查敏感字段不会回显。

**完成条件：** 所有 Phase 1 用户流程可通过键盘和手机宽度完成。

### Step 18 — 建立 Tailwind 与静态资产流程

**目标：** 生成可重现的 Phase 1 样式和静态资源。

**指令：** 建立 Tailwind 输入、source scanning、Development watch 和 Production build；通过 npm 锁定前端依赖，将 HTMX、Alpine.js 和 MapLibre GL JS 作为版本固定的本地静态资源提供；集中定义深黑、炭灰、暖白、金色、字体、间距、Focus 和小圆角 tokens；仅使用获准或本地占位资产；Production 不使用 Tailwind Play CDN 或第三方库 CDN。

**验证：** 执行 Development watch smoke test 和 Production CSS build；确认模板使用的固定 class 被扫描；断开外部网络后确认 Phase 1 页面仍能加载所需 CSS 与 JavaScript；检查 Production 不依赖 Tailwind Play CDN 或第三方库 CDN；验证关键文字、按钮和 Focus 对比度达到 WCAG 2.2 AA。

**完成条件：** CSS 可从锁定依赖重复生成，关键页面没有缺失样式或对比度阻塞。

### Step 19 — 建立质量与安全检查

**目标：** 形成可重复运行的 Phase 1 检查链。

**指令：** 配置 pytest、pytest-django、coverage、Ruff、Django checks 和 Playwright；禁止测试访问外部网络；加入 Secret、敏感日志、公开字段和上传边界检查；使用 Playwright 覆盖 Phase 1 核心浏览器流程，并为 CI 保留单一检查入口。

**验证：** 从干净 PostgreSQL test database 运行 migrations、Ruff、system checks、全部 pytest 测试和 Playwright 核心流程；运行 Production deployment check；确认测试失败会产生非零结果；检查日志不包含 Password、验证码、完整 USU ID 或 session token。

**完成条件：** 全部检查可重复运行，任何失败都会阻止继续交付。

### Step 20 — Phase 1 端到端验收

**目标：** 确认账户与认证基础可以交付给下一阶段。

**指令：** 使用全新环境通过 `uv` 和 npm 执行锁定依赖安装、PostgreSQL 启动、migrate、CSS build 和本机 Django 启动；使用 Playwright 并辅以手工检查走查注册、邮箱验证、密码登录、Magic Code、Account 更新、USU 审核和 POST logout；更新 README 与 `progress.md`。

**验证：** 运行完整自动化套件；执行桌面与手机 smoke test；确认未提交 Secret、`.env`、数据库、真实会员资料或用户上传文件；检查未公开 University Branding。

**完成条件：** Phase 1 的 Roadmap 退出门槛全部满足；记录遗留问题；向项目负责人申请更新 `architecture.md`，并在获批后再展开 Phase 2。

## 六、Phase 2 概要：英文宣传网站

**展开条件：** Phase 1 已验收，真实模板结构、Design Tokens 和认证导航稳定。

**范围：** Home、About、Beginners & Safety、Risk Notice、403、404、500、metadata、Open Graph 和 sitemap。Home 以 `Join the Club` 为主操作，使用紧凑活动日程；复杂人体结构和受力插画继续后置。

**关键约束：** 正式环境只展示已确认 Risk Notice；Preview 必须标记 draft；不得制造 University 官方部门或正式研究实验室的误解；页面遵循既定黑金视觉、字体和新手友好比例。

**阶段验证：** 公共页面内容、导航、SEO metadata、error pages、键盘、窄屏、内容放大、对比度和 JavaScript 失效路径全部通过；Production 在 Risk Notice 未确认时不得开放报名。

## 七、Phase 3 概要：会员资料

**展开条件：** Phase 2 已验收，公开页面结构和 media 策略可用。

**范围：** 基于 Phase 1 已建立的完整字段实现 Profile edit、preview、publish、unpublish、Members list、Member detail 和 Admin hide/unhide；根据届时确定的 media 策略补充上传处理。

**关键约束：** 资料默认隐藏；公开必须由会员主动开启；管理员隐藏不修改会员自述；Executive role 首期不公开；上传需要验证类型、大小和真实图像内容，并移除不必要 metadata。

**阶段验证：** 公开 queryset、对象所有权、管理员权限、未发布与隐藏资料、停用账户、直接 URL、上传伪装文件及公开字段泄露测试全部通过。

## 八、Phase 4 概要：活动、Risk Notice 与报名

**展开条件：** Phase 3 已验收，Risk Notice 正式文本或获准测试版本可用。

**范围：** Event、RiskNoticeVersion、EventRegistration、Events 页面、Event detail、报名、取消、重新报名、My registrations 和管理员名单。

**关键约束：** 不增加 capacity、waitlist、deadline、payment 或 external registration；每次报名主动确认当前 Risk Notice；历史记录保留当时版本；同一用户和活动最多一条有效报名；取消不删除记录；报名与确认在同一事务完成。

**阶段验证：** 权限、报名开关、重复提交、并发报名、Risk Notice 版本竞争、取消幂等、重新报名、历史保留、名单隐私、普通 POST 与 HTMX 回退全部通过。

## 九、Phase 5 概要：地点与地图

**展开条件：** Phase 4 已验收，地点地址、坐标和联系人已由管理员确认。

**范围：** Location、地点卡片、MapLibre 地图、Marker、Popup、卡片联动和无 JavaScript 回退。

**关键约束：** 未确认坐标不得显示 Marker；文字地点列表始终可用；地图数据通过安全 JSON 输出；不得在 template 中拼接未转义 JavaScript；tile provider 未确定前不得假设额度或 attribution。

**阶段验证：** 数据精度、缺失坐标、键盘操作、手机点击、地图加载失败、脚本禁用、Popup 与卡片联动、公开字段和 attribution 检查全部通过。

## 十、Phase 6 概要：上线与运维

**展开条件：** Phase 5 已验收，hosting、SMTP、media storage、monitoring、tile provider 和数据保留决策已确认。

**范围：** Production image、部署流程、HTTPS、domain、collectstatic、migrations、health check、日志、监控、数据库和 media 备份、恢复演练、回滚及生产 smoke test。

**关键约束：** `DEBUG` 关闭；Secret 仅由平台管理；正式 Risk Notice 已锁定；Branding 获得批准；Production 与 Preview 数据和凭据隔离；上线步骤可回滚。

**阶段验证：** Production deployment check、干净部署、升级与回滚、Email、持久化 media、备份恢复、health check、安全 headers、错误监控和核心用户流程全部通过。

## 十一、Migration 顺序

1. `accounts.0001_initial` 创建 Custom User；
2. `members.0001_initial` 创建 MemberProfile；
3. `locations.0001_initial` 创建 Location；
4. `safety.0001_initial` 创建 RiskNoticeVersion；
5. `events.0001_initial` 创建 Event 与 EventRegistration；
6. 仅在内容确认后使用 data migration 写入初始地点或 Risk Notice。

不得在 Custom User 建立前运行项目首次业务 migration。初始管理员使用明确的管理命令建立，不写入 migration。

## 十二、统一 Definition of Done

一个步骤只有同时满足以下条件才算完成：

- 行为符合 `design_document.md`；
- 技术实现符合 `tech_stack.md` 和已批准的 `architecture.md`；
- 修改范围没有扩展到后续步骤或排除项；
- 正常、错误、权限和重复提交路径已经测试；
- 数据库约束与应用层校验一致；
- 用户文案使用英文且可理解；
- 核心操作支持键盘和手机宽度；
- 未泄露敏感字段或 Secret；
- 相关文档、环境示例和 `progress.md` 已同步；
- 本步骤列出的验证全部通过。

## 十三、禁止自行决定的事项

- Risk Notice 的最终法律或政策文本；
- 未成年人是否需要额外措施；
- University Branding 的使用范围；
- 会员退出、账户删除和数据保留规则；
- 中文版本范围；
- 正式 hosting、SMTP、media storage、monitoring 和 tile provider；
- 新增付款、容量、候补、截止时间、排名或比赛管理功能。

遇到以上事项或文档冲突时，记录阻塞并请求明确决定，不得通过默认值、占位实现或扩大范围继续。
