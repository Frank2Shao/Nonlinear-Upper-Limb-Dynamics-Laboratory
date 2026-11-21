# NULDL 网站 Implementation Plan

**项目名称：** Nonlinear Upper Limb Dynamics Laboratory Website  
**文档职责：** 为 AI 开发者提供可验证、可逐步执行的开发指令  
**实施根目录：** `../`  
**文档状态：** Progressive  
**最后更新：** 2026 年 11 月 20 日

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

- 始终保留首期各阶段的范围、依赖、验收门槛及取消记录；
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
- 活动地点使用 Event 的地点文字和可选 Google Maps HTTPS 链接；
- 使用 npm 管理并锁定前端依赖，HTMX 和 Alpine.js 作为本地静态资源提供，Production 不依赖第三方 CDN；
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
| `apps/events/` | Event、活动地点文字与可选地图外链、报名、取消及历史记录 |
| `apps/locations/` | 前期创建的 App 骨架 |
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
| `researcher_number` | Visual Refresh 第四轮（V14）加入。可空正整数；非空时全站唯一且不小于 1；仅授权管理员可以修改；随已发布资料公开为 `Researcher 07`（至少两位，补零） |
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

## 六、Phase 2：英文宣传网站

**展开条件：** Phase 1 已验收；全局模板、Design Tokens、认证导航、静态资源和 Playwright 门禁稳定；Phase 2 英文内容已经记录在 `design_document.md`。

**范围边界：** 本阶段只实现静态英文宣传页面和相关展示基础。不增加 Event、RiskNoticeVersion 或其他数据库模型，不创建 migration，不建立 CMS，不提供活动报名。正式活动数据、Risk Notice 版本管理和报名继续属于 Phase 4。

### Step 21 — 建立公开页面基础与品牌命名

**目标：** 为 Phase 2 页面建立一致的 metadata、内容组件和响应式导航基础。

**指令：** 扩展全局 base template，提供每页可覆盖的 description、robots、Open Graph 和附加 head 内容边界；建立可复用的 public page、section、card、CTA 和状态样式；将 Header 对外品牌文字改为 `NULDL Armwrestling Club`，不得单独显示 `NULDL`；建立键盘可用的移动导航，但只链接当前已经存在的页面；保持 Anonymous 与 Member 的认证入口行为不变。

**验证：** 增加模板测试，检查 metadata block、唯一页面标题、品牌完整名称、Anonymous/Member 导航差异、当前页状态和不存在失效链接；使用 Playwright 验证桌面及手机导航、键盘操作、Focus、菜单展开关闭和禁用 JavaScript 时的基础链接；运行现有认证与全局模板回归测试。

**完成条件：** 公共页面共享基础可复用，Header 不出现含义不明的单独 `NULDL`，认证流程与无 JavaScript 导航没有回归。

### Step 22 — 完成 Home、Logo 与静态日程

**目标：** 用已确认内容完成招新导向的正式首页。

**指令：** 按 `design_document.md` 实现 Hero、`Join the Club`、`New to Armwrestling?`、训练内容、参与资格和 Upcoming Session；静态日程只显示 `1 December 2026`、`3:00–7:00 pm`、`Training Session` 与 `Venue details to be confirmed`，不建立 Event model、报名状态或 Events 链接；将仓库根目录外 `../../Logo_without_USYD.png` 作为源资产纳入仓库，保留原始文件并通过可重复流程生成适合 Hero 的响应式、压缩网页版本；Header 继续使用文字品牌；不得改动 Logo 图形内容或加入 University Branding。

**验证：** 测试 Home 的标题、正文、CTA 目标、静态日程及缺少 Events 链接；验证 Anonymous 与 Member 的 CTA 行为；检查源图和生成图尺寸、格式、文件大小、可重复生成及浏览器加载；使用 Playwright 检查 desktop/mobile 无水平溢出、Logo 不失真、文字不被裁切、CTA 可用及 JavaScript 关闭后的内容完整性。

**完成条件：** Home 使用获准英文内容和新 Logo，静态日程准确，页面不提前引入 Phase 4 功能或受限 Branding。

### Step 23 — 完成 About 与 Beginners & Safety

**目标：** 提供清晰的社团介绍、新手参与说明和安全基础信息。

**指令：** 在 `core` 中建立 About 与 Beginners & Safety 的命名 URL、views 和 templates；逐项采用 `design_document.md` 已确认文案；About 使用 `student-led`，明确网站参与资格与 constitutional governance rights 的边界；Beginners & Safety 展示 induction、supervised practice、dedicated equipment、活动风险和停止参与条件；加入 Header 导航和当前页标识；不得公开 USYD、University affiliation、联系邮箱或具体训练地点。

**验证：** 测试两条 URL、状态码、模板、Heading 层级、metadata、准确文案、导航及 CTA；扫描公开响应，确认没有单独 `NULDL`、`USYD`、`Sydney University`、`University of Sydney`、Email、USU ID 或未经批准地点；使用 Playwright 检查手机换行、键盘导航、内容放大和禁用 JavaScript 后的可读性。

**完成条件：** About 与 Beginners & Safety 内容完整、事实边界明确，并进入所有适用的公开导航。

### Step 24 — 实施 Draft Risk Notice 环境隔离

**目标：** 允许 Development 和 Preview 审阅 draft，同时确保 Production 不公开正文。

**指令：** 在 `safety` 中建立 Risk Notice view、URL 和 template；正文逐字使用 `design_document.md` 保存的当前 draft，包括源文本的重复 acknowledgement；显示 `DRAFT — NOT APPROVED FOR PARTICIPATION USE`、说明文字和 `noindex, nofollow`；通过显式配置控制 draft 可见性，默认安全关闭，Development 和获准 Preview 明确开启，Production 强制关闭；关闭时页面返回 404，并从 Header、页面 CTA 和 sitemap 排除；不得编辑责任限制文本，不得增加确认或报名表单。

**验证：** 分别测试 draft 开启和关闭配置；检查开启时正文、banner、robots、导航及 Beginners CTA，关闭时返回 404 且没有可发现链接；验证 Production settings 无法公开 draft；检查页面没有 POST、checkbox、报名入口或 RiskNoticeVersion 数据访问；运行敏感信息和 Branding 回归测试。

**完成条件：** Draft 只在明确允许的非正式环境可见，Production 无法通过直接 URL、导航或 sitemap 获取正文。

### Step 25 — 建立 403、404 与 500 页面

**目标：** 让公开错误状态保持一致、可理解且不暴露内部信息。

**指令：** 建立共享视觉下的 403、404 和 500 templates，并接入 Django handlers；提供返回 Home 的明确操作；错误页面只使用中性英文说明，不显示 traceback、Exception、内部路径、Secret 或虚构联系方式；在 `DEBUG=False` 条件下验证真实 handler 行为。

**验证：** 对三个状态执行模板和 handler 测试，确认正确状态码、页面标题、唯一 H1、Home link 和无敏感内容；使用 Playwright 在 desktop/mobile 检查布局、键盘 Focus、CSS 加载及无 JavaScript 可用性；确认现有权限测试仍返回预期状态。

**完成条件：** 403、404 和 500 均使用项目页面壳、保持正确 HTTP 状态且不泄露技术细节。

### Step 26 — 完成 Metadata、Open Graph、Sitemap 与 Footer

**状态：** 已完成并通过项目负责人验证（2026 年 10 月 27 日）。

**目标：** 建立可验证的搜索与分享基础，并加入唯一获准的公开社交入口。

**指令：** 为 Home、About 和 Beginners & Safety 使用已确认 title 与 description；建立通用 Open Graph site name、页面 title、description 和 URL；在最终域名未确认前不硬编码 canonical host；建立只包含 Production 可公开页面的 sitemap；Footer 加入 Instagram `@nuldl_armwrestlingclub` 及 HTTPS 链接，不加入联系邮箱；draft Risk Notice 只在允许环境使用 `noindex, nofollow`，且永不进入 Production sitemap。

**验证：** 测试每页 title、description、Open Graph 值、绝对或环境派生 URL、Instagram 文本与目标；解析 sitemap 并确认只包含允许页面、无认证页面、无 error page、无 draft Risk Notice 和无后续 Phase 路由；检查没有硬编码 `nuldl.com`、测试 host 或未经批准 Branding。

**完成条件：** 所有正式公开页面具有准确 metadata，sitemap 与环境可见性一致，Footer 只公开已批准的 Instagram。

### Step 27 — 完成响应式与 Accessibility 验证

**目标：** 对 Phase 2 全部公开页面执行统一的 WCAG 2.2 AA 风险检查。

**指令：** 在现有 Playwright 工具上扩展公共页面测试；覆盖 Header、移动菜单、Hero、Logo、CTA、长文、安全列表、Draft banner、Footer 和错误页面；检查语义 landmarks、Heading 顺序、link name、Focus、键盘顺序、触控目标、文本重排、200% 内容放大、颜色对比度、reduced motion 和图片替代文本；不引入未经确认的新测试框架或外部网络服务。

**验证：** 在 desktop、mobile 和 200% 放大场景运行公共页面 browser suite；执行键盘-only 路径、JavaScript disabled smoke、reduced-motion 检查和关键前景/背景对比度计算；确认浏览器没有 page error、外部资源请求、水平溢出或不可见 Focus；运行完整 pytest 与现有认证 browser 回归。

**完成条件：** Phase 2 页面在目标场景下可读、可操作且没有已知 WCAG 2.2 AA 阻塞问题。

### Step 28 — Phase 2 质量门禁与阶段验收

**目标：** 在全新环境验证英文宣传网站，并形成可交接的阶段结果。

**指令：** 扩展单一质量入口以覆盖 Phase 2 静态资产、页面、environment gating、metadata、sitemap、error handlers 和 Playwright 公共流程；在全新环境执行锁定依赖安装、PostgreSQL 启动、migrate、静态资源构建、Development server 和 Production 配置检查；人工复核全部英文文案、Logo、Instagram、日期时间、地点占位、Risk Notice draft 标识和禁止 Branding；更新 README、`progress.md` 与 Roadmap。

**验证：** 运行 Ruff、format check、migration drift、Django checks、完整 pytest、coverage、Production deploy check、collectstatic 和 Playwright desktop/mobile suite；确认没有新增 migration、Secret、真实会员资料、外部字体/CDN、未经批准 University Branding 或 Production draft Risk Notice；从干净环境复现全部检查。

**完成条件：** Roadmap 的 Phase 2 退出门槛全部满足；记录遗留内容与外部依赖；将阶段标记为 `Ready for review`；向项目负责人申请更新 `architecture.md`，获得批准并完成阶段验收后才能标记 `Complete` 和展开 Phase 3。

## 七、Phase 3：会员资料

**展开条件：** Phase 2 已验收；公开页面、响应式导航、共享质量门禁和本地 media 基础可用；Phase 3 产品规则已经记录在 `design_document.md`。

**范围边界：** 本阶段复用 Phase 1 已建立的 MemberProfile schema，预计不新增 model 字段或 migration。实现 Profile edit、Avatar 生命周期、Preview、Publish、Unpublish、Members list、Member detail 和 Django Admin hide/unhide。不增加年龄判断、筛选、专用隐藏权限、隐藏原因、独立审核表或 Production media provider。

### Step 29 — 建立本人 Profile 编辑入口与所有权边界

**目标：** 让已验证会员安全编辑本人资料，同时保持保存与发布状态分离。

**指令：** 在 `members` 建立命名 URL、views 和 templates；Account 页面加入 `Edit profile` 入口；编辑页只读取和更新当前登录用户的一对一 Profile；表单包含 Display name、Avatar、Bio、Experience level、Preferred arm、Instagram Username 和一个 HTTPS social URL，移除 `is_published`，继续排除 `is_hidden_by_admin`、`executive_role` 和时间戳；保存成功只更新资料，不改变发布状态；未验证、停用或 Anonymous 用户不得进入编辑流程。

**验证：** 测试 Anonymous、未验证账户、有效会员及对象所有权；测试正常保存、验证错误、重复 Display name、Bio HTML、Instagram 与 HTTPS social URL；伪造 User、发布状态和管理员字段必须被忽略或拒绝；验证 Account 入口、成功消息、错误保持和无 JavaScript 普通 POST；运行现有账户与 MemberProfile 回归测试。

**完成条件：** 会员只能编辑本人允许字段，保存不会意外 Publish、Unpublish 或改变管理员状态。

### Step 30 — 完成 Avatar 上传、删除与文件清理

**目标：** 按已确认的简化策略安全保存原始 Avatar，并避免替换后的旧文件残留。

**指令：** 继续支持 JPG、PNG、WebP 和 5 MB 上限，复用扩展名、声明 MIME 与 Pillow 真实内容验证；验证通过后直接保存原文件，不执行 EXIF 转向、metadata 删除、缩放或格式转换；编辑页提供明确删除操作和已确认的 metadata 隐私提示；页面通过方形容器与 CSS `object-fit` 展示；只有新资料保存成功后才清理被替换的旧文件，主动删除成功后清理对应文件；失败更新必须保留当前有效 Avatar；在 Development 中接入本地 media URL serving，Production 不启用开发用 media helper；测试使用隔离的临时 media，不提交上传文件。

**验证：** 测试允许格式、大小边界、伪装扩展名、错误 MIME、损坏图片、原文件字节保持、替换、主动删除、失败更新不删旧文件及无孤立旧文件；检查 Development media URL 可访问且 Production URLConf 不提供开发 helper；检查 Git ignore 与安全扫描不会跟踪 media；使用 Playwright 验证上传错误、当前 Avatar、方形展示、删除控制和隐私提示。

**完成条件：** Avatar 验证保持 Phase 1 安全边界，原文件按决定保存，替换和删除不会留下旧文件或破坏有效文件。

### Step 31 — 建立 Preview、Publish 与 Unpublish 流程

**目标：** 让会员在公开前查看效果，并通过独立确认控制资料可见性。

**指令：** 建立仅本人可访问的 Profile Preview，并与公开 detail 复用字段顺序和展示组件；建立独立 Publish confirmation，明确列出公开字段、Username detail URL、Display name 为空时的 Username 回退和 Avatar metadata 风险；Publish 与 Unpublish 使用 CSRF 保护的 POST，重复操作保持幂等；管理员隐藏优先于会员发布状态，页面显示中性提示且不泄露管理员信息；会员不能通过 Publish 解除 `is_hidden_by_admin`。

**验证：** 测试 Preview 所有权、未发布 Preview、GET 不得改变状态、Publish/Unpublish 正常路径、重复 POST、CSRF、开放 redirect、管理员隐藏及停用账户；确认普通编辑保存不改变 `is_published`；检查 Preview 和 confirmation 不输出 Email、USYD、USU ID、审核状态或 Executive role。

**完成条件：** 保存、预览、发布和取消发布具有独立清晰的状态转换，管理员隐藏始终具有更高公开优先级。

### Step 32 — 建立 Members 公开目录

**目标：** 公开展示主动发布且符合隐私边界的会员资料。

**指令：** 建立 `/members/` 列表页和 Header `Members` 导航；数据只来自 `MemberProfile.objects.public()`；按 Display name 或 Username 的不区分大小写顺序稳定排序；卡片显示 Avatar 或非敏感 fallback、Display name 或 Username、已填写的 Experience level 与 Preferred arm；隐藏 `Not specified`；不加入搜索、HTMX 筛选或分页复杂度；没有公开资料时显示明确 empty state。

**验证：** 测试公开 queryset、排序、Display name 回退、字段隐藏、empty state、导航和认证状态；覆盖未发布、管理员隐藏、停用和未验证账户；扫描响应，确认没有 Email、USYD、USU ID、审核字段、Executive role、Bio、非卡片 social 字段或后台信息；执行 desktop/mobile、键盘及无 JavaScript browser test。

**完成条件：** Members 目录只展示允许的公开卡片字段，没有筛选扩展或隐私泄露。

### Step 33 — 建立 Member detail 与搜索边界

**目标：** 通过稳定 Username URL 展示单个公开 Profile，并统一不可见状态。

**指令：** 建立 `/members/<username>/` 详情页并使用公开 queryset 查询；展示卡片字段以及 Bio、Instagram Username 和一个 HTTPS social URL；隐藏 `Not specified`、时间戳及全部账户和管理员字段；外部链接使用安全属性；未发布、管理员隐藏、账户停用、邮箱未验证或不存在的 Username 统一返回 404；页面使用普通公开 metadata 和 robots 规则，不增加 `noindex`；sitemap 只加入 Members 列表，不枚举个人详情 URL。

**验证：** 测试 Username URL、大小写与不存在路径、公开字段、HTML escaping、安全外链及统一 404；确认不同不可见原因无法从状态码或正文区分；解析 sitemap 确认只含 Members 列表；检查 detail 没有 `noindex` 且没有 Email、USYD、USU ID、审核字段、Executive role 或未公开值；执行浏览器导航和直接 URL smoke。

**完成条件：** 公开详情可从 Members 卡片访问，隐私状态统一，搜索与 sitemap 行为符合已确认规则。

### Step 34 — 完成 Django Admin Hide/Unhide

**目标：** 使用 Django Admin 标准修改权限管理公开隐藏状态，同时保护会员自述内容。

**指令：** 保留现有 `is_hidden_by_admin` 字段；MemberProfile Admin 使用标准 `change_memberprofile` 权限，不增加专用 permission 或自定义 action；Admin change form 将 User、会员自述字段和时间戳设为只读，只允许维护 `is_hidden_by_admin` 与 `executive_role`；依赖 Django Admin log 记录修改，不增加原因或历史 model；隐藏不修改 `is_published`、资料内容或账户状态；会员页面只显示中性隐藏提示。

**验证：** 测试普通会员、无 change 权限 Staff、有 change 权限 Staff 和 Superuser；确认授权管理员可勾选和取消隐藏、维护 Executive role，但不能通过 Admin 修改会员自述、User 或时间戳；验证 Django Admin log 产生记录；检查隐藏后公开列表和 detail 消失、账户登录和本人编辑继续可用、Unpublish 仍可执行。

**完成条件：** Hide/Unhide 使用标准 Admin 权限完成，会员内容和账户状态不被后台隐藏操作改写。

### Step 35 — 完成 Phase 3 响应式、Accessibility 与隐私门禁

**状态：** 已完成并通过项目负责人验证（2026 年 11 月 12 日）。

**目标：** 对全部 Profile 页面执行统一的浏览器、可访问性和公开数据检查。

**指令：** 扩展现有 Playwright 与 Django 安全测试，覆盖 Edit、Avatar、Preview、Publish confirmation、Unpublish、Members、Member detail、empty state 和管理员隐藏提示；检查语义、Heading、Label、错误关联、键盘、Focus、触控目标、200% 内容放大、reduced motion、图片 alt、长 Bio、长 Username、社交链接、无 JavaScript 提交和媒体加载；所有已验证会员使用同一流程，不加入年龄字段、年龄推断或年龄分支。

**验证：** 在 desktop、mobile、200% 放大、JavaScript disabled 和 reduced-motion 场景运行 Phase 3 browser suite；确认无横向溢出、page error、外部资源请求或不可见 Focus；执行公开响应敏感字段扫描、对象所有权测试、直接 URL 测试和 media 临时目录清理检查；运行完整 pytest、现有 Phase 1–2 browser 回归及静态资源检查。

**完成条件：** Profile 全流程在目标设备和辅助场景可用，公开响应、media 和权限边界没有已知阻塞问题。

### Step 36 — Phase 3 质量门禁与阶段验收

**状态：** 已完成并通过项目负责人验证（2026 年 11 月 12 日）。

**目标：** 在全新环境验证会员资料功能，并形成可交接的阶段结果。

**指令：** 扩展共享项目门禁和 Phase 3 全新环境验收入口，覆盖资料编辑、Avatar、Preview、Publish/Unpublish、目录、详情、Admin hide/unhide、media serving 和隐私边界；使用合成账户与临时 media 完成人工走查；更新 README、`progress.md` 与 Roadmap；不得提交真实会员资料、用户上传文件或 media 目录。

**验证：** 运行锁定依赖安装、PostgreSQL、migrations、Ruff、format check、migration drift、Django checks、完整 pytest、coverage、Production deploy check、collectstatic 和 Playwright desktop/mobile suite；确认 Phase 3 没有新增 migration、年龄逻辑、筛选、专用隐藏权限、排行榜或 Production media provider；从干净环境复现全部检查并人工验证主要状态。

**完成条件：** Roadmap 的 Phase 3 退出门槛全部满足；记录遗留 media 与外部依赖；将阶段标记为 `Ready for review`；向项目负责人申请更新 `architecture.md`，获得批准并完成验收后才能标记 `Complete` 和展开 Phase 4。

## 八、Phase 4：活动、Risk Notice 与报名

**展开条件：** Phase 3 已验收。开发和测试仅使用明确标记的合成 Risk Notice。正式文本获批前，Production 报名保持关闭。

**范围：** Event、RiskNoticeVersion、EventRegistration、Events 列表与详情、报名、取消、重新报名和管理员名单。会员在活动详情页查看本人的当前状态。

**关键约束：** 不增加 capacity、waitlist、deadline、payment 或 external registration；每次报名主动确认当前 Risk Notice；历史记录保留当时版本；同一用户和活动最多一条有效报名；取消不删除记录；报名与确认在同一事务完成。

**阶段验证：** 权限、报名开关、重复提交、并发报名、Risk Notice 版本竞争、取消幂等、重新报名、历史保留、名单隐私、普通 POST 与 HTMX 回退全部通过。

| 步骤 | 实施与验收 |
| --- | --- |
| 37 | 建立 `RiskNoticeVersion` 和 Admin 切换流程。验证唯一当前版本、原版本保留和环境隔离。 |
| 38 | 建立 `Event` 和 Admin。验证公开状态、报名开关、起止时间及可选 Google Maps HTTPS URL。 |
| 39 | 建立 `EventRegistration` 和事务服务。验证单一有效报名约束、Risk Notice 版本引用、时间记录和并发一致性。 |
| 40 | 从 Home 接入 Events 列表及详情（Step 45 另在 Header 增加 Events 导航）。仅支持 Upcoming 和 Past（无效参数回退到 Upcoming），按悉尼时间在活动结束日期过后的首个本地午夜自动归档。Home 改用数据库近期活动，支持空状态。由管理员录入已确认的 12 月 1 日日程。活动详情在提供地图 URL 时显示 `View location in map`。验证日期边界、公开范围、地图链接和普通链接回退。 |
| 41 | 实现已验证会员报名，主动确认当前 Risk Notice。验证过期版本重提、关闭及 Past 时拒绝报名、Production 门禁、普通 POST 与 HTMX。 |
| 42 | 实现幂等取消和重新报名。验证关闭及 Past 时拒绝取消、保留取消记录及重新确认当前版本。 |
| 43 | 建立 Admin 报名名单。验证最小权限及报名和 Risk Notice 历史只向获授权管理员开放。 |
| 44 | 验证并发、隐私、响应式、Accessibility、禁用 JavaScript 和浏览器流程。 |
| 45 | 完成全新环境验收、人工走查和文档收尾。 |

原 Step 43（My registrations）已取消，其余步骤沿用已讨论的编号。首场活动通过 Admin 录入。

## 九、Phase 5：地点与地图（已取消）

项目负责人确认，以 Phase 4 的 Event 地点文字和可选 Google Maps HTTPS 链接满足首期地点展示需求。Phase 5 状态为 `Cancelled`，保留阶段编号。

## 九点五、Visual Refresh：视觉优化（Phase 6 前置）

**展开条件：** Phase 1–4 已验收，代码清理已完成。设计以 Design canvas `NULDL Home hero concepts` 为视觉参考，以 `design_document.md` 7.4、7.7、9.2–9.6 为权威规则。

**推进方式：** 一次设计确认一个页面，再实施该页面；第一轮同时建立全站共用的视觉基础。每个页面完成后更新 `design_document.md`（若有新决定）与 `progress.md`。

**关键约束：** 不改变业务逻辑、权限、URL、表单字段或 migration；不新增第三方 CDN，字体与图片均为本地静态资产；保持 WCAG 2.2 AA、键盘、200% 放大、禁用 JavaScript 与 `prefers-reduced-motion` 门禁；画布中的固定像素尺寸不得照搬，必须改为流式布局。

| 步骤 | 实施与验收 |
| --- | --- |
| V1 | 视觉 Tokens 与资产管线。更新 `static_src/css/site.css` 的 `@theme`：暖黑页面底色、金色材质色阶（暗部、主色、亮部）、正文与次要文字色、网格线色、等宽字体族；以 npm 锁定方式加入 JetBrains Mono 本地字体并纳入现有静态资产流程；扩展图片构建脚本，从 `static_src/images/brand/gold-texture-source.png` 与 `static_src/images/home/hero-specimen-source.png` 生成带校验的 WebP 变体，并纳入 `images:check`。验证 `static:check`、静态资产测试及对比度。 |
| V2 | 全站共用组件。实现金色质感文字、金色材质填充、切角主按钮（悬停一次性高光，尊重 reduced motion）、金色渐变描边次要按钮、金色分隔线、等宽金色标签、坐标网格页面背景，以及使用这些组件的 Header 与 Footer。替换现有按钮样式时检查所有页面不回退。验证完整测试、全部页面 Accessibility 浏览器门禁（对比度、Focus、24px 触控目标、重排）及人工截图走查。 |
| V3 | Home Hero 布局。按 7.4 的单一栏宽方案重建 Hero：三行金色标题、标签与 eyebrow、介绍、三个等宽按钮（`Join the Club` 仅 Anonymous、`Join on USU`、`New to Armwrestling?`）、右侧 Logo、底部图纸标题栏；窄屏时 Logo 移至标题下方。更新 Home 页面测试中依赖旧结构与旧文案的断言。验证 Anonymous 与 authenticated member 的按钮集合与顺序、desktop/mobile 布局和无 JavaScript 场景。 |
| V4 | **已取消。** 原计划在 Hero 中以信息表显示最近一场 Upcoming Event，与下方 `Upcoming Events` 区第一张活动卡片重复；项目负责人决定取消，其等宽信息行样式并入 V6 活动卡片。保留步骤编号。 |
| V5 | Hero 背景彩蛋。照片层仅在宽屏且支持悬停的媒体条件下渲染（光照只显现照片，不叠加受力标注），照片通过 CSS 背景加载，窄屏和触屏设备不下载该图片；指针移动只更新 CSS 自定义属性驱动遮罩，不持续动画；整层对辅助技术隐藏且不拦截指针事件。验证 desktop 光照可见、mobile 无该图片网络请求、无 page error、文字与按钮可点击性不受影响。 |
| V6 | Home 其余区块（`New to Armwrestling?` 卡片与 `Upcoming Events`）。先在设计画布确认样式，再以 V2 组件实施；活动卡片的日期、时间与地点采用原 V4 信息表风格（等宽标签、低优先级标签色与主要文字色数值、半透明金色细边框）；活动卡片样式同时作用于 Events 列表。 |
| V7 | 第一轮质量门禁。完整测试、Ruff、`static:check`、Django checks、Phase 2–4 desktop/mobile smoke 与 Accessibility 门禁全部通过；提交 desktop 与 mobile 截图供项目负责人走查；记录 `progress.md`，申请批准后再更新 `architecture.md`。 |

后续页面顺序：Events 列表与详情 → About、Beginners & Safety → Members → 认证与 Account → 403/404/500。每个页面在设计确认后再展开为具体步骤。

### Visual Refresh 第二轮：Events 列表与详情

**展开条件：** 第一轮 V1–V7 已验收；项目负责人已确认 Events 列表与详情的设计 mockup（规则见 `design_document.md` 7.5）。约束与第一轮相同：不改变业务逻辑、权限、URL、表单字段或 migration；报名与取消的 HTMX、Alpine 与普通 POST 契约保持不变。

| 步骤 | 实施与验收 |
| --- | --- |
| V8 | Events 列表页。页头改为 `.section-heading` 式等宽标签与大标题；`Upcoming`/`Past` 由两个按钮改为标签页导航（仍为带 `?view=` 的普通链接与 `aria-current`）；Past 卡片日期数字弱化；无结果状态使用 `.events-empty`。验证筛选、无效参数回退、无 JavaScript、键盘 Focus、24px 触控目标、desktop/mobile 无溢出与对比度。 |
| V9 | 活动详情页与报名区。顶部 `Back to events` 小链接、页头状态标签、两栏布局（窄屏单栏且信息面板在前）、信息面板（含星期的日期、时间、地点、地图链接）；报名区各状态按 7.5 呈现，`Registered` 改为状态标签并保留 `role="status"`、`x-ref="status"` 与 HTMX 后聚焦；报名与取消 dialog 及无 JavaScript 确认页按 7.5 restyle。验证 Anonymous、可报名、已报名、取消、关闭、Past 各状态，HTMX 与普通 POST，dialog 键盘与 Focus，200% 放大与 desktop/mobile 截图。 |
| V10 | 第二轮质量门禁。`accept_phase_4.py` 全新环境验收通过；提交 Events 列表与详情（含报名各状态）的 desktop 与 mobile 截图供项目负责人走查；记录 `progress.md`，申请批准后更新 `architecture.md`。 |

### Visual Refresh 第三轮：About 与 Beginners & Safety

**展开条件：** 第二轮 V8–V10 已验收；项目负责人已确认 About 与 Beginners & Safety 的设计 mockup（规则见 `design_document.md` 7.9，页头小标签见 7.7）。约束与前两轮相同：不改变业务逻辑、权限、URL、Metadata、文案或 migration；Draft Risk Notice 入口仍只在环境允许时出现，Anonymous 与已登录会员的 `Join` 分支不变。

| 步骤 | 实施与验收 |
| --- | --- |
| V11 | About 页与共用报告分节组件。建立页头（等宽小标签、H1、介绍，左对齐、占满共享内容宽度）、报告分节（金色细线、对辅助技术隐藏的编号、宽屏 1 : 2 两列、窄屏单列）与补充说明段落样式；`What We Do` 改用编号功能卡片（宽屏两列）；Anonymous 的 `Join` 改为页面末尾居中、Hero 尺寸的主按钮。更新依赖旧结构的 About 测试。验证 Anonymous/会员、Heading 顺序、desktop/mobile、200% 放大、无 JavaScript、键盘 Focus、24px 触控目标、无溢出与对比度。 |
| V12 | Beginners & Safety 页。复用 V11 的页头与报告分节；`What to Expect` 改为编号流程；风险说明改为带顶部金色渐变细线的暖色面板，Draft Risk Notice 入口在面板内左对齐且只在环境允许时出现；`During Training` 改为单框分行规则列表。更新依赖旧结构的测试。验证 Draft 开关两种状态、Heading 顺序、desktop/mobile、200% 放大、无 JavaScript、键盘 Focus、触控目标、无溢出与对比度。 |
| V13 | 第三轮质量门禁。`accept_phase_4.py` 全新环境验收通过；提交两页（含 Anonymous/会员、Draft 开/关）的 desktop 与 mobile 截图供项目负责人走查；记录 `progress.md`，申请批准后更新 `architecture.md`。 |

### Visual Refresh 第四轮：Members

**展开条件：** 第三轮 V11–V13 已验收；项目负责人已确认 Members 列表与详情的设计 mockup（规则见 `design_document.md` 7.10），并决定加入由管理员手动分配的 Researcher 编号（规则见 4.4、11.1）。

**与前几轮约束的差异：** 本轮经项目负责人批准新增一个 MemberProfile 字段及其 migration（只在 V14）；其余约束不变：不改变 URL、Metadata、会员可写表单、发布/隐藏逻辑与公开查询边界。

| 步骤 | 实施与验收 |
| --- | --- |
| V14 | Researcher 编号的数据与 Admin。新增 `MemberProfile.researcher_number`（可空正整数；数据库约束保证非空值唯一且不小于 1）与 migration `members.0002`；提供 `Researcher 07` 格式的显示属性；Admin change form 允许维护该字段（与 `is_hidden_by_admin`、`executive_role` 并列），列表显示并可按编号排序；会员可写表单仍排除该字段；Publish confirmation 的公开字段清单加入 Researcher 编号。验证：约束（重复、0、空值共存）、显示格式（`07`、`100`）、会员表单无法提交该字段、Admin 权限与修改、Publish confirmation 文案、`makemigrations --check`。本步不改公开页面版式。 |
| V15 | Members 列表页。页头改为 `.page-heading`（`Club community`、H1、介绍，左对齐）；卡片按 7.10 restyle：金色细边框与顶部渐变细线、方形 Avatar、名称上方的 Researcher 标签（仅已分配时）、图纸式资料格；名称链接覆盖整张卡片，Focus 显示在卡片外框。更新依赖旧结构的测试。验证有/无编号、有/无 Avatar、长名称、空状态、排序、Heading 顺序、desktop/mobile、200% 放大、无 JavaScript、键盘 Focus、24px 触控目标、无溢出与对比度。 |
| V16 | Member detail 与本人 Preview。顶部 `← Back to members`；信息面板（Avatar、`Member profile` · Researcher 标签、H1、`@username`、资料格）；`Bio` 与 `Links` 为报告分节，缺失内容的分节不显示且编号连续；Preview 共用同一组件（H2 版本保持 Heading 层级）。更新依赖旧结构的测试。验证有/无编号、Avatar、Bio、Links 的组合，Preview 与隐藏提示，未发布/隐藏 404 不变，Heading 顺序、desktop/mobile、200% 放大、键盘、外链属性、无溢出与对比度。 |
| V17 | 第四轮质量门禁。`accept_phase_4.py` 全新环境验收通过；提交 Members 列表、详情与 Preview（含有/无编号与 Avatar）的 desktop 与 mobile 截图供项目负责人走查；记录 `progress.md`，申请批准后更新 `architecture.md`。 |

### Visual Refresh 第五轮：认证与 Account

**展开条件：** 第四轮 V14–V17 已验收；项目负责人已确认认证、Account、Edit Profile、Preview 与 Publish/Unpublish 的设计 mockup（规则见 `design_document.md` 7.11）。约束与前几轮相同：不改变业务逻辑、权限、URL、Metadata、表单字段与顺序、验证规则或 migration；allauth 流程、频率限制与防枚举行为保持不变；USYD/USU 条件字段的 Alpine 与无 JavaScript 回退保持不变。7.11 列出的新增短文案、Log in 页删除重复的 `Forgot password?` 按钮和去掉 Label 末尾冒号是本轮仅有的文案变动。

| 步骤 | 实施与验收 |
| --- | --- |
| V18 | 共用表单字段与认证页面。全站 `.field` 改为等宽大写 Label、直角金色细边框输入框与同一行 Checkbox；去掉 Label 末尾冒号（只改 label suffix，不改字段）；建立访问面板与认证页两栏版式，套用到 Log in、Join the Club、Verify email、Log in by email code 与密码重置/修改等 allauth 模板；Log in 页删除重复的 `Forgot password?` 按钮。更新依赖旧结构与冒号的测试。验证注册（含 USYD 条件字段、无 JavaScript）、密码登录与错误、验证码登录、密码重置各页，Heading 顺序、Label 关联、错误提示位置、desktop/mobile、200% 放大、键盘 Focus、24px 触控目标、无溢出与对比度。 |
| V19 | Account 页。页头与四个报告分节；图纸式表格展示账户与 Profile 资料；资料摘要（Avatar、发布状态标签、Researcher 标签、公开名称、公开路径）与操作入口；USYD/USU 表单与 Security 按钮左对齐。更新依赖旧结构的测试。验证已发布/未发布/管理员隐藏、有/无编号与 Avatar、USU 各审核状态、非 USYD 用户、Heading 顺序、隐私边界不变、desktop/mobile、200% 放大、键盘、无溢出与对比度。 |
| V20 | Edit Profile、Preview 外壳与 Publish/Unpublish 确认页。编辑表单分为三个报告分节与末尾操作栏（Avatar 编辑区宽屏两列）；Preview 页头与 `Public view` 虚线框，隐藏提示与按钮在框外；Publish/Unpublish 确认页的分节、规则列表、`Public name`/`Profile URL` 表格与警示。更新依赖旧结构的测试。验证编辑保存与错误回显、Avatar 上传/删除、Preview 的已发布/未发布/隐藏状态、Publish 与 Unpublish 的 POST、CSRF 与幂等不变、Username 回退说明、Heading 顺序、desktop/mobile、200% 放大、键盘、无溢出与对比度。 |
| V21 | 第五轮质量门禁。`accept_phase_4.py` 全新环境验收通过；提交认证页面、Account、Edit Profile、Preview 与 Publish/Unpublish 的 desktop 与 mobile 截图供项目负责人走查；记录 `progress.md`，申请批准后更新 `architecture.md`。 |

## 十、Phase 6 概要：上线与运维

**展开条件：** Phase 1–4 已验收，hosting、SMTP、media storage、monitoring 和数据保留决策已确认。

**范围：** Production image、部署流程、HTTPS、domain、collectstatic、migrations、health check、日志、监控、数据库和 media 备份、恢复演练、回滚及生产 smoke test。

**关键约束：** `DEBUG` 关闭；Secret 仅由平台管理；正式 Risk Notice 已锁定；Branding 获得批准；Production 与 Preview 数据和凭据隔离；上线步骤可回滚。

**阶段验证：** Production deployment check、干净部署、升级与回滚、Email、持久化 media、备份恢复、health check、安全 headers、错误监控和核心用户流程全部通过。

## 十一、Phase 7 概要：Training Records & Leaderboards

**阶段定位：** Phase 7 属于首期正式上线后的增强功能，只有 Phase 6 完成后才能展开，不得混入 Phase 3–6。

**范围：** 为不同训练动作建立成绩记录和公开排行榜；具体 Exercise、Result、单位、左右手、证明材料、审核、并列、分类和隐私规则必须在该阶段开始前由项目负责人确认。

**关键约束：** 不默认采用 Elo、体重级别、性别分类、自报成绩或管理员审核中的任何一种方案；不得在未定义动作标准和成绩可信度规则时建立排名。

**阶段验证：** 在 Phase 7 展开时单独定义数据约束、权限、审核、并发、排序、并列、历史和公开隐私测试；当前文档不提前生成代码级步骤。

## 十二、Migration 顺序

1. `accounts.0001_initial` 创建 Custom User；
2. `members.0001_initial` 创建 MemberProfile；
3. `safety.0001_initial` 创建 RiskNoticeVersion；
4. `events.0001_initial` 创建 Event，后续 migration 创建 EventRegistration；
5. `members.0002` 为 MemberProfile 加入 `researcher_number`（Visual Refresh V14，项目负责人批准）。

不得在 Custom User 建立前运行项目首次业务 migration。初始管理员使用明确的管理命令建立，不写入 migration。

Phase 3 按当前已确认范围不需要新增 migration；若实施时发现 schema 变更需求，必须停止并请求批准。Phase 7 的 migration 顺序在该阶段展开后确定。

## 十三、统一 Definition of Done

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

## 十四、禁止自行决定的事项

- Risk Notice 的最终法律或政策文本；
- 新增年龄字段、年龄判断或年龄分支；
- University Branding 的使用范围；
- 会员退出、账户删除和数据保留规则；
- 中文版本范围；
- 正式 hosting、SMTP、media storage 和 monitoring；
- 在 Phase 7 之前新增训练成绩、排行榜、Elo 或比赛管理功能；
- Phase 7 的动作、单位、审核、并列、分类和公开规则。

遇到以上事项或文档冲突时，记录阻塞并请求明确决定，不得通过默认值、占位实现或扩大范围继续。
