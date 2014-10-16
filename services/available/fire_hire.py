#!/usr/bin/python
#fire_hire.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: fire_hire

"""

from services.local_service import LocalService

def create_service():
    return FireHireService()
    
class FireHireService(LocalService):
    
    name = 'fire_hire'
    
    def dependent_on(self):
        return []
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    

    