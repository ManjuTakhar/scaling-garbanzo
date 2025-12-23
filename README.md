# syncup-core

Monorepo note: issues-core service is vendored at `syncup-core/issues-core`.

Run services (Windows, PowerShell):

1) Syncup API on port 8000
```
.\.scripts\run-syncup.ps1
```

2) Issues API on port 8001
```
.\.scripts\run-issues.ps1
```

3) Both APIs
```
.\.scripts\run-both.ps1
```

Requirements:
- Python 3.9 for syncup-core (ensure deps installed in 3.9)
- Python env for issues-core as needed
- Uvicorn installed in the respective environments

Notes:
- Each service keeps its own config, DB, and migrations.
- If ports conflict, edit the scripts under `.scripts`.