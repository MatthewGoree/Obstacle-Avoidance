"""Contains the Distance class that represents distances in vector form
between two points.
"""

from math import atan2, sin, cos, sqrt, pi, copysign


class Distance(object):

    """Represents a distance between two points in vector form.

    Two distances can be added together and distances can be transformed
    by an angle.
    """

    def __init__(self, x, y, z):
        """Instantiate a Distance object with components x, y, and z."""
        self.x = x
        self.y = y
        self.z = z

    def add(self, dist):
        """Add two Distance objects together and return a new
        Distance.
        """

        x = self.x + dist.x
        y = self.y + dist.y
        z = self.z + dist.z

        return Distance(x, y, z)

    def subtract(self, dist):
        """Subtract a Distance object and return a new Distance."""
        x = self.x - dist.x
        y = self.y - dist.y
        z = self.z - dist.z

        return Distance(x, y, z)

    def get_magnitude(self):
        """Return the magnitude of the Distance object from its
        components.
        """

        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def get_magnitude_xy(self):
        """Return the magnitude of the Distance object from its x and y
        components.
        """

        return sqrt(self.x ** 2 + self.y ** 2)

    def get_transform(self, angle):
        """Transform the Distance object by an angle clockwise and
        return a new Distance.
        """

        x = self.x * cos(angle) - self.y * sin(angle)
        y = self.x * sin(angle) + self.y * cos(angle)
        z = self.z
        
        return Distance(x, y, z)

    @staticmethod
    def get_turn_angle(plane, loc=None, heading=None):
        """Returns the angle the plane must turn. It is assumed that the
        plane turns in a circular path and then flies directly to the
        next waypoint where a negative angle indicates that the plane
        turns left and where a positive angle indicates that the plane
        turns right.
        """

        if not loc:
            loc = plane.loc

        if not heading:
            heading = plane.heading

        # Get the distance of the next waypoint relative to the plane.
        wp_dist = loc.get_distance(plane.next_wp, angle=heading)

        i = wp_dist.x
        j = wp_dist.y

        r = plane.turning_radius
        
        # If the waypoint is to the left make the plane turn left.
        if i < 0:
            r *= -1
            
        # If the plane cannot make a tight enough turn, turn the other
        # way.
        if (i - r) ** 2 + j ** 2 < r ** 2:
            r *= -1
        
        # Find a and b, the distances relative to the plane of the point
        # where the plane no longer turns in the xy plane.
        
        # Try to find a
        try:
            a = (r * i ** 2 - r ** 2 * i + r * j ** 2 - r * j * sqrt(i ** 2 - 2
                * r * i + j ** 2)) / float(r ** 2 - 2 * r * i + i ** 2 + j **
                2)
        
        # Find a and b due to floating point errors for when the plane
        # doesn't turn at all or when the plane turns pi radians left or
        # right.
        except (ZeroDivisionError, ValueError):
            if abs(i) < abs(r):
                a = 0
            else:
                a = 2 * r

            b = 0

        # Otherwise, find b.
        else:
            b = sqrt(r ** 2 - (a - r) ** 2)
            
            if (j < 0 and abs(i) < 2 * abs(r)) or i / float(r) < 0:
                b *= -1

        # Find how what angle the plane must turn, will be negative for
        # left and positive for turning right.
        return copysign((atan2(b, abs(r) / r * (r - a))) % (2 * pi), r)

    @staticmethod
    def get_turn_dist(plane, loc=None, heading=None):
        """Returns the distance relative to the plane of the point where
        the plane no longer turns. It is assumed that the plane turns in
        a circular path and then flies directly to the next waypoint.
        """

        if not loc:
            loc = plane.loc

        if not heading:
            heading = plane.heading

        # Get the distance of the next waypoint relative to the plane.
        wp_dist = loc.get_distance(plane.next_wp, angle=heading)

        i = wp_dist.x
        j = wp_dist.y
        k = wp_dist.z

        r = plane.turning_radius
        
        # If the waypoint is to the left make the plane turn left.
        if i < 0:
            r *= -1
            
        # If the plane cannot make a tight enough turn, turn the other
        # way.
        if (i - r) ** 2 + j ** 2 < r ** 2:
            r *= -1
        
        # Find a, b, and c, the distances relative to the plane of the
        # point where the plane no longer turns.
        
        # Try to find a
        try:
            a = (r * i ** 2 - r ** 2 * i + r * j ** 2 - r * j * sqrt(i ** 2 - 2
                * r * i + j ** 2)) / float(r ** 2 - 2 * r * i + i ** 2 + j **
                2)
        
        # Find a and b due to floating point errors for when the plane
        # doesn't turn at all or when the plane turns pi radians left or
        # right.
        except (ZeroDivisionError, ValueError):
            if abs(i) < abs(r):
                a = 0
            else:
                a = 2 * r

            b = 0

        # Otherwise, find b.
        else:
            b = sqrt(r ** 2 - (a - r) ** 2)
            
            if (j < 0 and abs(i) < 2 * abs(r)) or i / float(r) < 0:
                b *= -1

        # Find how what angle the plane must turn.
        angle = (atan2(b, abs(r) / r * (r - a))) % (2 * pi)

        # Find the distances in the xy plane of the circular and linear
        # path.
        circ_dist_xy = abs(r) * abs(angle)
        lin_dist_xy = sqrt((i - a) ** 2 + (j - b) ** 2)

        # Try to find c as a ratio of the circular distance to the total
        # distance times k.
        try:
            c = circ_dist_xy / float(circ_dist_xy + lin_dist_xy) * k

        # c is zero due to floating point errors if the plane is very
        # close to the next waypoint.
        except ZeroDivisionError:
            c = 0

        # Return the distance relative to the plane of the point where
        # the plane no longer turns.
        return Distance(a, b, c)

    @staticmethod
    def from_magnitude(dist, bearing):
        """Return a new Distance object from a magnitude in the xy plane
        and a bearing.
        """

        return Distance(dist * sin(bearing), dist * cos(bearing), 0)
