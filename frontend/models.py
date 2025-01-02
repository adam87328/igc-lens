from django.db import models

from importer.models import *

def empty_dict():
    return {}

#class UserSettings(models.Model):
#
#    # glide ratio, unit is 1 (meter/meter)
#    glide_rating_good = models.FloatField(default=10)
#    glide_rating_neutral = models.FloatField(default=7.5)
#    # else bad
#
#    # average vertical velocity, unit is m/s
#    thermal_rating_good = models.FloatField(default=2.0)
#    thermal_rating_neutral = models.FloatField(default=1.0)
#    # else bad
#    



class FlightFilter(models.Model):
    
    all = models.JSONField(default=empty_dict)
    active = models.JSONField(default=empty_dict)

    def add_default(self):
        self.all.update({
            "50km+": "xc_dist",
            "100km+": "xc_dist",
            "150km+": "xc_dist",
            "200km+": "xc_dist",
            "250km+": "xc_dist",
            "1h+": "airtime",
            "3h+": "airtime",
            "5h+": "airtime",
            "7h+": "airtime",
            "Closed FAI Triangle": "scoring_name",
            "Closd Free Triangle": "scoring_name",
            "FAI Triangle": "scoring_name",
            "Free Triangle": "scoring_name",
            "Free Distance": "scoring_name",
        })

    def add_takeoffs(self):
        """Add unique list of takeoffs"""
        for x in Flight.objects.all().get_unique_takeoffs():
            self.all[x] = 'takeoff'

    def set_filter(self,name):
        """Copy to active filter set"""
        if name in self.all:
            self.active[name] = self.all[name]
            self.save()