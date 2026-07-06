# Shipcheck Rules for Codex

Use the bundled scripts whenever possible:

```bash
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/init_delivery_project.py --name "项目名" --output /path/to/project
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/check_delivery_stage.py --path /path/to/project/project-delivery
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/record_delivery_event.py --path /path/to/project/project-delivery --type change --phase "03_前端检查" --summary "..." --go NO-GO
```

When the current repository contains the packaged version instead of an installed global skill, run scripts from the local package:

```bash
python3 content-vault/90_Assets/shipcheck-skill/scripts/init_delivery_project.py --name "项目名" --output /path/to/project
```

Do not overwrite an existing `project-delivery/` folder without explicit user approval.

