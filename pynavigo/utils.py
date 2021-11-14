#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time
import datetime
import urllib.request, urllib.parse, urllib.error
import json
import io as StringIO

# some multipliers for interpreting GPS output
METERS_TO_FEET = 3.2808399  # Meters to U.S./British feet
METERS_TO_MILES = 0.00062137119  # Meters to miles
KNOTS_TO_MPH = 1.1507794  # Knots to miles per hour
KNOTS_TO_KPH = 1.852  # Knots to kilometers per hour
KNOTS_TO_MPS = 0.51444444  # Knots to meters per second
MPS_TO_KPH = 3.6  # Meters per second to klicks/hr
MPS_TO_MPH = 2.2369363  # Meters/second to miles per hour
MPS_TO_KNOTS = 1.9438445  # Meters per second to knots


def translate_address_to_coordinates(address):
    """
    Translates an address to coordinates with a request
    to Google Maps.

    >>> print(translateAddressToCoordinates('17 chemin sous les vignes, Montenach'))
    {'lat': 49.4226396, 'lng': 6.378915}
    """
    urlParams = {
        "address": address,
        "sensor": "false",
    }
    url = "http://maps.google.com/maps/api/geocode/json?" + urllib.parse.urlencode(
        urlParams
    )
    response = urllib.request.urlopen(url)
    responseBody = response.read()
    body = StringIO.StringIO(responseBody)
    result = json.load(body)
    if "status" not in result or result["status"] != "OK":
        return None
    else:
        return {
            "lat": result["results"][0]["geometry"]["location"]["lat"],
            "lng": result["results"][0]["geometry"]["location"]["lng"],
        }


def Deg2Rad(x):
    """
    Degrees to radians.
    """
    return x * (math.pi / 180)


def Rad2Deg(x):
    """
    Radians to degress.
    """
    return x * (180 / math.pi)


def CalcRad(lat):
    """
    Radius of curvature in meters at specified latitude.
    """
    a = 6378.137
    e2 = 0.081082 * 0.081082
    # the radius of curvature of an ellipsoidal Earth in the plane of a
    # meridian of latitude is given by
    #
    # R' = a * (1 - e^2) / (1 - e^2 * (sin(lat))^2)^(3/2)
    #
    # where a is the equatorial radius,
    # b is the polar radius, and
    # e is the eccentricity of the ellipsoid = sqrt(1 - b^2/a^2)
    #
    # a = 6378 km (3963 mi) Equatorial radius (surface to center distance)
    # b = 6356.752 km (3950 mi) Polar radius (surface to center distance)
    # e = 0.081082 Eccentricity
    sc = math.sin(Deg2Rad(lat))
    x = a * (1.0 - e2)
    z = 1.0 - e2 * sc * sc
    y = pow(z, 1.5)
    r = x / y

    r = r * 1000.0  # Convert to meters
    return r


def EarthDistance(xxx_todo_changeme, xxx_todo_changeme1):
    """
    Distance in meters between two points specified in degrees.
    """
    (lat1, lon1) = xxx_todo_changeme
    (lat2, lon2) = xxx_todo_changeme1
    x1 = CalcRad(lat1) * math.cos(Deg2Rad(lon1)) * math.sin(Deg2Rad(90 - lat1))
    x2 = CalcRad(lat2) * math.cos(Deg2Rad(lon2)) * math.sin(Deg2Rad(90 - lat2))
    y1 = CalcRad(lat1) * math.sin(Deg2Rad(lon1)) * math.sin(Deg2Rad(90 - lat1))
    y2 = CalcRad(lat2) * math.sin(Deg2Rad(lon2)) * math.sin(Deg2Rad(90 - lat2))
    z1 = CalcRad(lat1) * math.cos(Deg2Rad(90 - lat1))
    z2 = CalcRad(lat2) * math.cos(Deg2Rad(90 - lat2))
    a = (x1 * x2 + y1 * y2 + z1 * z2) / pow(CalcRad((lat1 + lat2) / 2), 2)
    # a should be in [1, -1] but can sometimes fall outside it by
    # a very small amount due to rounding errors in the preceding
    # calculations (this is prone to happen when the argument points
    # are very close together).  Thus we constrain it here.
    if abs(a) > 1:
        a = 1
    elif a < -1:
        a = -1
    return CalcRad((lat1 + lat2) / 2) * math.acos(a)


def MeterOffset(xxx_todo_changeme2, xxx_todo_changeme3):
    """
    Return offset in meters of second arg from first.
    """
    (lat1, lon1) = xxx_todo_changeme2
    (lat2, lon2) = xxx_todo_changeme3
    dx = EarthDistance((lat1, lon1), (lat1, lon2))
    dy = EarthDistance((lat1, lon1), (lat2, lon1))
    if lat1 < lat2:
        dy *= -1
    if lon1 < lon2:
        dx *= -1
    return (dx, dy)


def delta_time(dt, delta, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Adds a time delta to a datetime object with a specific format.

    Example of call:
    >>> new_dt = delta_time('2012-10-27 12:05:54', datetime.timedelta(minutes=45))
    >>> print("%s:%s:%s" % (new_dt.hour, new_dt.minute, new_dt.second))
    12:50:54
    """
    try:
        return datetime.datetime(*time.strptime(dt, fmt)[:6]) + delta
    except ValueError as e:
        return e


def compare_time_approx(
    dt1, dt2, delta=datetime.timedelta(minutes=15), fmt="%Y-%m-%d %H:%M"
):
    """
    Return True if dt1 and dt2 are approximate.
    """
    return abs((dt1 - datetime.datetime(*time.strptime(dt2, fmt)[:6]))) < delta


def isotime(s):
    """
    Convert timestamps in ISO8661 format to and from Unix time.
    """
    if type(s) == type(1):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
    elif type(s) == type(1.0):
        date = int(s)
        msec = s - date
        date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
        return date + "." + repr(msec)[2:]
    elif type(s) == type(""):
        if s[-1] == "Z":
            s = s[:-1]
        if "." in s:
            (date, msec) = s.split(".")
        else:
            date = s
            msec = "0"
        # Note: no leap-second correction!
        return calendar.timegm(time.strptime(date, "%Y-%m-%dT%H:%M:%S")) + float(
            "0." + msec
        )
    else:
        raise TypeError


if __name__ == "__main__":
    # Point of execution in entry mode
    pass
