#! /usr/bin/env python
# -*- coding: utf-8 -*-

from priodict import priorityDictionary

class Dijkstra(object):
    """
    Implementation of Dijkstra.
    """
    def __init__(self, G, start, end=None):
        self.D = {}    # dictionary of final distances
        self.P = {}    # dictionary of predecessors
        self.Q = priorityDictionary()   # est.dist. of non-final vert.
        self.start = start
        self.Q[start] = 0

        for v in self.Q:
            self.D[v] = self.Q[v]
            if v == end:
                break

            for w in G[v]:
                if G[v][w].distance < 0:
                    continue
                vwLength = self.D[v] + G[v][w].distance
                if w in self.D:
                    if vwLength < self.D[w]: #cost must be greater than 0
                        raise ValueError, "Dijkstra: found better path to already-final vertex"
                elif w not in self.Q or vwLength < self.Q[w]:
                    self.Q[w] = vwLength
                    self.P[w] = v

    def get(self, end):
        try:
            Path = []
            cost = self.D[end]
            while True:
                Path.append(end)
                if end == self.start:
                    break
                end = self.P[end]
            Path.reverse()
            return (Path, cost)
        except Exception, e:
            #print e
            return ([], 0)