#!/usr/bin/env python3
import sys
import glob
from functools import partial
import multiprocessing
import re
import os


class Node:
    def __init__(self, char, parent):
        self.char = char
        self.children = dict()
        self.end_of_target = False
        self.suffix_link = None
        self.parent = parent


class Trie:
    def __init__(self):
        self.root = Node('', None)

    def add_sequence(self, seq):
        seq = seq.strip()
        node = self.root
        for char in seq:
            if char not in node.children:
                node.children[char] = Node(char, parent=node)
            node = node.children[char]
        node.end_of_target = True

    def search(self, sequence):
        node = self.root
        counter = 0
        for char in sequence:
            if char not in node.children:
                return None
            node = node.children[char]
            counter += 1
            if node.end_of_target:
                return sequence[:counter]

    def search_suffix(self, sequence):
        node = self.root
        sequence = iter(sequence)
        try:
            counter = 0 # Keep track of offset from beginning of sequence
            char = next(sequence)
            while True:
                if char not in node.children:
                    # If we are at the root, there is no suffix link to follow.
                    if node is self.root:
                        counter += 1
                        char = next(sequence)
                    else:
                        node = node.suffix_link
                        if node.end_of_target:
                            return counter, get_string(node)
                else: # Edge exists from current node using char, so follow it
                    node = node.children[char]
                    if node.end_of_target: # We've reached a terminal node, return offset and matched sequence
                        return counter, get_string(node)
                    counter += 1 # Incremement offset and look at next char
                    char = next(sequence)

        except StopIteration:
            return counter, None


def build_trie(sequences):
    trie = Trie()
    for seq in sequences:
        trie.add_sequence(seq.strip().upper())
    make_suffix_links(trie)
    return trie


def make_suffix_links(trie):
    """Use breadth first search to build the suffix links of the Trie
    """
    # Initialize queue with children of root
    queue = [(k,v) for k,v in trie.root.children.items()]
    while queue:
        char, node = queue.pop(0)
        suffix_node = node.parent.suffix_link # Get node pointed to by parent suffix_link
        queue += [(k,v) for k,v in node.children.items()] # add current node's children to queue
        while True:
            if suffix_node is None: # Only the root doesn't have a suffix_link, so set suffix_link to root
                node.suffix_link = trie.root
                break
            # If candidate suffix node has edge with current char, follow edge to new node and set suffix_link to new node
            elif char in suffix_node.children:
                node.suffix_link = suffix_node.children[char]
                break
            # Otherwise, follow suffix link of candidate suffix node
            else:
                suffix_node = suffix_node.suffix_link


def get_string(node):
    """Build string from terminal node by following ancestors back to root
    """
    string_array = []
    while node:
        string_array.append(node.char)
        node = node.parent
    return ''.join(string_array[::-1])

def match_sequences(target_sequences, file):
    trie = build_trie(target_sequences)

    with open(file) as fin:
        dna_sequence = fin.read().strip().upper()
    i = 0
    matches = []
    while True:
        offset, match = trie.search_suffix(dna_sequence[i:])
        if match:
            matches.append('{0:09X}'.format(i + offset + 1 -len(match))+'\t'+match)
            i += offset + 2 - len(match)
        else:
            break
    return matches


def main(files, target_sequences):
    trie = build_trie(target_sequences)
    for file in files:
        print(file)
        with open(file) as fin:
            sequence = fin.read().strip().upper()
        i = 0
        while True:
            offset, match = trie.search_suffix(sequence[i:])
            if match:
                print('{0:09X}'.format(i + offset + 1 -len(match))+'\t'+match)
                i += offset + 2 - len(match)
            else:
                break

def main_parallel(files, target_sequences):
    extra_credit = {}
    match_seq_partial = partial(match_sequences, target_sequences)
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    with p:
        results = p.map(match_seq_partial, files)
        for file, matches in zip(files, results):
            print(file)
            for match in matches:
                print('\t' + match)
                idx, matched_seq = match.split()
                if matched_seq not in extra_credit:
                    extra_credit[matched_seq] = []
                extra_credit[matched_seq].append((idx, os.path.split(file)[1]))
            sys.stdout.write('\n')

    with open('extra_credit.txt', 'wt') as f:
        for k,v in extra_credit.items():
            f.write(k + '\n')
            for idx, matched_seq in v:
                f.write('\t' + idx + '\t' + matched_seq + '\n')
            f.write('\n')

if __name__ == '__main__':
    regex = re.compile('/hg19-GRCh37/chr([^\.]+).*')
    files = glob.glob('/hg19-GRCh37/*')
    files = [(regex.search(f).groups()[0],f) for f in files]
    files = sorted(files, key = lambda x: int(x[0]) if x[0].isdigit() else ord(x[0]))
    files = [f[1] for f in files]

    with open('targets') as f:
        target_sequences = [line.strip().upper() for line in f]

    main_parallel(files, target_sequences)
