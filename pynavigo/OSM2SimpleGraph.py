#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme, Jose Hermida Prado"
__version__ = "$Revision: 0.5 $"
__date__ = "$Date: 2012/03/18 $"
__revision__ = "$Date: 2012/05/10 $"
__copyright__ = "Copyright (c) 2013-2021 Cedric Bonhomme"
__license__ = ""

from imposm.parser import OSMParser

import simpleGraph
import utils
#import client
import dijkstra
import maxspeed

whitelist = set(("motorway", "motorway_link", "trunk", "trunk_link", "primary", \
                "primary_link", "secondary", "tertiary", "minor", "unclassified", \
                "residential", "living_street", "mini_roundabout"))

class OSM2SimpleGraph(object):
    """
    Simple class that handles the parsed OSM data.
    """
    def __init__(self, graph):
        """
        Initialization.
        """
        self.graph = graph
        try:
            self.max_speed = maxspeed.load_max_speed('france')
        except Exception, e:
            print e
            exit(1)

    def coords(self, coords):
        """
         Callback method for coords.
        """
        for osm_id, longitude, latitude in coords:
            #print '%s %.4f %.4f' % (osm_id, lon, lat)
            self.graph.addNode(osm_id, longitude, latitude)

    def ways(self, ways):
        """
        Callback method for ways.
        """
        speed_limit = self.max_speed["default"]
        for osm_id, tags, refs in ways:
            oneway = False
            if "highway" not in tags:
                continue
            if tags["highway"] not in whitelist:
                continue
            if tags["highway"] == "mini_roundabout":
                oneway = True
            if "junction" in tags and tags["junction"] == "roundabout":
                oneway = True
            if "oneway" in tags:
                if tags["oneway"] in ["yes", "true", "True", "Yes", "1"]:
                    # "true" and "1" are discouraged alternative, see:
                    # http://wiki.openstreetmap.org/wiki/Key:oneway#Values
                    oneway = True
            try:
                speed_limit = int(tags["maxspeed"])
            except:
                try:
                    speed_limit = self.max_speed[tags["highway"]]
                except:
                    speed_limit = self.max_speed["default"]

            self.graph.addWay(refs, oneway, speed_limit)

    def nodes(self, nodes):
        """
        Callback method for nodes.
        """
        for osm_id, tags, position in nodes:
            self.graph.addNode(osm_id, position[0], position[1])

    def relations(self, relations):
        """
        """
        for osm_id, tags, link  in relations:
            print link


if __name__ == "__main__":
    # Point of entry in execution mode.
    import time
    from random import choice
    OSM_FILE = "./var/luxembourg-little.osm"

    graph = simpleGraph.Graph()

    simple_graph = OSM2SimpleGraph(graph)

    print "Generation of the graph for", OSM_FILE
    print "Creating nodes..."
    p = OSMParser(concurrency=2, coords_callback=simple_graph.coords, ways_callback=simple_graph.ways)
    start_user = time.time()
    p.parse(OSM_FILE)
    print "Creating structures (relations between nodes and distance)..."
    graph.create_graph_structure()
    print "Removing isolated nodes..."
    nb_isolated_nodes = graph.remove_isolated_nodes()
    print nb_isolated_nodes, "node(s) removed."
    print "Trying to remove islands..."
    graph.remove_islands()
    end_user = time.time()
    print "Generation done."
    print "User time:", end_user - start_user, "seconds."

    print graph

    from_node = choice(graph.graph_structure.keys())
    to_node = choice(graph.graph_structure.keys())