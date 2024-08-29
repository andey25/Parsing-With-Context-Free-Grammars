"""
COMS W4705 - Natural Language Processing - Fall 20 
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum, isclose

# the codes were run on VSCode directly instead of cmd, that's why 
# there have been slight modification of the code to run the file

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    
   
    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise, return False. 
        """
        nonterminals = set(self.lhs_to_rules.keys())  

        # Checking CNF compliance and probability sums
        for lhs, rules in self.lhs_to_rules.items():
            total_prob = 0.0
            for rule in rules:
                _, rhs, prob = rule
                total_prob += prob

               
                if len(rhs) == 2:  # A -> B C
                    if not all(rhs_part in nonterminals for rhs_part in rhs):
                        return False
                elif len(rhs) == 1:  # A -> a
                    if rhs[0] in nonterminals:  
                        return False
                else:  
                    return False

            # Probability sum check
            if not isclose(total_prob, 1.0, rel_tol=1e-9):
                return False

        return True  



# if __name__ == "__main__":
#     with open(sys.argv[1],'r') as grammar_file:
#         grammar = Pcfg(grammar_file)
    


if __name__ == "__main__":
    dataset_path = 'atis3.pcfg'

    with open(dataset_path, 'r') as grammar_file:
        grammar = Pcfg(grammar_file)

   