import os
from pathlib import Path
from ghost_ai.brain.code_cleaner import clean_code_file

def self_heal(files_or_dirs, suggest_only=True):
    """
    Scans files or directories for code that needs cleaning/fixing.
    Uses the code_cleaner to suggest or auto-apply fixes.
    Archives all actions in memory.
    """
    if isinstance(files_or_dirs, str):
        files_or_dirs = [files_or_dirs]
    files_to_clean = []
    for entry in files_or_dirs:
        path = Path(entry)
        if path.is_file() and path.suffix == '.py':
            files_to_clean.append(path)
        elif path.is_dir():
            for pyfile in path.rglob('*.py'):
                files_to_clean.append(pyfile)
    print(f"[SelfHeal] Found {len(files_to_clean)} Python files to check.")
    for f in files_to_clean:
        print(f"[SelfHeal] Cleaning {f}...")
        clean_code_file(f, reason="Self-heal sweep", suggest_only=suggest_only)
    print("[SelfHeal] Sweep complete.") 