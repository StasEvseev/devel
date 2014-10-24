#!/usr/bin/python
#tcp_connections.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: tcp_connections

"""

from services.local_service import LocalService

def create_service():
    return TCPConnectionsService()
    
class TCPConnectionsService(LocalService):
    
    service_name = 'tcp_connections'
    
    def dependent_on(self):
        return []
    
    def start(self):
        return True
    
    def stop(self):
        return True
    
    

    