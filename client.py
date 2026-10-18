"""
client.py
---------
Python equivalent of Client.java.

Java RMI                                        ->  Pyro5
---------------------------------------------------------------------------
LocateRegistry.getRegistry("127.0.0.1", 9000)   ->  Pyro5.api.locate_ns(
                                                        "127.0.0.1", 9000)
(Product) registry.lookup("laptop")             ->  Pyro5.api.Proxy(
                                                        ns.lookup("laptop"))
laptop.getName()                                ->  laptop.getName()

Client.java only looked up "laptop". This version looks up all four
objects that Server.java binds, so every remote object is demonstrated.
"""

import Pyro5.api
import Pyro5.errors

from product import PRODUCT_METHODS

HOST = "127.0.0.1"
NS_PORT = 9000

# The same names Server.java binds in the registry.
PRODUCT_NAMES = ["laptop", "ram", "bag", "charger"]


def check_is_product(proxy, name):
    """Equivalent of Java's (Product) cast: make sure the remote object
    exposes every method declared in the Product interface."""
    proxy._pyroBind()   # connect now and fetch the remote object's metadata
    missing = [m for m in PRODUCT_METHODS if m not in proxy._pyroMethods]
    if missing:
        raise TypeError(f"'{name}' is not a Product (missing {missing})")


def main():
    try:
        # Get the registry (Name Server).
        ns = Pyro5.api.locate_ns(host=HOST, port=NS_PORT)
        print(f"Connected to registry at {HOST}:{NS_PORT}\n")

        for name in PRODUCT_NAMES:
            # Look up the remote object and create a proxy (the "stub").
            uri = ns.lookup(name)
            with Pyro5.api.Proxy(uri) as product:
                check_is_product(product, name)

                # Every call below is a remote method invocation.
                productName = product.getName()
                productDescription = product.getDescription()
                price = product.getPrice()

            print(f"Lookup name : {name}")
            print("Name:" + productName)
            print("Description: " + productDescription)
            print("Price: " + str(price))
            print("-" * 40)

    except Pyro5.errors.NamingError:
        print("Exception in client side: cannot find the registry. "
              "Is server.py running?")
    except Exception as e:
        print("Exception in client side " + str(e))


if __name__ == "__main__":
    main()
