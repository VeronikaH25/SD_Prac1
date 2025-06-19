# Lanzar varios servers en diferentes puertos
import subprocess, sys #subprocess: lanza comandos como si fuera en shell

# python spawn_filters_xmlrpc.py X
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3 # 3 por defecto
for i in range(n):
    port = 8100 + i
    subprocess.Popen(["python", "insult_filter_xmlrpc.py", str(port)])
# python insult_filter_xmlrpc.py 8100
# python insult_filter_xmlrpc.py 8101
# python insult_filter_xmlrpc.py 8102...