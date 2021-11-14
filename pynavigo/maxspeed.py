#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/04/24 $"
__revision__ = "$Date: 2012/04/30 $"
__copyright__ = "Copyright (c) 2013-2021 Cedric Bonhomme"
__license__ = ""

import configparser


def load_max_speed(country="france"):
    """
    Load information about speed limits.
    """
    config = configparser.SafeConfigParser()
    try:
        config.read("./pynavigo/cfg/maxspeed.cfg")
    except:
        raise Error("File of max speeds not found.")

    max_speed = {
        "motorway": int(config.get(country, "motorway")),
        "trunk": int(config.get(country, "trunk")),
        "primary": int(config.get(country, "primary")),
        "secondary": int(config.get(country, "secondary")),
        "tertiary": int(config.get(country, "tertiary")),
        "unclassified": int(config.get(country, "unclassified")),
        "residential": int(config.get(country, "residential")),
        "default": int(config.get(country, "default")),
    }

    return max_speed


if __name__ == "__main__":
    # Point of entry in execution mode
    max_speed_france = load_max_speed("france")

    max_speed_germany = load_max_speed("germany")
