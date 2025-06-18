# Lanzar varios servers en diferentes puertos
import subprocess, sys

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
for i in range(n):
    port = 8100 + i
    subprocess.Popen(["python", "insult_filter_xmlrpc.py", str(port)])
