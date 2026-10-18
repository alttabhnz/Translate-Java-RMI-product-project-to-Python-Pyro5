# PYTHON_RMI_LAB: Java RMI → Python Pyro5

A translation of the Java RMI project
[`nix1947/sunway_dpp/JAVA_RMI_IV`](https://github.com/nix1947/sunway_dpp/tree/master/JAVA_RMI_IV)
into an equivalent Python distributed-object system using
[Pyro5 (Python Remote Objects)](https://pyro5.readthedocs.io/).

The server creates four `Product` objects, exports them, and registers them by
name in a registry. The client looks each one up by name and calls its methods
remotely.

## Project structure

```
PYTHON_RMI_LAB/
├── product.py        # Equivalent to Product.java (Remote Interface)
├── server.py         # Equivalent to Server.java, ProductImpl.java and ServerImpl.java
├── client.py         # Equivalent to Client.java
├── requirements.txt  # Pyro5 dependency
└── README.md
```

## How the Java files map to Python

| Java file | Python file | What it does |
|---|---|---|
| `client/Product.java`, `server/Product.java` | `product.py` | The remote interface. Declares `getName()`, `getDescription()` and `getPrice()`. Java needed a copy in both folders; Python shares one file. |
| `server/ProductImpl.java` | `ProductImpl` class in `server.py` | Implements the interface and stores name, description and price. |
| `server/Server.java` | `main()` in `server.py` | Creates the four products, exports them, and binds them in the registry. |
| `server/ServerImpl.java` | *(none)* | **This file is empty in the original repository**, so there is no code to translate. A note is kept in `server.py`. |
| `client/Client.java` | `client.py` | Connects to the registry, looks up products, and calls their methods remotely. |

## How the Java RMI concepts map to Pyro5

| Java RMI | Pyro5 |
|---|---|
| `interface Product extends Remote` | `class Product(ABC)` with `@abstractmethod`s |
| `class ProductImpl implements Product` | `class ProductImpl(Product)` decorated with `@Pyro5.api.expose` |
| `rmiregistry 9000` (run separately) | Pyro5 Name Server on port 9000, started inside `server.py` |
| `UnicastRemoteObject.exportObject(p1, 0)` | `daemon.register(p1)` |
| `registry.bind("laptop", stub1)` | `ns.register("laptop", uri1)` |
| `LocateRegistry.getRegistry("127.0.0.1", 9000)` | `Pyro5.api.locate_ns(host="127.0.0.1", port=9000)` |
| `(Product) registry.lookup("laptop")` | `Pyro5.api.Proxy(ns.lookup("laptop"))` plus an interface check |
| Stub | Proxy |
| `throws RemoteException` | `Pyro5.errors.CommunicationError` / `NamingError` |

### Design decisions

- **One server terminal.** In Java you start `rmiregistry 9000` in its own
  terminal first. Here, `server.py` starts the Pyro5 Name Server itself and
  runs it in the same event loop as the product objects (`daemon.combine()`),
  so the whole project runs in two terminals: one server, one client.
- **Same names and data.** The products, prices and registry names are the
  same as in `Server.java`. The original binds the "Mobile" product under the
  name `ram`. That is kept as-is to stay faithful to the source.
- **Same method names.** The methods keep Java's camelCase names
  (`getName`, not `get_name`) so the mapping is easy to follow.
- **All four products.** `Client.java` only looked up `laptop`. `client.py`
  looks up all four registered objects so every remote object is shown.
- **Interface check.** Java's `(Product)` cast checks that the stub really is a
  `Product`. `client.py` does the same by checking that the remote object
  exposes every method declared in `product.py`.

## Requirements

- Python 3.8 or later (tested with Python 3.12)
- Pyro5

## How to run (Windows)

### 1. Install Pyro5

Open a terminal (Command Prompt or PowerShell) in the project folder and run:

```
pip install -r requirements.txt
```

If `pip` is not recognized, use `py -m pip install -r requirements.txt`.

### 2. Start the server (Terminal 1)

```
python server.py
```

Expected output:

```
Server is booting....
Name Server (registry) running at PYRO:Pyro.NameServer@127.0.0.1:9000

Registered objects:
  laptop   -> PYRO:obj_...@127.0.0.1:9001
  ram      -> PYRO:obj_...@127.0.0.1:9001
  bag      -> PYRO:obj_...@127.0.0.1:9001
  charger  -> PYRO:obj_...@127.0.0.1:9001

Server is ready. Waiting for client requests... (press Ctrl+C to stop)
```

Leave this terminal open.

### 3. Run the client (Terminal 2)

Open a **second** terminal in the same folder and run:

```
python client.py
```

Expected output:

```
Connected to registry at 127.0.0.1:9000

Lookup name : laptop
Name:Laptop
Description: Lenovo laptop
Price: 800000.0
----------------------------------------
Lookup name : ram
Name:Mobile
Description: MI 9 mobile
Price: 24000.0
----------------------------------------
Lookup name : bag
Name:Bag
Description: Branded bag
Price: 800.0
----------------------------------------
Lookup name : charger
Name:Charger
Description: MI Charger
Price: 230.0
----------------------------------------
```

At the same time, the server terminal logs each remote call it receives:

```
  [remote call] getName()        on 'Laptop'
  [remote call] getDescription() on 'Laptop'
  [remote call] getPrice()       on 'Laptop'
  ...
```

### 4. Stop the server

Press **Ctrl+C** in the server terminal. It may take up to two seconds to stop.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'Pyro5'` | Run `pip install -r requirements.txt`. |
| Client says `cannot find the registry. Is server.py running?` | Start `server.py` first and keep its terminal open. |
| `Address already in use` / `WinError 10048` | Ports 9000 or 9001 are taken, usually by an older `server.py` still running. Close it, or change `NS_PORT` / `DAEMON_PORT` in both files. |
| `python` is not recognized | Use `py server.py` and `py client.py`. |

## Ports used

| Port | Used by |
|---|---|
| 9000 | Name Server (same port as the Java RMI registry) |
| 9001 | Pyro daemon serving the product objects |

Both listen only on `127.0.0.1`, matching `java.rmi.server.hostname` in `Server.java`.
