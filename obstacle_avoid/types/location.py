"""Handles representating a GPS location and finding a location with a
distance object and the distance between GPS locations using a flat-
earth approximation.
"""

from math import sin, cos, atan2, pi, sqrt

from dronekit import LocationGlobalRelative

from distance import Distance
from ..constants import EARTH_RADIUS, EARTH_ECCEN
from ..util import deg_to_rad, rad_to_deg


class Location(object):

    """Represents a GPS location with a lattitude, longitude, and 
    altitude with respect to the ground.
    """

    def __init__(self, lat, lon, alt):
        """Instantiate a Location object at lat, lon and at alt."""
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def _get_earth_radii(self):
        """Return the radii used for the flat-earth approximation."""
        r_1 = (EARTH_RADIUS * (1 - EARTH_ECCEN ** 2) /
               (1 - EARTH_ECCEN ** 2 * sin(self.lat) ** 2) ** (3 / 2))
        r_2 = EARTH_RADIUS / sqrt(1 - EARTH_ECCEN ** 2 * sin(self.lat) ** 2)
           
        return r_1, r_2

    def get_distance(self, loc, angle=0):
        """Get the distance between two Locations and return a Distance
        object using the flat-earth approximation.
        """

        e_radii = self._get_earth_radii()
        
        x = e_radii[1] * cos(self.lat) * (loc.lon - self.lon)
        y = e_radii[0] * (loc.lat - self.lat)
        z = loc.alt - self.alt
        
        dist = Distance(x, y, z)
        
        if angle:
            dist = dist.get_transform(angle)

        return dist

    def get_location(self, dist):
        """Return a Location object dist away from the Location object 
        using the flat-earth approximation.
        """

        e_radii = self._get_earth_radii()
    
        lat = dist.y / e_radii[0] + self.lat
        lon = dist.x / e_radii[1] / cos(self.lat) + self.lon
        alt = self.alt + dist.z
    
        return Location(lat, lon, alt)
    
    def get_bearing(self, loc):
        """Return the bearing from the Location object to loc."""
        dist = self.get_distance(loc)
    
        return atan2(dist.x, dist.y) % (2 * pi)
    
    @staticmethod
    def from_command(command):
        """Return a Location object from a dronekit command."""
        lat = deg_to_rad(command.x)
        lon = deg_to_rad(command.y)
        alt = command.z

        return Location(lat, lon, alt)

    @staticmethod
    def from_dronekit_location(dk_loc):
        """Return a Location object from a dronekit location."""
        lat = deg_to_rad(dk_loc.lat)
        lon = deg_to_rad(dk_loc.lon)
        alt = dk_loc.alt

        return Location(lat, lon, alt)

    def to_dronekit_location(self):
        """Return a dronekit location from a Location object."""
        lat = rad_to_deg(self.lat)
        lon = rad_to_deg(self.lon)
        alt = self.alt

        return LocationGlobalRelative(lat, lon, alt)
