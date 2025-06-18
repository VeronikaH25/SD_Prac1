import subprocess
import sys

def spawn_filters(num_instances=5, base_port=9094, script="insult_filter_pyro.py"):
    procs = []
    for i in range(num_instances):
        port = base_port + i #puerto
        name = f"insult_filter_pyro{i}"
        p = subprocess.Popen([ #lanza el script
            sys.executable, script,
            "--port", str(port),
            "--name", name
        ])
        procs.append(p)
        print(f"Spawned {name} on port {port} (pid={p.pid})")
    return procs

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv)>1 else 3 #Defrcto 3
    procs = spawn_filters(num_instances=n)
    print(f"Total: {len(procs)} filter instances running.")
    for p in procs:
        p.wait()