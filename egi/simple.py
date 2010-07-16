#!/usr/bin/python
# -*- coding: cp1251 -*- 

#
# inspired by Andrew Butcher's 'libnetstation' cpp library : [ http://code.google.com/p/libnetstation/ ]     
#

from __future__ import with_statement # for debug dumps     


"""
    This module provides a simple Python wrapper
    to the EGI Netstation GES hardware communication protocol;     

    ref.: see "EGI Hardware Technical Manual" of Dec 21 2006,
          Chapter 7 and Appendix G 

    One can also see "EGI Systems Technical Manual", Ch. 6 and App. G,
    or "EGI System 200 Technical Manual" -- Ch. 6 and Appendix E,
    ( though the last one seems to be a little bit more incomplete than the other ones )     
    
"""     

# import socket
from socket_wrapper import Socket     
import struct     

import math, time # for time in milliseconds     

import sys, exceptions # sys.

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

#
# our very special exception     
#

class Eggog( exceptions.Exception ) :
    """
        general exception, will make things more specific if necessary ;
        at the moment it means that the server has returned an error --
        -- or one of the strings was not a 4-byte one when it should =%:-(     
    """

    @staticmethod     
    def check_type( string_key ) :
        """     
            check if the type of the key is string type --
            -- and raise an exception if it isn't )
        """     

        if type( string_key ) != type( '' ) :     

            raise self.__class__(  "'%s': EGI wants the key to be four _characters_ (not %s) !" % (type(string_key), )  )     
        
        else :
            
            return True
        

    @staticmethod     
    def check_len( string_key ) :
        """     
            check if the length of the key is exactly four characters --
            -- and raise an exception if it isn't )
        """     

        if len( string_key ) != 4 :

            raise self.__class__(  "'%s': EGI wants the key to be exactly four characters!" % (string_key, )  )     
        
        else :
            
            return True     
        
    
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

#
# accessory functions     
#

global _ts_last 
_ts_last = 0     
def ms_localtime(warnme = True) :
    """ gives the local time in milliseconds ( modulo 1.000.000.000 ) """

    global _ts_last
  
    # we just need some standard way to represent local time with ms precision
    # ( and by a 32-bit integer, but this can wait until 2036 )

    #             ms    s    m    h     
    # ms_one_day = 1000 * 60 * 60 * 24     
    # current_time = math.floor( time.time() * 1000 ) % ms_one_day     

    ## ms_current_time = int(  math.floor( time.time() * 1000 )  )  
    ## return ms_current_time     

    # debug ( check the byte order )
    # return 1     
    
    ## seconds_in_a_day = 60 * 60 * 24 # 86400     
    ## day_time_ms = int(   math.floor(  ( time.time() % seconds_in_a_day ) * 1000  )   )     
    ## 2^32 = 4294967296
    modulo = 1000000     
    # modulo = 10 # tests     
    ms_remainder = int(   math.floor(  ( time.time() % modulo ) * 1000  )   )     

    if warnme and ( ms_remainder < _ts_last ) :     

        raise Eggog( "internal 32-bit counter passed through zero, please resynchronize ( call .synch() once again )" )     

    _ts_last = ms_remainder
  
    return ms_remainder # finish the recording before midnight ( and start after 00:00 )     


# -----------------------------------------------------------------------------

# a predicate for external timestamps     
def is_32_bit_int_compatible( i ) :
    """ check if we can transmit the given number as a 32-bit integer """

    #
    # can we convert the input to an integer value ?     
    #

    try :     

        i_ = int( i )

    except :

        return False

    if i_ != i :

        return False
        
    #
    # now check if it fits 32-bits     
    #

    if i_ < 0 :

        i_ = - ( i_ + 1 ) # -128 .. 127, etc     

        signed_max = 0x7FFFFFFF

        return ( i_ <= signed_max )     

    # for positive values the limit is twice bigger
    allf = 0xFFFFFFFF

    return ( i_ <= allf )     
    

# -----------------------------------------------------------------------------

#
# ineffective quick-and-dirty snippet for 'uniq(list)'     
#

def _uniq( list ) :     
        """ returns list without duplicates """     
        
        d = {}     
        for e in list :     
                d[e] = 1     
                
        return d.keys()     
        

# -----------------------------------------------------------------------------

# 
# key padding and truncation : as the keys probably have to be unique,
# we want these operations to be explicit
#
def pad_key( k ) :

    n = len(k)
    d = n - 4

    if d > 0 :

        return  ( k + ' ' * d )

    else :

        return k

# pad or cut the key string to get exactly four characters     
def make_fit( k ):

    n = len(k)
    d = n - 4

    if d > 0 :

        return  ( k + ' ' * d )

    else :

        return k[0:4]     
    

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

#
# "packing things"     
#

class _Format :
    """     
        a wrapper around a dictionary that contains 'struct' format strings
        for the command extentions     
    """     

    def __init__( self ) :
        """ create the dictionary """

        # ref. : p.193 of App.G: "Experimental Control Protocol"     
        self._format_strings = \
        { 'Q' : "=4s" ,
          'X' : '' ,
          'B' : '' ,
          'E' : '' ,
          'A' : '' ,
          'T' : "=L" , # "=l" , 
          'D' : None , # a variable-length structure can follow, but the header is "=cHll4s"     
          'I' : "=B" ,
          'Z' : '' ,
          'F' : "=4c" # in theory, it should be "=h" ; but for the protocol v.1, it isn't .     
        }

    def __getitem__( self, key ) :

        ## return self._format_strings.get(key, None)
        return self._format_strings.get( key ) ## get() throws no exception     

    def format_length( self, key ) :
        """ return the number of the bytes to read or write for the given command code """

        return struct.calcsize( self[key] )     

    def pack( self, key, *args ) :
        """ pack the arguments according to the format """

        ## return struct.pack(self[key], arg)
        # packing and unpacking here are assymetrical,
        # as for packing we want to send a complete string :
        ## fmt = '=c' + self[key].lstrip('@=<>!')     

        fmt = '=c' + self[key].lstrip('=')     

        # or more strict ( though not tested ) :     
	'''
        fmt_ = self[key].lstrip('=')     
        prefix = '='  
        PREFIXES = '@=<>!'        
        if fmt_[0] in PREFIXES :     

            prefix = fmt_[0]     

        fmt = prefix + 'c' + self[key].lstrip( PREFIXES )     
        '''     


	# # debug     
	# print "format string: '%s', args: " % (fmt, ), args     

        result = struct.pack(fmt, key, *args)     

	# # debug     
        # print result

        return result
        
    
    def unpack( self, key, data ) :
        """ unpack the argument according to the format """

        return struct.unpack(self[key], data)     
    

## 
## #
## # we need only one object of this kind     
## #
## _formats = _Formats()     
## 

def _get_endianness_string( _map = { 'little' : 'NTEL', 'big' : 'UNIX' } ) :
    """ check the endianness of the system """

    # NB: Netstation also accepts 'MAC-' .     
    key = sys.byteorder

    return _map[ key ]
    

# -----------------------------------------------------------------------------

#
# pack accessory utilities     
#

def _cat( *strings ) :
    """ concatenate all the strings in a 'packed' string """ # % operator does not make any padding by default, does it ?

    # filter empty strings or None values :
    args = [s for s in strings if s is not None and len(s) > 0 ]

    fmt_list = []
    for s in args :
        fmt_list.append( '%ds' % ( len(s), ) )

    fmt = ''.join( fmt_list )     

    ## return struct.pack( fmt, *args )     
    result = struct.pack( fmt, *args )     

    # # debug     
    # print "cat '%s' =-> '%s'" % ( strings, result )

    return result     
    

# -----------------------------------------------------------------------------

#
# structures and utilities to help sending extended events     
#

def pstring( s ) :
    """ pack 's' as a single-byte-counter Pascal string """

    if s is None :     
        return None     

    # else ...     

    fmt = '%dp' % ( len(s) + 1 )     

    ps = struct.pack(fmt, s)     

    # # debug     
    # print "pstring('%s', '%s') : '%s'" % (fmt, s, ps)

    return ps     


'''     
def cstring( s ) :
    """ we do not need to pack any strings to send them, except for the case if we need zero padding """

    return s ## todo : add a 'length' argument for padding ?

'''     


class _DataFormat :
    """ a helper for creating the "Extended" events (many key fields, variable data) """

    def __init__( self ) :     
        """ create the main reference table """

        # ref. : p.196 of App.G: "Experimental Control Protocol"     
        self._translation_table = \
        { type(True) : ( 'bool', '=?' ) , # Python standard ("struct"): one byte     
          # there are no "short" integers by default in Python     
          type(1) : ( 'long', '=l' ) ,  # '=' -- translation is: four bytes
          # type(1.0) : ( 'doub', '=d' ) ,  # " 64 bit I3E floating-point number "     
          ## temp test     
          ## type(1.0) : ( 'sing', '=f' ) ,  # " 64 bit I3E floating-point number "     
          # bugfix: due to another bug, Netstation seems to ignore the byte order 
          # for the floating-point values ( and assumes 'UNIX' ( i.e. network / 
          # / "big-endian" ) order of bytes )
          type(1.0) : ( 'doub', '!d' ) ,  # " 64 bit I3E floating-point number "     
          type('') : ( 'TEXT', '%ds' ) , # !! a special case
          ## ---------------------------------
          ## type( None ) : ( '\x00' * 4, '=H' ) # one more special case for a bugfix ,
          ##                                     # see pack() method comments below     
        }     
        
    
    def _pack_data( self, data ) :
        """ try to pack the argument according to its type; by default, a str() conversion is sent """     
        
        hints = self._translation_table.get( type(data), None )
        
        if hints is None :

            # "one-level recursion" :     
            return self.pack( str(data) )
        
        ## # our special case ( grep 'bugfix' to see why we want a zero block )     
        ## if data is None: data = 0
        
        # else ...     
        
        # 'DescType' + 'length' + 'data'
        desctype = hints[0]
        if desctype == 'TEXT' :     
            length = len(data)
            data_str = data     
        else :
            length = struct.calcsize( hints[1] )
            data_str = struct.pack( hints[1], data )
            
        length_str = struct.pack('=H', length)
        
        
        return _cat(desctype, length_str, data_str)
        
    
    def _pack_dict( self, table, pad = False ) :     
        """     
            pack the data from the given dictionary for sending ;
            if the 'pad' argument is False, the keys must be four-character strings ,
            otherwise they will be converted to strings by str() and then truncated
            or padded with spaces .
            Note that for the latter case the uniqueness of the generated key ids is not quaranteed .     
        """

        keys, values = zip( *table.items() )

        # we hope not to be called with an empty dict(), but ...     
        if len( keys ) <= 0 :
            return struct.pack('0s', '')     

        #
        # preprocess the keys ...     
        #

        # 4-byte condition check
        if not pad :     
            # "try" ... 
            map( Eggog.check_type, keys )     
            map( Eggog.check_len, keys )

        else : # else convert to string and truncate or pad
            
            for i in xrange(len(keys)) :

                k = keys[i]     
                if type(k) != type( '' ) :
                    
                    k = make_fit( str(k) )
                    keys[i] = k
                    
                
            
        # check uniqueness of the keys
        

        # 
        # pack the values     
        #

        nkeys = len(keys)     
        
        if nkeys > 255 :
            raise Eggog( "too many keys to send (%d > 255)" % (nkeys, ) )     
        
        nkeys_str = struct.pack( '=B', nkeys )     

        values_packed = map( self._pack_data, values )

        items_packed = [nkeys_str, ] * ( 2 * nkeys + 1 )
        items_packed[1::2] = keys[:]
        items_packed[2::2] = values_packed

        result = _cat( *items_packed )     

        return result     
        
    '''
    def _make_simple_event( self, timestamp = None, key, pad = False ) :
        """     
            pack a simple message with the given key ;

            if the 'pad' argument is 'False' -- an exception is raised in the case
            if the key is not a (unique) four-character string ;
            otherwise, if the 'pad' value is True,
            the routine tries to convert truncate or pad the key
            to form a 4-byte string .
            
            nb. if the 'timestamp' argument is None -- the according field is set
                by a local routine at the moment of the call .     
        """     

        sss     
        
    '''

    def _make_event_header( self, size_of_the_rest, timestamp, duration, keycode ) :
        """
            make an event message header from the given data according to the protocol

            'size_of_the rest' is the size of the rest part of the event message     
        """     

        # 'D' and the size of the message are not counted     
        sizeof_int32 = 4     
        addendum = 3 * sizeof_int32
        
        total_length = addendum + size_of_the_rest

        ## return struct.pack( "=sH2L4s", 'D', total_length, timestamp, duration, keycode )     
        result_str = struct.pack( "=sH2L4s", 'D', total_length, timestamp, duration, keycode )     

        # # debug     
        # print 'header: "%s" ' % (result_str, )

        return result_str     


    def pack( self, key, timestamp = None, label = None, description = None, table = None, pad = False ) :     
        """     
            pack the arguments according to the Netstation Event structure ;     

            if the 'pad' argument is 'False' -- an exception is raised in the case
            if either the main key or one from the table keys is not a (unique)
            four-character string ; otherwise, if the 'pad' value is True,
            the routine tries to convert truncate or pad the key to form a 4-byte string .

            nb. if the 'timestamp' argument is None -- the according field is set
                by a local routine at the moment of the call .     
        """     

        duration = 1
        if timestamp is None :
            timestamp = ms_localtime()     

        #
        # bufix : as it seems that NetStation
        #
        #        (a) does not clean the internal buffer for the "event" data
        #          and
        #        (b) ignores the "total packet length" from the "event" message header
        #            when reading the "label" / "description" / "key/data" information ,     
        #
        #        we have to append a fake "tail" to our message if the case if it is incomplete --
        #        -- otherwise either garbage or the information from the previous datagram
        #        would be erroneously recognized as belonging to ours .     
        #
        #        nb. this also means that the 'label' / 'description' / 'key/data' entries
        #            cannot be optional .     
        #        

        if not is_32_bit_int_compatible( timestamp ) :
            
            raise Eggog(  "only 'small' 32-bit integer values less than %d are accepted as timestamps, not %s"  %  ( 0xffffFFFF, timestamp )  )     
        
        if label is None : label = ''
        if description is None : description = ''

        label_str = pstring( label )     
        description_str = pstring( description )     

        if table is None or len( table.keys() ) <= 0 :
            # explicitly state that the number of keys is zero ( see above comment )     
            table_str = struct.pack( 'B', 0 )     
        else :     
            table_str = self._pack_dict(table, pad)

        size = len( label_str ) + len( description_str ) + len( table_str )     
        
        # # debug     
        # print "+size: ", size     

        header_str = self._make_event_header( size, timestamp, duration, key )     

        # # debug     
        # print "'%s', '%s', '%s', '%s'" % ( header_str, label_str, description_str, table_str )     

        result_str = _cat( header_str, label_str, description_str, table_str )     
        
        return result_str     
        

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

class Netstation :     
    """ Provides Python interface for a connection with the Netstation via a TCP/IP socket. """

    def __init__( self ) :

        self._socket = Socket()     
        self._system_spec = _get_endianness_string()
        self._fmt = _Format()
        self._data_fmt = _DataFormat()     

    def connect( self, str_address, port_no ):
        """ connect to the Netstaton machine """

        self._socket.connect( str_address, port_no )

        # return None     

    def disconnect( self ):
        """ close the connection """

        self._socket.disconnect()     

        # return None         

    ## -----------------------------------------------------------
        
    def GetServerResponse( self, b_raise = True ):
        """ read the response from the socket and convert it to a True / False resulting value """

        code = self._socket.read(1)


        if code == 'Z':

            return True

        elif code == 'F' : # an 'F' <error code> sequence     

            error_info_length = self._fmt.format_length( code )     
            error_info = self._socket.read( error_info_length )

            if b_raise :

                err_msg = "server returned an error : " + repr( self._fmt.unpack(code, error_info) )     
                raise Eggog( err_msg )     
                
            else :     
                return False     
        
        elif code == 'I' : # a version byte should follow     

            version_length = self._fmt.format_length( code )     
            version_info = self._socket.read( version_length )
            version = self._fmt.unpack( code, version_info )     

            ## # debug
            ## print version

            self._egi_protocol_version = version     
            self._egi_protocol_version = version[0]     

            return self._egi_protocol_version # just a bit more informative than 'None'     
            
        else : # something completely unexpected     

            if b_raise :
                
                raise Eggog(  "unexpected character code returned from server: '%s'" % (code, )  )     

            else :

                return False     
            
    
    ## -----------------------------------------------------------
    
    def BeginSession( self ) :     
        """ say 'hi!' to the server """     

        ## self._connection.write( 'Q%s' % ( systemSpec, )  )     
        ## assert self.GetServerResponse() == True # " the quick-&-dirty way " // to-do: create an own exception     

        message = self._fmt.pack( 'Q', self._system_spec )
        self._socket.write( message )     

        # debug
        print "BS: ", message     

        return self.GetServerResponse()     
        

    def EndSession( self ):
        """ say 'bye' to the server """

        self._socket.write( 'X' )     
        # self._connection.write( 'X' ).flush()     

        return self.GetServerResponse()     
        
    
    ## -----------------------------------------------------------

    def StartRecording( self ):
        """ start recording to the selected ( externally ) file """

        self._socket.write( 'B' )     
        
        return self.GetServerResponse()     


    def StopRecording( self ):
        """ stop recording to the selected file;     
            the recording can be resumed with the BeginRecording() command     
            if the session is not closed yet .     
        """     

        self._socket.write( 'E' )     
        
        return self.GetServerResponse()     

    ## -----------------------------------------------------------

    def SendAttentionCommand( self ):
        """ Sends and 'Attention' command """ # also pauses the recording ?

        self._socket.write( 'A' )
        
        return self.GetServerResponse()     


    def SendLocalTime( self, ms_time = None ):
        """ Send the local time (in ms) to Netstation; usually this happens after an 'Attention' command """     

        if ms_time is None :     
            ms_time = ms_localtime()

        message = self._fmt.pack( 'T', ms_time )     

	# # debug     
	# print message, struct.unpack('=L', message[1:])     

        self._socket.write( message )     

        return self.GetServerResponse()     
        
    ## -----------------------------------------------------------

    def sync( self, timestamp = None ) :
        """ a shortcut for sending the 'attention' command and the time info """

        if ( self.SendAttentionCommand() ) and ( self.SendLocalTime( timestamp ) ) :

            return True

        else :

            raise Eggog( "sync command failed!" )
        
    
    ## -----------------------------------------------------------

    # send_event, send_simple_event

    ## def pack( self, key, timestamp = None, label = None, description = None, table = None, pad = False ) :     
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

        '''
        
        #
        # bufix : as it seems that NetStation
        #
        #        (a) does not clean the internal buffer for the "event" data
        #          and
        #        (b) ignores the "total packet length" from the "event" message header
        #            when reading the "label" / "description" / "key/data" information ,     
        #
        #        we have to append a fake "tail" to our message if the case if it is incomplete --
        #        -- otherwise either garbage or the information from the previous datagram
        #        would be erroneously recognized as belonging to ours .     
        #

        # 
        # the following would make the _DataFormat.pack() method     
        # to create (empty) description and label fields as well, if necessary     
        #
        
        if ( table is None ) or ( len( table.keys() ) <= 0 ) :     

            zero_entry = { '\x00' * 4 : 0 }     
            
        '''     

        message = self._data_fmt.pack( key, timestamp, label, description, table, pad )     
        self._socket.write( message )     

        '''     
        # # debug     
        # print message     
        with open('message.dump', 'ab') as l :     
             l.write("'")
             l.write(message)
             l.write("'")
             l.write('\n\n---\n\n')

        '''     

        return self.GetServerResponse()     


    ## -----------------------------------------------------------

    # legacy code     
    def SendSimpleEvent(self, markercode, timestamp = None ):
        """ send a 'simple' marker event -- i.e. an event marker without any additional information;     
        
            nb. the marker code must be a string of exactly four characters
        """     

        ## assert len(markercode) == 4, "the length of the event marker code must be *exactly* four characters"

        #
        # read the time     
        #

        if timestamp:

            current_time = timestamp

        else: 

            # one day is 1000 * 60 * 60 * 24 milliseconds
            one_day = 1000 * 60 * 60 * 24
            current_time = math.floor( time.time() * 1000 ) % one_day     


        default_duration = 1 # also in milliseconds     


        sizeof_int32 = 4     

        event_min_size = 3 * sizeof_int32     
        data_string = 'D%s%s%s%s' % ( struct.pack('h', event_min_size), # using 'default', or "native", endianness     
                                      struct.pack('l', current_time),
                                      struct.pack('l', default_duration),
                                      struct.pack('4s', markercode),
                                      )

        self._socket.write( data_string )     

        return self.GetServerResponse()     





# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

if __name__ == "__main__" :

    print __doc__
    print "\n === \n"
    # print "module dir() listing: ", __dict__.keys()
    print "module dir() listing: ", dir()


