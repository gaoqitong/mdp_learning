from __future__ import division
import random
import numpy as np
from collections import deque
import os
import networkx as nx
import time


class Rabin_Automaton(object):
    
    def __init__(self, ltl, coord_dict):
        self.ltl = ltl
        self.coord_dict = coord_dict

        with open("my.ltl", "w") as ltlfile:
            ltlfile.write(ltl)
        os.system("ltlfilt -l -F \"my.ltl\" --output=\"my.ltl\" ")
        os.system("./ltl2dstar --ltl2nba=spin:ltl2ba --stutter=no --output-format=dot my.ltl my.dot")
        rabin_graph = nx.nx_agraph.read_dot("my.dot")
        rabin_graph.remove_nodes_from(["comment", "type"])
        
        self.graph = rabin_graph
        self.num_of_nodes = len(self.graph.node)
        
        self.accept = [int(i) for i in self.graph.node if "+0" in self.graph.node[i]["label"]]
        self.reject = [int(i) for i in self.graph.node if "-0" in self.graph.node[i]["label"]]
        
        self.deadlock = []
        for i in self.reject:
            if str(i) in self.graph[str(i)].keys():
                if " true" in [ self.graph[str(i)][str(i)][j]["label"] 
                              for j in range(len(self.graph[str(i)][str(i)])) ]:
                    self.deadlock.append(i)
        
        for i in self.graph.node:
            if "fillcolor" in self.graph.node[i].keys():
                if self.graph.node[i]["fillcolor"] == "grey":
                    self.init_state = int(i)
                    break
        
    def get_graph(self):
        return self.graph
    
    def get_init_state(self):
        return self.init_state
    
    def next_state(self, current_state, next_coord):
        ap_next = self.coord_dict[tuple(next_coord)]
        next_states = self.possible_states(current_state[2])
        for i in next_states:
            next_state_aps = [self.graph[str(current_state[2])][str(i)][k]["label"] 
                              for k in range(len(self.graph[str(current_state[2])][str(i)]))]
            # May need to change later
            if " true" in next_state_aps:
                return current_state[-1]
            else:
                for j in next_state_aps:
                    if self.check_ap(ap_next, j):
                        return i
                
    def possible_states(self, current_rabin_state):
        return [int(i) for i in self.graph[str(current_rabin_state)].keys()]
    
    def check_ap(self, ap_next, ap_sentence):
        pos, neg = seperate_ap_sentence(ap_sentence)
        if set(ap_next).issuperset(set(pos)) and self.check_neg(ap_next, neg):
            return True
        return False
    
    def check_neg(self, ap, negs):
        for i in ap:
            if i in negs:
                return False
        return True
        
def seperate_ap_sentence(input_str):
        if len(input_str)>1:
            index = find_ampersand(input_str)
            if len(index)>=1:
                return_str = [input_str[0:index[0]]]
            else:
                return_str = input_str
                if '!' in return_str:
                    return [],[return_str.replace('!','')]
                else:
                    return [return_str],[]
            for i in range(1,len(index)):
                return_str += [input_str[index[i-1]+1:index[i]]]
            return_str = return_str + [input_str[index[-1]+1:]]
            return_str = [i.replace(' ','') for i in return_str]
        elif len(input_str)==1:
            return_str = input_str
        elif len(input_str) == 0:    
            raise AttributeError('input_str has no length')
            
        without_negs = []
        negations = []
        for i in range(len(return_str)):
            if '!' in return_str[i]:
                negations += [return_str[i].replace('!','')]
            else:
                without_negs += [return_str[i]]
        return without_negs,negations
    
def find_ampersand(input_str):
        index = []
        original_length = len(input_str)
        original_str = input_str
        while input_str.find('&')>=0:
            index += [input_str.index('&')-len(input_str)+original_length]
            input_str = original_str[index[-1]+1:]
        return index