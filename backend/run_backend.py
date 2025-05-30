import subprocess
subprocess.run(["uvicorn", "backend.main:app", "--reload"])
# Script para lanzar el backend en modo desarrollo (con recarga automática)
