#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/06/01 $"
__revision__ = "$Date: 2012/06/01 $"
__copyright__ = "Copyright (c) 2013-2021 Cedric Bonhomme"
__license__ = ""

import os
import time
import pickle
import random
import ConfigParser
import threading

import dijkstra
import simpleGraph
import OSM2SimpleGraph

from imposm.parser import OSMParser

class GraphLoader(object):
    """
    Generates or loads the graph and over-graph.
    """
    def __init__(self, osm_file, clients_file=None, serialize=True):
        self.nb_cores = os.sysconf('SC_NPROCESSORS_ONLN')
        self.serialize = serialize
        self.osm_file = osm_file
        self.clients_file = clients_file
        self.dump_over_graph = os.path.splitext(osm_file)[0] + "_over-graph.dump"

    def load_graph(self):
        """
        Load the graph in memory from an
        OSM file or from a serialized object.
        """
        self.graph = None
        try:
            dump_graph = open(os.path.normpath(self.osm_file + ".dump"), "r")
            print "Loading serialized graph from:", self.osm_file + ".dump"
            self.graph = pickle.load(dump_graph)
            dump_graph.close()
        except:
            self.graph = simpleGraph.Graph()

            simple_graph = OSM2SimpleGraph.OSM2SimpleGraph(self.graph)

            print "Generation of the graph for", self.osm_file
            print "Creating nodes..."
            p = OSMParser(concurrency=self.nb_cores, coords_callback=simple_graph.coords, ways_callback=simple_graph.ways)
            start_user = time.time()
            p.parse(self.osm_file)
            print "Creating structures (relations between nodes and distance)..."
            self.graph.create_graph_structure()
            print "Removing isolated nodes..."
            #nb_isolated_nodes = graph.remove_isolated_nodes()
            #print nb_isolated_nodes, "node(s) removed."
            print "Trying to remove islands..."
            self.graph.remove_islands()
            end_user = time.time()
            print "Generation done."
            print "User time:", end_user - start_user, "seconds."
            print "Serializing graph to", self.osm_file + ".dump"
            dump_graph = open(os.path.normpath(self.osm_file + ".dump"), "w")
            pickle.dump(self.graph, dump_graph)
            dump_graph.close()
        return self.graph

    def load_over_graph(self):
        """
        Load the over-graph in memory from a
        graph object or from a serialized object.

        The over-graph is a complete graph based
        on the initial graph (generated from the OSM file).
        It is a simpleted graph in which every pair of distinct
        vertices is connected by a unique edge.
        If 'n' is the number of vertices, 'n(n-1) / 2' is the
        number of edges. K(5000): 1247500 edges.
        """
        self.over_graph = simpleGraph.Graph()
        try:
            dump_graph = open(self.dump_over_graph, "r")
            print "Loading serialized over-graph from:", self.dump_over_graph
            self.over_graph = pickle.load(dump_graph)
            dump_graph.close()
        except:
            if self.clients_file == None:
                return None
            print "Generation of the over-graph (complete graph based only of pickup points)..."

            # Automatically place pickup points at clients depart and destination nodes.
            print "\tPreparing pickup points (based on clients departure/destination points)..."
            clients = []
            config = ConfigParser.RawConfigParser()
            if self.serialize:
                config.read(self.clients_file)
            else:
                # When this method is called via the Web service.
                from cStringIO import StringIO
                f = StringIO(self.clients_file)
                f.seek(0)
                config.readfp(f)
                del f

            # Get the list of client sections available in the config file.
            clients_sections = [section for section in config.sections()]
            # Creation of clients
            for client_section in clients_sections:
                print "\t- " + client_section
                try:
                    client_depart_original = config.get(client_section, 'depart')
                    client_destination_original = config.get(client_section, 'destination')
                except ConfigParser.NoOptionError:
                    continue
                try:
                    client_depart_latitude_original = float(client_depart_original.split(' ')[0])
                    client_depart_longitude_original = float(client_depart_original.split(' ')[1])
                    client_destination_latitude_original = float(client_destination_original.split(' ')[0])
                    client_destination_longitude_original = float(client_destination_original.split(' ')[1])
                except (ValueError, IndexError):
                    continue

                client_depart_OSM, client_depart_latitude, client_depart_longitude = \
                                self.graph.osm_node_from_coordinates(client_depart_latitude_original, \
                                                            client_depart_longitude_original)
                client_destination_OSM, client_destination_latitude, client_destination_longitude = \
                                self.graph.osm_node_from_coordinates(client_destination_latitude_original, \
                                                            client_destination_longitude_original)
                clients.append((client_depart_OSM, client_depart_latitude, client_depart_longitude, \
                                client_destination_OSM, client_destination_latitude, client_destination_longitude))

            nodes=[]
            result = []
            # pickup points will be departure and destinations of clients
            for client in clients:
                nodes.append(client[0])
                nodes.append(client[3])
            # insert random pickup points
            #for i in range(5000):
                #node = random.choice(self.graph.graph_structure.keys())
                #nodes.append(node)

            for node in nodes:
                self.over_graph.addNode(node, self.graph.get_node(node).longitude, self.graph.get_node(node).latitude)
                dj = dijkstra.Dijkstra(self.graph.graph_structure, node)
                for node1 in nodes:
                    shortest_path, distance = dj.get(node1)
                    if shortest_path != []:
                        average = self.graph.average_speed(shortest_path)
                        self.over_graph.addNode(node1, self.graph.get_node(node1).longitude, self.graph.get_node(node1).latitude)
                        self.over_graph.addEdge(node, node1, distance+75*4, average, False)

            #list_threads = []
            #for i in range(self.nb_cores + 1):
                ## Each thread (hopefully each core) will process a part of the list of pickup points
                #sublist =  nodes[(i*(len(nodes))/self.nb_cores):((i+1)*(len(nodes)/self.nb_cores))]
                #thr = threading.Thread(None, self.create_new_edges, None, (sublist,))
                #list_threads.append(thr)
                #thr.start()

            #for thread in list_threads:
                ## Waiting for all threads to be done.
                #thread.join()

            if self.serialize:
                print "Serializing graph to", self.dump_over_graph
                dump_graph = open(self.dump_over_graph, "w")
                pickle.dump(self.over_graph, dump_graph)
                dump_graph.close()

        return self.over_graph

    def create_new_edges(self, nodes):
        """
        Creates new edges of the over-graph.
        Called in a separate thread.
        """
        for node in nodes:
            self.over_graph.addNode(node, self.graph.get_node(node).longitude, self.graph.get_node(node).latitude)
            dj = dijkstra.Dijkstra(self.graph.graph_structure, node)
            for node1 in nodes:
                shortest_path, distance = dj.get(node1)
                if shortest_path != []:
                    average = self.graph.average_speed(shortest_path)
                    self.over_graph.addNode(node1, self.graph.get_node(node1).longitude, self.graph.get_node(node1).latitude)
                    self.over_graph.addEdge(node, node1, distance+75*4, average, False)



if __name__ == "__main__":
    # Point of entry in execution mode
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("-m", "--map", dest="osm_file",
                        help="Path to the OSM map file (OSM, PBF or BZ2).")
    parser.add_option("-g", "--graph", dest="graph_type",
                        help="Type of the graph to generate (simple or complete.")

    parser.set_defaults(graph_type="graph")

    (options, args) = parser.parse_args()

    gl = None
    if options.osm_file != "":
        gl = GraphLoader(options.osm_file)
        if options.graph_type == "graph":
            gl.load_graph()
        elif options.graph_type == "over":
            gl.load_over_graph()
        else:
            gl.load_graph()
            gl.load_over_graph()
            #load_over_graph(os.path.splitext(OSM_FILE)[0] + "_over-graph.dump")
