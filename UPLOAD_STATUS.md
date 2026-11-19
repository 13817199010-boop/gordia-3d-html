# 格尔黛项目上传状态

已由用户确认将 GitHub 仓库保持公开。

- `README.md`、`CODEX_TASK_PROMPT.md`、`docs/REFERENCE_EVIDENCE.md` 和 `docs/VIDEO_METADATA.txt`：已提交。
- 完整 15 文件交接包：已无损分割为 `handoff_parts/part_00.bin` ... `part_26.bin` 并提交。
- `scripts/restore_handoff.py`：验证 ZIP SHA256、恢复全部原素材。
- `.github/workflows/restore-handoff.yml`：在分块首次提交时尝试自动还原并提交素材。
- 如果 GitHub Actions 没有运行或被权限限制，云端 Codex 可以先执行 `python scripts/restore_handoff.py`。

完整原 ZIP 的 SHA256：`07ae448d1616d5123db6554d1f779e89d798d34f354ac1c5f29623660b9af071`。只有执行并验证后才能宣称单个原始文件已解压至 `references/`。
