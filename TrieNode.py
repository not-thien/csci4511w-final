class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.is_word = True

    def build(self, word_list):
        for word in word_list:
            self.insert(word)

    def leftmost_word(self):
        node = self.root
        word = ""
        while node.children:
            char, child_node = sorted(node.children.items())[0]
            word += char
            node = child_node
        return word