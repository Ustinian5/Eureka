# Contributing

Eureka is a course project and a practical local-first research copilot. Contributions should keep the project easy to run, easy to review, and safe to open source.

## Development

1. Create the Conda environment from `environment.yml`.
2. Copy `.env.example` to `.env` and fill local API keys only on your machine.
3. Run tests before submitting changes:

```powershell
.\scripts\run_tests.ps1
```

## Rules

- Do not commit `.env`, API keys, local databases, or packaged zip files.
- Keep Chrome extension permissions minimal.
- Add or update tests for behavior changes.
- Update `README.md` and `docs/report.md` when user-facing features change.
