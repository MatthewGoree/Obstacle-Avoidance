# -*- coding: utf-8 -*-
"""Handles converting units of latitude and longitude, distance, and
speed.
    
Latitude and longitude can be switched between decimal degrees, radians,
and degrees, minutes, and seconds (e.g. 23° 32' 34.4432" N), distance
can be switched between feet and meters, and speed can be switched
between knots and meters per second.
"""

from math import floor, pi
from re import split


def deg_to_rad(degrees):
    """Convert an angle in decimal degrees to radians."""  
    return degrees * pi / 180


def deg_to_dms(degrees, coordinate):
    """Convert an angle in decimal degrees to degrees, minutes, and
    seconds in a string. Latitude ('lat') or longitute ('lon') must be
    specified.
    """

    deg = floor(degrees)
    min = floor((degrees - deg) * 60)
    sec = (degrees - deg - min/60.0) * 3600
    dir = (('N' if degrees >= 0 else 'S') if coordinate == 'lat' else 
        ('E' if degrees >= 0 else 'W'))
    
    return '%.0f° %.0f\' %.4f" %s' % (deg, min, sec, dir)


def rad_to_deg(radians):
    """Convert an angle in radians to decimal degrees."""  
    return radians / pi * 180


def rad_to_dms(radians, coordinate):
    """Convert an angle in radians to degrees, minutes, and seconds in a
    string. Latitude ('lat') or longitute ('lon') must be specified.
    """

    return deg_to_dms(rad_to_deg(radians), coordinate)


def dms_to_deg(dms):
    """Convert an angle in degrees, minutes, and seconds in a string to
    decimal degrees.
    """

    values = split('[^0-9.]+', dms[:-1])

    return (-1 if dms[-1] in ['S', 'W'] else 1) * (float(values[0])
        + float(values[1]) / 60 + float(values[2]) / 3600)


def dms_to_rad(dms):
    """Convert an angle in degrees, minutes, and seconds in a string to
    radians.
    """
    
    return deg_to_rad(dms_to_deg(dms))


def feet(meters):
    """Convert a distance in meters to feet."""
    return meters / 0.3048


def meters(feet):
    """Convert a distance in feet to meters."""
    return feet * 0.3048


def knots(meters_per_second):
    """Convert a speed in meters per second to knots."""
    return meters_per_second / 0.514444


def meters_per_second(knots):
    """Convert a speed in knots to meters per second."""
    return knots * 0.514444
