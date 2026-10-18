"""
server.py
---------
Python equivalent of Server.java, ProductImpl.java and ServerImpl.java.

Java RMI                                  ->  Pyro5
---------------------------------------------------------------------------
System.setProperty("java.rmi.server       ->  HOST = "127.0.0.1"
    .hostname", "127.0.0.1")
rmiregistry 9000 (separate process)       ->  Pyro5 Name Server on port 9000,
                                              started by this script itself
class ProductImpl implements Product      ->  class ProductImpl(Product)
                                              decorated with @Pyro5.api.expose
UnicastRemoteObject.exportObject(p1, 0)   ->  daemon.register(p1)
registry.bind("laptop", stub1)            ->  ns.register("laptop", uri1)

Note on ServerImpl.java:
    ServerImpl.java is EMPTY in the original repository
    (nix1947/sunway_dpp/JAVA_RMI_IV/server/ServerImpl.java has 0 lines).
    It contains no code to translate, so it has no Python counterpart.
    All of the server's real work is done in Server.java and ProductImpl.java,
    which are both translated below.
"""

import Pyro5.api
import Pyro5.nameserver

from product import Product

HOST = "127.0.0.1"          # same as java.rmi.server.hostname
NS_PORT = 9000              # same port the Java RMI registry used
DAEMON_PORT = 9001          # fixed port for the product objects

# Use the single-threaded "multiplex" server so the Name Server and the
# product objects can share one event loop (see daemon.combine() below).
Pyro5.config.SERVERTYPE = "multiplex"


# ---------------------------------------------------------------------------
# ProductImpl  (equivalent of ProductImpl.java)
# ---------------------------------------------------------------------------
@Pyro5.api.expose           # makes the methods callable remotely
class ProductImpl(Product):
    """Implements every method defined in the Product interface."""

    def __init__(self, newName: str, newDescription: str, newPrice: float):
        # Parametrized constructor, same attributes as the Java class.
        self.name = newName
        self.description = newDescription
        self.price = newPrice

    def getName(self) -> str:
        print(f"  [remote call] getName()        on '{self.name}'")
        return self.name

    def getDescription(self) -> str:
        print(f"  [remote call] getDescription() on '{self.name}'")
        return self.description

    def getPrice(self) -> float:
        print(f"  [remote call] getPrice()       on '{self.name}'")
        return self.price


# Server  (equivalent of Server.java)

def main():
    try:
        print("Server is booting....")

        # 1. Start the Name Server (replaces running "rmiregistry 9000").
        ns_uri, ns_daemon, _ = Pyro5.nameserver.start_ns(
            host=HOST, port=NS_PORT, enableBroadcast=False
        )
        print(f"Name Server (registry) running at {ns_uri}")

        # 2. Create the product objects (same data as Server.java).
        p1 = ProductImpl("Laptop", "Lenovo laptop", 800000.0)
        p2 = ProductImpl("Mobile", "MI 9 mobile", 24000.0)
        p3 = ProductImpl("Bag", "Branded bag", 800.0)
        p4 = ProductImpl("Charger", "MI Charger", 230.0)

        # 3. Create the Pyro daemon (the object server) and export the objects.
        #    daemon.register() == UnicastRemoteObject.exportObject()
        daemon = Pyro5.api.Daemon(host=HOST, port=DAEMON_PORT)
        uri1 = daemon.register(p1)
        uri2 = daemon.register(p2)
        uri3 = daemon.register(p3)
        uri4 = daemon.register(p4)

        # 4. Bind the exported objects in the Name Server so the client can
        #    look them up by name.  ns.register() == registry.bind()
        #    (The names are kept exactly as in Server.java. Note that the
        #    original binds the "Mobile" product under the name "ram".)
        ns = ns_daemon.nameserver
        ns.register("laptop", uri1)
        ns.register("ram", uri2)
        ns.register("bag", uri3)
        ns.register("charger", uri4)

        print("\nRegistered objects:")
        for name, uri in [("laptop", uri1), ("ram", uri2),
                          ("bag", uri3), ("charger", uri4)]:
            print(f"  {name:<8} -> {uri}")

        # 5. Run the Name Server and the object daemon in one event loop,
        #    so only ONE terminal is needed for the server side.
        daemon.combine(ns_daemon)
        print("\nServer is ready. Waiting for client requests... "
              "(press Ctrl+C to stop)\n")
        daemon.requestLoop()     # returns when Ctrl+C is pressed

        print("\nServer is shutting down....")
        daemon.close()
        ns_daemon.close()

    except KeyboardInterrupt:
        print("\nServer is shutting down....")
    except Exception as e:
        print("Server error " + str(e))


if __name__ == "__main__":
    main()
