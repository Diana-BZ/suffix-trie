# suffix-trie

### DNA Sequencing with Trie Structure and Suffix Links

For this assignment, the task is to match 4,965 target DNA sequences in the 24 chromosomes of the complete hg19 GRCh37 human genome. To do this, we create a Trie structure, load the target sequences, and scan the corpus to find matches. 
A major challenge we faced was resolving performance issues. The benchmark C# solution executes in about 4 minutes (4:09) on a 3.17GHz machine. We first attempt the task in Python (multithreaded), and then but also offer a single threaded Nim solution.

## Python Implementation:
We implemented a prefix trie using a dictionary for the edges of each node. Each node keeps track of the parent, the character, its children, suffix_link, and whether it is a terminal node.

For our first attempt with a prefix trie, the execution time was over two hours for a single file (chr1.dna). We assumed this was due to having to repeatedly begin the search again at the root and revisiting characters for partial matches. We suspected there was a way to avoid revisiting characters by adding suffix links.

To build a prefix trie, for each sequence, we start at the root and follow edges for the current character if it exists. If it does not exist, we add a new node as a child of the current node and follow it. We then get the next character in the target sequence. At the end of the target sequence, we label the current node as terminal.

Once the prefix trie is built, suffix links are added in a breadth first search starting at the root. The rules we used for adding suffix links are (e.g. for character A):
  Follow parent node w's suffix link to node x.
If node xA exists, wA has a suffix link to xA.
Otherwise, follow x's suffix link and repeat.
If you need to follow backwards from the root, then wA's suffix link points to the root

To search for a match to one of the target strings, We start at the beginning of the sequence and the root of the trie. If there is an edge from the current node using the current character, take the edge. Otherwise, keep following suffix links until there is an available edge, or we are at the root and cannot proceed. Then, look at the next character in the sequence. If we reach a terminal node, follow the parents back to the root to get the target string. Then, continue matching from the second character of the previously matched string. By starting at the second character, we will find overlapping target strings in the sequence. If we reach the end of the sequence without a match, there are no more target strings to find. We can then move on to the next chromosome.

Using suffix links takes the runtime of the largest file (chr1.dna) down from over 2 hours to a couple of minutes. By using Python's multiprocessing module to simultaneously match multiple files, the total runtime for all 23 files was under 6 ½ minutes using 8 cores and 10 GB of memory.


## Nim Solution:
https://repl.it/@diazhang/MakeSuffixes#main.nim

By comparison, the C# benchmark did not require the use of suffix links to perform the task in under 4 minutes for all DNA files. We suspected that since Python is an interpreted language, we needed to switch to a compiled language in order to make improvements in efficiency and speed. We decided to rewrite our system in Nim, a language that compiles to C. 

Our Nim system implements a prefix trie with suffix nodes, like our Python code. It also adds a type, Nucleotide. In our single threaded Nim solution, the runtime of all 23 files is approximately 3 1/2 minutes. 
