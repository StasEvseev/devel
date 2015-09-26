

"""
.. module:: proxy_receiver
.. role:: red

BitDust proxy_receiver(at_startup) Automat

.. raw:: html

    <i>generated using <a href="http://bitdust.io/visio2python/" target="_blank">visio2python</a> tool</i><br>
    <a href="proxy_receiver.png" target="_blank">
    <img src="proxy_receiver.png" style="max-width:100%;">
    </a>

EVENTS:
    * :red:`found-one-node`
    * :red:`inbox-packet`
    * :red:`init`
    * :red:`nodes-not-found`
    * :red:`send-file`
    * :red:`service-accepted`
    * :red:`service-refused`
    * :red:`shutdown`
    * :red:`start`
    * :red:`stop`
    * :red:`timer-10sec`
"""

import random

from twisted.internet import reactor

from logs import lg

from automats import automat

from dht import dht_service

from p2p import p2p_service
from p2p import commands

from contacts import identitydb
from contacts import identitycache

#------------------------------------------------------------------------------ 

_Debug = False
_DebugLevel = 14

#------------------------------------------------------------------------------

_ProxyReceiver = None

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    """
    Access method to interact with proxy_receiver() machine.
    """
    global _ProxyReceiver
    if _ProxyReceiver is None:
        # set automat name and starting state here
        _ProxyReceiver = ProxyReceiver('proxy_receiver', 'AT_STARTUP')
    if event is not None:
        _ProxyReceiver.automat(event, arg)
    return _ProxyReceiver

#------------------------------------------------------------------------------

class ProxyReceiver(automat.Automat):
    """
    This class implements all the functionality of the ``proxy_receiver()`` state machine.
    """

    timers = {
        'timer-10sec': (10.0, ['ACK?','SERVICE?']),
        }

    def init(self):
        """
        Method to initialize additional variables and flags
        at creation phase of proxy_receiver() machine.
        """

    def state_changed(self, oldstate, newstate, event, arg):
        """
        Method to catch the moment when proxy_receiver() state were changed.
        """

    def state_not_changed(self, curstate, event, arg):
        """
        This method intended to catch the moment when some event was fired in the proxy_receiver()
        but its state was not changed.
        """

    def A(self, event, arg):
        """
        The core proxy_receiver() code, generated using `visio2python <http://bitdust.io/visio2python/>`_ tool.
        """
        #---ACK?---
        if self.state == 'ACK?':
            if event == 'inbox-packet' and self.isAckFromNode(arg) :
                self.state = 'SERVICE?'
                self.doSendRequestService(arg)
            elif event == 'shutdown' :
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'timer-10sec' :
                self.state = 'RANDOM_NODE?'
                self.doDHTFindRandomNode(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
                self.doReportStopped(arg)
        #---AT_STARTUP---
        elif self.state == 'AT_STARTUP':
            if event == 'init' :
                self.state = 'STOPPED'
                self.doInit(arg)
        #---LISTEN---
        elif self.state == 'LISTEN':
            if event == 'send-file' :
                self.doSendFileToRouter(arg)
            elif event == 'shutdown' :
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
                self.doStopListening(arg)
                self.doUpdateMyIdentity(arg)
                self.doReportStopped(arg)
        #---RANDOM_NODE?---
        elif self.state == 'RANDOM_NODE?':
            if event == 'found-one-node' :
                self.state = 'ACK?'
                self.doRememberNode(arg)
                self.doSendMyIdentity(arg)
            elif event == 'shutdown' :
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'nodes-not-found' :
                self.doWaitAndTryAgain(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
                self.doReportStopped(arg)
        #---SERVICE?---
        elif self.state == 'SERVICE?':
            if event == 'service-accepted' :
                self.state = 'LISTEN'
                self.doRememberProxyNode(arg)
                self.doUpdateMyIdentity(arg)
                self.doStartListening(arg)
                self.doReportStarted(arg)
            elif event == 'shutdown' :
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
                self.doReportStopped(arg)
            elif event == 'timer-10sec' or event == 'service-refused' :
                self.state = 'RANDOM_NODE?'
                self.doDHTFindRandomNode(arg)
        #---CLOSED---
        elif self.state == 'CLOSED':
            pass
        #---STOPPED---
        elif self.state == 'STOPPED':
            if event == 'start' :
                self.state = 'RANDOM_NODE?'
                self.doDHTFindRandomNode(arg)
            elif event == 'shutdown' :
                self.state = 'CLOSED'
                self.doDestroyMe(arg)
        return None

    def isAckFromNode(self, arg):
        """
        Condition method.
        """
        newpacket, info, status, error_message = arg
        if newpacket.Command == commands.Ack():
            if newpacket.OwnerID == self.router_idurl:
                return True
        return False

    def doInit(self, arg):
        """
        Action method.
        """
        self.router_idurl = None
        self.router_identity = None
        self.request_service_packet_id = None

    def doDHTFindRandomNode(self, arg):
        """
        Action method.
        """
        self._find_random_node()

    def doWaitAndTryAgain(self, arg):
        """
        Action method.
        """
        reactor.callLater(10, self._find_random_node)
    
    def doSendMyIdentity(self, arg):
        """
        Action method.
        """
        p2p_service.SendIdentity(self.router_idurl, wide=True)

    def doSendRequestService(self, arg):
        """
        Action method.
        """
        request = p2p_service.SendRequestService(
            self.router_idurl, 'service_proxy_server', self._router_acked)
        self.request_service_packet_id = request.PacketID

    def doRememberNode(self, arg):
        """
        Action method.
        """
        self.router_idurl = arg        

    def doRememberProxyNode(self, arg):
        """
        Action method.
        """
        self.router_identity = identitydb.get(self.router_idurl)

    def doUpdateMyIdentity(self, arg):
        """
        Action method.
        """
        from p2p import network_connector
        network_connector.A('reconnect')        
        
    def doStartListening(self, arg):
        """
        Action method.
        """

    def doStopListening(self, arg):
        """
        Action method.
        """
        self.router_identity = None
        self.router_idurl = None

    def doSendFileToRouter(self, arg):
        """
        Action method.
        """

    def doReportStarted(self, arg):
        """
        Action method.
        """

    def doReportStopped(self, arg):
        """
        Action method.
        """

    def doReportResponseTimeout(self, arg):
        """
        Action method.
        """

    def doReportServiceRefused(self, arg):
        """
        Action method.
        """

    def doReportNodesNotFound(self, arg):
        """
        Action method.
        """

    def doDestroyMe(self, arg):
        """
        Remove all references to the state machine object to destroy it.
        """
        automat.objects().pop(self.index)
        global _ProxyReceiver
        del _ProxyReceiver
        _ProxyReceiver = None

    def _find_random_node(self):
        if _Debug:
            lg.out(_DebugLevel, 'proxy_receiver._find_random_node')
        new_key = dht_service.random_key()
        d = dht_service.find_node(new_key)
        d.addCallback(self._some_nodes_found)
        d.addErrback(lambda x: self.automat('nodes-not-found'))
        return d

    def _some_nodes_found(self, nodes):
        if _Debug:
            lg.out(_DebugLevel, 'proxy_receiver._some_nodes_found : %d' % len(nodes))
        if len(nodes) > 0:
            node = random.choice(nodes)
            d = node.request('idurl')
            d.addCallback(self._got_remote_idurl)
            d.addErrback(lambda x: self.automat('nodes-not-found'))
        else:
            self.automat('nodes-not-found')
        return nodes
            
    def _got_remote_idurl(self, response):
        if _Debug:
            lg.out(_DebugLevel, 'proxy_receiver._got_remote_idurl response=%s' % str(response) )
        try:
            idurl = response['idurl']
        except:
            idurl = None
        if not idurl or idurl == 'None':
            self.automat('nodes-not-found')
            return response
        d = identitycache.immediatelyCaching(idurl)
        d.addCallback(lambda src: self.automat('found-one-node', idurl))
        d.addErrback(lambda x: self.automat('nodes-not-found'))
        return response

    def _router_acked(self, response):
        if _Debug:
            lg.out(_DebugLevel, 'proxy_receiver._router_acked response=%s' % str(response))
        #TODO
        
        
#------------------------------------------------------------------------------



def main():
    from twisted.internet import reactor
    reactor.callWhenRunning(A, 'init')
    reactor.run()

if __name__ == "__main__":
    main()
