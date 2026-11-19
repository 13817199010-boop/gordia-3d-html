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
