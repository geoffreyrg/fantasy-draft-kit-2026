import sys
import runpy
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Unload any cached src modules to ensure fresh code execution on redeploy
for mod in list(sys.modules.keys()):
    if mod.startswith("src.") or mod == "src":
        del sys.modules[mod]

dashboard_path = root_dir / "src" / "dashboard" / "streamlit_app.py"
runpy.run_path(str(dashboard_path), run_name="__main__")
