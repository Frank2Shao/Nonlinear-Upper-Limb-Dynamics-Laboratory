# NULDL 网站 Design Document

**项目名称：** Nonlinear Upper Limb Dynamics Laboratory Website  
**文档职责：** 定义产品目标、用户体验、页面、流程、业务规则和权限  
**首期语言：** English  
**文档状态：** Baseline  
**最后更新：** 2026 年 11 月 20 日

## 一、文档边界

本文档回答以下问题：

- 网站为谁服务；
- 首期提供哪些功能；
- 用户如何完成注册、资料管理和活动报名；
- 各角色可以查看和操作哪些内容；
- 页面需要处理哪些正常、空白、错误和受限状态；
- 内容、隐私、accessibility 和 Branding 应遵守哪些原则。

技术版本和基础设施决策见 [tech_stack.md](tech_stack.md)。代码结构、模型字段、配置和测试步骤见 [implementation.md](implementation.md)。交付阶段和进度见 [项目开发_Roadmap.md](项目开发_Roadmap.md)。

## 二、产品定位

NULDL Armwrestling Club 网站首先承担社团信息发布和会员入口功能，随后扩展为活动报名及基础会员管理系统。

社团以 USU 社团体系为基础，同时允许社会爱好者参加。网站账户与 USU 资格分别管理：

- 用户完成注册和邮箱验证后，即成为网站定义的社团会员；
- USYD 学生身份由用户声明；
- USU ID 是可选的附加信息，由管理员人工审核；
- USU 审核结果不影响普通会员身份和活动报名资格。

### 2.1 产品目标

1. 提供清晰、可信的英文社团介绍和安全信息；
2. 为所有符合网站规则的用户提供统一注册入口；
3. 让会员能够查看、报名和取消活动；
4. 保存每次活动报名对应的 Risk Notice 确认记录；
5. 减少管理员整理会员、USU ID 和活动名单的人工工作；
6. 允许会员选择性公开个人资料；
7. 为后续中文内容、更多活动功能和运营工具保留扩展空间。

### 2.2 首期成功标准

- Visitor 可以理解社团性质、活动类型和基本安全要求；
- 用户可以使用任意邮箱完成注册和验证；
- 已验证会员可以正常登录并管理个人资料；
- 管理员可以审核 USU ID；
- 会员可以在报名开放时完成活动报名和 Risk Notice 确认；
- 会员可以取消报名，历史记录仍可追溯；
- 未公开资料、邮箱、USU ID 和活动名单不会出现在公开页面；
- 网站不公开使用未经批准的 USYD Branding。

## 三、用户与角色

### 3.1 Visitor

未登录访问者，可以：

- 查看公开宣传页面；
- 查看公开活动和地点信息；
- 查看已主动公开的会员资料；
- 进入注册和登录流程。

不能：

- 报名活动；
- 查看会员私有信息；
- 查看活动参与名单；
- 查看 USU ID 或审核状态。

### 3.2 Pending user

已经提交注册表单但尚未完成邮箱验证的用户，可以：

- 输入邮箱验证码；
- 请求重发验证码；
- 在允许的情况下重新开始注册流程。

验证完成前不能登录、发布资料或报名活动。

### 3.3 Member

已经完成邮箱验证的会员，可以：

- 使用 Username/Password 登录；
- 选择使用 Email Magic Code 登录；
- 管理自己的账户资料；
- 提交或修改自己的 USYD 学生声明和可选 USU ID；
- 管理自己的公开资料；
- 报名和取消自己的活动报名；
- 查看与本人有关的报名状态。

### 3.4 Staff administrator

获得后台权限的管理员，可以：

- 审核 USU ID；
- 管理公开内容、地点、活动和 Risk Notice；
- 开启或关闭活动报名；
- 查看活动报名名单；
- 隐藏不适当的公开会员资料；
- 停用违反规则的账户。

管理员权限应按照职责分配，不默认向所有 Staff 开放全部敏感数据。

### 3.5 Superuser

负责系统级配置、权限和紧急维护。Superuser 账户不用于日常内容管理。

## 四、核心业务定义

### 4.1 会员

- 有效会员是已完成邮箱验证且账户未停用的用户；
- 任何邮箱均可注册；
- 成为会员不要求 USYD 或 USU 身份；
- 公开文案将网站账户参与资格与 Constitution 下的投票权、Executive eligibility 等治理权利明确区分；
- 面向社会参与者时，不将网站账户描述为 USU constitutional membership；
- 首期不收取网站会员费；
- 会员退出后的数据保留与账户处理暂未确定。

### 4.2 未成年人

- 首期不设置最低年龄；
- 首期不收集出生日期；
- 首期不要求监护人同意；
- 首期不收集监护人联系方式或紧急联系人；
- 注册、Profile 编辑与公开发布流程不进行年龄判断或年龄分支；
- 后续如出现强制性外部要求，必须先更新产品规则，不得由开发者自行增加年龄字段或限制。

### 4.3 USYD 学生声明与 USU ID

- 注册和账户页面提供 **Are you a USYD student?** 勾选框；
- 未勾选时不显示 USU ID 输入框；
- 勾选后显示可留空的 USU ID 输入框；
- 非 USYD 用户不能提交 USU ID；
- 新增或修改 USU ID 后进入 `pending` 状态；
- 管理员可以将其设为 `verified` 或 `rejected`；
- 审核过程依赖管理员掌握的网站外部信息；
- 审核状态不公开展示。

### 4.4 公开会员资料

- 每个有效会员都可以建立资料；
- 资料默认隐藏；
- 会员保存资料后先进行本人 Preview，再通过独立确认操作主动 Publish；
- Publish 与 Unpublish 只接受本人已认证的 POST 操作，不由普通编辑表单直接切换；
- 会员主动 Publish 后才出现在 Members 页面；
- 公开详情 URL 使用 `/members/<username>/`；Username 是公开 URL 的一部分，Display name 为空时也作为公开回退名称；
- Members 卡片公开 Avatar、Display name 或 Username、Experience level 和 Preferred arm；值为 `Not specified` 时不显示对应项目；
- Member detail 在卡片字段之外公开 Bio、Instagram Username 和一个 HTTPS social URL；
- `created_at`、`updated_at`、Email、USYD 声明、USU ID 和审核信息不公开；
- `executive_role` 由管理员维护；
- 首期不在公开页面展示 Executive 角色；
- 管理员通过 Django Admin 的现有 `is_hidden_by_admin` checkbox 隐藏或恢复资料；使用标准 `change_memberprofile` 权限和 Django Admin 日志，不增加专用权限、action、原因字段或历史表；
- Admin 中会员自述字段保持只读，管理员只能维护隐藏状态、Executive role 及必要的只读识别信息；
- 被隐藏的会员可以继续编辑和 Unpublish，并看到中性提示，但不能通过本人操作恢复公开可见性；
- 管理员隐藏不能修改会员自述内容；
- 隐藏资料不影响会员登录或活动报名。
- Members 列表不提供筛选，按 Display name 或 Username 排序，并在没有公开资料时显示明确 empty state；
- Member detail 使用普通公开页面的搜索引擎规则，不增加 `noindex`；sitemap 只列出 Members 列表，不逐个列出个人详情 URL。
- 所有已验证会员使用同一 Profile 发布流程，不收集或判断年龄。

### 4.5 活动报名

- Visitor 和 Pending user 不能报名；
- Member 只能以本人账户报名；
- 管理员可手动开启或关闭报名。活动进入 Past 后，报名和取消按钮均移除，服务端也拒绝这两项操作；
- 首期不设置容量、候补名单或报名截止时间；
- 同一会员在同一活动中最多有一条有效报名；
- 会员取消后保留历史记录；
- 取消后再次报名时产生新的有效报名记录，并保留以前的取消记录；
- 按 `Australia/Sydney` 计算，活动结束日期过后的首个本地午夜自动将活动从 Upcoming 归入 Past。活动当天的报名与取消继续受管理员报名开关控制。

### 4.6 Risk Notice

- 所有活动均要求确认 Risk Notice；
- 每次报名都必须主动确认；
- 系统记录本次确认的版本和时间；
- 新版本不修改历史报名记录；
- 同一时间只有一个当前版本；
- 正式 Risk Notice 尚未批准。Phase 4 的报名开发与测试仅使用明确标记的合成文本，Production 在正式文本获批前不开放报名；
- 在与 USU 确认前，预览环境必须明确标记正文为 draft。

## 五、信息架构

### 5.1 公开导航

```text
Home
About
Beginners & Safety
Events
Members
Log in / Account
```

Events 列表同时从 Header 导航和 Home 近期活动区进入。Development/Preview 开启 Draft 开关时，导航额外显示 `Draft Risk Notice`。

桌面端 Header 使用以下结构：

- 左侧显示 `NULDL Armwrestling Club` 文字品牌；
- 中间显示主要页面导航；
- 右侧显示 `Log in` 或账户入口，并始终突出 `Join the Club`；
- 移动端将页面导航收纳为菜单，同时保留清晰的招新入口。

### 5.2 页面清单

| 页面 | 访问者 | 主要目的 | 计划阶段 |
| --- | --- | --- | --- |
| Home | Public | 介绍社团、核心活动及主要入口 | Phase 2 |
| About | Public | 说明社团目标、活动形式和参与方式 | Phase 2 |
| Beginners & Safety | Public | 介绍新手参与方式和安全要求 | Phase 2 |
| Risk Notice | Public | 展示当前正式版本；预览环境可展示 draft 标记 | Phase 2 / 4 |
| Sign up | Visitor | 创建待验证账户 | Phase 1 |
| Verify email | Pending user | 输入或重发邮箱验证码 | Phase 1 |
| Log in | Visitor | Username/Password 登录 | Phase 1 |
| Log in by code | Visitor | Email Magic Code 登录 | Phase 1 |
| Account | Member | 管理邮箱状态、USYD 声明和 USU ID | Phase 1 |
| Edit profile | Member | 编辑并控制个人资料是否公开 | Phase 3 |
| Preview profile | Member | 查看本人资料的公开效果，不改变发布状态 | Phase 3 |
| Members | Public | 浏览已公开会员资料 | Phase 3 |
| Member detail | Public | 查看单个已公开资料 | Phase 3 |
| Events | Public | 浏览公开活动 | Phase 4 |
| Event detail | Public / Member | 查看活动；会员报名或取消 | Phase 4 |
| Django Admin | Staff | 审核、内容和运营管理 | Phase 1–4、6 |

## 六、关键用户流程

### 6.1 注册

```text
Visitor 打开 Sign up
        ↓
填写 Username、Email、Password
        ↓
再次输入 Password
        ↓
选择是否为 USYD student
        ↓
如选择 Yes，可选填写 USU ID
        ↓
提交并进入邮箱验证页面
        ↓
输入验证码
        ↓
验证成功，账户成为有效会员
```

要求：

- 注册信息在同一表单页面完成，不使用步骤条；
- 提交注册表单后进入独立的邮箱验证码页面；
- 条件字段在前端即时显示或隐藏；
- 后端执行相同规则，不能依赖前端隐藏；
- 密码错误、邮箱已使用、Username 已使用和验证码错误分别给出明确提示；
- 不通过登录或重置流程泄露任意邮箱是否存在；
- 验证码过期后允许在频率限制内重发。

### 6.2 密码登录

```text
输入 Username 和 Password
        ↓
认证成功
        ↓
返回原目标页面或 Account
```

错误信息不区分 Username 不存在和 Password 错误。

### 6.3 Email Magic Code 登录

```text
选择 Log in by email code
        ↓
输入 Email
        ↓
接收并输入一次性验证码
        ↓
认证成功
```

该方式是可选入口，不强制所有密码登录追加验证码。

### 6.4 USU ID 审核

```text
USYD Member 提交或修改 USU ID
        ↓
状态变为 Pending
        ↓
管理员在 Django Admin 核对
        ↓
Verified 或 Rejected
```

用户可以在 Account 页面查看自己的状态，但不能查看审核人或其他会员的信息。`rejected` 状态需要提供中性提示，首期不要求复杂的申诉工作流。

### 6.5 公开资料

```text
Member 编辑资料
        ↓
Save changes，不改变发布状态
        ↓
预览公开效果
        ↓
确认公开字段与 Username URL
        ↓
POST Publish
        ↓
资料出现在 Members 页面
```

会员通过独立 POST 操作 Unpublish，或管理员隐藏资料后，公开 URL 统一返回 404，不泄露资料是否曾存在。管理员隐藏优先于会员发布状态；会员不能通过重新 Publish 绕过隐藏。

### 6.5.1 Avatar 上传与删除

- 接受 JPG、PNG 和 WebP，最大 5 MB；
- 保留扩展名、声明 MIME 和真实图片内容三层验证；
- 验证成功后直接保存原文件，不处理 EXIF 方向、不移除 metadata、不缩放、不转换格式；
- 页面使用方形容器与 CSS 裁切展示，不修改保存文件；
- 替换或主动删除 Avatar 后清理旧文件；失败的更新不得提前删除当前有效文件；
- 上传字段显示：`Uploaded images are stored as provided and may contain location, device or other metadata. Remove sensitive metadata before uploading.`
- Development 与 Test 使用本地 media；Production persistent media storage 继续由 Phase 6 决定。

### 6.6 活动报名

```text
Member 打开 Event detail
        ↓
系统确认报名开放且无有效重复报名
        ↓
展示当前 Risk Notice 及确认框
        ↓
会员主动确认并提交
        ↓
系统以同一事务保存报名和确认记录
        ↓
页面显示 Registered
```

当 Risk Notice 在用户打开页面后被管理员更新，提交时必须以服务器当前版本重新校验；版本不一致时要求用户阅读并确认新版本。

### 6.7 取消与重新报名

```text
Registered Member 选择 Cancel registration
        ↓
确认取消
        ↓
原记录变为 Cancelled
        ↓
如报名仍开放，会员可以重新报名
        ↓
重新确认当前 Risk Notice 并建立新记录
```

## 七、页面与交互要求

### 7.1 全局布局

- 页面必须具有一致的 Header、主内容区和 Footer；
- 页面整体使用统一的深色视觉体系，以纯黑、炭灰和深灰表面建立层级，不使用大面积暖白内容区；
- 当前页面在导航中可识别；
- 登录状态和主要操作入口清晰；
- `Join the Club` 是全站最高优先级的招新操作；
- 重要操作使用明确动词，例如 `Register`、`Cancel registration`、`Publish profile`；
- 成功、警告和错误消息在视觉及语义上可区分；
- 手机端优先保证内容和表单可读性。

### 7.2 表单

- Sign up 使用单页纵向表单；Verify email 使用独立页面；
- 字段顺序为 `Username`、`Email`、`Password`、`Confirm password`、`Are you a USYD student?` 和条件显示的 `USU ID`；
- 每个输入项具有可见 Label；
- 必填与可选状态明确；
- 错误信息靠近对应字段；
- 服务端错误返回后保留非敏感输入；
- Password 不回显；
- 条件隐藏 USU ID 时同时清除前端值，并由后端拒绝绕过提交；
- 破坏性或撤销性操作需要确认步骤。

### 7.3 HTMX 交互

- HTMX 用于增强活动报名和取消；Events 的 Upcoming/Past 切换使用普通链接，Members 列表不使用筛选；
- 核心操作必须保留普通 HTTP POST 回退路径；
- 返回片段需要更新状态消息和焦点；
- 网络失败时显示可恢复提示；
- 不将权限判断放在 HTML 属性中。

### 7.4 Home

- Hero 以强视觉建立品牌识别，核心操作为 `Join the Club`；
- Hero 次级操作为 `New to Armwrestling?`；完整 Events 入口位于近期活动区的 `View all events`；
- Hero 另提供 `Join on USU` 外部链接，指向 USU 平台上的社团页面 `https://usu.edu.au/clubs/armwrestling/`。Anonymous 与已登录会员都显示该链接，顺序为 `Join the Club`（仅 Anonymous）、`Join on USU`、`New to Armwrestling?`；使用普通链接打开，禁用 JavaScript 时同样可用；
- `Join on USU` 只是指向 USU 页面的文字链接：网站不读取、提交或同步 USU 数据，也不据此改变网站会员身份或报名资格；链接不使用 USU 或 USYD 的 Logo、校徽或其他视觉资产，符合 9.6 的 Branding 限制；
- Hero 下方直接展示独立的 `New to Armwrestling?` 板块，说明无需经验、基本训练方式、安全原则和加入路径；板块标题区为等宽金色小标签加两行标题（第二行 `Join Us !` 使用金色质感文字），四张卡片带 `1px` 半透明金色边框、顶部金色渐变细线和装饰性等宽编号 `01–04`（对辅助技术隐藏）；
- 首页 `Upcoming Events` 区从数据库读取最多三条已发布的 Upcoming Event，与 Events 列表共用活动卡片；没有近期活动时显示 `No upcoming events are currently available.`；该区始终提供 `View all events` 入口；
- `Upcoming Events` 区不使用整块面板：标题区右侧放 `View all events` 次要按钮（窄屏换行至标题下方），活动卡片纵向排列；空状态为半透明金色虚线框内的等宽文字；
- Phase 2 的静态日程卡已被上述动态预览取代，首场 Training Session 由管理员在 Admin 录入；
- Hero 视觉采用"实验报告"方向（设计稿：Design canvas `NULDL Home hero concepts` 的 `D · Refined`）：
  - 页面背景为深黑底叠加极淡的金色坐标网格；
  - 左侧依次为 `Research Field` 金色标签与 Hero eyebrow、金色质感主标题、介绍文字和操作按钮；近期活动只在下方 `Upcoming Events` 区展示，Hero 不另设近期活动信息表，以免与该区第一张活动卡片重复；
  - 左栏采用单一栏宽（设计稿 `E · Aligned · three-line title`）：主标题固定三行 `Nonlinear` / `Upper Limb Dynamics` / `Laboratory`，桌面约 86px（`clamp(3rem, 6vw, 5.5rem)`），由第二行决定左栏宽度；标签与 eyebrow、介绍文字和按钮行全部对齐该栏宽，三个按钮等宽平分一行，按钮文字约 22px；
  - 左栏与 Logo 作为一组在 Hero 内居中，栏间距约 56px，Hero 内容最大宽度约 1360px；Logo 随剩余空间在 300–500px 之间伸缩；
  - 右侧展示完整透明背景 Logo（见 9.6）；
  - 页面底部以等宽字体显示图纸式标题栏（`Dwg no.`、`Scale`、`Est. 2026`）作为装饰；
- Hero 背景彩蛋：社团对抗照片拼贴（黑金调色、黑色底）铺满整个 Hero 的背景层，可被文字和 Logo 遮挡，不为其单独预留布局空间；平时仅显示极淡轮廓，指针经过 Hero 时以跟随指针的圆形光照局部显现照片；照片为装饰性内容，对辅助技术隐藏；
- 当视口变窄、Logo 移至标题下方时，背景彩蛋整体不渲染，窄屏和手机布局不受其影响；无指针悬停能力的设备同样不显示光照效果；
- 背景彩蛋参数：照片按比例覆盖整个 Hero（项目负责人在更换横版照片后决定，取代原先横向约 36%、底边对齐、高约 80% 的放置），超出部分主要裁去照片底部；常态透明度约 7%；照片四边渐隐融入页面底色；光照为半径约 200px 的柔边圆形，指针离开 Hero 后熄灭；光照只显现照片本身，不叠加受力标注、箭头、引线或文字标签（项目负责人在 V5 走查后决定删除原计划的受力标注）；
- Logo 带极轻微的金色外发光（半径约 40px、不透明度约 12%），仅用于让透明背景 Logo 与暗底分离，不属于大范围发光；

### 7.5 Events

- 完整 Events 页面使用信息卡片布局；
- 仅支持 Upcoming 和 Past 两个视图，默认显示 Upcoming，无效参数回退到 Upcoming；使用普通链接切换，禁用 JavaScript 时仍可用；
- 管理员可为活动填写可选的 Google Maps HTTPS URL，活动详情页有有效链接时显示 `View location in map`；
- 首场 Training Session 由管理员录入现有日程（2026 年 12 月 1 日，悉尼时间 3:00–7:00 pm）。地点未确认时显示 `Venue details to be confirmed`。Home 没有已公开的近期活动时显示空状态；
- 每张卡片突出日期、标题、时间、地点、报名状态和明确的详情或报名入口：左侧为金色细边框日期块（星期、日、月份与年份，与下方日期行重复，对辅助技术隐藏）；中间为标题链接和图纸式信息行（`Date`/`Time`/`Location`，起止不在同一天时为 `Starts`/`Ends`）；右侧为报名状态标签与 `View details` 次要按钮（可访问名称包含活动标题）。状态标签一律为不填充的细描边文字框（不使用材质底，避免被误认为按钮）：`Registration open` 为金色文字，`Registration unavailable` 与 `Past event` 为次要文字色，状态始终由文字表达；状态标签与 `View details` 等宽（窄屏时两者各占一半并等高）；`View details` 保持描边次要按钮，金色材质填充只留给 `Join the Club`、`Register` 等主要操作；窄屏时日期块与标题一行，信息行与状态、按钮各占整行；
- 在缺少高质量活动照片时，以排版、日期模块和抽象图形建立层级，不要求每场活动配置封面；
- 后续加入照片时，卡片结构应允许渐进扩展，不改变核心信息顺序。
- Events 列表页（项目负责人在 Visual Refresh 第二轮确认的 mockup）：页头为等宽金色小标签 `Club activities` 与大标题 `Events`；`Upcoming` / `Past` 以标签页呈现——一行等宽大写文字链接，下方一条半透明金色细线，当前项为金色文字加 `2px` 金色下划线（与 Header 导航当前页一致），其余为次要正文色；卡片沿用首页活动卡片，`Past` 中卡片的日期数字改用低优先级文字色；无结果时显示金色虚线框中的 `No events found.`；
- 活动详情页：
  - 页面顶部为等宽大写小链接 `← Back to events`（箭头为装饰），取代原先位于底部的 `Back to events` 按钮；
  - 页头为等宽金色小标签 `Club activity`、大标题（活动名称）及其旁边的状态标签（与列表卡片同一不填充样式）；
  - 宽屏为两栏：左栏为活动说明正文；右栏为带顶部金色渐变细线的信息面板，依次为图纸式信息行（`Date` 含星期、`Time`、`Location`，跨天时为 `Starts`/`Ends`）、有地图链接时的 `View location in map`，以及报名区；窄屏为单栏，信息面板位于说明之前；
  - 报名区按状态显示：Anonymous 且可报名时为 `Log in to register` 金色材质主按钮；会员可报名时为 `Register` 金色材质主按钮；已报名时为金色文字状态标签 `Registered` 加 `Cancel registration` 描边次要按钮（取代原先的警示色状态横幅）；不可报名与 Past 为次要文字色状态标签；面板内按钮与状态标签占满面板宽度；
  - 报名与取消确认 dialog 使用半透明金色细边框；标题上方为等宽金色小标签 `Risk Notice`；Risk Notice 正文放在暖黑底、半透明金色细边框的区域中，版本号以等宽小字 `Notice version` 呈现；按钮文案与顺序不变。禁用 JavaScript 时的完整确认页沿用同一正文与按钮样式。

### 7.6 活动地点

管理员在 Event 中填写可公开的地点文字，并可附上 Google Maps HTTPS 链接。活动详情页直接显示地点文字，有链接时提供 `View location in map`，使用普通链接打开 Google Maps。

### 7.7 Phase 2 英文内容基线

以下内容已经由项目负责人确认。实现时可以进行不改变含义的语法、标点和响应式断行调整；不得增加未经确认的地点、联系人、University affiliation、法律结论或活动承诺。

#### Home

- Metadata title：`NULDL Armwrestling Club | Training and Community`
- Metadata description：`Learn armwrestling technique, practise under supervision and join a welcoming strength-sport community. Beginners are welcome.`
- Hero eyebrow：`STUDYING CHAOTIC UPPER-LIMB INTERACTIONS SINCE 2026.`
- Hero heading：`Nonlinear Upper Limb Dynamics Laboratory`
- Hero introduction：`NULDL Armwrestling Club is an armwrestling community based near Sydney’s CBD, welcoming people of all experience levels. Learn the fundamentals, develop your technique and practise with purpose in a supervised environment.`
- Primary action：`Join the Club`
- External action：`Join on USU`，链接 `https://usu.edu.au/clubs/armwrestling/`，Anonymous 与 authenticated member 都显示
- Secondary action：`New to Armwrestling?`
- Hero tag：`Research Field`（位于 eyebrow 前的金色标签）
- 图纸标题栏：`Dwg no. NULDL-001`、`Scale 1:1`、`Est. 2026`，对辅助技术可读但不承载功能（原装饰文字 `Specimen 001 is kept in the dark. Bring a light.` 已由项目负责人删除）

`New to Armwrestling?`

`Join Us !`

- `Beginner Induction`：`Learn the basic rules, positions and safety principles before your first practice pull.`
- `Supervised Practice`：`Develop technique through structured practice using dedicated armwrestling equipment.`
- `Technique and Rules`：`Build a clearer understanding of movement, leverage, match rules and training methods.`
- `Community and Competition`：`Take part in social training sessions, workshops and internal competitions.`

`Upcoming Events`

- Eyebrow：`Club activities`
- 内容：由管理员在 Django Admin 录入并发布的 Event 动态生成，最多三张 Upcoming Event 卡片（见 7.4、7.5）；不在模板中写死活动日期、时间或地点
- Empty state：`No upcoming events are currently available.`
- Section action：`View all events`
- Authenticated member：不显示 Hero 的 `Join the Club`；`Join on USU` 外部链接仍然显示

#### About

- Metadata title：`About NULDL Armwrestling Club`
- Metadata description：`Learn about NULDL Armwrestling Club, our training activities and our approach to technique, safety and inclusive participation.`
- Heading：`About NULDL Armwrestling Club`
- Introduction：`Nonlinear Upper Limb Dynamics Laboratory is a student-led, community-focused armwrestling club.`

`Our Purpose`

`Our purpose is to make armwrestling more accessible as a strength-and-skill sport while building a welcoming community for participants from different backgrounds and experience levels.`

`We provide structured instruction, supervised practice and opportunities to learn about armwrestling technique, rules, training methods and risk-aware participation.`

`What We Do`

- `Beginner induction sessions`
- `Regular supervised practice pulls`
- `Technique and rules workshops`
- `Internal competitions`

`Who Can Participate?`

`The website is open to students and community enthusiasts. After creating an account and verifying their email address, users can access member features and participate in eligible activities.`

`Website access does not automatically provide voting rights or eligibility for an Executive position. Those rights are governed separately by the club’s constitutional requirements.`

`How We Train`

`Good armwrestling depends on technique, control and respect for your training partner. Sessions combine instruction with supervised practice so that participants can develop progressively.`

`Beginners are welcome, and competitive ambition is encouraged without creating unnecessary barriers for new participants.`

- Anonymous page action：`Join`
- Authenticated member：不显示页面招新按钮

#### Beginners & Safety

- Metadata title：`Beginners and Safety | NULDL Armwrestling Club`
- Metadata description：`Learn what to expect at your first NULDL Armwrestling Club session and review the essential safety principles for participation.`
- Heading：`Beginners Are Welcome`

`You do not need previous armwrestling experience to attend a beginner session. Your first session will introduce the basic rules, safe positioning, equipment and fundamental techniques before controlled practice begins.`

`What to Expect`

1. `Introductions to the session and equipment`
2. `Explanations of basic rules and positions`
3. `Technique demonstrations`
4. `Guided and supervised practice pulls`
5. `Time to ask questions and review your technique`

`Armwrestling Involves Risk`

`Armwrestling is a high-intensity competitive activity. Possible injuries include muscle strain, tendon or ligament injury, joint sprain or dislocation, and bone injury or fracture. Some risks cannot be completely predicted or avoided.`

`Before Participating`

`Do not participate if a medical condition or previous injury makes competitive physical activity unsuitable for you. Relevant concerns may include previous shoulder, elbow or wrist injuries, musculoskeletal conditions, cardiovascular or cerebrovascular disease, osteoporosis or neurological conditions.`

`If you are uncertain about your fitness to participate, do not take part until you have obtained appropriate advice.`

`During Training`

- `Follow the instructions of the session supervisor.`
- `Use the equipment only as directed.`
- `Train with control and respect your partner’s experience level.`
- `Do not force a movement through pain or loss of control.`
- `Stop immediately if you experience pain, numbness, dizziness or other discomfort.`

`Shared Responsibility`

`Safe training depends on clear communication, controlled practice and respect between participants. Ask for clarification whenever an instruction or position is unclear.`

- 不显示页面底部招新按钮组。
- Conditional Development/Preview action：`Read the Draft Risk Notice`，位于 `Armwrestling Involves Risk` panel 内并居中显示。

#### Risk Notice — Development/Preview only

- Metadata title：`Draft Risk Notice | NULDL Armwrestling Club`
- Robots directive：`noindex, nofollow`
- Draft banner：`DRAFT — NOT APPROVED FOR PARTICIPATION USE`
- Introductory notice：`This draft is displayed for development and review purposes only. It has not been approved as the final NULDL Armwrestling Club Risk Notice and must not be relied upon as the terms for participation.`

当前 Draft 正文：

> This public arm wrestling experience is a voluntary, high-intensity competitive activity. Arm wrestling involves inherent risks of injury, including but not limited to muscle strain, tendon or ligament injury, joint sprain or dislocation, bone injury and fracture. Some risks may not be fully foreseeable or avoidable.
>
> Before participating, please confirm that you do not have a condition that makes competitive physical activity unsuitable for you, including previous shoulder, elbow or wrist injuries or other musculoskeletal conditions, cardiovascular or cerebrovascular disease, osteoporosis, neurological conditions, or similar health concerns. If you are unsure about your fitness to participate, do not take part. Stop immediately if you experience pain, numbness, dizziness or other discomfort.
>
> By participating, you acknowledge and voluntarily accept the potential risks described above and confirm that you are choosing to participate based on your own physical condition. To the maximum extent permitted by law, the activity organiser, venue provider and relevant staff accept no liability for injury or loss arising from the inherent or obvious risks of the activity. Nothing in this notice excludes or limits any liability that cannot lawfully be excluded or limited. By participating, you acknowledge that you have read and understood this risk notice and voluntarily choose to take part.
>
> By participating, you acknowledge that you have read and understood this risk notice. If you are unsure about your health or the risks of the activity, do not participate.

实现时必须逐字使用上述正文，包括源文件中重复的 acknowledgement；在最终文本获批前不得擅自修订法律或责任限制措辞。Development 和 Preview 可以显示上述 banner 与正文；Production 必须禁用正文路由、从导航和 sitemap 排除该页面，并且不得提供报名功能。

#### Global Footer

- Social link text：`Follow NULDL Armwrestling Club on Instagram: @nuldl_armwrestlingclub`
- Social link target：`https://www.instagram.com/nuldl_armwrestlingclub/`
- Phase 2 不公开联系邮箱。

### 7.8 Phase 3 会员资料页面

- Account 页面保留 Account details、USYD and USU details 与 Security 三个主卡片；Account details 内展示本人 Profile 摘要、公开状态和 Edit、Preview、Publish/Unpublish 入口；
- Account 的 Profile 摘要说明 Username 始终属于公开 URL；其他可选资料只在提供时公开，不希望展示时应留空、选择 `Not specified` 或删除 Avatar；
- 会员资料编辑、Preview、Publish 和 Unpublish 使用独立命名 URL；编辑保存成功后返回 Account，Preview 提供返回 Account 的普通链接；
- 编辑表单包含 Display name、Avatar、Bio、Experience level、Preferred arm、Instagram Username 和一个 HTTPS social URL，不包含管理员字段或直接发布 checkbox；
- Preview 只允许当前 Profile 所有者访问，并使用与公开 detail 相同的字段顺序和视觉组件；
- Publish confirmation 明确列出将公开的字段，并说明 Username 会出现在公开 URL，Display name 为空时也会作为公开名称；
- 已发布会员可以 Unpublish；管理员隐藏时显示简单中性提示，不公开管理员身份或后台操作记录；
- Members 列表提供 cards、字母顺序和 empty state，不提供搜索或 HTMX 筛选；
- Members card 以左侧紧凑 Avatar 或非敏感 fallback、右侧公开名称及已填写的 Experience level 与 Preferred arm 构成；desktop/mobile 均不得因原图尺寸形成超大 Avatar；
- Member detail 显示公开名称、Avatar、Bio、已填写的 Experience level、Preferred arm、Instagram 和其他 HTTPS social link；
- Instagram 与其他 social link 使用安全外部链接属性；
- 未发布、管理员隐藏、账户停用或邮箱未验证的详情页统一返回 404；
- Header 在 Members 页面可用后增加 `Members` 公开导航；
- Members 列表进入 sitemap；个人 detail 不进入 sitemap，但不设置特殊 robots directive。

## 八、状态与异常处理

| 场景 | 用户结果 |
| --- | --- |
| 邮箱或 Username 已存在 | 显示可执行的通用提示，同时避免无必要的信息泄露 |
| 验证码错误 | 保留验证页面，显示剩余操作提示 |
| 验证码过期 | 提供受频率限制的重发入口 |
| 账户停用 | 拒绝登录并提供联系入口 |
| 报名已关闭 | 隐藏报名和取消按钮并显示 Closed |
| 活动已归入 Past | 保留活动信息，隐藏报名和取消按钮 |
| 重复提交报名 | 返回当前报名状态，不建立重复有效记录 |
| Risk Notice 已更新 | 要求重新阅读并确认当前版本 |
| 取消请求重复提交 | 保持 Cancelled 状态并返回幂等结果 |
| 资料未公开或被隐藏 | 公共页面返回不存在或不可用状态，不泄露原因 |
| 无公开会员或活动 | 显示明确 Empty state |
| 未提供地图链接 | 活动详情照常显示地点文字，省略地图入口 |

## 九、视觉、内容与 Branding 原则

### 9.1 品牌性格

- 整体感受以力量感、硬朗和竞技为核心；
- 视觉与内容比例约为竞技 `70%`、新手友好与社群氛围 `30%`；
- 竞技感不得通过贬低新手、过度威吓或制造参与门槛表达；
- 保持力量运动主题与清晰、克制的信息呈现；
- 避免制造 University 官方部门或正式研究实验室的误解。

### 9.2 色彩与表面

- 主配色为深黑、炭灰、暖白和金色；
- 深黑用于页面背景，炭灰和深灰用于卡片、表单及分层表面；
- 暖白主要用于正文和高优先级文字，不作为大面积页面背景；
- 金色承担品牌强调、主要操作、Focus 状态和少量结构装饰；
- 金色以"材质"而非单一色值表达：参考废案 Logo，以偏橙的饱和金（约 `#BF8933`）为主色，亮部约 `#F2BF5A`、暗部约 `#7E5015`，叠加细微锤纹材质贴图，避免大面积发白高光或条纹式渐变；
- 金色质感文字（Hero 主标题等展示标题）使用材质贴图裁切到文字，每行上亮下暗，并以顶部细亮边、底部暗边和柔和投影形成浮雕感；
- 主要按钮和金色标签使用同一金色材质，配合顶部内高光与底部内暗边；次要按钮使用金色渐变描边；材质承载小号深色文字时使用提亮暗部的材质贴图变体，使文字在每个像素上都达到 4.5:1；
- 链接、Focus、表单状态和其他高频小尺寸元素继续使用稳定的平面金色，保证可读性与对比度：链接与小号金色文字使用 `#E2B04A`（悬停 `#F3D58A`），Focus 指示使用更亮的 `#FFD166`；
- 不使用大范围发光、持续闪烁或降低文字对比度的金属效果；
- 表面与文字基准值（设计稿取值，实施时集中为 Tokens）：页面底色为暖黑 `#0A0908`，叠加 40px 间距、约 4.5% 不透明度的金色坐标网格线；主要文字 `#ECE4D3`，次要正文 `#C9C0AE`，表格标签和低优先级文字 `#9C9483`；金色细边框使用约 30% 不透明度的 `#E2B04A`；
- Header 使用半透明暖黑底，下边缘为一条两端渐隐、中间提亮的金色渐变细线（暗金 → 亮金 → 暗金），与 Logo 下方分隔线呼应；该分隔线样式也可用于页面内的区块分隔；
- 所有具体 Design Tokens 集中管理，并在实现阶段通过 WCAG 2.2 AA 对比度验证。

### 9.3 字体与排版

- 展示标题使用 `Barlow Condensed`，建议字重为 `600–800`；
- Hero 主标题以 `800` 为基准，桌面端可从约 `64px` 起建立响应式字号；
- 正文、导航、表单和其他界面文字使用 `Inter`，字重范围为 `400–600`；
- 活动日期、时间和状态可使用 `Barlow Condensed 600–700` 强化竞技节奏；
- 正文不得使用压缩字体，长段内容以可读性优先；
- 等宽字体 `JetBrains Mono`（`400–500`）用于"实验报告"语气的小号元素：Hero 标签与 eyebrow、活动卡片的信息行和图纸标题栏；统一大写，字号约 `11–12px`，字距约 `0.08–0.14em`；不用于正文、导航或按钮；
- Home Hero 主标题桌面约 `86px`，行高约 `0.92`；Hero 按钮文字约 `22px`（Inter，主按钮 `600`、次要按钮 `500`）；
- 字号、行高和间距通过 Design Tokens 统一管理。

### 9.4 组件外观

- 卡片采用约 `4–8px` 小圆角；
- 按钮、状态标签和局部边框可以使用克制的切角细节：主按钮与次要按钮均切去左上角和右下角，Hero 按钮约 `10px`，Header 按钮约 `8px`；
- 导航当前页使用金色文字加 `2px` 金色下划线；其他导航项为次要正文色；
- 次要按钮为 `1px` 金色渐变描边包裹暖黑内芯，悬停时内芯变为深金褐色；
- 图纸标题栏使用 `1px` 半透明金色边框、等宽字体，标签列为低优先级文字色、数值列为主要文字色；活动卡片的日期、时间与地点信息行沿用同一风格（V6 已实施，见 7.5）；
- 主要按钮为金色材质填充配近黑文字，悬停时一次性扫过高光（不循环，遵守 `prefers-reduced-motion`）；
- 次要按钮使用金色描边，低优先级操作使用文字链接或中性样式；
- Hover 和 Pressed 状态以短促的亮度、边框或轻微位移反馈表达，不使用大范围发光；
- 表单以清晰易用为主，不为追求竞技外观牺牲 Label、错误提示和 Focus 状态；
- 成功、警告、错误和关闭状态必须同时使用文字或图标，不能只依赖颜色。

### 9.5 动效

- 使用克制动态，包括内容进入、按钮反馈，以及 Home Hero 由指针驱动的背景光照彩蛋（不自动运动）；
- 动效应短促且服务于层级或状态变化；
- 不使用持续运动背景、持续闪烁或影响阅读的视差效果；
- 所有非必要动效尊重 `prefers-reduced-motion`。

### 9.6 Logo 与图像资产

- 主视觉 Logo 源文件为仓库内的 `static_src/images/brand/nuldl-club-logo-transparent.png`。它由项目负责人在 Phase 4 期间确认，替换了 Phase 2 使用的黑底版本 `Logo_without_USYD.png`；旧文件已从仓库删除，可从 Git 历史恢复；
- 源文件为 1254 × 1254 透明背景的方形完整组合图，适合 Home Hero 或较大的品牌展示区域；
- Header 使用文字 `NULDL Armwrestling Club`，不在小尺寸导航中缩放完整 Logo；
- 实现阶段从源文件生成保留透明度的响应式压缩网页版本，不改变图形内容，并保留原始源文件；
- 未获得书面批准前，不使用 USYD 名称、Logo、校徽或视觉规范；
- 首期以黑金抽象图形、线条、波形和简单静态结构作为主要视觉素材；
- 肌肉、骨骼、关节轴线和受力轨迹等复杂插画在基础框架与功能稳定后统一设计；
- 不直接复制网上的知名选手、比赛或媒体照片；
- 第三方图片必须具有适用于网站宣传用途的明确许可，并保存授权记录；
- 社团自行拍摄的成员照片应在公开使用前取得适当同意；Home Hero 背景彩蛋当前使用由项目负责人提供的社团对抗照片拼贴，画面包含多名成员，按本条在公开上线前需取得其适当同意；照片正式版本后续统一处理；
- 后续活动照片应逐步补充，且不得成为活动信息可用性的前置条件。

### 9.7 内容原则

- 首期所有面向用户的正式内容使用英文；
- 对外使用缩写时必须完整写作 `NULDL Armwrestling Club`；不得单独使用 `NULDL`，Instagram Username 等外部标识除外；
- 技术错误不得直接暴露给用户；
- 安全内容采用清晰、直接和非营销化表达；
- Risk Notice draft 必须在非正式环境中明确标记；
- 正式环境只展示已经确认的 Risk Notice；
- 地点、联系人和活动信息必须来自管理员确认的数据。

## 十、Accessibility 与响应式要求

项目以 WCAG 2.2 AA 作为设计和测试目标。

- 所有功能支持键盘操作；
- 使用语义化 HTML 和正确的 Heading 层级；
- Form error、status message 和 dialog 具有适当的可访问语义；
- Focus 状态清晰可见；
- 不仅依赖颜色表达状态；
- 触控目标具有足够尺寸和间距；
- 内容在窄屏、放大和文字换行时保持可读；
- 动效尊重 `prefers-reduced-motion`；
- 活动地点文字始终可读，地图外链可用键盘操作。

## 十一、隐私与数据展示边界

### 11.1 允许公开

- 网站标题和公开内容；
- 公开活动信息；
- 已确认的地点信息；
- 会员主动发布的 Avatar、公开名称、Bio、Experience level、Preferred arm、Instagram Username 和一个 HTTPS social URL；
- Published Profile 的 Username detail URL，以及 Display name 为空时的 Username 回退名称；
- 已发布 Avatar 原文件中保留的 metadata；上传界面必须提前提示其中可能包含位置、设备或其他信息。

### 11.2 仅本人和获授权管理员可见

- Email；
- USYD 学生声明；
- USU ID 及审核状态；
- 未公开的 MemberProfile；
- 本人在活动详情页的当前报名状态。

### 11.3 仅获授权管理员可见

- 活动参与名单、报名历史及 Risk Notice 确认记录；
- USU 审核人和审核时间；
- 账户停用及后台操作信息。

首期不收集医疗信息、出生日期、监护人资料或紧急联系人。

## 十二、首期排除项

- 中文页面；
- 在线支付；
- 自动同步 USU 平台；
- 活动容量、候补名单和报名截止时间；
- 排名、Elo 或比赛管理不进入首期上线范围；训练动作排行榜计划在上线后的 Phase 7 单独设计；
- SMS 通知；
- Executive 角色公开展示；
- 资料发布前的管理员审批；
- 自动证明 USYD 或 USU 身份；
- 完整的会员退出、账户删除和数据保留流程。

## 十三、待确认事项

1. Risk Notice 最终文本及 USU 确认结果；
2. University Branding 的书面批准范围；
3. 复杂人体结构、受力轨迹插画的最终范围和制作时间；
4. 各场活动可公开的地点名称或地址，由管理员在确认后录入；
5. 会员退出、账户删除和数据保留规则；
6. 中文版本的时间和范围；
7. Phase 7 排行榜的训练动作、成绩单位、左右手区分、审核方式、并列规则和公开范围。

待确认事项不得由开发者自行补全。任何决定都应先更新本文档，再进入技术和实施文件。
