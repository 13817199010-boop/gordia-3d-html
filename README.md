# 格尔黛 | Codex 3D HTML 建模交接包

本包包含用户提供的角色参考立绘、海报、原始PV截取视频，以及从上传视频独立提取的关键帧。

## 提交给云端 Codex
1. 仓库 `gordia-3d-html` 已由用户明确选择为公开；上传前请确认参考素材的版权和公开传播限制。
2. 在 Codex 中打开该仓库，复制 `CODEX_TASK_PROMPT.md` 的任务文本。
3. 让 Codex 首先建立环境能力报告、参考资料证据表，并测试 Blender 是否可用。
4. 先完成可以从四个角度查看的 GLB 静态模型，再继续骨骼和网页。

## 资料说明
- `references/gordia_official_character_cutout.png`：正面人物立绘（仍未展示脚掌和背面）。
- `references/gordia_official_poster.jpg`：原始海报辅助比对。
- `references/gordia_official_pv_clip.mp4`：用户上传的13.406s视频片段，1440x2038，画面含上下黑边。
- `references/video_frames/*.png`：按上传片段相对时间提取的关键帧，并已经裁掉黑边（参考裁剪，不作为对色依据）。
- `references/frame_index.jpg`：视频关键帧索引。
- `docs/REFERENCE_EVIDENCE.md`：可见、部分可见、未知的部件事实表。

**注意**：帧时间相对的是上传的13.406s片段，非 B 站原视频绝对时间。原官方页面：https://www.bilibili.com/video/BV16Bs26FEAM/ 。

该素材可能受原游戏及视频著作权限制；用于个人复原研究；仓库公开不代表官方素材自动获得再分发授权。