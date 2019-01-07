from node import node

class LinkedList(object):
    head = None
    tail = None
    size = 0
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
    def remove(self, email):
        '''
        Remove a node based off of the email/username
        '''
        currNode = head
        while currNode.next is not None: 
            if currNode.email is email:
                currNode.previous.next = currNode.next
                currNode.next,previous = currNode.previous
            else :
                currNode = currNode.next

    pass




