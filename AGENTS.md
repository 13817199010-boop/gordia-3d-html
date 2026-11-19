# Gordia 3D — Codex project instructions

This repository stores the 15-file Gordia character handoff in 27 lossless Git blobs under `handoff_parts/`, because the original ~20 MB ZIP could not be transferred as one GitHub API request.

Before any modeling or reference inspection, check `references/gordia_official_character_cutout.png`. If missing, run:

```bash
python scripts/restore_handoff.py
```

It reconstructs and SHA256-verifies the original ZIP, extracts the missing files to `references/` and `docs/`, and preserves existing README/Codex prompt files. Never treat missing reference paths as evidence that the uploaded pictures or video are unavailable before running the restoration script.

Then follow `CODEX_TASK_PROMPT.md`, analyze `docs/REFERENCE_EVIDENCE.md`, and do not invent hidden costume, footwear, or body details. Only free/open-source tools; paid AI generation is forbidden.
