#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2012/03/17 $"
__revision__ = "$Date: 2012/05/10 $"
__copyright__ = "Copyright (c) 2013-2021 Cedric Bonhomme"
__license__ = ""

from . import dijkstra
from . import isolated
from . import utils


class Node(object):
    """
    Represent a node.
    """

    def __init__(self, osm_id, longitude, latitude):
        """
        Components of a node.
        """
        self.osm_id = osm_id
        self.longitude = longitude
        self.latitude = latitude
        self.use = 0

    def __str__(self):
        """
        Display.
        """
        return str(self.osm_id) + " " + str(self.latitude) + " " + str(self.longitude)


class Edge(object):
    """
    Represent an edge (can be oriented).
    """

    def __init__(self, fromnode, tonode, time, distance, speed):
        self.fromnode = fromnode
        self.tonode = tonode
        self.time = time
        self.distance = distance
        self.speed = speed

    def __str__(self):
        """
        Display.
        """
        return str(self.time) + " " + str(self.distance) + " " + str(self.speed)

    def __repr__(self):
        return str(self.distance)


class Way(object):
    """
    Represent an OSM way. In our graph structure an OSM way
    is represented by one ore more edges.
    """

    def __init__(self, refs, oneway, speed_limit=50):
        """
        A way can be one sided.
        """
        self.refs = refs
        self.oneway = oneway
        self.speed_limit = speed_limit

    def __str__(self):
        """
        Display.
        """
        return str(self.refs)


class Graph(object):
    """Represent a graph.

    A graph is represented with dictionaries.
    http://www.python.org/doc/essays/graphs/
    """

    def __init__(self):
        """
        Initializes the graph.
        """
        self.graph_structure = {}
        self.graph_info = {}
        self.ways = []

    def addNode(self, node_id, longitude, latitude):
        """
        Adds a node with no neighbors.
        """
        if node_id not in list(self.graph_structure.keys()):
            self.graph_structure[node_id] = {}
            self.graph_info[node_id] = Node(node_id, longitude, latitude)

    def get_node(self, osm_id):
        """
        Return a Node object.
        """
        try:
            return self.graph_info[osm_id]
        except:
            return None

    def removeNode(self, node_id):
        """
        Delete a node from the graph.
        """
        for neighbor_id in list(self.graph_structure[node_id].keys()):
            del self.graph_structure[neighbor_id][node_id]
        del self.graph_structure[node_id]
        del self.graph_info[node_id]

    def removeEdge(self, node_id, neighbor_id, oriented=False):
        """
        Delete an edge from the graph.
        """
        del self.graph_structure[node_id][neighbor_id]
        if oriented == False:
            del self.graph_structure[neighbor_id][node_id]

    def remove_isolated_nodes(self):
        """
        Remove nodes with no relation.
        """
        isolated_nodes = [
            node
            for node in list(self.graph_structure.keys())
            if self.graph_structure[node] == {}
        ]
        for node in isolated_nodes:
            self.removeNode(node)
        return len(isolated_nodes)

    def remove_islands(self):
        """
        Reduce to the biggest connected graph.
        """
        remove = isolated.RemoveIslands(self)
        biggest_connected_graph = remove.getNodesIslands()

        for node in list(self.graph_structure.keys()):
            if node not in biggest_connected_graph:
                self.removeNode(node)

    def len_way(self, way):
        """
        Return the length in meter of a way.
        """
        way_list = list(zip(way, way[1:]))
        return sum(
            [self.graph_structure[edge[0]][edge[1]].distance for edge in way_list]
        )

    def time_way(self, way):
        """
        Returns the time needed to cross a way.
        """
        way_list = list(zip(way, way[1:]))
        return sum(
            [
                self.graph_structure[edge[0]][edge[1]].distance
                / (self.graph_structure[edge[0]][edge[1]].speed * 1000)
                for edge in way_list
            ]
        )

    def average_speed(self, path):
        """
        Evaluates the average speed of a path.
        """
        way_list = list(zip(path, path[1:]))
        l = [self.graph_structure[edge[0]][edge[1]].speed for edge in way_list]
        try:
            return sum(l) / len(l)
        except ZeroDivisionError:
            return 90

    def osm_node_from_coordinates(self, latitude, longitude):
        """
        Given a point in the map (latitude, longitude)
        returns the closest OSM node of the graph.
        """
        result = None
        distance_min = float("inf")
        for node in list(self.graph_info.values()):
            distance = utils.EarthDistance(
                (latitude, longitude), (node.latitude, node.longitude)
            )
            if distance <= distance_min:
                distance_min = distance
                result = node
        return result.osm_id, result.latitude, result.longitude

    def nb_nodes(self):
        """
        Return the number of nodes.
        """
        return len(list(self.graph_info.keys()))

    def nb_edges(self, oriented=False):
        """
        Return the number of edges.
        """
        count = 0
        if oriented:
            for i in list(self.graph_structure.keys()):
                for j in list(self.graph_structure[i].keys()):
                    if self.graph_structure[i][j].distance != float("inf"):
                        count += 1
        else:
            count = (
                sum(
                    [
                        len(list(self.graph_structure[i].keys()))
                        for i in list(self.graph_structure.keys())
                    ]
                )
                / 2
            )
        return count

    def matrix(self):
        """
        Matrix display of the graph.
        """
        print(" ", end=" ")
        for i in sorted(self.graph_structure.keys()):
            print(i, end=" ")
        print()
        for i in sorted(self.graph_structure.keys()):
            print(i, end=" ")
            for j in sorted(self.graph_structure.keys()):
                if i in list(self.graph_structure[j].keys()):
                    # print self.graph_structure[i][j],
                    print("1", end=" ")
                else:
                    print("0", end=" ")
            print()

    def adjacency_list(self):
        """
        Displays the graph as an adjacency lists.
        """
        for i in sorted(self.graph_structure.keys()):
            print(i, " --> ", end=" ")
            print(list(self.graph_structure[i].items()))

    def __eq__(self, graphe1):
        """ """
        return self.graph_structure == graphe1

    def __str__(self):
        """
        Pretty display of the graph (adjacency lists).
        """
        result = ""
        for i in sorted(self.graph_structure.keys()):
            result += str(i) + " --> "
            result += (
                ", ".join([str(elem) for elem in list(self.graph_structure[i].keys())])
                + "\n"
            )
        return result

    def __repr__(self):
        """
        Representation of the graph.
        """
        return repr(self.graph_structure)

    def addWay(self, refs, oneway, speed_limit=50):
        """
        Add a way in the list of ways.
        A way is a sorted list of OSM node.
        In the graph a way could be composed of directed edges.
        """
        way = Way(refs, oneway, speed_limit)
        # add the new way
        self.ways.append(way)

        # Counts the number of connection of each nodes
        # of the current way.
        for ref in refs:
            try:
                self.graph_info[ref].use += 1
            except:
                print("Key Error with node id:", ref)
                pass

    def addEdge(self, fromnode, tonode, distance, speed_limit=None, oneway=False):
        """
        Add a directed edge with a cost (distance).
        An edge is a part of a way.
        """
        self.graph_structure[fromnode][tonode] = Edge(
            fromnode, tonode, None, distance, speed_limit
        )  # TODO: None should be the time
        if not oneway:
            self.graph_structure[tonode][fromnode] = Edge(
                tonode, fromnode, None, distance, speed_limit
            )
        else:
            self.graph_structure[tonode][fromnode] = Edge(
                tonode, fromnode, None, float("inf"), speed_limit
            )

    def create_graph_structure(self):
        """
        Creates the structure of the graph with the nodes that were
        previously stored in self.ways.
        """

        # Option 1 - Keep only the fist and last node of ways (save CPU usage but less accurate).
        # for way in self.ways:
        # fromnode = way.refs[0]
        # tonode = way.refs[-1]
        # try:
        # distance = utils.EarthDistance((self.graph_info[fromnode].latitude, self.graph_info[fromnode].longitude), \
        # (self.graph_info[tonode].latitude, self.graph_info[tonode].longitude))
        # self.addEdge(fromnode, tonode, distance, way.oneway)
        # except:
        # pass

        # Option 2 - All nodes are loaded in the graph (more CPU usage and more accurate).
        for way in self.ways:
            try:
                for fromnode, tonode in zip(way.refs, way.refs[1:]):
                    distance = utils.EarthDistance(
                        (
                            self.graph_info[fromnode].latitude,
                            self.graph_info[fromnode].longitude,
                        ),
                        (
                            self.graph_info[tonode].latitude,
                            self.graph_info[tonode].longitude,
                        ),
                    )
                    self.addEdge(
                        fromnode, tonode, distance, way.speed_limit, way.oneway
                    )
            except:
                pass


if __name__ == "__main__":
    # Point of entry in execution mode.
    graph = Graph()

    graph.addNode("A", None, None)  # OSM_id, latitude, longitude
    graph.addNode("B", None, None)
    graph.addNode("C", None, None)
    graph.addNode("D", None, None)
    graph.addNode("E", None, None)
    graph.addNode("F", None, None)
    graph.addNode("G", None, None)
    graph.addNode("H", None, None)
    graph.addNode("I", None, None)

    graph.addEdge(
        "C", "A", 2, oneway=True
    )  # OSM_id, OSM_id, cost, oneway (False by default)
    graph.addEdge("C", "D", 4)
    graph.addEdge("A", "D", 8)
    graph.addEdge("A", "E", 800)

    graph.addEdge("F", "H", 7)
    graph.addEdge("F", "G", 6)
    graph.addEdge("H", "I", 4)

    print(graph)
    print()
    graph.adjacency_list()
    print()
    graph.matrix()
    print()
    print("Shortest path from A to D:")
    dj = dijkstra.Dijkstra(graph.graph_structure, "A")
    shortest_path, distance = dj.get("D")
    print(shortest_path, distance)
