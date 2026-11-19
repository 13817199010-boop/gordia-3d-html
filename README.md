# 格尔黛 | Codex 3D HTML 建模交接工程

本仓库用于《鸣潮》格尔黛角色复原研究和可交互 3D HTML 开发。公开仓库由用户明确选择。参考图片和官方 PV 片段可能受第三方版权保护，公开并不表示获得其再分发授权。

## 文件结构与恢复

完整交接包包括角色原始立绘、海报、13.406 秒 PV 片段、7 张视频关键帧、参考证据文档及 Codex 提示词，共 15 个文件。受单次接口传输限制，原始 ZIP 以 27 个无损分块存于 `handoff_parts/`。

GitHub Actions 会尝试自动恢复并提交 `references/` 与 `docs/` 中的素材。如素材尚未显示，使用：

```bash
python scripts/restore_handoff.py
```

恢复脚本会检查全部分块、验证原 ZIP 的 SHA256，并只解压缺失文件。原始 ZIP SHA256：

```
07ae448d1616d5123db6554d1f779e89d798d34f354ac1c5f29623660b9af071
```

## 提交给云端 Codex

1. 在 Codex 中打开本仓库 `13817199010-boop/gordia-3d-html`。
2. 先检查参考素材是否已恢复，否则运行上方 Python 命令。
3. 读取 `CODEX_TASK_PROMPT.md` 和 `docs/REFERENCE_EVIDENCE.md`。
4. 先检测 Blender、FFmpeg、Node 和 GPU 环境，再制作可编辑静态模型；通过 0°/45°/90°/180° 渲染验收后继续骨骼与 HTML。
5. 不允许擅自调用付费模型、fal 等按次计费服务。

官方视频来源：https://www.bilibili.com/video/BV16Bs26FEAM/

## 第一阶段静态模型

在 Blender 4.3 中打开 [可编辑工程](models/gordia-static.blend)。按集合编辑头脸、发束、军帽、礼服、手臂、下装、披风和武器。角色采用放松站姿，`UNVERIFIED_` 前缀标明缺少官方视图的补形。[五视图与头部细节](renders/) · [还原依据](docs/MODEL_SPEC.md) · [修正记录与限制](docs/PROGRESS.md)

[下载单文件 HTML 预览](preview/gordia.html)。模型和渲染代码均内嵌在文件内，可用 GitHub 的 Download raw file 下载。修改模型后用 `npm run model:mobile && npm run build:offline` 重新打包。

**网页预览**使用 Node.js 24 和 npm。拖动模型旋转，使用滚轮或双指缩放，底栏可复位至标准视角或切换武器。

```sh
npm ci
npm run dev -- --host 0.0.0.0
```

生成静态站点用 `npm run build`，输出位于 `dist/`。构建仅打包页面、脚本与实时模型。查看开发环境的具体版本见 [环境报告](docs/ENV_REPORT.md)。

**重新生成模型和验收**需 Blender 4.3.x、已安装的项目 npm 依赖及可运行的 Chromium。Blender 步骤会重新生成工程、完整 GLB 与五张全身视图。

```sh
blender -b --python-exit-code 1 --python scripts/build_character.py
npm run model:mobile
npm run model:check
# 在独立终端保持 Vite 运行，再执行浏览器检查
CHROMIUM_PATH=/usr/bin/chromium node scripts/check-preview.mjs
```

[完整 GLB](models/gordia-static.glb) 保留建模细节，[网页 GLB](models/gordia-mobile.glb) 保留具名部件并减少三角面。网页截图来自桌面 Chromium 和触控平板模拟。
