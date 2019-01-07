from node import node

class LinkedList(object):
    head = None
    tail = None
    size = 0

    #O(1)
    def add(self, node):
        '''
        Adds a node to the chain
        '''
        if self.head is None: #adding first node to list
            self.head = self.tail = node
        else:
            node.previous = self.tail
            node.next = None
            self.tail.next = node
            self.tail = node
        self.size+=1
    #O(n)
    def remove(self, email):
        '''
        Remove a node based off of the email/username
        '''
        currNode = self.head
        while currNode is not None:
            if currNode.email is email:
                next = currNode.next
                previous = currNode.previous
                previous.next = next
                next.previous = previous
                currNode.next = None
                currNode.previous = None
                currNode = next
            else :
                currNode = currNode.next
    #O(n)
    def prnt(self):
        currNode = self.head
        while currNode is not None: 
            print(currNode.email)
            currNode = currNode.next
    pass




