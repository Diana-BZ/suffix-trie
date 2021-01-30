# suffix-trie

We implemented a prefix trie using a dictionary for the edges of each node. Each node keeps track of the parent, the character, its children, suffix_link, and whether it is a terminal node.

For our first attempt with a prefix trie, the execution time was over two hours for a single file. We assumed this was due to having to repeatedly begin the search again at the root and revisiting characters for partial matches. We suspected there was a way to avoid revisiting characters by adding suffix links.

To build a prefix trie, for each sequence, we start at the root and follow edges for the current character if it exists. If it does not exist, we add a new node as a child of the current node and follow it. We then get the next character in the target sequence. At the end of the target sequence, we label the current node as terminal.

Once the prefix trie is built, suffix links are added in a breadth first search starting at the root. The rules I used for adding suffix links are (e.g. for character A):
  -Follow parent node w's suffix link to node x.
  -If node xA exists, wA has a suffix link to xA.
  -Otherwise, follow x's suffix link and repeat.
  -If you need to follow backwards from the root, then wA's suffix link points to the root

In Python, using suffix links takes the runtime of the largest file down from over 2 hours to a couple of minutes. 

In Nim, the runtime of the largest file 24 times is approximately 3 1/2 minutes.

Notes:
Makes it go faster: nim -d:release c main.nim

To run an example:https://repl.it/@diazhang/MakeSuffixes#main.nim 
