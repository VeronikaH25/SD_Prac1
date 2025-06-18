import Pyro4

@Pyro4.expose
class Subscriber:
    def receive_insult(self, insult):
        print(f"[Subscriber] Insult received: {insult}")
        return True


def run_subscriber():
    subscriber = Subscriber()
    daemon = Pyro4.Daemon()  #instancia de subscriber
    uri = daemon.register(subscriber)  #Lanza el subscriber

    nameserver = Pyro4.locateNS() #Registra el subscriber en el nameserver
    nameserver.register("subscriber", uri)

    print(f"[Subscriber] Subscriber running at {uri}")
    daemon.requestLoop()  


if __name__ == "__main__":
    run_subscriber()