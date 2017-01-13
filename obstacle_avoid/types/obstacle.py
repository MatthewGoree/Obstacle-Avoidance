from abc import ABCMeta, abstractmethod, abstractproperty
from math import sqrt, pi

from distance import Distance
from ..constants import AVOID_DIST_STAT, AVOID_DIST_MOV

class BaseObstacle(object):
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cross_sectional_radius(self, alt):
        
        pass

    @abstractmethod
    def get_avoid_radius(self, alt):
        
        pass

    @abstractproperty
    def loc(self):

        pass

    def does_overlap(self, obs, alt):
        
        radius_1 = self.get_avoid_radius(alt)
        radius_2 = obs.get_avoid_radius(alt)

        if radius_1 == 0 or radius_2 == 0:
            
            return False

        dist = self.loc.get_distance(obs.loc)
        dist_xy = dist.get_magnitude_xy()

        return radius_1 + radius_2 > dist_xy

    def is_in_wp(self, plane, wp_loc):

        radius = self.get_avoid_radius(wp_loc.alt)

        if radius == 0:

            return False

        dist = self.loc.get_distance(wp_loc)
        dist_xy = dist.get_magnitude_xy()

        return radius + plane.wp_radius > dist_xy

    def is_in_next_wp(self, plane):

        return self.is_in_wp(plane, plane.next_wp)

    def is_loc_inside(self, loc):
    
        radius = self.get_cross_sectional_radius(loc.alt)
    
        dist = self.loc.get_distance(loc)
        dist_xy = dist.get_magnitude_xy()
            
        return radius > dist_xy
    
    def is_loc_in_avoid_radius(self, loc):
        
        radius = self.get_avoid_radius(loc.alt)
        
        dist = self.loc.get_distance(loc)
        dist_xy = dist.get_magnitude_xy()
        
        return radius > dist_xy

    def is_in_way(self, plane, start_loc=None, heading=None):

        # FIXME currently only testing linear part

        if not start_loc:
            
            start_loc = plane.loc

        if not heading:
            
            heading = plane.heading

        turn_dist = Distance.get_turn_dist(plane)
        turn_angle = Distance.get_turn_angle(plane)

        wp_dist = start_loc.get_distance(plane.next_wp, angle=heading) \
            .subtract(turn_dist).get_transform(turn_angle)

        obs_dist = start_loc.get_distance(self.loc, angle=heading) \
            .subtract(turn_dist).get_transform(turn_angle)

        if obs_dist < 0 or obs_dist > wp_dist.y:

            return False

        pass_alt = plane.loc + turn_dist.z + obs_dist.y / float(wp_dist.y) \
            * wp_dist.z
        radius = self.get_avoid_radius(pass_alt)

        return radius > obs_dist.x

class StaticObstacle(BaseObstacle):

    def __init__(self, loc, radius, height):
        
        self._loc = loc
        self.radius = radius
        self.height = height

    @property
    def loc(self):

        return self._loc

    def get_cross_sectional_radius(self, alt):
        
        if abs(alt - self.loc.alt) < self.height / 2.0:

            return self.radius
    
        return 0

    def get_avoid_radius(self, alt):

        if abs(alt - self.loc.alt) <= self.height / 2.0:

            return self.radius + AVOID_DIST_STAT
        
        if abs(alt - self.loc.alt) < self.height / 2.0 + AVOID_DIST_STAT:

            return self.radius + sqrt(AVOID_DIST_STAT ** 2 - (abs(alt
                - self.loc.alt) - self.height / 2.0) ** 2)

        return 0

class MovingObstacle(BaseObstacle):

    def __init__(self, loc, radius):
        
        self._loc = loc
        self.radius = radius

    @property
    def loc(self):

        return self._loc

    @loc.setter
    def loc(self, loc):

        self._loc = loc

    def get_cross_sectional_radius(self, alt):
    
        if abs(alt - self.loc.alt) < self.radius:

            return sqrt(self.radius ** 2 - (alt - self.loc.alt) ** 2)
        
        return 0

    def get_avoid_radius(self, alt):
        
        if abs(alt - self.loc.alt) < AVOID_DIST_MOV + self.radius:

            return sqrt((AVOID_DIST_MOV + self.radius) ** 2 - (alt
                - self.loc.alt) ** 2)
    
        return 0
