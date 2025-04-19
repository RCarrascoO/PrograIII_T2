from Exceptions import OwnEmpty

class LinkedQueue:
    """FIFO queue implementation using a singly linked list for storage."""

    class Node:
        """Lightweight, non-public class for storing a singly linked node."""
        __slots__ = 'element', 'next'

        def __init__(self, element, next_node):
            self.element = element
            self.next = next_node

    def __init__(self):
        """Create an empty queue."""
        self.head = None
        self.tail = None
        self.size = 0  # number of elements in the queue

    def __len__(self):
        """Return the number of elements in the queue."""
        return self.size

    def is_empty(self):
        """Return True if the queue is empty."""
        return self.size == 0

    def first(self):
        """Return (but do not remove) the element at the front of the queue.

        Raise OwnEmpty if the queue is empty.
        """
        if self.is_empty():
            raise OwnEmpty("Queue is empty")
        return self.head.element  # front aligned with head of list

    def dequeue(self):
        """Remove and return the first element of the queue (FIFO).

        Raise OwnEmpty if the queue is empty.
        """
        if self.is_empty():
            raise OwnEmpty("Queue is empty")
        answer = self.head.element
        self.head = self.head.next
        self.size -= 1
        if self.is_empty():  # special case: queue is now empty
            self.tail = None  # the removed node was also the tail
        return answer

    def enqueue(self, e):
        """Add an element to the back of the queue."""
        newest = self.Node(e, None)  # node will become the new tail
        if self.is_empty():
            self.head = newest  # special case: queue was empty
        else:
            self.tail.next = newest
        self.tail = newest  # update reference to the new tail
        self.size += 1
