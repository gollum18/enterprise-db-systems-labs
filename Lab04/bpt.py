# Name: btp.py
# Since: 10/28/2019
# Author: Christen Ford
# Purpose: Implements a B+ tree (insertion only) for CIS 611: Enterprise
#   Databases and Parallel Database Processing lab 4.


import click
from sortedcontainers import SortedList


def split(parent, child):
    """Splits a node according to B+ tree insertion algorithm rules.

    Arguments:
        parent (_BPTNode): The parent of the node being split.
        child (_BPTNode): The node being split.
    """
    if child and parent and child.count() > child.n * child.ff:
        # create the left and right leafs
        left_leaf = _BPTNode(parent.n, parent.ff, False)
        right_leaf = _BPTNode(parent.n, parent.ff, False)
        left_leaf.next = right_leaf
        right_leaf.prev = left_leaf
        # stride the entries list so we dont process one entry at a time
        for i in range(len(child.entries)//2):
            left_entry = child.entries[i]
            right_entry = child.entries[i*2]
            left_leaf.add(_BPTEntry(left_entry.k, left_entry.v))
            right_leaf.add(_BPTEntry(right_entry.k, right_entry.v))
        # make this node an internal node
        parent.internal = True
        parent.entries.clear()
        parent.entries.add(_BPTEntry(k=left_leaf.last().k, lp=left_leaf))
        parent.entries.add(_BPTEntry(k=right_leaf.last().k, lp=right_leaf))


class BPTree(object):
    """Implements a 'public' B+ tree class. This class is invoked by clients
    to utilize the underlying B+ tree algorithms to for example, build effective
    indexes.
    """

    def __init__(self, n=5, ff=0.75):
        """Returns a new instance of a BPTree object. Each node contains a
        maximum of 'n' keys and 'n+1' pointers and is filled to a fill factor
        of 'ff'.

        Arguments:
            n (int): The max number of keys per node. int n | n >= 5
            (default: 5).
            ff (float): The fill factor for each node. float ff | 0 < bf < 1,
            (default: 0.75).

        Returns:
            (BPTree): An instance of a B+ tree with 'n' keys per node and
            'ff' fill factor.
        """
        if n < 5:
            n = 5
        self.n = n
        if ff <= 0 or ff >= 1:
            ff = 0.75
        self.ff = ff
        self.root = _BPTNode(n=n, ff=ff)


    def add(self, k, v):
        """Adds a key-value pair to the B+ tree.

        Arguments:
            k (int): The key to add to the tree.
            v (object): The value to add to the tree.
        """
        if not self.root:
            raise Exception()
        split(self.root, self.root.add(k, v))


    def contains(self, k):
        """Determines if the B+ tree contains an entry with the specified key.

        Arguments:
            k (int): The key to search for.

        Returns:
            (boolean): True if at least one entry was found with the key,
            False otherwise.
        """
        if not self.root:
            raise Exception()
        return self.root.contains(k)


    def iterate(self):
        """Returns a Python generator over the entries in the B+ tree.

        Returns:
            (generator): A generator over the entries in the B+ tree.
        """
        if not self.root:
            raise Exception()
        for entry in self.root.iterate():
            yield entry


    def get(self, k):
        """Gets the value of the first appearance of key 'k' in the B+ tree.

        Arguments:
            k (int): The key corresponding to the value to retrieve.
        """
        if not self.root:
            raise Exception()
        return self.root.get(k)


    def height(self):
        """Returns the height of the B+ tree.

        Returns:
            (int): The height of the B+ tree.
        """
        if not self.root:
            raise Exception()
        return self.root.height()


    def remove(self, k):
        """Removes the entry pointed to by k.

        Arguments
            k (int): A key corresponding to an entry to remove.
        """
        if not self.root:
            raise Exception()
        return self.root.remove(k)


    def size(self):
        """Returns the number of key-value pairs stored in the entire B+ tree.

        Returns:
            (int): The number of key-value pairs in the B+ tree.
        """
        if not self.root:
            raise Exception()
        return self.root.size()


class _BPTEntry(object):
    """Implements a 'private' representing an entry in a B+ tree.

    For the purposes of safely resolving ambiguity on tree operations,
    each BPTEntry only contains a pointer to the left (<) sub-tree."""

    def __init__(self, k, v=None, lp=None):
        """Returns a new instance of a BPTEntry object.

        Arguments:
            k (int): The key for a B+ tree entry - always an integer.
            v (object): A value or record pointer (default: None).
            lp (BPTNode): A pointer to the left sub-tree (default: None).

        Returns:
            (BPTEntry): An entry in a B+ tree.
        """
        self.k = k
        self.v = v
        self.lp = None


    # Implement comparing methods for sortedcontainers support.
    # Raise a ValueError on None or for classes that are not a BPTEntry.
    # This class can only be compared against an instance of itself, other
    #   classes are not supported.
    def __eq__(self, other):
        """Determines whether this BPTEntry is equal to another BPTEntry.

        Argument:
            other (BPTEntry): An instance of a BPTEntry object.
        """
        if not other:
            raise ValueError

        if not isinstance(other, _BPTEntry):
            raise ValueError

        return self.k == other.k


    def __lt__(self, other):
        """Determines whether this BPTEntry is less than another BPTEntry.

        Argument:
            other (BPTEntry): An instance of a BPTEntry object.
        """
        if not other:
            raise ValueError

        if not isinstance(other, _BPTEntry):
            raise ValueError

        return self.k < other.k


    def __le__(self, other):
        """Determines whether this BPTEntry is less than or equal to another
        BPTEntry.

        Argument:
            other (BPTEntry): An instance of a BPTEntry object.
        """
        if not other:
            raise ValueError

        if not isinstance(other, _BPTEntry):
            raise ValueError

        return self.k <= other.k


    def __gt__(self, other):
        """Determines whether this BPTEntry is greater than another BPTEntry.

        Argument:
            other (BPTEntry): An instance of a BPTEntry object.
        """
        if not other:
            raise ValueError

        if not isinstance(other, _BPTEntry):
            raise ValueError

        return self.k > other.k


    def __ge__(self, other):
        """Determines whether this BPTEntry is greater than or equal to another
        BPTEntry.

        Argument:
            other (BPTEntry): An instance of a BPTEntry object.
        """
        if not other:
            raise ValueError

        if not isinstance(other, _BPTEntry):
            raise ValueError

        return self.k >= other.k


class _BPTNode(object):
    """Implements a 'private' class representing a B+ tree node.

    A B+ tree node can be in one of two states:
        1.) Internal (index) node
        2.) Leaf (data) node
    Which state the node is in ultimately drives the behavior of the
    underlying B+ tree algorithms.
    """

    def __init__(self, n=5, ff=0.75, internal=False, prev=None, next=None):
        """Returns a new instance of a BPTNode object. Each node contains a
        maximum of 'n' keys and 'n+1' pointers and is filled to a fill factor
        of 'ff'.

        Arguments:
            n (int): The max number of keys per node. int n | n >= 5
            (default: 5)
            ff (float): The fill factor for each node. float ff | 0 < bf < 1,
            (default: 0.75)
            internal (boolean): If True the node is an internal node, otherwise
            it is a leaf node.
            prev (BPTNode|None): The prior BPTNode (default: None).
            next (BPTNode|None): The next BPTNode (default: None).

        Returns:
            (BPTNode): An instance of a B+ tree node with 'n' keys per node
            and 'ff' fill factor.
        """
        # used to control the underlying B+ tree algorithms
        self.n = n
        self.ff = ff
        self.internal = internal
        # the next and previous sibling leaf lodes
        self.prev = None
        self.next = None
        # the key-pointer entries
        self.entries = SortedList(key=lambda e: e.k)


    def add(self, k, v=None):
        """Adds a key-value pair to the B+ tree node. As a convenience,
        'v' defaults to None for use in adding entries to internal nodes
        since internal nodes do not contain values.

        Arguments:
            k (int): The key for the entry.
            v (object|None): The value for the entry (default: None).
        """
        # move to the correct leaf node
        inserted_node = None
        if self.internal:
            for entry in self.entries:
                if entry.k <= k:
                    inserted_node = entry.lp.add(k, v)
                    break
        else: # in the leaf node
            self.entries.add(_BPTEntry(k, v))
            return self
        # did the insertion cause an overflow? split the node if so
        print('Inserted node:', inserted_node)
        split(self, inserted_node)
        return self


    def contains(self, k):
        """Determines if the B+ tree contains an entry with the given key
        value.

        Arguments:
            k (int): The key to search for.

        Returns:
            (boolean): True if at least one entry was found with the key,
            False otherwise.

        Note: This function may be optimized by storing a bloom filter in
        each node and updating it appropriately on each insert. This way
        we gain a chance to skip thorough checking of a key.
        """
        if not self.internal:
            for entry in self.entries:
                if entry.k == k:
                    return True
            if self.next:
                return self.next.contains(k)
            else:
                return False
        else:
            return self.entries[0].lp.contains(k)


    def count(self):
        """Returns the number of entries stored in this B+ tree node.

        Returns:
            (int): The number of entries in this B+ tree node.
        """
        return len(self.entries)


    def first(self):
        """Returns the first entry in the entries list.

        Returns:
            (_BPTEntry): The first entry in the entries list (entry with
            lowest key).

        Raises:
            (Exception): If the entries list is empty or does not exist.
        """
        if not self.entries:
            raise Exception()
        return self.entries[0]


    def get(self, k):
        """Retrieves the value corresponding to the given key.

        Arguments:
            k (int): The key to lookup.

        Returns:
            (object|None): The corresponding key in the tree or None if
            the key does not exist.
        """
        if not self.internal:
            for entry in self.entries:
                if entry.k == k:
                    return entry.v
            # call get on the next sibling
            if self.next:
                self.next.get(k)
        else:
            self.entries[0].lp.get(k)


    def height(self):
        """Returns the height of the B+ tree.

        Returns:
            (int): The height of the B+ tree.
        """
        if not self.internal:
            return 1
        return self.entries[0].lp.height() + 1


    def iterate(self):
        """Returns a Python generator over the key-value entries in the B+
        tree.

        Returns:
            (generator): Python generator that iterates an ordered list of
            (k, v) pairs.
        """
        if self.internal:
            yield self.entries[0].lp.iterate()
        else:
            for entry in self.entries:
                yield (entry.k, entry.v)
            if self.next:
                yield self.next.iterate()


    def last(self):
        """Returns the last entry in the entries list.

        Returns:
            (_BPTEntry): The last entry in the entries list (the entry with
            the greatest key).

        Raises:
            (Exception): If the entries list is empty or does not exist.
        """
        if not self.entries:
            raise Exception()
        return self.entries[-1]


    def remove(self, k):
        """Removes the entry pointed to by k.

        Arguments
            k (int): A key corresponding to an entry to remove.
        """
        pass


    def size(self):
        """Returns the number of key-value pairs stored in the entire B+ tree.

        Returns:
            (int): The number of key-value pairs in the B+ tree.
        """
        if not self.internal:
            s = self.count()
            if self.next:
                s += self.next.count()
            return s
        else:
            return self.entries[0].size()


@click.command()
@click.option('-n', '--max-keys', default=5)
@click.option('-ff', '--fill-factor', default=0.75)
def test_bpt(max_keys=5, fill_factor=0.75):
    items = [0, 55, 24, 88, 11, 90, 70, 6, 17, 33]
    tree = BPTree(max_keys, fill_factor)
    for i in range(len(items)):
        tree.add(items[i], i)
    print('Items in tree: {n}'.format(n=tree.size()))
    print('Height of tree: {n}'.format(n=tree.height()))
    print('Tree contents:')
    for entry in tree.iterate():
        print('==> Key: {k}, Value: {v}'.format(k=entry[0], v=entry[1]))


if __name__ == '__main__':
    test_bpt()
