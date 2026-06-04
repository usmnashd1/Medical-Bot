# Replit Bot GitHub Export Toolkit

This ZIP contains `export_github_zip.py`. Upload/run the script inside your Replit workspace root to create a GitHub-safe ZIP of your actual bot.

## Run in Replit Shell

```bash
set +H
cd /home/runner/workspace || cd "$REPL_HOME" || exit 1
python3 export_github_zip.py
```

The generated file will be named `whatsapp-medical-bot-github-ready-<timestamp>.zip`.
