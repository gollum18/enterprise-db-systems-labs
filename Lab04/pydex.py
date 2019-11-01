# Name: pydex.py
# Since: 10/28/2019
# Author: Christen Ford
# Purpose: Implements the dynamic hashing index algorithm.

from sortedcontainers import SortedList

# used to consume bits in a bitstring.
LEFT_TO_RIGHT = 0  # consumes from the left to the right
RIGHT_TO_LEFT = 1  # consumes from the right to the left

# provided for convenience when traversing the tree.
LEFT_KEY = '0'  # maps all entries keyed to '0'
RIGHT_KEY = '1'  # maps all entries keyed to '1'


# used by the SortedList to compare keys
def extract_key(e):
    return e.key


def consume_bitstring(bitstring, direction):
    """
    Consumes one bit from a binary string returning both the consumed bit and the partially consumed bitstring.
    :param bitstring: A bitstring to consume.
    :param direction: The direction to consume from. One of {LEFT_TO_RIGHT, RIGHT_TO_LEFT}.
    :return: A pair consisting of (bit, bitstring-1).
    :raises ValueError: If the bitstring is None or is not a string.
    :raises ValueError: It the direction is not one of {LEFT_TO_RIGHT, RIGHT_TO_LEFT}.
    """
    if bitstring is None or not isinstance(bitstring, str):
        raise ValueError
    if not (direction == LEFT_TO_RIGHT or direction == RIGHT_TO_LEFT):
        raise ValueError
    if len(bitstring) == 1:
        return bitstring[0], ""
    if direction == LEFT_TO_RIGHT:
        bit = bitstring[0]
        consumed = bitstring[1:len(bitstring)]
    else:
        bit = bitstring[-1]
        consumed = bitstring[0:len(bitstring)-1]
    return bit, consumed


def key_to_binary(key, n=32):
    """
    Converts the given key to binary with a fixed number of bits.
    :param key: The key to convert to binary.
    :param n: The number of bits to fix the binary representation of the key to.
    :return:
    :raises ValueError: If the key is None or not an integer.
    :raises ValueError: If n is less than 0.
    """
    if key is None or not isinstance(key, int):
        raise ValueError
    if n < 0:
        raise ValueError
    return format(key, '0{bits}b'.format(bits=n))


class _IndexEntry(object):
    """
    Implements a generic index entry for use in the indexing classes.
    """

    def __init__(self, key, value):
        """
        Returns a new instance of a _IndexEntry.
        :param key: The key stored in the index entry.
        :param value: The value stored in the index entry.
        :return: An instance of a _IndexEntry object.
        """
        self.key = key
        self.value = value

    def __lt__(self, other):
        """
        Implements rich comparison for less-than on two index entries as well as an index entry and a key.
        :param other: An _IndexEntry or key type.
        :return:  self.key < other.key OR self.key < other
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key < other.key
        elif isinstance(other, type(self.key)):
            return self.key < other
        else:
            raise ValueError

    def __le__(self, other):
        """
        Implements rich comparison for less-than-or-equal-to on two index entries as well as an index entry and a key.
        :param other: An _IndexEntry or key type.
        :return: self.key <= other.key OR self.key <= other
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key <= other.key
        elif isinstance(other, type(self.key)):
            return self.key <= other
        else:
            raise ValueError

    def __gt__(self, other):
        """
        Implements rich comparison for greater-than on two index entries as well as an index entry and a key.
        :param other: An _IndexEntry or key type.
        :return: self.key > other.key OR self.key > other
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key > other.key
        elif isinstance(other, type(self.key)):
            return self.key > other
        else:
            raise ValueError

    def __ge__(self, other):
        """
        Implements rich comparison for greater-than-or-equal-to on two index entries as well as an index entry and a
        key.
        :param other: An _IndexEntry or key type.
        :return: self.key >= other.key OR self.key >= other
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key >= other.key
        elif isinstance(other, type(self.key)):
            return self.key >= other
        else:
            raise ValueError

    def __eq__(self, other):
        """
        Implements rich comparison for equal-to on two index entries as well as an index entry and a key.
        :param other: An _IndexEntry or key type.
        :return: self.key == other.key OR self.key == other
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key == other.key
        elif isinstance(other, type(self.key)):
            return self.key == other
        else:
            raise ValueError

    def __ne__(self, other):
        """
        Implements rich comparison for not-equal-to on two index entries as well as an index entry and a key.
        :param other: An _IndexEntry or key type.
        :return: self.key != other.key OR self.key != other.
        """
        if other is None:
            raise ValueError
        if isinstance(other, _IndexEntry):
            return self.key != other.key
        elif isinstance(other, type(self.key)):
            return self.key != other
        else:
            raise ValueError

    def __hash__(self):
        """

        :return:
        """
        return hash(self.key)

    def __str__(self):
        """

        :return:
        """
        return "({k}, {v})".format(k=self.key, v=self.value)


class _BPTNode(object):
    """
    Implements an internal class that handles the heavy lifting for the B+ tree class.
    """

    def __init__(self, n=8, ff=0.75, internal=False, parent=None, sibling=None):
        """
        Returns a new instace of a _BPTNode.
        :param n: The maximum number of keys to store in the node.
        :param ff: The fill factor for the node.
        :param internal: Whether this node is an internal node. True=internal, False=leaf.
        :param parent: The parent node of this node.
        :param sibling: The next sibling from this node.
        """
        self.n = n
        self.ff = ff
        self.internal = internal
        self.parent = parent
        self.sibling = sibling
        self.entries = SortedList(key=extract_key)
        self.pointers = []

    def add(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        if self.internal:
            index = self.entries.bisect_right(key)
            self.pointers[index].add(key, value)
        else:
            self.entries.add(_IndexEntry(key, value))
        if len(self.entries) > self.n * self.ff:
            self._overflow()

    def contains(self, key):
        """

        :param key:
        :return:
        """
        if self.internal:
            return self.pointers[0].contains(key)
        else:
            index = self.entries.bisect_right(key)
            if index < len(self.entries):
                return True
            if self.sibling:
                return self.sibling.contains(key)
            return False

    def delete(self, key):
        """

        :param key:
        :return:
        """
        if self.internal:
            index = self.entries.bisect_right(key)
            self.pointers[index].delete(key)
        else:
            self.entries.discard(key)
        if len(self.entries) < 1 - (self.n * self.ff):
            self._underflow()

    def get(self, key):
        """

        :param key:
        :return:
        """
        if self.internal:
            return self.pointers[0].get(key)
        else:
            index = self.entries.bisect_right(key)
            if index < len(self.entries):
                return self.entries[index].value
            if self.sibling:
                return self.sibling.get(key)
            return None

    def height(self):
        """

        :return:
        """
        if self.internal:
            return self.pointers[0].height() + 1
        return 1

    def traverse(self):
        """

        :return:
        """
        if self.internal:
            yield from self.pointers[0].traverse()
        else:
            for entry in self.entries:
                yield entry.key, entry.value
            if self.sibling:
                yield from self.sibling.traverse()

    def _overflow(self):
        """

        :return:
        """
        raise NotImplementedError

    def _underflow(self):
        """

        :return:
        """
        raise NotImplementedError


class _DHTNode(object):
    """
    Implements a node in a dynamic hash tree. Used by the DHT class to perform internal operations on the tree.
    """

    def __init__(self, parent=None, depth=0, n=8, direction=RIGHT_TO_LEFT):
        """
        Returns an instance of a _DHTNode with the specified max bucket size and parent.
        :param parent: A pointer to the parent node.
        :param depth: The depth of this node.
        :param n: The max bucket size.
        :param direction: The direction to consume the key from.
        """
        self.n = n
        self.depth = depth
        self.parent = parent
        self.direction = direction
        self.internal = False
        self.left_child = SortedList(key=extract_key)
        self.right_child = SortedList(key=extract_key)

    def add(self, key, bitstring, value):
        """
        Adds a key-value pair to the DHTNode.
        :param key: The key ordinate of the key-value pair.
        :param bitstring: The key as a partially consumed bitstring.
        :param value: The value ordinate of the key-value pair.
        """
        tree_key, consumed_key = consume_bitstring(bitstring, self.direction)
        if tree_key == LEFT_KEY:
            if isinstance(self.left_child, _DHTNode):
                self.left_child.add(key, consumed_key, value)
            elif isinstance(self.left_child, SortedList):
                self.left_child.add(_IndexEntry(key, value))
                if len(self.left_child) > self.n:
                    self._overflow(LEFT_KEY)
            else:
                raise Exception()
        elif tree_key == RIGHT_KEY:
            if isinstance(self.right_child, _DHTNode):
                self.right_child.add(key, consumed_key, value)
            elif isinstance(self.right_child, SortedList):
                self.right_child.add(_IndexEntry(key, value))
                if len(self.right_child) > self.n:
                    self._overflow(RIGHT_KEY)
            else:
                raise Exception()
        else:
            raise KeyError()

    def contains(self, key, bitstring):
        """
        Determines if the tree contains the given key.
        :param key: The key to lookup.
        :param bitstring: A partially consumed bitstring representation of the key.
        :return: True if the key is found in the tree, False otherwise.
        """
        tree_key, consumed_key = consume_bitstring(bitstring, self.direction)
        if tree_key == LEFT_KEY:
            if isinstance(self.left_child, _DHTNode):
                return self.left_child.contains(key, consumed_key)
            elif isinstance(self.left_child, SortedList):
                for entry in self.left_child:
                    if entry.key == key:
                        return True
                return False
            else:
                raise KeyError
        elif tree_key == RIGHT_KEY:
            if isinstance(self.right_child, _DHTNode):
                return self.right_child.contains(key, consumed_key)
            elif isinstance(self.right_child, SortedList):
                for entry in self.right_child:
                    if entry.key == key:
                        return True
                return False
            else:
                raise KeyError
        else:
            raise Exception()

    def delete(self, key, bitstring):
        """
        Deletes a key-value pair from the value with the specified key.
        :param key: The key ordinate of the key-value pair.
        :param bitstring: The key as a partially consumed bitstring.
        """
        tree_key, consumed_key = consume_bitstring(bitstring, self.direction)
        if tree_key == LEFT_KEY:
            if isinstance(self.left_child, _DHTNode):
                self.left_child.delete(key, consumed_key)
            elif isinstance(self.left_child, SortedList):
                self.left_child.discard(key)
            else:
                raise Exception()
        elif tree_key == RIGHT_KEY:
            if isinstance(self.right_child, _DHTNode):
                self.right_child.delete(key, consumed_key)
            elif isinstance(self.right_child, SortedList):
                self.right_child.discard(key)
            else:
                raise Exception()
        else:
            raise KeyError()
        # can only underflow when we are a leaf node and both buckets are empty
        if (isinstance(self.left_child, SortedList) and not self.left_child and
                isinstance(self.right_child, SortedList) and not self.right_child):
            self._underflow()

    def get(self, key, bitstring):
        """
        Gets a value from the tree.
        :param key: The key to lookup.
        :param bitstring: A partially consumed bitstring version of the key.
        :return: The value corresponding to the first instance of the key, else None.
        """
        tree_key, consumed_key = consume_bitstring(bitstring, self.direction)
        if tree_key == LEFT_KEY:
            if isinstance(self.left_child, _DHTNode):
                return self.left_child.get(key, consumed_key)
            elif isinstance(self.left_child, SortedList):
                for entry in self.left_child:
                    if entry.key == key:
                        return entry.value
                return None
            else:
                raise KeyError
        elif tree_key == RIGHT_KEY:
            if isinstance(self.right_child, _DHTNode):
                return self.right_child.get(key, consumed_key)
            elif isinstance(self.right_child, SortedList):
                for entry in self.right_child:
                    if entry.key == key:
                        return entry.value
                return None
            else:
                raise KeyError
        else:
            raise Exception()

    def height(self):
        """
        Returns the height of this node.
        :return: The height of this node.
        """
        if isinstance(self.left_child, _DHTNode):
            left_height = self.left_child.height() + 1
        elif isinstance(self.left_child, SortedList):
            left_height = 1
        else:
            raise Exception()
        if isinstance(self.right_child, _DHTNode):
            right_height = self.right_child.height() + 1
        elif isinstance(self.right_child, SortedList):
            right_height = 1
        else:
            raise Exception()
        return max(left_height, right_height)

    def traverse(self):
        """
        Traverse the tree left to right yielding entries as key-value pairs.
        :return: A Python generator over the contents of the tree that yields key-value pairs.
        """
        if isinstance(self.left_child, SortedList):
            for entry in self.left_child:
                yield entry.key, entry.value
        elif isinstance(self.left_child, _DHTNode):
            yield from self.left_child.traverse()
        else:
            raise Exception()
        if isinstance(self.right_child, SortedList):
            for entry in self.right_child:
                yield entry.key, entry.value
        elif isinstance(self.right_child, _DHTNode):
            yield from self.right_child.traverse()
        else:
            raise Exception()

    def _overflow(self, tree_key):
        """
        Handles overflows when they occur. This process converts the node into an internal node and redistributes its
        data values between two new DHTNodes that take the place of `left` and `right`.
        :param tree_key: Key corresponding to the branch that overflowed, one of {LEFT_KEY, RIGHT_KEY}.
        """
        if tree_key == LEFT_KEY:
            if not isinstance(self.left_child, SortedList):
                raise Exception()
            new_left = _DHTNode(self, n=self.n, depth=self.depth+1)
            for entry in self.left_child:
                consumed_key = key_to_binary(entry.key)
                for i in range(self.depth):
                    _, consumed_key = consume_bitstring(consumed_key, self.direction)
                new_left.add(entry.key, consumed_key, entry.value)
            if self.parent is not None:
                self.parent.left_child = new_left
        elif tree_key == RIGHT_KEY:
            if not isinstance(self.right_child, SortedList):
                raise Exception()
            new_right = _DHTNode(self, n=self.n, depth=self.depth+1)
            for entry in self.right_child:
                consumed_key = key_to_binary(entry.key)
                for i in range(self.depth):
                    _, consumed_key = consume_bitstring(consumed_key, self.direction)
                new_right.add(entry.key, consumed_key, entry.value)
            if self.parent is not None:
                self.parent.right_child = new_right
        else:
            raise ValueError()
        self.internal = True

    def _underflow(self):
        """
        Handles underflows when they occur. An underflow occurs when a deletion causes a node branches to both have
        empty buckets. Collapses two empty branches into a single bucket.
        """
        self.left_child = None
        self.right_child = None
        if self.parent.left_child == self:
            self.parent.left_child = SortedList(key=extract_key)
        elif self.parent.right_child == self:
            self.parent.right_child = SortedList(key=extract_key)
        else:
            raise Exception
        self.internal = False


class BPT(object):
    """
    Implements a B+ tree.
    """

    def __init__(self, n=8, ff=0.75):
        """
        Returns a new instance of a B+ tree.
        :param n: The max number of keys to store in each node of the tree.
        :param ff: The maximum fill factor of each node in the tree.
        """
        self.n = n
        self.ff = ff
        self.root = _BPTNode(n=n, ff=ff)

    def add(self, key, value):
        """
        Adds a key-value pair to the tree.
        :param key: The key ordinate of the key-value pair.
        :param value: The value ordinate of the key-value pair.
        """
        self.root.add(key, value)

    def contains(self, key):
        """
        Determines if at least one entry exists in the tree with the given key ordinate.
        :param key: The key ordinate of the key-value pair.
        :return: True if a key-value pair is found in the tree containing the key ordinate, False otherwise.
        """
        return self.root.contains(key)

    def delete(self, key):
        """
        Deletes the first key-value pair found in the tree with the given key ordinate.
        :param key: The key ordinate of the key-value pair.
        """
        return self.root.delete(key)

    def get(self, key):
        """
        Retrieves the first corresponding value ordinate for an entry in the tree given a key ordinate.
        :param key: The key ordinate of the key-value pair.
        :return: A value if an entry is found, None otherwise.
        """
        return self.root.get(key)

    def height(self):
        """
        Returns the height of the tree.
        :return: The number of levels in the tree.
        """
        return self.root.height()

    def traverse(self):
        """
        Yields the key-value pairs in the tree in ordered fashion.
        :return: An ordered generator over the key-value pairs in the tree.
        """
        yield from self.root.traverse()


class DHT(object):
    """
    Implements a dynamic hash tree for use in indexing.
    """

    def __init__(self, n=8):
        """
        Returns a new instance of a DHT with a specified max number of entries per node.
        :param n: The max number of entries per node.
        """
        self.root = _DHTNode(n=n)

    def add(self, key, value):
        """
        Adds a key-value pair to the DHT.
        :param key: The key ordinate of the key-value pair.
        :param value: The value ordinate of the key-value pair.
        """
        self.root.add(key, key_to_binary(key), value)

    def contains(self, key):
        """
        Determines if the DHT contains a key-value pair given its key.
        :param key: The key ordinate of the key-value pair.
        :return: True if the DHT contains a key-value pair with the given key.
        """
        return self.root.contains(key, key_to_binary(key))

    def delete(self, key):
        """
        Deletes the first instance of a matching key-value pair with the given key.
        :param key: The key ordinate of the key-value pair.
        """
        self.root.delete(key, key_to_binary(key))

    def get(self, key):
        """
        Retrieves a the value from a key-value pair in the DHT.
        :param key: The key ordinate of the key-value pair to lookup.
        :return: The value if the key-value pair is found, otherwise None.
        """
        return self.root.get(key, key_to_binary(key))

    def height(self):
        """
        Gets the height of the DHT.
        :return: The height of the DHT.
        """
        return self.root.height()

    def traverse(self):
        """
        Traverse the tree left to right yielding entries as key-value pairs.
        :return: A Python generator over the contents of the tree that yields key-value pairs.
        """
        yield from self.root.traverse()


def test_bpt():
    sl = SortedList([
        _IndexEntry(0, None),
        _IndexEntry(5, None),
        _IndexEntry(10, None),
        _IndexEntry(15, None),
        _IndexEntry(20, None)
    ])
    print(sl.bisect_right(-3))
    print(sl.bisect_right(3))
    print(sl.bisect_right(7))
    print(sl.bisect_right(13))
    print(sl.bisect_right(17))
    print(sl.bisect_right(23))


def test_dht():
    items = [5, 1, 9, 3, 8, 2, 6, 0, 7]
    tree = DHT(n=3)
    for i in range(len(items)):
        tree.add(items[i], i)
    for key, value in tree.traverse():
        print("==> ({k}, {v})".format(k=key, v=value))
    assert tree.contains(9)
    assert tree.height() == 2
    assert tree.get(9) == 2
    print("Dynamic hash tree testing succeeded!")


if __name__ == '__main__':
    test_bpt()
