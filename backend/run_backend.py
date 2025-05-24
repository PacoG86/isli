import subprocess
subprocess.run(["uvicorn", "backend.main:app", "--reload"])
# run_backend.py - Script de utilidad para lanzar el backend en modo desarrollo (con recarga automática)
