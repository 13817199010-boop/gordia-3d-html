# 上传状态（2026-11-19）

仓库公开状态已由用户确认。角色图片和 PV 视频仍可能受第三方版权保护，公开仓库不等于获得素材再分发授权。

## 已上传
- `CODEX_TASK_PROMPT.md` — 云端 Codex 开发任务提示词。
- `README.md` — 交接说明（已调整为用户选择的公开仓库）。

## 尚未上传（目前本地交接压缩包中存在）
- `docs/REFERENCE_EVIDENCE.md`
- `docs/VIDEO_METADATA.txt`
- `references/frame_index.jpg`
- `references/gordia_official_character_cutout.png`
- `references/gordia_official_poster.jpg`
- `references/gordia_official_pv_clip.mp4`
- `references/video_frames/clip_05.40s.png`
- `references/video_frames/clip_07.10s.png`
- `references/video_frames/clip_07.50s.png`
- `references/video_frames/clip_07.80s.png`
- `references/video_frames/clip_08.45s.png`
- `references/video_frames/clip_08.65s.png`
- `references/video_frames/clip_08.85s.png`

原因：当前 GitHub 连接只能写入 UTF-8 文本或者由连接可读取的对象；上传会话中的二进制 ZIP 无法直接通过该连接批量解压推送。不要将缺失文件伪装为已上传。

## 需要执行的后续上传
将交接 ZIP 解压，在 GitHub 仓库的 `Add file → Upload files` 中拖入解压后的 `references`、`docs` 目录（保留相对路径），提交到 `main`。注意 GitHub 网页不接受仅上传 ZIP 后自动展开：必须先解压。

进入云端 Codex 前，核实上述 13 个参考素材及文档文件均出现在仓库中。
