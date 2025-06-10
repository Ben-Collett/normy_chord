
from collections import deque


class RingBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def add(self, item):
        """Add item to the buffer (removes oldest if full)"""
        self.buffer.append(item)

    def get(self):
        """Get the current buffer as a list"""
        return list(self.buffer)

    def remove_last(self):
        if not self.is_empty():
            self.buffer.pop()

    def is_empty(self):
        return len(self.buffer) == 0

    def get_last(self):
        """Get the last inserted value"""
        if not self.is_empty():
            return self.buffer[-1]
        else:
            return None  # Return None if buffer is empty

    def is_full(self):
        """Check if buffer is full"""
        return len(self.buffer) == self.capacity
