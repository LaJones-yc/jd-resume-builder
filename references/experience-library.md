# Dynamic experience library

The library is a living user-owned JSON file. Never prefill it with fictional examples in a real workflow.

## Record model

```json
{
  "schema_version": 1,
  "profile": {"name_zh": "", "name_en": "", "contact": {}},
  "experiences": [
    {
      "id": "exp-stable-id",
      "type": "internship|research|project|education|award|activity",
      "title_zh": "",
      "title_en": "",
      "organization_zh": "",
      "organization_en": "",
      "role_zh": "",
      "role_en": "",
      "location_zh": "",
      "location_en": "",
      "start": "YYYY.MM",
      "end": "YYYY.MM|present",
      "verified_facts": [],
      "metrics": [],
      "tools": [],
      "sources": [{"path": "", "kind": "pdf|paper|slides|repo|user", "evidence": ""}],
      "open_questions": [],
      "bullets_zh": [],
      "bullets_en": [],
      "status": "draft|needs_confirmation|verified"
    }
  ]
}
```

## Evidence rules

- `verified_facts` should be atomic and sourceable.
- Store exact numbers separately in `metrics`; never round or strengthen them without approval.
- A repository proves implementation artifacts, not automatically business impact or sole ownership.
- A paper proves reported methods/results, not necessarily the user's individual contribution. Ask what they personally owned.
- A slide deck may contain plans rather than completed work. Distinguish proposed, implemented, tested, launched, and measured.
- User testimony is valid evidence when explicitly provided; mark its source as `user`.
- Keep unresolved ambiguity in `open_questions` and exclude it from final claims.

## Updating records

Use `scripts/experience_library.py`:

```powershell
python scripts/experience_library.py init resume-workspace/experience-library.json
python scripts/experience_library.py upsert resume-workspace/experience-library.json record.json
python scripts/experience_library.py list resume-workspace/experience-library.json
python scripts/experience_library.py validate resume-workspace/experience-library.json
```

Upsert by stable `id`. Preserve older evidence when adding new sources. Do not overwrite a confirmed fact with an inferred claim.

