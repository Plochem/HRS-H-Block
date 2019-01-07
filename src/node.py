class node(object):
    previous = None
    next = None
    email = None
   
    def __init__(self, previous, next, email):
        '''
        Constructor for a node
        '''
        self.next = next
        self.previous = previous
        self.email = email
       
    pass




