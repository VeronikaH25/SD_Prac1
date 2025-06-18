# Lanzar varios servers en diferentes puertos
import subprocess, sys

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3 # 3 servers si no se indica
for i in range(n):
    port = 8000 + i
    subprocess.Popen(["python", "insult_service_xmlrpc.py", str(port)])
