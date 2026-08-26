import runpy
from pathlib import Path

root_dir = Path(__file__).resolve().parent
target = root_dir / "src" / "dashboard" / "streamlit_app.py"
print(f"Target exists: {target.exists()}")
