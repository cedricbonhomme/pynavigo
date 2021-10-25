#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cédric Bonhomme, Jose Hermida Prado"
__date__ = "$Date: 2012/03/20 $"
__revision__ = "$Date: 2012/04/03 $"
__license__ = ""

import sys
import simpleGraph

class RemoveIslands(object):
    """
    Remove islands in a graph. Return there
    biggest connected graph.
    """
    def __init__(self, graph):
        """
        Initializes variables and set the maximum recursion limit to
        the number of nodes.
        """
        self.graph = graph
        self.graphs = {}
        self.checked = []
        self.allnodes = []
        self.bigestGraph = []
        self.allnodes = self.graph.graph_structure.keys()
        sys.setrecursionlimit(len(self.allnodes))

    def getNodesIslands(self):
        n = 0
        maxi = 0;
        while True:
            self.checked = []
            self.getIsland(self.allnodes[0])
            if len(self.checked) > maxi:
                self.bigestGraph = self.checked
                maxi = len(self.checked)
            for node in self.checked:
                # remove of the list with all nodes the ones already used
                self.allnodes.remove(node)
            self.graphs[n] = {}
            self.graphs[n] = self.checked
            n = n + 1
            if len(self.allnodes) == 0:
                break
        #return self.graphs
        return self.bigestGraph

    def getIsland(self,node):
        if node in self.checked:
            return
        self.checked.append(node)
        try:
            # maybe there is a street of one way that finish in an isolated node
            # (think about an entrance for a parking..)
            for nod in self.graph.graph_structure[node]:
                self.getIsland(nod)
        except:
            return