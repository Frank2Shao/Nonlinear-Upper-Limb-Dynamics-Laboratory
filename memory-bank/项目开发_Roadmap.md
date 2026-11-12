# NULDL 网站开发 Roadmap

**项目名称：** Nonlinear Upper Limb Dynamics Laboratory Website  
**候选域名：** `nuldl.com`  
**文档职责：** 定义交付阶段、依赖、里程碑、退出门槛和项目状态  
**当前阶段：** Phase 1、Phase 2 与 Phase 3 已完成；Phase 4 尚未开始
**最后更新：** 2026 年 11 月 12 日

## 一、文档体系

本项目使用六份文档管理需求、实施和已完成状态：

| 文档 | 唯一职责 | 权威内容 |
| --- | --- | --- |
| [design_document.md](design_document.md) | 产品与体验设计 | 用户、页面、流程、业务规则、权限、内容、accessibility 和 Branding |
| [tech_stack.md](tech_stack.md) | 技术决策 | 技术选型、版本、架构、环境、安全、部署和运维边界 |
| [implementation.md](implementation.md) | 代码实施方案 | Apps、模型、约束、URL、配置、测试、migration 和执行顺序 |
| [项目开发_Roadmap.md](项目开发_Roadmap.md) | 阶段与进度 | 依赖、交付物、退出门槛、状态和外部阻塞事项 |
| [architecture.md](architecture.md) | 已实施架构 | 已经落地并通过验证的结构、边界和理由 |
| [progress.md](progress.md) | 执行记录 | 各步骤实际修改、验证结果、修补和下一步门槛 |

内容发生冲突时，先按职责确定权威文件，再修改引用该决定的下游文档。Roadmap 不重复维护字段级模型或配置项。

## 二、项目交付目标

项目按照以下顺序形成完整首期版本：

1. 建立技术基础、会员注册和账户管理；
2. 完成英文宣传网站；
3. 增加可选的公开会员资料；
4. 增加会员活动报名和 Risk Notice 确认；
5. 增加地点信息和地图；
6. 完成正式环境、安全、运维及外部审批；
7. 正式上线后再扩展训练成绩与排行榜。

首期结束时，NULDL Armwrestling Club 网站应具备公开信息展示、会员注册、USU ID 人工审核、公开资料、活动报名、报名取消、Risk Notice 版本追溯和地点地图功能。

## 三、状态定义

| 状态 | 含义 |
| --- | --- |
| `Not started` | 尚未开始实施 |
| `In progress` | 已开始，退出门槛尚未全部满足 |
| `Blocked` | 存在明确外部依赖，无法继续完成当前阶段 |
| `Ready for review` | 开发和内部验证完成，等待阶段验收 |
| `Complete` | 退出门槛全部通过并记录验收结果 |

阶段状态只能依据退出门槛更新，不能仅凭代码已经编写而标记完成。

## 四、阶段总览

| Phase | 名称 | 主要依赖 | 当前状态 |
| --- | --- | --- | --- |
| 1 | 项目基础、账户与 USU ID 审核 | 已确认的 Design 与 Tech Stack | `Complete` |
| 2 | 英文宣传网站 | Phase 1 页面框架 | `Complete` |
| 3 | 会员资料管理 | Phase 1 有效会员与权限 | `Complete` |
| 4 | 活动、报名与 Risk Notice | Phase 1 认证；Risk Notice 上线前确认 | `Not started` |
| 5 | 地点与地图 | 已确认地点；Phase 2 页面系统 | `Not started` |
| 6 | 正式环境准备与上线 | Phase 1-5；Provider 与外部审批 | `Not started` |
| 7 | Training Records & Leaderboards | Phase 6 已上线；动作与成绩规则已确认 | `Not started` |

## 五、Phase 1：项目基础、账户与 USU ID 审核

### 目标

建立可运行、可测试的 Django 项目基础，完成注册、邮箱验证、两种登录方式、账户管理及管理员 USU ID 审核闭环。

### 主要交付物

- 可重复建立的本地开发环境；
- Django 项目、分层 settings 和 PostgreSQL；
- 第一次 migration 中的自定义 User；
- 注册和强制邮箱验证码验证；
- Username/Password 登录；
- 可选 Email Magic Code 登录；
- Account 页面和 USYD 条件字段；
- Django Admin USU ID 审核；
- 默认隐藏的 MemberProfile；
- 英文响应式基础页面框架；
- Phase 1 自动化测试和开发文档。

### 退出门槛

- 空 PostgreSQL 数据库可以完整执行 migrations；
- 注册、邮箱验证、密码登录、Magic Code 登录和登出均通过测试；
- 非 USYD 用户不能提交 USU ID；
- 会员不能自行修改 USU 审核结果；
- 管理员审核会记录状态、审核人和时间；
- 新会员资料默认不公开；
- 公开响应不泄露 Email、USU ID 或未公开资料；
- CSS production build、Django system checks、lint 和测试全部通过；
- README 可以指导新开发环境启动；
- 仓库不包含 Secret、`.env`、真实会员数据或用户上传文件。

### 阶段状态

`Complete`

## 六、Phase 2：英文宣传网站

### 目标

使用中性的 `NULDL Armwrestling Club` Branding 完成首期英文公开信息页面。

### 主要交付物

- Home；
- About；
- Beginners & Safety；
- Risk Notice 页面；
- Header、Footer 和公开导航；
- 已确认的新 Logo Hero 展示和文字 Header 品牌；
- `1 December 2026, 3:00–7:00 pm` 静态训练日程；
- Instagram `@nuldl_armwrestlingclub`；
- 403、404 和 500 页面；
- 基础 metadata、sitemap 和 accessibility 支持。

### 依赖

- Phase 1 基础模板和静态文件流程；
- 已确认并记录在 `design_document.md` 的英文页面内容；
- 已确认的 `Logo_without_USYD.png` 源文件；
- Risk Notice 当前为 draft，Development 和 Preview 使用明确 draft 标记，Production 禁用正文；
- 不使用未经批准的 USYD Branding。

### 退出门槛

- 所有计划页面具有完整英文内容；
- 桌面、手机、键盘和内容放大场景可用；
- 导航不存在指向未完成功能的失效入口；
- 对外缩写统一写作 `NULDL Armwrestling Club`；
- Home 准确展示日期、时间和未确认地点状态，且不提前提供活动报名；
- Preview 中的临时 Risk Notice 具有清晰 draft 标记；
- Production 不公开未经确认的 Risk Notice 或 University Branding；
- Footer 只公开已确认的 Instagram，不公开联系邮箱；
- 页面测试、accessibility 检查和浏览器 smoke test 通过。

### 阶段状态

`Complete`

验收结果：Step 21–28 已完成并通过项目负责人验证；Home、About、Beginners & Safety、公开导航、响应式与 accessibility、Draft Risk Notice 环境隔离、共享视觉的 403、404、500 页面、准确 Metadata/Open Graph、公开 sitemap、已批准 Instagram Footer、共享项目质量门禁及全新环境端到端验收均已落地。项目负责人已完成最终人工走查并确认 Phase 2 验收通过。Risk Notice 最终文本、University Branding、地点详情、Production 域名与 Provider、数据保留规则及中文版本继续按外部依赖或后续阶段管理。

## 七、Phase 3：会员资料管理

### 目标

允许会员维护资料并主动决定是否公开，同时保证私有账户信息不会进入公开页面。

### 主要交付物

- Profile edit 和 preview；
- 原文件 Avatar 上传、删除、替换和旧文件清理；
- 独立 Publish confirmation 和 unpublish；
- Members 列表；
- `/members/<username>/` Member detail；
- 管理员在 Django Admin 使用标准 change 权限 hide 和 unhide；
- Profile 页面响应式、Accessibility、隐私与媒体测试。

### 依赖

- Phase 1 User、MemberProfile 和权限体系；
- Phase 2 公开页面、导航和共享质量门禁；
- Avatar 的 Development/Test 本地存储；
- 视觉方向可以继续使用基础 Design Tokens，不阻塞功能开发。

### 退出门槛

- 资料默认隐藏；
- 会员只能修改本人资料；
- 保存资料不改变发布状态，Preview、Publish 与 Unpublish 相互分离；
- 管理员可以隐藏资料而不影响账户；
- 公开 queryset 只返回主动公开且未被管理员隐藏的有效会员；
- Members 列表无筛选并具有稳定排序与 empty state；
- Member detail 使用 Username URL、普通公开 robots 规则，且不进入 sitemap；
- Email、USU ID、审核状态和未公开字段不出现在公共响应；
- Avatar 保留原文件并通过扩展名、MIME、真实内容和 5 MB 验证；替换或删除后旧文件得到清理；
- 上传界面明确提示原文件 metadata 可能公开；
- 所有已验证会员使用相同流程，不增加年龄字段或判断；
- Admin 只允许维护隐藏状态和 Executive role，不修改会员自述；
- Avatar、对象所有权、权限、公开边界、Accessibility 和浏览器测试通过；
- 首期不展示 Executive 角色。

### 阶段状态

`Complete`

Phase 3 不包含训练成绩或排行榜；该功能已登记为首期上线后的 Phase 7。

验收结果：Step 29–36 已完成并通过项目负责人验证；本人 Profile 编辑、Avatar 原文件验证与生命周期、Preview、独立 Publish/Unpublish、公开 Members 目录与 Username detail、统一 404、Admin hide/unhide、Account Profile 摘要与状态操作、响应式与 Accessibility、公开隐私扫描、共享项目门禁及全新环境端到端验收均已落地。最终全新环境执行 `313` 个测试并达到 `95%` branch coverage，Production deploy check、collectstatic、desktop/mobile smoke 与人工走查全部通过。Phase 3 没有新增 migration、年龄逻辑、目录筛选、专用隐藏权限、排行榜或 Production media provider。

## 八、Phase 4：活动、报名与 Risk Notice

### 目标

建立仅限会员使用、可追溯每次 Risk Notice 确认记录的活动报名系统。

### 主要交付物

- Event 和 RiskNoticeVersion 后台管理；
- Events 列表和 Event detail；
- 管理员手动开启或关闭报名；
- 会员报名和取消；
- My registrations；
- Risk Notice 版本和确认时间记录；
- 管理员报名名单。

### 依赖

- Phase 1 有效会员和权限；
- Phase 2 Safety 内容结构；
- 正式启用报名前完成 Risk Notice 文本确认。

### 退出门槛

- Visitor 可以查看公开活动，但不能报名；
- 报名关闭时不能建立有效报名；
- 同一会员和活动最多存在一条有效报名；
- 每次报名必须确认服务器当前 Risk Notice 版本；
- Risk Notice 更新后，过期页面提交会要求重新确认；
- 取消为幂等操作并保留历史记录；
- 取消后重新报名会建立新的确认记录；
- 管理员名单、权限、并发和事务测试通过；
- 不包含容量、候补名单、报名截止时间或付款功能。

### 阶段状态

`Not started`

## 九、Phase 5：地点与地图

### 目标

展示已确认的训练地点，并将地点与活动关联。

### 主要交付物

- Location 后台管理；
- Locations 页面；
- 地点文字卡片；
- MapLibre 地图；
- Marker、Popup 和活动卡片联动；
- 无 JavaScript 和地图加载失败时的文本回退。

### 依赖

- 确认后的地点名称、地址、坐标和联系人；
- 确定 Map tile provider 及 attribution 要求；
- Phase 2 页面系统；
- Phase 4 Event 与 Location 关系。

### 退出门槛

- 每个公开 Marker 对应已确认的 Location；
- 坐标缺失时不生成虚假 Marker；
- 地点信息在地图不可用时仍可阅读；
- 桌面、手机触控和键盘操作通过测试；
- Map provider attribution 正确展示；
- Location 与 Event 关联测试通过。

### 阶段状态

`Not started`

## 十、Phase 6：正式环境准备与上线

### 目标

完成安全、运维、Provider、外部审批和生产验收，使网站能够稳定公开运行。

### 主要交付物

- Production image 和部署配置；
- 托管 PostgreSQL；
- SMTP；
- Persistent media storage；
- HTTPS 和 `nuldl.com` 域名配置；
- 日志、health check 和 error monitoring；
- Database 和 media backups；
- 恢复和回滚文档；
- 管理员操作文档；
- 正式 Risk Notice；
- Branding 审核记录。

### 外部依赖

- Hosting provider；
- SMTP provider；
- Media storage；
- Error monitoring provider；
- Map tile provider；
- Risk Notice 确认；
- University Branding 书面批准范围；
- `nuldl.com` 注册和 DNS 控制权。

### 退出门槛

- `DEBUG = False`，Secret 和 hosts 配置正确；
- HTTPS、secure cookies、CSRF 和 security headers 验证通过；
- `manage.py check --deploy` 通过或每项例外均有记录；
- 全部 migrations、测试、CSS build 和 smoke tests 通过；
- Production 不包含未经批准的 Branding；
- Production 使用确认后的 Risk Notice；
- 匿名访问不能读取会员私有信息或报名名单；
- Email、备份、恢复、监控和回滚完成实际验证；
- 部署可以依据仓库和文档重复执行。

### 阶段状态

`Not started`

## 十一、Phase 7：Training Records & Leaderboards

### 定位

首期正式上线后的增强阶段。该功能依赖 Phase 3 的会员公开身份，并在 Phase 6 完成后单独规划，不影响当前首期交付。

### 计划范围

- 训练动作定义；
- 会员训练成绩记录；
- 不同动作的公开排行榜；
- 成绩提交、审核与修订；
- 并列、排序和历史记录；
- 公开隐私与 Member Profile 关联。

### 开始前必须确认

- 具体训练动作；
- 每个动作的成绩单位与有效精度；
- 是否区分左手和右手；
- 成绩由会员自报、现场录入或管理员审核；
- 是否需要证明材料；
- 并列规则、无效成绩和修改历史；
- 是否存在体重、性别或其他分类；
- 未公开 MemberProfile 在排行榜中的显示方式。

### 阶段状态

`Not started`

## 十二、跨阶段质量门槛

每个 Phase 在进入 `Ready for review` 前必须满足：

- 实现范围与 `design_document.md` 一致；
- 技术方案与 `tech_stack.md` 一致；
- 对应测试、lint 和 system checks 通过；
- 权限和敏感数据边界得到验证；
- 用户页面使用英文；
- 手机端和键盘核心流程可用；
- 文档、环境示例和 migration 同步；
- 未将后续 Phase 或排除项混入当前范围；
- 新产生的外部依赖已记录。

## 十三、当前外部确认事项

| 事项 | 最晚需要时间 | 当前影响 |
| --- | --- | --- |
| Risk Notice 最终文本 | Phase 4 正式启用报名前 | Phase 2 仅允许非正式环境展示 draft；Production 禁用正文；限制正式报名 |
| University Branding 批准 | 任何相关内容公开前 | 使用中性 `NULDL Armwrestling Club` Branding，不公开 USYD affiliation |
| 地点地址和坐标 | Phase 5 开始前 | Phase 2 日程显示 `Venue details to be confirmed`；不阻塞其他公开内容 |
| Hosting 与相关 Provider | Phase 6 开始前 | 不阻塞本地开发 |
| 会员退出和数据保留规则 | 对外提供删除流程前 | 首期不实现退出工作流 |
| 中文版本 | 首期完成后再决定 | 不进入首期范围 |

## 十四、项目状态更新规则

每次阶段状态变化时更新：

1. 当前 Phase 状态；
2. 已完成的主要交付物；
3. 尚未通过的退出门槛；
4. 新的外部依赖或阻塞；
5. 对其他项目文档产生的变更。

Roadmap 不记录逐个代码文件的完成情况。具体开发任务、测试和实现顺序维护在 `implementation.md` 或项目任务系统中。

## 十五、变更控制

- 新的用户行为或业务规则先修改 `design_document.md`；
- 新的框架、服务或基础设施选择先修改 `tech_stack.md`；
- 新的模型、约束、URL 或测试方案修改 `implementation.md`；
- 阶段、依赖、交付物或进度变化修改本 Roadmap；
- 涉及范围扩大的决定需要先确认，再更新文件；
- 修改一份文件时检查其他项目文档是否需要同步引用，但不复制完整内容。

## 十六、项目资料

本 Roadmap 的需求来源仅包括：

- 本项目已经确认的对话需求；
- `design_document.md`；
- `tech_stack.md`；
- `implementation.md`；
- `Nonlinear Upper Limb Dynamics Laboratory constitution.pdf`；
- `3_ClubSociety_Agreement_Armwrestling_NULDL.pdf`；
- `Armwrestling_Risk_Notice_EN.pdf`；
- `Armwrestling_Risk_Notice_CN.pdf`；
- `Logo_without_USYD.png`。

当前没有其他未提供的原始构思文件。
