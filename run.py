"""
Convenience launcher.

Runs the Streamlit app without needing to remember the exact command:

    python run.py

Equivalent to:  streamlit run app/main.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    app_path = Path(__file__).resolve().parent / "app" / "main.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    print("Launching:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
