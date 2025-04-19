class _DoublyLinkedBase:
    """A base class providing a doubly linked list representation."""

    class _Node:
        """Lightweight, nonpublic class for storing a doubly linked node."""
        __slots__ = '_element', '_prev', '_next'  # Memory optimization

        def __init__(self, element, prev, next):
            self._element = element  # Reference to user's element
            self._prev = prev         # Reference to previous node
            self._next = next         # Reference to next node

    def __init__(self):
        """Create an empty list with sentinel nodes."""
        self._header = self._Node(None, None, None)  # Dummy header
        self._trailer = self._Node(None, None, None) # Dummy trailer
        self._header._next = self._trailer  # Header points to trailer
        self._trailer._prev = self._header  # Trailer points to header
        self._size = 0  # Number of elements

    def __len__(self):
        """Return the number of elements in the list (O(1))."""
        return self._size

    def is_empty(self):
        """Return True if the list is empty (O(1))."""
        return self._size == 0

    def _insert_between(self, e, predecessor, successor):
        """
        Add element e between two existing nodes and return new node (O(1)).
        
        Args:
            e: Element to insert
            predecessor: Node before the new node
            successor: Node after the new node
            
        Returns:
            Newly created node
        """
        newest = self._Node(e, predecessor, successor)
        predecessor._next = newest
        successor._prev = newest
        self._size += 1
        return newest

    def _delete_node(self, node):
        """
        Delete a non-sentinel node from the list and return its element (O(1)).
        
        Args:
            node: Node to delete
            
        Returns:
            Element of the deleted node
            
        Raises:
            ValueError: If node is a sentinel
        """
        if node in (self._header, self._trailer):
            raise ValueError('Cannot delete sentinel nodes')
            
        predecessor = node._prev
        successor = node._next
        predecessor._next = successor
        successor._prev = predecessor
        self._size -= 1
        
        element = node._element  # Store deleted element
        # Clear references to help garbage collection
        node._prev = node._next = node._element = None  
        return element

    def _search(self, e):
        """
        Search for element e in the list (O(n)).
        
        Args:
            e: Element to search for
            
        Returns:
            First node containing the element or None if not found
        """
        current = self._header._next  # Skip header
        while current != self._trailer:  # Until we reach trailer
            if current._element == e:
                return current
            current = current._next
        return None

    def add_first(self, e):
        """Insert element e at the front of the list (O(1))."""
        return self._insert_between(e, self._header, self._header._next)

    def add_last(self, e):
        """Insert element e at the end of the list (O(1))."""
        return self._insert_between(e, self._trailer._prev, self._trailer)

    def delete_first(self):
        """Remove and return the first element (O(1))."""
        if self.is_empty():
            raise Exception('List is empty')
        return self._delete_node(self._header._next)

    def delete_last(self):
        """Remove and return the last element (O(1))."""
        if self.is_empty():
            raise Exception('List is empty')
        return self._delete_node(self._trailer._prev)

    def contains(self, e):
        """Check if element e is in the list (O(n))."""
        return self._search(e) is not None

    def __str__(self):
        """String representation of the list (O(n))."""
        elements = []
        current = self._header._next
        while current != self._trailer:
            elements.append(str(current._element))
            current = current._next
        return ' <-> '.join(elements) if elements else 'Empty list'
    

dll = _DoublyLinkedBase()
dll.add_first('A')  # A
dll.add_last('B')   # A <-> B
dll.add_first('C')  # C <-> A <-> B
print(dll)          # Output: C <-> A <-> B

dll.delete_first()  # Removes C
print(dll.contains('A'))  # True