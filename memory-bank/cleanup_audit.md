# NULDL 代码清理审计

**审计日期：** 2026-11-17
**审计基线：** `main` @ `38a9d8c`，另含工作区未提交的 Phase 4 改动（`git status` 所示）
**范围：** `apps/`、`config/`、`templates/`、`static_src/`、`scripts/`、`tests/`；补充检查 `package.json`、`.env.example`、`static/` 中受版本控制的生成物
**排除：** `.venv/`、`node_modules/`、`staticfiles/`、全部 migrations
**性质：** 只列清单；除附注 N3b 经项目负责人确认后删除的一句误拷贝文案外，未修改任何代码。每条给出位置、问题、建议、风险（低/中/高）和受影响测试。
**注意：** 行号对应审计时的工作区；执行前应重新定位。按 `AGENTS.md`，涉及架构结论的条目（如删除 `locations`、MapLibre）执行后需经项目负责人批准再更新 `architecture.md`。

## 一、Python / Django

| ID | 位置 | 问题 | 建议改法 | 风险 | 受影响测试 |
| --- | --- | --- | --- | --- | --- |
| A1 | `config/settings/base.py:34`；`apps/locations/__init__.py`、`apps.py`、`migrations/__init__.py` | **死代码**：`locations` App 只有骨架，原 Phase 5 已取消，没有 Model、URL、模板或 migration。 | 从 `PROJECT_APPS` 移除并删除目录。因为它没有 migration，所以不涉及数据库变更。 | 低 | `tests/test_project_scaffold.py:10`（`EXPECTED_APP_CONFIGS`）；`architecture.md` 中“六个 App”的描述 |
| A2 | `package.json:22`；`scripts/build-static-assets.mjs:16-23,49-52,71`；`static/vendor/maplibre/*`（约 1.1 MB `.mjs` + 70 KB `.css`）；`static/vendor/licenses/maplibre-gl.txt`；`static/vendor/manifest.json` | **死资产**：页面从不加载 MapLibre，详情页只使用 Google Maps 外链；这些依赖和资产却仍被构建、校验和提交。 | 删除依赖，重建 `package-lock.json` 和 manifest，然后删除 vendor 文件与 license。 | 低 | `tests/test_static_assets.py:38-44`（manifest packages 精确列表）；`tech_stack.md` 与 `architecture.md` 2.2/3.16 需同步 |
| A3 | `apps/accounts/forms.py:55-96` 与 `117-157` | **重复**：`AccountIdentityForm` 与 `SignupForm` 都定义了相同的两个字段、Alpine widget attrs、`clean_usu_id` 和 `clean()`。`SignupForm.save` 在 `update_usu_identity` 已返回最新对象后，又执行一次 `refresh_from_db`（`166-174`）。 | 抽出 `UsuIdentityFieldsMixin`，承载字段、attrs 和两个 clean。`save` 直接使用 service 返回值覆盖字段，从而减少一次查询。 | 低 | `test_signup_form.py`、`test_account_page.py`、`test_authentication_templates.py` |
| A4 | `accounts/models.py:105-108`、`services.py:15-22`、`forms.py:79-89,147-157` | **同一规则重复 4 处**：文案 “USU ID is only available to USYD students.” 硬编码了 4 次，规范化与数字校验在 form、service 和 `model.save`（`110-115`）中各执行一次。按文档要求，model、service 和 DB 三层防线需要保留，但三处应用层副本可以共享同一实现。 | 在 `accounts/models.py` 提供单一的 `validate_usu_identity(is_usyd, usu_id)` 和消息常量，供 `model.clean`、service 和 form 共同调用；同时保留 service 行锁和 DB `CheckConstraint`。 | 低 | `test_user_identity_rules.py`、`test_signup_form.py`、`test_account_page.py`（文案保持不变即可） |
| A5 | `apps/accounts/admin.py:1,149` | **无意义间接**：`review: Callable[..., User] = review_usu_id` 只是别名，测试中也没有 patch 这个别名。 | 直接调用 `review_usu_id`，并删除 `Callable` import。 | 低 | `test_user_admin.py` |
| A6 | `accounts/admin.py:84-88` | `has_add/delete_permission` 中的 `request.user.is_active` 重复了 AdminSite 已有的 active staff 检查。 | 只保留 `is_superuser`。 | 低 | `test_user_admin.py` |
| A7 | `accounts/views.py:23-27`、`members/views.py:50-58`、`events/views.py:16-21`、`events/services.py:25-29,64-68`、`members/models.py:87-98` | **“有效会员”规则重复 6 处**：启用账户 + 已验证 Email 的判断被分别手写。service 在锁内复核是文档要求的防线，应保留调用，但实现应当统一。 | 新增 `apps/accounts/selectors.py::is_verified_active_member(user)`，让 view 和 service 共用。queryset 中的 `Exists` 可共用同一个 `verified_email_subquery()`。 | 低 | `test_profile_edit.py`、`test_profile_publication.py`、`test_event_registration*.py`、`test_account_page.py` |
| A8 | `apps/events/services.py:15-51` 与 `54-90` | **重复前置流程**：`register_for_event` 与 `cancel_event_registration` 中的环境开关、认证、锁 Event、锁 User、资格判断和活动开放判断几乎逐行相同。 | 抽出 `_lock_member_and_open_event(user, event_id, *, closed_message)`，并且**必须保持 Event → User → RiskNoticeVersion 的加锁顺序**。 | 中 | `test_event_registration.py`（并发报名/取消/版本切换）、`test_event_registration_pages.py` |
| A9 | `events/views.py:47-54,129,189-194`；`events/templates/events/includes/event_card.html:7`；`registration_panel.html:26` | **开放规则在 UI 层重复 3 处且写法不一**：context、view 前置检查和卡片模板各自拼接 `registration_open`、`is_upcoming`、`notice`、`DRAFT` 开关。`registration_panel.html:26` 的 `registration_available and can_register` 中，`can_register` 已经包含 `registration_available`。 | 在 Event 上提供 `registration_is_available(notice)` 和 `cancellation_is_available()`，供 view、context 和卡片共用，同时删除模板中的冗余条件。service 内的锁内复核保留，这是文档要求的防线。 | 低 | `test_event_pages.py`、`test_event_registration_pages.py`、`event-pages.mjs` |
| A10 | `events/views.py:63-68,118,128,151` | **重复查询**（非 N+1）：一次请求中 `_is_verified_member` 执行 2 次 EXISTS，`current_risk_notice()` 执行 2–3 次，`_active_registration` 在 `event_register` 与 context 中各执行一次。 | 在 view 中计算一次，再传入 `_registration_context`。可以补充 `django_assert_num_queries` 回归。 | 低 | `test_event_registration_pages.py` |
| A11 | `events/views.py:120,157,173,214,230` | **硬编码重复**：`request.headers.get("HX-Request") == "true"` 出现 5 次，`"events/includes/registration_panel.html"` 也出现 5 次。register 与 cancel 末尾的“HTMX 渲染片段或 redirect/400 页面”分支结构相同。 | 抽出 `_is_htmx(request)` 与 `_respond(request, event, page_template, context, status)`。 | 低 | `test_event_registration_pages.py`（HTMX 分支） |
| A12 | `events/models.py:17-22` 与 `members/models.py:79-82`；`events/models.py:94-95` 与 `members/models.py:206-211` | **重复校验器**：两份 `validate_https_url` 和两份 HTTPS scheme 小写化逻辑并存。`URLValidator(schemes=["https"])` 已经会拒绝非 https，因此随后的 `startswith("https://")` 分支不可达。 | 移到 `apps/core/validators.py`，统一为“先判断 scheme 并给出 ‘Use an HTTPS URL.’，再执行 URLValidator”。DB 约束保留。 | 低 | `test_member_profile.py`、`test_profile_edit.py`、`test_event_model_admin.py` |
| A13 | `apps/events/models.py:75-80` | **重复校验**：title、description、venue 的空值检查与字段的 `blank=False` 重复；`save()` 已先 normalize 再执行 `full_clean`，所以 `clean_fields` 会先报错。测试没有断言这三条文案。 | 删除这三条检查，保留 `ends_at` 检查（model + DB 双层防线是文档要求）。 | 低 | `test_event_model_admin.py` |
| A14 | `events/models.py:29-37,97-102` | `upcoming()` 与 `past()` 重复计算 Sydney 当地零点。 | 抽出 `_sydney_midnight_today()`。 | 低 | `test_event_pages.py`、`test_event_model_admin.py:98` |
| A15 | `members/models.py:197-200`、`events/models.py:84-87`、`members/services.py:54` | **双重完整校验**：ModelForm 的 `_post_clean` 已执行 `full_clean`，`save()` 又执行一次，导致 Avatar 被 Pillow 再解码一次。`validate_avatar` 中 reopen/close 的 Windows 补丁（`members/models.py:39-53`）正是为此存在。`set_profile_publication` 只翻转一个布尔值，也会触发完整校验和 Avatar 解码。 | `save()` 只保留 normalize，由 form、Admin 和 DB 约束负责校验；或者在 `update_fields` 不含受校验字段时跳过 `full_clean`。这一项改变了 `architecture.md` 3.28 记录的行为，需要项目负责人决定。 | 中 | `test_member_profile.py`、`test_avatar_lifecycle.py`、`test_event_model_admin.py`、`test_profile_publication.py` |
| A16 | `members/models.py:124-127` | `FileExtensionValidator` 被 `validate_avatar` 中“扩展名必须匹配真实格式”的更严格检查完全覆盖。 | 删除。注意这会产生一条 `AlterField` migration。 | 低 | `test_member_profile.py`、`test_avatar_lifecycle.py` |
| A17 | `members/models.py:186-191` | `__str__` 与 `resolved_display_name` 实现重复。 | `__str__` 直接返回该 property。 | 低 | 无 |
| A18 | `members/views.py:112` | **硬编码 URL**：`f"/members/{username}/"`。 | 改为 `reverse("members:detail", kwargs={"username": ...})`。 | 低 | `test_profile_publication.py`（输出不变） |
| A19 | `safety/admin.py:30-48` | 4 个 `has_*_permission` 重复编写 `settings.RISK_NOTICE_DRAFT_VISIBLE and super()...`。 | 抽成一个私有 `_draft_enabled()`；收益较小，可选。 | 低 | `test_risk_notice_versions.py` |

**N+1 检查结论：** 未发现真正的 N+1。已检查 `member_list`（`select_related("user")`）、`EventRegistrationAdmin`（`list_select_related`）、`MemberProfileAdmin`（Django 对 `list_display` 中的 FK 会自动执行 `select_related`）、Home/Events 卡片（`is_past` 为纯 Python 计算），以及 `UserAdmin` 列表。

**异常捕获结论：** 未发现有害的过宽捕获。`members/services.py:28` 的 `except Exception` 只执行“清理孤立文件后原样 re-raise”，`scripts/accept_phase_*.py` 中的 `except Exception` 只执行“打印 server log 后 re-raise”，两者都合理。

**注释结论：** 代码注释整体有效。过时描述集中在文档中，见第六节附注。

## 二、模板

| ID | 位置 | 问题 | 建议改法 | 风险 | 受影响测试 |
| --- | --- | --- | --- | --- | --- |
| T1 | `apps/core/templates/core/includes/header.html:14-44` | **重复的 aria-current 判断**：8 处长 `or` 链，混用 `url_name`、`namespace` 和 `view_name` 三种口径。 | 用 context processor 或 simple tag，把 `resolver_match.view_name` 映射为 `nav_section`，模板统一写 `{% if nav_section == "events" %}`。渲染结果必须保持字节级一致。 | 低 | `test_global_templates.py:44` 等、`test_member_directory.py`、`test_public_information_pages.py`、`public-foundation.mjs`、`phase2-accessibility.mjs` |
| T2 | `header.html:8` 与 `static_src/css/site.css:940` | **断点重复**：JS `matchMedia('(max-width: 60rem)')` 与 CSS 断点分别硬编码，存在漂移风险。 | 由 CSS 自定义属性提供断点，JS 读取；至少要建立单一来源。 | 低 | `public-foundation.mjs`、`phase2-accessibility.mjs` |
| T3 | `core/errors/403.html`、`404.html`、`500.html` | **重复片段**：三个 19 行文件只有状态码、标题和说明不同。 | 新建 `core/errors/_error_page.html` 基模板，三个子模板只覆盖 block，从而保留模板名供测试使用。 | 低 | `test_error_pages.py:22`（断言模板名）、`error-pages.mjs` |
| T4 | 9 个页面模板（home、about、beginners_safety、3 个错误页、member_list、member_detail、risk_notice） | **重复 metadata**：每页把 title 与 og:title、description 与 og:description 各写两遍。 | 在 base 中让 OG 默认值来自同一变量，例如 `{% with %}`/include 或 view context；同时必须保持获准 metadata 逐字不变。 | 中 | `test_public_metadata_sitemap_footer.py`、`test_global_templates.py:51-61` |
| T5 | 约 35 个模板的 `{% block title %}` | 品牌后缀 ` \| NULDL Armwrestling Club` 被硬编码。Home 和 About 使用获准的非后缀格式，所以无法一刀切。 | 与 T4 一并处理，只对后缀型标题提供默认拼接；可选。 | 中 | 同 T4，加上全部页面的 title 断言 |
| T6 | `templates/account/signup.html:16-28` 与 `apps/accounts/templates/accounts/account.html:85-93`；`accounts/forms.py:70-71,131-132` | **重复 Alpine 片段**：USYD/USU 的 `x-data`、`$watch` 清空逻辑和 `x-show` 在两个模板中重复，而 `x-model`/`x-ref` 又在 Python form 中注入，导致 Alpine 职责分散在 3 处。 | 新建 `includes/usyd_fields.html`，承载完整包装标记；widget attrs 收进 A3 的 mixin。 | 低 | `test_authentication_templates.py:83-88,165`、`authentication-ui.mjs`、`phase1-core-flows.mjs` |
| T7 | `templates/account/includes/*` 被 `members/profile_edit.html:14-43` 与 `accounts/account.html:89-92` 引用 | **跨域耦合**：通用表单 include 放在 allauth 覆盖目录中，却被会员 App 依赖。 | 迁至 `templates/includes/forms/`，并更新所有 include 路径。 | 低 | 所有表单页测试（输出不变） |
| T8 | `templates/account/` 下 13 个模板；`confirm_email_verification_code.html` 与 `confirm_login_code.html` | **重复骨架**：13 个模板都重复 `content-narrow > eyebrow > h1 > lede > panel > form.stack`，两个 code 页面几乎完全一样。 | 建立 `account/_form_page.html`，提供 eyebrow、heading、lede、action、submit 等 block，并让两个 code 页共用 include。 | 中 | `test_authentication_templates.py`、`authentication-ui.mjs`、`phase1-core-flows.mjs` |
| T9 | `accounts/account.html:67-75` 与 `members/profile_preview.html:14-22` | Edit、Preview、Publish/Unpublish 按钮组及发布状态分支重复。 | 新建 `members/includes/profile_actions.html`。 | 低 | `test_account_page.py`、`test_profile_publication.py`、`phase3-accessibility.mjs` |
| T10 | `members/member_list.html:20-32`、`includes/profile_public_fields.html:12-24`、`account.html:43-50`、`profile_edit.html:19-25` | **重复 Avatar/fallback 标记且 a11y 不一致**：列表 fallback 使用 `aria-hidden`；详情 fallback 在无 role 的 `div` 上使用 `aria-label`，辅助技术不会读出。 | 新建 `members/includes/avatar.html`，用 size 参数控制尺寸，并统一 fallback 语义。 | 低 | `test_member_directory.py`、`test_member_detail.py`、`member-directory.mjs`、`phase3-accessibility.mjs` |
| T11 | `profile_public_fields.html:26,28,32`；`member_list.html:38,40,46` | **模板里的业务规则 + 硬编码 choice 值**：公开字段白名单依赖 6 处 `!= "not_spec"`。 | 在 MemberProfile 上增加 `public_experience_level` 和 `public_preferred_arm` property，未指定时返回 `None`；模板只判断真值。 | 低 | `test_member_directory.py`、`test_member_detail.py`（默认值隐藏） |
| T12 | `events/includes/registration_panel.html:1-8,17,30`；`registration_form.html:17,23`；`cancellation_form.html:13,18` | **Alpine 与 HTMX 职责混杂**：服务端用 `open_dialog`/`open_cancel_dialog` 驱动 Alpine `x-init`；include 依赖 4 个布尔开关在“dialog/整页”模式间切换；HTMX 的 `outerHTML` 目标同时是 Alpine 根，替换后状态会重新初始化；`aria-live` 包住了 modal dialog。 | 明确契约：HTMX 只负责请求与替换，Alpine 只负责 dialog 开关；include 改为单一 `mode="dialog"\|"page"` 参数；用一个 `data-open-dialog` 属性触发；`aria-live` 移到独立状态元素。 | 中 | `test_event_registration_pages.py`、`event-registration.mjs`、`test_event_registration_browser.py` |
| T13 | `core/home.html:72`、`events/event_list.html:16`、`event_detail.html:11` | `{% timezone "Australia/Sydney" %}` 与 `TIME_ZONE` 设置重复；`event_card.html` 依赖父模板提供时区包裹，无法单独复用。 | 把时区处理移进 `event_card.html`，或者依赖 `TIME_ZONE`。日期分类仍由 `EventQuerySet` 固定 Sydney，不受影响。 | 低 | `test_event_pages.py`（时间格式） |
| T14 | `events/event_registration_confirm.html` 与 `event_cancellation_confirm.html` | 两个整页确认模板骨架相同。 | 共用一个模板，通过 include 参数区分。 | 低 | `test_event_registration_pages.py` |
| T15 | `core/base.html:19-22` | 为了运行一段“聚焦首个错误”的脚本，把 `<body>` 设为全局 Alpine 组件。 | 改为本地 `static/js/focus-errors.js`（defer）；可选。 | 低 | `authentication-ui.mjs`（错误焦点） |
| T16 | `members/profile_edit.html:9`、`profile_preview.html:9`（`page-introduction`）；`member_list.html:10`（`section-heading`）；`member_detail.html:10`（`text-link`） | **模板引用了不存在的 CSS class**。 | 补齐样式，或改用现有 `public-section__header`/`lede`；也可删除无效 class。 | 低 | 无，仅影响视觉 |

## 三、CSS（`static_src/css/site.css`）

| ID | 位置 | 问题 | 建议改法 | 风险 | 受影响测试 |
| --- | --- | --- | --- | --- | --- |
| C1 | `:750` | **Bug：未定义 token**。`var(--color-text)` 不存在，Members 名称链接颜色意外回退为继承色。 | 改为 `var(--color-cream)`。 | 低 | `member-directory.mjs`、`phase3-accessibility.mjs` 的对比度检查 |
| C2 | `:156,924`（`#34302a`）；`:312,396,496,553,631,712,808`（`#37332c`）；`:191,433,616,657,721,802,833`（`#706858`）；`:568`（`#4a4438`）与 `:785`（`#4a4439`，近似重复）；`:528,546`（`#2a2110`）；`:539`（`#211b10`）；`:860`（`#291413`）；`:835`（`#0e0e0e`）；`:157`、`:440`（rgb） | **未使用 Design Tokens**：约 25 处硬编码颜色，违反 `design_document.md` 9.2 中“所有具体 Design Tokens 集中管理”的要求。 | 在 `@theme` 增加 `--color-border`、`--color-border-strong`、`--color-divider`、`--color-warning-surface`、`--color-error-surface`、`--color-input` 和 `--color-overlay`。两个近似色应合并为一个。 | 低 | `test_static_assets.py:49-57`；浏览器对比度检查在取值不变时不受影响 |
| C3 | `:863-865` | **`!important` 优先级补丁**：`[aria-invalid="true"]` 用 `!important` 压过 `.field input:not(...):not(...)` 的高优先级（0,3,1）。`:1022-1025` 中 reduced-motion 使用的 `!important` 合理。 | 改为 `.field [aria-invalid="true"]`，并放在输入框规则之后；或者用 `:where()` 降低输入框选择器的优先级。 | 低 | `authentication-ui.mjs`（错误态） |
| C4 | `:933-1016` | **隐性优先级覆盖**：所有 `@media` 都写在 `@layer components` 之外，未分层规则会无视优先级压过全部分层规则。例如 `.nav-link, .button { width: 100% }`（`974-977`）会覆盖任何组件宽度。 | 把 media 规则移入对应组件，或放进 `@layer components`。 | 中 | 全部布局类浏览器测试（`public-foundation`、`phase2/3-accessibility`、`event-pages`、`member-directory`、`home-page`） |
| C5 | `:933`（`min-width: 54rem`）、`:940`（`max-width: 60rem`）、`header.html:8`（JS `60rem`）、`home.html:28`（`sizes` 中的 78/54/36rem） | **断点不统一**：mobile-first 与 desktop-first 混用，数值也分散在 CSS、JS 和 HTML 中。 | 在 `@theme` 定义 `--breakpoint-*`，统一采用 mobile-first `min-width`，并与 T2 一并处理。 | 中 | 同 C4 |
| C6 | `:458-460`（`.home-page .content-card h3 { font-size: calc(1rem + 3px) }`）；`:339-344`（About 专用 `.public-page__join-action .button`：`90%`、`4.675rem`、`0.94rem 2.2rem`、`2rem`）；`:988-990`（`.home-hero__actions > :nth-child(3)`） | **单页面补丁 + 像素硬补**。`nth-child(3)` 依赖按钮数量：登录会员只有 2 个按钮，规则失效且布局随认证状态改变。 | 改为语义修饰类，例如 `.button--hero`、`.button-row--hero` 配合 `grid-template-columns: repeat(auto-fit, minmax(...))`；字号改用 token 或 `rem`。 | 低 | `home-page.mjs`、`public-information.mjs`、`phase2-accessibility.mjs` |
| C7 | `:394` + `:401-403`；`:992-998`；`:1000-1007` | **覆盖式补丁 / 可流式化的 media query**：`.content-card { height: 100% }` 再被 `.event-card { height: auto }` 撤销，而 grid 默认 stretch 已能等高；`.profile-public-card > .definition-list` 的 media 规则与 `.definition-list` 重复；`.member-card` 的列宽与 fallback 字号先用了 `clamp`，又在 media 中覆盖。 | 删除 `content-card` 的 `height: 100%` 及 `.event-card` 补丁；删除重复的 definition-list 规则；改用 `clamp(5.5rem, 12vw, 10rem)`，去掉 media 覆盖。 | 低 | `member-directory.mjs:38`（断言 avatar 宽度）、`event-pages.mjs`、`home-page.mjs` |
| C8 | `:558-590` | **死 CSS**：`.session-details`（及其 `div`/`dt`/`dd`）和 `.session-note` 在 Step 40 移除静态日程后已无引用。 | 删除。 | 低 | 无 |
| C9 | `.panel` 309、`.content-card` 393、`.step-list li` 491、`.session-card` 551、`.profile-public-card` 627、`.member-card` 704、`.empty-state` 806；Avatar：611、653、717、797；fallback：667、731 | **重复的卡片表面声明**（border + radius + surface + padding）出现 7 次；Avatar 样式 4 套，fallback 样式 2 套。 | 抽出 `.surface` 组件或 `@utility`，以及 `.avatar`、`.avatar--sm/md/lg`、`.avatar-fallback`。 | 低–中 | 浏览器布局与尺寸测试 |
| C10 | `:72-76`、`:83`、`:124-129`；`:5` | **与 Tailwind preflight 重复**：`box-sizing`、`body margin`、表单 font inherit 已由 preflight 提供。`@source "../../apps/**/*.py"` 扫描 Python 文件，但 Python 中没有任何 utility class。 | 删除重复 base 规则和 `.py` source。 | 低 | `test_static_assets.py` |
| C11 | `:356-358`、`:641-646`、`:648-651`、`:677-680`、`:745-747`、`:777-780`、`:918-921` | **零散的 `overflow-wrap: anywhere` 补丁**，共 7 处。 | 集中到 base（标题、`dd`、`code`）或提供一个 `.break-anywhere`。 | 低 | `phase3-accessibility.mjs`（长 Username/Bio） |
| C12 | `:202`、`:957`、`:961` | **过度限定选择器**：`.site-nav .nav-disclosure > .nav-menu`。 | 改为 `.nav-menu` 或 `.nav-disclosure[open] > .nav-menu`。 | 低 | `public-foundation.mjs` |

## 四、测试

| ID | 位置 | 问题 | 建议改法 | 风险 | 受影响测试 |
| --- | --- | --- | --- | --- | --- |
| D1 | `create_user` 有 8 份：`test_magic_code_authentication.py:23`、`test_password_authentication.py:27`、`test_member_profile_admin.py:17`、`test_user_admin.py:15`、`test_member_profile.py:20`、`test_account_page.py:15`、`test_event_registration_admin.py:17`、`test_user_identity_rules.py:12`；`create_member`：`test_profile_edit.py:11`、`test_profile_publication.py:18`；`create_profile`：`test_member_detail.py:13`、`test_member_directory.py:11`、`test_member_profile_admin.py:26`；`verified_member` fixture 有 4 份：`test_authentication_templates.py:15`、`test_global_templates.py:12`、`test_home_page.py:10`、`test_public_information_pages.py:35` | **重复 helper/fixture**，共约 17 份。 | 新增 `tests/factories.py`（`create_user(verified=…, usyd=…)`、`create_member`、`create_published_profile`）以及 `conftest.py` 中的 fixture。各变体语义（是否建立 EmailAddress 等）用参数保留。 | 低 | 上述全部文件 |
| D2 | 13 个 `tests/test_*_browser.py`（例如 `test_home_browser.py:10-25`） | **重复样板**：每个文件都手写 env、`subprocess.run(node)` 和输出断言。 | 新增 `tests/browser_runner.py::run_node_scenario(script, live_server_url, extra_env=None, timeout=90)`。 | 低 | 13 个 browser wrapper |
| D3 | `tests/browser/*.mjs` | **验收脚本间复制粘贴**：`assertPageBounds` 有 4 份，`assertNoHorizontalOverflow` 有 3 份，`assertTouchTargets`、`assertVisibleContentFits`、`assertFocusIndicator`、`assertPageStructure`、`assertNoOverflow`、`addSession` 各 2 份；`externalRequests`/`pageErrors` 的收集逻辑在 11–17 个文件中重复。 | 收敛到 `browser-support.mjs` 导出。合并前需要逐份 diff，确认阈值一致。 | 低–中 | 全部 Playwright 场景 |
| D4 | `test_phase1_acceptance.py` 至 `test_phase4_acceptance.py`；`test_quality_gate.py` | **重复测试**：`run` 的失败传播和 `stop_process` 分别针对 4 份相同函数测试了 4 次。 | 与 E5 一起做：只测一次共享 helper，按 phase 参数化 smoke 列表。 | 低 | 这 5 个文件 |
| D5 | `test_phase1..4_acceptance.py`（例如 `test_phase4_acceptance.py:88-104`） | **断言文档措辞而非行为**：README 中出现特定短语即算通过，脆弱且与需求无关。 | 降为“README 提及验收脚本路径”，或删除。是否把 README 视为验收物，需要项目负责人决定。 | 低 | 这 4 个文件 |
| D6 | `test_global_templates.py:63-73`（读取 `base.html` 源码并断言存在 `{% block %}`）；`test_public_metadata_sitemap_footer.py:116-137`（grep 源文件中的 host）；`test_authentication_templates.py:83-88,165`（断言 `x-data="{ isUsyd: false }"`、`x-show="isUsyd \|\| false"` 等精确 Alpine 字符串）；`test_global_templates.py:38,41,92,94,117,119`（断言 `class="site-header"`、`class="nav-disclosure"` 等 class 名） | **断言实现细节而非需求**。渲染出的 metadata 已在 `test_global_templates.py:51-61` 断言；“无 JS 仍可见”和条件显示由 `authentication-ui.mjs` 真实验证。 | 删除源码读取类断言；Alpine 断言改为“`usu_id` 字段已渲染，且无 `x-cloak`”；class 断言改为 landmark 级断言（`<header`、`<summary>Menu`）。 | 低 | 上述文件 |
| D7 | `test_static_assets.py:49-57` 与 `60-65` | **脆弱/空转断言**：一方面依赖 minifier 输出格式（`--color-ink:#090909`）；另一方面对比度测试使用硬编码 hex 字面量，没有从 CSS 读取，CSS 改色也不会失败。 | 从 `static_src/css/site.css` 的 `@theme` 解析 token，再计算对比度；同时删除 minified 子串断言。 | 低 | `test_static_assets.py` |
| D8 | `test_static_assets.py:38-44`；`test_home_images.py:18` | 精确依赖版本和字节数重复了 `package.json` 与 manifest 的职责。 | 改为“manifest packages 与 `package.json` dependencies 一致”。 | 低 | 同文件 |
| D9 | `test_project_scaffold.py:5-30` | 只是 `PROJECT_APPS` 的快照测试，价值很低；完成 A1 后需要修改。 | 与 A1 一起删除，或者只保留“每个 AppConfig 可导入”。 | 低 | 同文件 |
| D10 | `test_quality_security.py`（Members 隐私扫描）与 `test_member_directory.py`、`test_member_detail.py`、`test_event_registration_admin.py`、`test_event_registration_pages.py` 中各自的敏感字段扫描 | 隐私扫描逻辑和 sentinel 构造重复。`AGENTS.md` 要求隐私边界有显式断言，所以**只合并实现，不减少覆盖**。 | 提供共享 `assert_no_private_fields(content, user)` helper，各测试保留调用。 | 低 | 上述文件 |

## 五、工程

| ID | 位置 | 问题 | 建议改法 | 风险 | 受影响测试 |
| --- | --- | --- | --- | --- | --- |
| E1 | `scripts/verify_steps_17_18.py` | **死脚本**：已被 `verify_project.py` 取代，没有任何引用，`FORMAT_TARGETS` 也已过时。 | 删除，并同步 `architecture.md` 的文件职责表。 | 低 | 无 |
| E2 | `scripts/accept_phase_1.py` 至 `accept_phase_4.py`（各约 140 行）；`run()` 的 6 份副本：`verify_project.py:12`、`verify_steps_17_18.py`、4 个 accept 脚本 | **验收脚本复制粘贴**：4 个文件约 95% 相同，差异只在临时目录前缀、门禁脚本和 smoke 列表。`accept_phase_1.py:14` 中的 `NPM` 常量未使用；`accept_phase_2.py` 缺少失败时打印 server log 的逻辑，行为不一致。 | 新增 `scripts/_acceptance.py`，提供 `run`、`environment_python`、`available_loopback_port`、`wait_for_server`、`stop_process` 和 `run_acceptance(phase, smokes)`。各 phase 文件改为约 5 行的薄包装，README 命令保持不变。 | 低 | `test_phase1..4_acceptance.py`（monkeypatch 目标需从 phase 模块迁到共享模块）、`test_quality_gate.py` |
| E3 | `scripts/build_home_images.py`、`static/images/brand/*.webp`（未提交改动） | **生成物体积增大（第 1 批实测后已更正）**：源图切换为 `nuldl-club-logo-transparent.png` 后，WebP 从 32,364/69,400/125,860 bytes 增至 119,388/270,636/507,662 bytes（约 4 倍）。审计初稿把原因归于 `exact=True`，但实测去掉 `exact=True` 只减少 1–2.5%，恢复 `method=6` 也只再减少约 3–4%（两项同时改为 114,446/256,642/482,766 bytes）。增大主要来自新源图本身，不是构建参数问题。另外，`architecture.md` 3.20 仍记录旧源图和旧尺寸。 | 第 1 批**不改构建参数**。若要显著降低体积，需要项目负责人决定是否降低 `quality`、裁掉透明边距，或接受当前体积；同时按 N2 修正 3.20 的源图与尺寸记录。 | 低 | `test_home_images.py`、`home-page.mjs` |
| E4 | `static_src/images/brand/08_Metal_gold_Black.png`（1.1 MB，未跟踪，无任何引用）；`Logo_without_USYD.png`（1.7 MB，在未提交的源图切换后已无引用） | **仓库中无用的源图**。 | 经项目负责人确认后不提交或删除。原批准源图若需存档，应在文档中说明。 | 低 | `test_home_images.py`（已指向新源图） |
| E5 | `static/css/site.css`、`static/vendor/**`、`static/fonts/**`、`static/images/brand/*.webp` | **仓库中的生成物**：`architecture.md` 3.16/四 明确将其作为部署输入提交，并由 `static:check` 防漂移，所以这不算违规。但这样会带来大体积 diff（例如 minified CSS 单行冲突），且 MapLibre 一并被提交。 | 短期只删 MapLibre（A2）。是否改为由 CI 构建并 gitignore，属于架构决策，需要项目负责人决定。 | 中 | `test_static_assets.py`、`static:check` |
| E6 | `package.json:22` | **用不到的依赖**：`maplibre-gl`（同 A2）。其余 npm 依赖（alpinejs、htmx.org、fontsource、tailwind、playwright）以及 Python 依赖（django、allauth、pillow、psycopg、pytest、pytest-django、coverage、ruff）均在使用中。 | 同 A2。 | 低 | 同 A2 |
| E7 | `.env.example:4-5` | `POSTGRES_HOST` 没有被 settings 或 compose 读取（settings 只读 `DATABASE_URL`）；`DATABASE_URL` 与 `POSTGRES_*` 中的端口、密码重复书写，存在漂移风险。`architecture.md` 2.4 称“Django 从 `POSTGRES_*` 读取”，与实际不符。 | 删除 `POSTGRES_HOST`，在注释中说明二者必须一致，或修正文档。 | 低 | `test_database_settings.py`、`test_environment_settings.py`（预计不受影响） |
| E8 | 仓库根目录 | 缺少 `.gitattributes`，Git 对多个文件报告 `LF will be replaced by CRLF`，在 Windows 上制造 diff 噪音，也会影响 minified CSS 的 hash 检查稳定性。**实测（2026-11-17）**：在 `core.autocrlf=true` 下，从 `28cd8fa` 新建的 worktree 会把 `static/vendor/alpine/alpine.min.js` 签出为 CRLF（55,935 → 55,956 bytes），导致 `test_static_assets.py::test_generated_vendor_manifest_matches_local_assets` 与 `npm run static:check` 失败；而直接由构建脚本写入文件的原工作区不受影响。因此任何全新的 Windows clone 都会让门禁失败。 | 新增 `.gitattributes`：`* text=auto eol=lf`，并对 `static/vendor/**`、`static/css/site.css` 等受 hash 校验的生成物，以及字体、图片标记 `-text` 或 `binary`。建议把本项提前到第 2–3 批完成。 | 低 | `static:check`、`test_static_assets.py`（hash） |
| E9 | `.gitignore`（227 行） | GitHub 模板中大量与本项目无关的条目（Flask、Scrapy、Celery、SageMath 等）。 | 可选精简，必须保留 `.env`、`media/`、`staticfiles/`、`node_modules/` 等关键项。 | 低 | `test_quality_security.py`（tracked 文件扫描） |

## 六、附注：审计中发现的文档/代码不一致（不属于清理，需项目负责人确认）

- **N1（安全相关，项目负责人正在处理）**：`architecture.md` 3.37/3.39 写明报名服务会拒绝首行不是 `SYNTHETIC TEST ONLY` 的当前 Notice，但 `apps/events/services.py` 并没有这项检查，只有 `apps/safety/admin.py:13-21` 的 Admin 表单检查。项目负责人已决定修正文档，修订获批后直接并入通过版本。Production 由开关强制关闭，因此当前不构成线上风险。
- **N2（项目负责人已同意改法）**：`architecture.md` 3.16 和文件职责表仍写着 HTMX “尚未接入业务请求”，但 Events 已经在使用 HTMX；`locations` 和 MapLibre 的描述在 A1/A2 后同步；2.4 的 `POSTGRES_*` 描述按 E7 修正；3.20 的 Logo 源图和尺寸按 E3 修正。
- **N3a（已确认，只需补文档）**：`apps/core/templates/core/home.html:20` 的 “Join on USU” 外链（`https://usu.edu.au/clubs/armwrestling/`）是项目负责人确认的新功能，但尚未写入 `design_document.md` 7.4 Home 和 7.7 Home 内容基线。应补录按钮文字、目标 URL、显示条件（当前对 Anonymous 和会员都显示），以及它与 “不使用 USYD Branding” 原则的关系（只是指向 USU 社团页的外链，不使用 USU/USYD 视觉资产）。
- **N3b（已确认为误拷贝，已随本审计删除该段并同步测试）**：`apps/core/templates/core/beginners_safety.html:13` 在 H1 下方、导语之后多出一段 `Develop technique through structured practice using dedicated armwrestling equipment.`。这句话是 `design_document.md:436` Home `Supervised Practice` 卡片的原文；7.7 Beginners & Safety 基线（`design_document.md:489-491`）在 Heading 下只有一段 `You do not need previous…` 导语。该句从 Phase 2（`39d8982`）起就存在，`tests/test_public_information_pages.py:118` 把 `"dedicated armwrestling equipment"` 当作获准文本断言，`progress.md:819` 也称其为已批准内容，但 design document 的历史版本中从未在 Beginners 页列出这句。项目负责人确认这是误拷贝，因此删除该段，并从测试的获准文本列表中移除对应断言。

## 七、复核后保留（不计为过度设计）

- `events/services.py` 在事务内锁定 Event/User/全部 Notice 版本后复核资格、开放状态和当前版本：这是文档要求的并发防线（仅实现去重见 A8）。
- `accounts/models.py` 的保存期状态机、3 条 `CheckConstraint`，以及 `accounts/services.py` 的行锁：这是文档规定的三层身份保护。
- `members/forms.py:42-52` 的 Display name 重复检查加上 DB 唯一约束：表单层负责字段级错误，DB 层负责并发，文档已说明理由。
- `members/forms.py:54-56` 的 Instagram `@` 前置清理：文档说明它必须在 field validator 之前运行。
- 各 `CheckConstraint`（HTTPS、时间顺序、报名状态），以及 `members/services.py:28` 的“清理后 re-raise”。
- 无 JS 回退：整页确认页、`details/summary` 导航、普通 POST 表单。
- `validate_avatar` 的 reopen/close 逻辑：只要 `save()` 仍调用 `full_clean`，就必须保留（见 A15）。

## 八、优先级排序（收益高且风险低 → 收益低或风险高）

| 排名 | ID | 理由 |
| --- | --- | --- |
| 1 | C1 | 真实视觉 bug，改动只有一行 |
| 2 | A2 / E6 | 删除约 1.2 MB 未用资产和一个依赖，构建更快 |
| 3 | A1 | 删除死 App，零 schema 影响 |
| 4 | C8、E1、A5、A17、E2 中的 `NPM` 常量、T16 | 纯删除或纠错，零行为变化 |
| 5 | E3 | 实测构建参数调优只能省约 5%；是否需要降低体积，等待项目负责人决定 |
| 6 | C2 | 满足 Design Token 集中管理要求，取值不变则零视觉变化 |
| 7 | A7、A4/A3、A12 | 消除规则多处副本，降低未来漂移风险 |
| 8 | A9、A10、A11、T11 | 报名/公开字段规则集中；减少重复查询 |
| 9 | T1、T3、T6、T7、T9、T10、T13、T14 | 模板去重，输出可保持一致 |
| 10 | D1、D2、D3、D4、E2 | 测试与验收样板大幅收敛，只改测试侧 |
| 11 | D6、D7、D8、D9、D10、D5 | 提升测试有效性，减少脆弱断言 |
| 12 | C3、C6、C7、C9、C10、C11、C12 | CSS 去补丁化，需要浏览器回归 |
| 13 | A13、A14、A6、A19、E7、E8、E9、T2、T15 | 收益较小的整洁项 |
| 14 | C4、C5、T12、T8、T4/T5 | 中风险：涉及 cascade、断点、交互契约或获准 metadata |
| 15 | A8、A15、A16、E5 | 中风险或需要架构决策：锁顺序、模型保存语义、migration、生成物策略 |

## 九、建议分批

每批独立提交（`chore:`/`refactor:`/`test:`），每批结束执行 `ruff check .`、`ruff format --check .`、`pytest`、`npm run static:check`；涉及模板或 CSS 的批次再执行完整 Playwright 浏览器测试，并附 desktop/mobile 截图。

1. **第 1 批：纯删除与明确 bug（低风险，半天）**：C1、A2/E6、A1、C8、E1、A5、`accept_phase_1.py:14` 中未用的 `NPM`、T16。E3 经实测后从本批移出，改为等待决策。需要更新：`test_static_assets.py`、`test_project_scaffold.py`。完成后请项目负责人批准 `architecture.md` 和 `tech_stack.md` 的对应修订。**状态（2026-11-17）：已完成**。Ruff、Django check、`static:check` 均通过，完整 pytest 结果为 `380 passed`；文档修订已获批准，并已更新 `architecture.md` 3.43 与 `tech_stack.md`。
2. **第 2 批：Python 规则去重（低风险，行为不变）**：A3、A4、A7、A12、A14、A13、A17、A18、A11、A10、A9（含 T11 的 model property）。原有测试应全部原样通过；如有失败，说明行为发生了变化，需要回退。
3. **第 3 批：模板去重**：T1、T2、T3、T6、T7、T9、T10、T13、T14、T15。以渲染输出不变为验收标准，必要时先补快照式比较。
4. **第 4 批：测试与脚本收敛（只改 tests/ 与 scripts/）**：D1、D2、D3、E2 + D4、D6、D7、D8、D9、D10。D5 先征求项目负责人意见。
5. **第 5 批：CSS Token 与去补丁**：C2、C3、C6、C7、C9、C10、C11、C12。浏览器全量回归并逐页截图对比。
6. **第 6 批：中风险/需决策项（逐项单独评审）**：C4、C5、T12、T8、T4/T5、A8、A15、A16、E5、E7、E8、E9、A6、A19。每项先确认方案，再单独实施。N1 由项目负责人修订文档；N2、N3a 属于文档同步，可随第 1 批的 `architecture.md`/`design_document.md` 修订一并提交审批。
