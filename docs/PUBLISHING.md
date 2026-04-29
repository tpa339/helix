# Publishing

Recommended first release flow:

```bash
cd helix-framework
git init
git add .
git commit -m "Initial Helix framework release"
gh repo create helix-framework --private --source=. --remote=origin --push
```

Use `--public` only after running the security checklist in `docs/SECURITY.md` and deciding on a license.
