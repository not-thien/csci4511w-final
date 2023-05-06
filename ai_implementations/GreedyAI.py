import random 

class Node:
    #Construction
    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}
        self.value = None
        self.word = None
        self.level = parent.level + 1 if parent is not None else 0
        self.total_successors = 0

    #Add
    #Recursive function which adds new words to the tree, then updates the number of total sucessors
    def add(self, word, final_word = None):
        #Update the Value of the Current Node
        self.value = word[0]

        if final_word is None:
            final_word = word

        #Add the remaining letters in the word to the tree
        #Base Case: If there are no other letters to add return 1 as parents total successors
        if len(word) == 1:
            #If word length is 1, then we are at level 5 and there are no other valid words
            self.word = final_word
            self.total_successors = 1
            return

        #Trim Word at Head and then add remainder recursively
        #Since we are not in the base case, we know that we have at least 1 more successor than us at this node
        self.total_successors += 1
        word = word[1:]
        next_val = word[0]

        if next_val not in self.children:
            self.children[next_val] = Node(self)

        self.children[next_val].add(word, final_word)


    def remove(self, successors=None):
        #Hard Delete Case: Actually Delete the Node Instead of Simply Update the Total Number of Scuccessors UpStream
        if successors is None:
            self.parent.children.pop(self.value, None)
            successors = self.total_successors

        self.total_successors -= successors

        if self.parent is not None:
            self.parent.remove(successors)

class NodeCollection:
    def __init__(self):
        self.Root = Node(None)
        self.LockedLetters = [None, None, None, None, None, None]
    
    # load all words
    def AddDictionary(self, path):
        with open(path, 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) == 5:
                    line = "#" + line.lower()
                    self.Root.add(line)
    
    #Green Letter Sceanrio. Delete all of the letters at a certain level\slot which are not the specified value.
    def LockLetter(self, level, value):
        self.LockedLetters[level] = value
        self._LockLetter(level, value, self.Root)
    
    def _LockLetter(self, level, value, search):
        if search == None:
            return
        #Go Deeper if we are not on the right level
        if search.level < level:
            for node_key in list(search.children.keys()):
                node = search.children[node_key]
                self._LockLetter(level, value, node)
        #If we are at the desired level, remove any nodes which are not the letter
        if search.level == level and search.value != value:
            search.remove()
    
    #Grey Letter Scenario. Remove all instances of a letter from the tree
    def RemoveLetter(self, value):
        self._RemoveLetter(value, self.Root)
    
    def _RemoveLetter(self, value, search):
        #Base Case. No expansion needed if searcb  node is null
        if search == None:
            return
        #Base Case. If the search node is the value we are looking for, delete it and as a result all of it's successors
        if search.value == value and self.isNotLocked(search):
            search.remove()
            return
        #Expand each of the children looking for the value of interest
        for node_key in list(search.children.keys()):
            node = search.children[node_key]
            self._RemoveLetter(value, node)

    def FloatLetter(self, levels, value):
        for level in levels:
            self.RemoveLetterAtLevel(level, value, self.Root)
        self.MustHaveLetter(value, len(levels), self.Root, 0)

    def MustHaveLetter(self, value, occurrences, search, found):
        if search is None:
            return
        
        if search.value == value and self.isNotLocked(search):
            found += 1
        
        if found >= occurrences:
            return
        
        if search.level == 5 and found < occurrences:
            search.remove()
            return
        
        for node_key in list(search.children.keys()):
            node = search.children[node_key]
            self.MustHaveLetter(value, occurrences, node, found)
    
    def RemoveLetterAtLevel(self, level, value, search):
        if search is None:
            return
        
        if search.level > level:
            return
        
        if search.level + 1 == level and value in search.children and search.children[value] is not None and self.isNotLocked(search.children[value]):
            search.children[value].remove()
            return
        
        if search.level + 1 < level:
            for node in search.children.values():
                self.RemoveLetterAtLevel(level, value, node)
    
    def isNotLocked(self, node):
        return self.LockedLetters[node.level] != node.value

    def MostLikely(self):
        return self._MostLikely(self.Root)

    def _MostLikely(self, search):
        maxSuccessors = float('-inf')
        maxNode = None

        # Find which of the children has the highest number of children
        for node in search.children.values():
            if node is not None and node.total_successors > maxSuccessors:
                maxSuccessors = node.total_successors
                maxNode = node

        # Base Case: We are at the bottom of the tree and need to return the most likely word
        if maxNode.level == 5:
            return maxNode.word
        else:
            return self._MostLikely(maxNode)

    def RandomSearch(self):
        search = Root
        r = random.Random()

        while search.level < 5:
            children = list(search.children.values())
            index = r.randrange(len(children))

            if children[index] is not None and children[index].total_successors > 0:
                search = children[index]

        return search.word

def main():
    nc = NodeCollection()
    nc.AddDictionary("data\official\shuffled_real_wordles.txt")
    nc.RemoveLetter('s')
    nc.RemoveLetter('t')
    nc.RemoveLetter('i')
    nc.RemoveLetter('d')
    nc.FloatLetter([2], 'a')
    nc.LockLetter(1, 'a')
    nc.RemoveLetter('l')
    nc.RemoveLetter('o')
    nc.RemoveLetter('y')
    nc.RemoveLetter('m')
    nc.RemoveLetter('a') # works cuz it checks if letter is confirmed or not before removal
    nc.RemoveLetter('z')
    nc.FloatLetter([5], 'e')
    print(nc.MostLikely())

if __name__ == "__main__":
    main()