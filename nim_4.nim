import algorithm
import strutils
import deques
import strformat

type
  Nucleotide {.pure.} = enum A, C, T, G, none

  Node = ref object
    character: char
    children: array[Nucleotide, Node]
    end_of_target: bool
    suffix_link: Node
    parent: Node

  Trie = ref object
    root: Node

proc toNucleotide(key: char): Nucleotide =
  case key
  of 'A': Nucleotide.A
  of 'C': Nucleotide.C
  of 'T': Nucleotide.T
  of 'G': Nucleotide.G
  else: Nucleotide.none

proc newNode(character: char, parent: Node = nil): Node =
  new result
  result.character = character
  result.parent = parent
  result.end_of_target = false

proc newTrie(): Trie =
  new result
  result.root =  newNode('\0')

proc get_string(startnode: Node): string =
  #Build string from terminal node by following ancestors back to root
  result = ""
  var node = startnode
  while node.parent != nil:
    result.add(node.character)
    node = node.parent
  reverse(result)

proc add_sequence(trie: Trie, sequence: string) =
  var
    stripped_sequence = sequence.strip()
    node: Node = trie.root
    nucleotide: Nucleotide
  for character in stripped_sequence:
    nucleotide = toNucleotide(character)
    if node.children[nucleotide] == nil:
      node.children[nucleotide] = newNode(character, node)
    node = node.children[nucleotide]
  node.end_of_target = true

proc make_suffix_links(trie: Trie) =
  #Use breadth first search to build the suffix links of the Trie
  #initialize queue with children of root
  var
    queue = initDeque[Node]()
    node: Node = trie.root
    suffix_node: Node
  for n in Nucleotide.low..Nucleotide.high:
    if node.children[n] != nil:
      queue.addLast(node.children[n])

  while queue.len > 0:
    node = queue.popFirst()
    suffix_node = node.parent.suffix_link # Get node pointed to by parent suffix_link
    for n in Nucleotide.low..Nucleotide.high: # add current node's children to queue
      if node.children[n] != nil:
        queue.addLast(node.children[n])
    while true:
      if suffix_node == nil: # Only the root doesn't have a suffix_link, so set suffix_link to root
        node.suffix_link = trie.root
        break
      # If candidate suffix node has edge with current char, follow edge to new node and set suffix_link to new node
      elif suffix_node.children[toNucleotide(node.character)] != nil:
        node.suffix_link = suffix_node.children[toNucleotide(node.character)]
        break
      # Otherwise, follow suffix link of candidate suffix node.
      else:
        suffix_node = suffix_node.suffix_link

proc build_trie(sequences: openArray[string]): Trie =
  var trie = newTrie()
  for sequence in sequences:
    trie.add_sequence(sequence.strip().toUpperAscii())
  make_suffix_links(trie)
  return trie

proc search(trie: Trie, sequence: string) =
  var
    node: Node = trie.root
    offset: int64 = 0
    character: char
    nucleotide: Nucleotide
    match: string

  while (offset < sequence.len):
    character = sequence[offset]
    nucleotide = toNucleotide(character)
    if node.children[nucleotide] == nil:
      if node == trie.root:
        offset += 1

      else: # follow the suffix link
        node = node.suffix_link
        if node == nil:
          node = trie.root
        elif node.end_of_target:
          match = get_string(node)
          echo &"{offset - len(match) + 1:08X}" & '\t' & match
    else: # edge exists from current node using char, so follow it
      node = node.children[nucleotide]
      if node.end_of_target: # We've reached a terminal node, return offset and matched sequence
        match = get_string(node)
        echo &"{offset - len(match) + 1:08X}" & '\t' & match
      offset+=1 # increment offset and look at next char

proc match_sequences(trie: Trie, fname: string) =
  var
    sequence: string

  let f : File = open(fname)
  sequence = f.readAll().strip().toUpperAscii()
  f.close()
  trie.search(sequence)

proc main() =
  var
    target_sequences: seq[string]

  let f : File = open("targets")
  for line in f.lines():
    target_sequences.add(line.strip().toUpperAscii())
  f.close()

  var trie = build_trie(target_sequences)

  const files = ["test_file"]

  for file in files:
    var file = files[0]
    echo file
    match_sequences(trie, file)
    stdout.write("\n")

when isMainModule:
  main()
