"""Reset database by running backend init_db and seed --reset."""
from pathlib import Path
import runpy
import sys

backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))
runpy.run_path(str(backend_dir / "init_db.py"), run_name="__main__")
sys.argv = ["seed.py", "--reset"]
runpy.run_path(str(backend_dir / "seed.py"), run_name="__main__")
