
"""
COMS W4705 - Natural Language Processing - Fall 2020  
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        
        start_symbol = self.grammar.startsymbol
        parse_table = defaultdict(dict)
        for idx in range(len(tokens)):
            for rule in self.grammar.rhs_to_rules[(tokens[idx],)]:
                parse_table[(idx, idx + 1)][rule[0]] = rule[1][0]
        for span_length in range(2, len(tokens) + 1):
            for start_idx in range(len(tokens) - span_length + 1):
                end_idx = start_idx + span_length
                for split_point in range(start_idx + 1, end_idx):
                    for lhs, _ in parse_table[(start_idx, split_point)].items():
                        for rhs, _ in parse_table[(split_point, end_idx)].items():
                            for prod_rule in self.grammar.rhs_to_rules[(lhs, rhs)]:
                                parse_table[(start_idx, end_idx)].setdefault(prod_rule[0], ((lhs, start_idx, split_point), (rhs, split_point, end_idx)))
        return True if start_symbol in parse_table[(0, len(tokens))] else False
        

       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        parse_chart = defaultdict(dict)
        log_probs = defaultdict(dict)
        for index in range(len(tokens)):
            for rule in self.grammar.rhs_to_rules[(tokens[index],)]:
                parse_chart[(index, index + 1)][rule[0]] = tokens[index]
                log_probs[(index, index + 1)][rule[0]] = math.log(rule[2])
        for span in range(2, len(tokens) + 1):
            for start in range(len(tokens) - span + 1):
                end = start + span
                for split in range(start + 1, end):
                    for left_nt, left_prob in log_probs[(start, split)].items():
                        for right_nt, right_prob in log_probs[(split, end)].items():
                            for production in self.grammar.rhs_to_rules[(left_nt, right_nt)]:
                                current_prob = math.log(production[2]) + left_prob + right_prob
                                if production[0] not in log_probs[(start, end)] or current_prob > log_probs[(start, end)][production[0]]:
                                    log_probs[(start, end)][production[0]] = current_prob
                                    parse_chart[(start, end)][production[0]] = ((left_nt, start, split), (right_nt, split, end))
        return parse_chart, log_probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
  
    if nt not in chart[(i, j)]:
        raise KeyError("Non-terminal not found in chart for given span.")
    if j - i == 1:
        return (nt, chart[(i, j)][nt])  # Base case 
    else:
        
        left_bp = chart[(i, j)][nt][0]
        right_bp = chart[(i, j)][nt][1]
        # Recursive calls to construct the left and right subtrees
        left_subtree = get_tree(chart, left_bp[1], left_bp[2], left_bp[0])
        right_subtree = get_tree(chart, right_bp[1], right_bp[2], right_bp[0])
    return (nt, left_subtree, right_subtree)

 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        