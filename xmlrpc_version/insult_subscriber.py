from xmlrpc.server import SimpleXMLRPCServer
import argparse

class Subscriber: # Se subscribe al server y recibe insultos
    def receive_insult(self, insult):
        print(f"[Subscriber] Insult received: {insult}")
        return True

def main():
    p = argparse.ArgumentParser() #parser para leer argumentos
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=8002)
    args = p.parse_args()

    server = SimpleXMLRPCServer((args.host, args.port),
                                allow_none=True, logRequests=False)
    server.register_instance(Subscriber())
    print(f"Subscriber XMLRPC running on http://{args.host}:{args.port}") #escucha el puerto 
    server.serve_forever()

if __name__=="__main__":
    main()
