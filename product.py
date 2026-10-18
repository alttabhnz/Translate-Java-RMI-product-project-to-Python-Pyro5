"""
product.py
----------
Python equivalent of Product.java (the Remote Interface).

In Java RMI:
    public interface Product extends Remote {
        public String getName() throws RemoteException;
        public String getDescription() throws RemoteException;
        public double getPrice() throws RemoteException;
    }

Python has no "interface" keyword, so we use an Abstract Base Class (ABC).
Any class that inherits from Product MUST implement all three methods,
just like a Java class that "implements Product".

In Java, Product.java had to be copied into BOTH the client and server
folders, because both sides need the interface (the server implements it,
the client casts the stub to it). In this Python version both server.py
and client.py import this single shared file instead.
"""

from abc import ABC, abstractmethod


class Product(ABC):
    """Remote interface: defines the behaviour (methods) of a product."""

    @abstractmethod
    def getName(self) -> str:
        """Return the product name."""

    @abstractmethod
    def getDescription(self) -> str:
        """Return the product description."""

    @abstractmethod
    def getPrice(self) -> float:
        """Return the product price."""


# The list of remote methods declared by the interface.
# The client uses this to check that a remote object really "is a" Product,
# the same way Java's (Product) cast checks the stub type.
PRODUCT_METHODS = sorted(Product.__abstractmethods__)
