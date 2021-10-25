#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from flask import render_template


import utils
import graphloader

from pynavigo import app


#GL = graphloader.GraphLoader("./pynavigo/var/tests-muriel/trips-cedric.osm.bz2")
GL = graphloader.GraphLoader("./pynavigo/var/luxembourg-little.osm")
GRAPH = GL.load_graph()

@app.route('/')
def index(departure=None, destination=None):
    if departure == None or destination == None:
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%MZ")
    else:
    # Get the requirements of the user
        m_departure = re.search('([ \d\.,]+),([ \d\.,]+)', departure)
        m_destination = re.search('([ \d\.,]+),([ \d\.,]+)', destination)
        try:
            # If inputs are coordinates
            departure_latitude_original = float(m_departure.group(1))
            departure_longitude_original = float(m_departure.group(2))
            destination_latitude_original  = float(m_destination.group(1))
            destination_longitude_original = float(m_destination.group(2))
        except:
            # If inputs are addresses
            departure = utils.translate_address_to_coordinates(departure)
            destination = utils.translate_address_to_coordinates(destination)
            if departure == None or destination == None:
                # We don't understand the inputs of the user
                return self.error("Incorrect value(s).")
            departure_latitude_original = departure['lat']
            departure_longitude_original = departure['lng']
            destination_latitude_original = destination['lat']
            destination_longitude_original = destination['lng']

        departure_osmid, departure_latitude, departure_longitude = \
                self.graph.osm_node_from_coordinates(departure_latitude_original, \
                                                    departure_longitude_original)
        destination_osmid, destination_latitude, destination_longitude = \
                self.graph.osm_node_from_coordinates(destination_latitude_original, \
                                                    destination_longitude_original)

        dj = dijkstra.Dijkstra(self.graph.graph_structure, departure_osmid)
        shortest_path, distance = dj.get(destination_osmid)
        print shortest_path
    return render_template('index.html', now=now)
