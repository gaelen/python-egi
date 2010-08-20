#!/usr/bin/python
# -*- coding: cp1251 -*- 

"""     

    A fake implementation of the "egi.netstation" component  (only prints  some info to the standard output, but does not try to communicate with Netstation ).     
    
"""     

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

import simple as internal # for the fake object we need only the exception and the timestamps          
# from socket_wrapper import Socket     
import sys

#
# "forward" these names to be used from outside     
#

Error = internal.Eggog     
ms_localtime = internal.ms_localtime     


# -----------------------------------------------------------------------------

#
# the simplest version without "packet stamping" and "back synchronization" ( needed for good sync()-ing )
#

def Print(*args, **kwargs) :     
	
	""" Print() function -- exchange typing two brackets for (not) typing the prefix  """     
	
	write = sys.stdout.write
	
	write (" Netstation [fake]: ")
	for arg in args: write( repr(arg) )     
	for (k,v) in kwargs.iteritems() : write( "%s=%s" % (k,v) )     
		
	write ('\n')     
	
		

#
# TODOtodo: (a) wrap the process of starting of the new thread ( and finalization ) in separate functions ;
#           (b) re-use (a) ;
#           (c) syncronize in single-threaded mode .     
#

class Netstation :     

    """ Imitates Python interface for a connection with the Netstation via a TCP/IP socket. """

    ## -----------------------------------------------------------

    def __init__( self ) :

        Print( '__init__()' )     

    ## -----------------------------------------------------------

    def enumerate_responses( self ) :
        """ (1) check .qsize() ; (2) .get() all these elements """     

        n_available = 0

        for i in xrange( n_available ) :     

            data = self._get()
            yield data     
        
        # ''' return None '''     

    ## # a shortcut to be exported     
    ## enumerate_responses = _enumerate_received     


    # a simple 'dummy processor' made for convenience     
    ## def process_responces( self, resp_handler = lambda resp: pass ) :     
    def process_responces( self ) :     

        for resp in self.enumerate_responses() :

            # resp_handler( resp )
            pass     

        # return None
        Print( 'process_responces()' )

        ## change the return value depending on the resp_handler() return result ?
        ## ( e.g. break the loop on True ? )

        # don't need all these complifications at the moment )     

    ## -----------------------------------------------------------

    def initialize( self, str_address, port_no ) :
        """ open the socket /and/ start the 'Mr. Postman' thread """     

        Print( 'initialize( %s, %s )' % (str_address, port_no)  )     
        

    def finalize( self, seconds_timeout = 2 ) :
        """ send the thread the 'Done' message and wait until it finishes """

        Print( 'finalize( timeout: %s seconds )' % (seconds_timeout, )  )     

        # debug
        print " egi: stopping ... "

        ## self._disconnect()     


    ## -----------------------------------------------------------     

    def BeginSession( self ) :     
        """ say 'hi!' to the server """     

        Print( 'BeginSession()' )
        

    def EndSession( self ):
        """ say 'bye' to the server """

        Print( 'EndSession()' )
        
        
    ## -----------------------------------------------------------

    def StartRecording( self ):
        """ start recording to the selected ( externally ) file """

        Print( 'StartRecording()' )     


    def StopRecording( self ):
        """ stop recording to the selected file;     
            the recording can be resumed with the BeginRecording() command     
            if the session is not closed yet .     
        """     

        Print( 'StopRecording()' )     

    ## -----------------------------------------------------------

    #
    # the next two are not supposed to be used "manually" ( by the user ) --
    # -- especially becuase at least our version of the Netstation software
    # often crashes if the delay between the 'attention' and the 'time' commands
    # exceeds some dark secretly defined timeout value     
    #

    def _SendAttentionCommand( self ):
        """ Sends and 'Attention' command """ # also pauses the recording ?

        # Print( 'SendAttentionCommand' )     


    def _SendLocalTime( self, ms_time = None ):
        """ Send the local time (in ms) to Netstation; usually this happens after an 'Attention' command """     

        # Print( 'SendAttentionCommand', { 'ms_time' : ms_time } )     
        
    ## -----------------------------------------------------------

    def sync( self, timestamp = None ) :
        """ a shortcut for sending the 'attention' command and the time info """

        # in the simplest form ,
        # we just send the instructions ( and hope they won't be delayed too much ) ;     
        # though it might be a good idea to wait for the reponse here     
        
        ## self.SendAttentionCommand()
        ## self.SendLocalTime( timestamp )

        # TODO/todo : change the code so that we'll wait for the result in the calling thread     

        Print(   'sync( %s = %s)' %  ('timestamp' , timestamp )   )     
    
    ## -----------------------------------------------------------

    # send_event, send_simple_event

    def send_event( self, key, timestamp = None, label = None, description = None, table = None, pad = False ) :     
        """
            Send an event ; note that before sending any events a sync() has to be called
            to make the sent events effective .     

            Arguments:
            -- 'id' -- a four-character identifier of the event ;
            -- 'timestamp' -- the local time when event has happened, in milliseconds ;
                              note that the "clock" used to produce the timestamp should be the same
                              as for the sync() method, and, ideally,
                              should be obtained via a call to the same function ;
                              if 'timestamp' is None, a time.time() wrapper is used .
            -- 'label' -- a string with any additional information, up to 256 characters .     
            -- 'description' -- more additional information can go here ( same limit applies ) .
            -- 'table' -- a standart Python dictionary, where keys are 4-byte identifiers,
                          not more than 256 in total ;
                          there are no special conditions on the values,
                          but the size of every value entry in bytes should not exceed 2 ^ 16 .     
                          
            Note A: due to peculiarity of the implementation, our particular version of NetStation
                    was not able to record more than 2^15 events per session .
                    
            Note B: it is *strongly* recommended to send as less data as possible .
            
        """     
        
        
        kwargs = {                             \
                   'key'         : key         ,
                   'timestamp'   : timestamp   ,
                   'label'       : label       ,
                   'description' : description ,
                   'table'       : table       ,
                   'pad'         : pad         \
                }     

        Print( 'send_event() : ', kwargs )     
        
    
    ## -----------------------------------------------------------



# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

if __name__ == "__main__" :

    print __doc__
    print "\n === \n"
    # print "module dir() listing: ", __dict__.keys()
    print "module dir() listing: ", dir()


