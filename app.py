"""
Root entrypoint for Streamlit Community Cloud.
Points directly to the full 2026 Draft Kit & Scouting Intelligence Engine.
"""
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute the primary Streamlit dashboard
import src.dashboard.streamlit_app
