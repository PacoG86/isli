# run_backend.py
import subprocess
subprocess.run(["uvicorn", "backend.main:app", "--reload"])