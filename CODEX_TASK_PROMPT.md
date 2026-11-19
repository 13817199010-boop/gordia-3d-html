# Codex 云端开发任务：《鸣潮》格尔黛（Gordia / Gelde）高还原 3D HTML 角色展示

## 任务与预算
- 主模型：优先 GPT-6.2 Astra（若当前 Codex 菜单可用），思考强度 High；复杂拓扑/骨骼问题可使用 Extra High。
- 工作原则：只使用免费开源工具、用户已具有的 Codex 能力及免费额度；不得擅自调用任何按次计费 3D API、购买 GPU、开通云服务器、消费 fal 余额。
- 输出：可编辑的真实三维角色工程（`.blend` + Blender Python 脚本），`.glb`，Three.js HTML 展示页，测试截图，技术文档。
- 角色主体必须是实际立体几何网格，不得用 PNG 立牌、2D 分层或平面贴图冒充真正的 3D 角色。

## 输入与证据优先级
当前仓库 `references/` 包括正面透明立绘、原始海报、13.406秒PV截取视频和已抽帧截图。
优先级：透明立绘确定正面造型与配色；PV关键帧确定腰部、短裤、腿部上段及披风动态；没有直接参考的背面和鞋尖/鞋跟不得冒充官方原型。
视频帧时间相对的是上传视频而不是B站全片。参见 `docs/REFERENCE_EVIDENCE.md`。任何新发现都要记录可验证的来源文件和帧时间。

## 第一轮必须检测并按实际可用能力调用工具
A. **Codex内置终端/文件工具**（必须）：运行 `git status`、`python --version`、`ffmpeg -version`、`ffprobe -version`、`blender --version`、`node --version`、`npm --version`、`nvidia-smi`（仅在存在时）。生成 `docs/ENV_REPORT.md`。
B. **FFmpeg + Pillow + Python**（必须）：检查PV，自动识别上下黑边或使用已提取关键帧；选定正面、半侧面、腿部/披风关键帧；不要凭空生成角色未展示的视角。
C. **Blender 4.x及 bpy**（必须）：尽量通过 `blender --background --python scripts/build_character.py` 生成、保存 `.blend`、导出 GLB。若未安装，优先在允许的免费环境内安装；如不可安装，完整保留可复现的脚本和环境阻碍报告，不得声称已完成渲染。可用 Blender MCP 仅为辅助；不可用时直接使用命令行，不能被 MCP 缺失卡住。
D. **Three.js + Vite + glTF/GLB**（必须）：GLTFLoader、OrbitControls、AnimationMixer（存在动画时）、移动端适配、加载失败提示。
E. **glTF Transform / glTF Validator**（推荐）：网格压缩、纹理优化和结构校验；不得在压缩后破坏骨骼与材质。
F. **Playwright（CLI或MCP）**（推荐）：打开页面、检验控制台和 WebGL、在PC及安卓平板尺寸下截图、测试触控、双指缩放可模拟的部分。模拟测试不等于OPPO Pad 5真机验证。
G. **GitHub工具**（有权限时）：提交到当前指定的专用仓库或生成PR，不得把本项目塞进无关仓库，不得未经授权推送到公开仓库。
H. **Context7 MCP**（若已配置）：查询 Three.js/Blender/glTF 的新接口；没有就使用官方文档。
I. **Hugging Face Spaces / 免费开源 Hunyuan3D、TRELLIS**（可选）：先检查 GPU、模型许可、免费入口、队列、可导出GLB与费用。只有确实可零额外付费且可以保存输出时才使用；不具备免费 GPU 时立即回退 bpy 程序化建模。不得在普通 CPU Codex 环境强行跑需要24GB GPU的生成模型。
J. **fal、Meshy、Tripo计费API禁止调用**，即使账户已连接；Figma 仅在确有页面视觉设计需要且已获访问权限时可选用。

## 建模方案
- 首版可编辑实时模型目标：主 LOD0 约30k~45k三角面（质量与实际设备性能优先；非硬阈值）。角色可见部件单独命名、保留材质槽：Face/Eyes/Hair/Cap/Bows/Jacket/Shoulder/Shorts/Stockings/Boots/Cape/Medals/Weapon。
- 注重正面轮廓准确：红瞳、黑灰发片与红色内层、金色军帽几何、红黑披风、白色双排扣礼服、黑色短裤、大腿薄透肤质感、黑靴金扣红纹、金属手套、细长武器。
- 模型有厚度、合理侧背结构和轮廓。未知结构用独立命名 `UNVERIFIED_*` 对象，不能伪称来自官方资料。
- 武器单独成模、可隐藏、具手部挂点，避免与头发/披风融成一个面。
- 发片优先实体轮廓，少用移动端透明层；披风红黑双面材质并保留可骨骼变形的分段；金属高光克制，脸部Toon/NPR表现。
- 先做静态 A Pose 或易于绑骨的站姿，先可视化验收，再做原画展示姿势。

## 骨骼与动画
- 人体基本骨骼：Root、Hips、Spine、Chest、Neck、Head、手臂、手掌、腿足；可选手指。
- 长发左右主发束、披风与蝴蝶结各自简化辅助骨骼，不使用昂贵的实时布料物理。
- 基础动作：Idle（呼吸+轻微重心）、Blink（Morph Target 或简易眼皮）、Pose（原画风格姿态，能维持武器持握）。
- 对每个动作检查骨骼权重、穿模、GLB导出后的动画是否仍可播放；不能实现的动作要明确列为未完成。

## Three.js 页面
- 交付可运行的 `index.html`，Vite 源码，模型和纹理；提供 `npm install && npm run dev -- --host 0.0.0.0` 和打包方法。
- 支持鼠标拖动/滚轮和安卓单指旋转、双指捏合、重置视角、动作选择、表情选择、展示/隐藏武器、加载进度。
- 夜色背景、低饱和黑红金UI，不遮挡人物；使用 WebGL 兼容路径。
- 移动端：控制DPR、材质draw calls、几何/贴图大小、阴影、透明层和加载时内存。对 OPPO Pad 5 以30fps可接受、45~60fps为目标，但无真机实测不得宣称达标。
- 若发布网页，用户提供的参考图/视频不得默认作为公开站点资源。

## 开发执行顺序（不得跳过真实验收）
P0: 读取 `references/` 和 `docs/REFERENCE_EVIDENCE.md`，创建环境能力报告；确认没有需要付费的调用。
P1: 创建 `docs/MODEL_SPEC.md` 与部件清单，列出可见/未知证据；提供至少4个关键帧的部件引用。
P2: 实现 `scripts/build_character.py`，生成可编辑静态 `.blend` 和 `.glb`；从正面、侧面、背面、45°渲染截图。即使没有AI GPU，也必须做到当前环境允许的最优可验证静态模型。
P3: 对照参考图按‘脸和头发→帽子→服装→腿部靴子→披风武器’逐轮修正。不要把任何照片直接放到平面上冒充角色。
P4: 加骨骼与基础动画并重新导出；验证可播放。
P5: 构建 Three.js 页面；使用 Playwright/浏览器截图验证移动端显示、触控替代测试、资源路径与控制台错误。
P6: 生成 `README.md`、`docs/PROGRESS.md`、`docs/REFERENCE_EVIDENCE.md` 更新，以及可运行命令；如遇环境阻碍，记录实际错误和复现方法，绝不伪造结果。

## 交付验收
必须提供：完整源码、建模脚本、可编辑 .blend（若环境允许成功运行）、真实3D .glb、前后左右及45°截图、网页启动命令、自动测试日志、手机适配策略和已知未确认细节表。不得用无作用的按钮、截图冒充模型或宣称未经验证的还原度。
优先完成第一轮可运行静态模型和预览网页，然后在同一个工程内迭代骨骼动画，不重新从零创建项目。