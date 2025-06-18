
import subprocess, sys

def spawn_services(num_instances=3, base_port=9091, script="insult_service_pyro.py"):
    procs = []
    for i in range(num_instances):
        port = base_port + i #puerto
        name = f"insult_service_pyro{i}"
        p = subprocess.Popen([ #lanza el script
            sys.executable, script,
            "--port", str(port),
            "--name", name
        ])
        procs.append(p)
        print(f"Spawned {name} on port {port} (pid={p.pid})")
    return procs

if __name__=="__main__":
    n = int(sys.argv[1]) if len(sys.argv)>1 else 3 #Defrcto 3
    ps = spawn_services(num_instances=n)
    for p in ps: 
        p.wait()
