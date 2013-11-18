# import egi

# import egi.simple as egi
import egi.threaded as egi
## # make the script reenterable )     
## # -- for ipython "%edit ... " tests     
## reload(egi)     

import sys # sys.argv[]     
import time # time.sleep()     

#
# probably 'ms_localtime()' stuff should be hidden under the hood as well,
# but at the moment we'll need to explicitly use this function when we send markers,
# as this is what we use internally in sync()     
#


## ms_localtime = egi.egi_internal.ms_localtime     
ms_localtime = egi.ms_localtime     


#
# Panels / Multi-Port ECI --> log
# or just Panels --> Log (I assume you have selected 'Long Form')
#

ns = egi.Netstation()

# sample address and port -- change according to your network settings
## ns.connect('11.0.0.42', 55513)
ns.initialize('11.0.0.42', 55513)  
# Multi-Port ECI Window: "Connected to PC"

ns.BeginSession()     
# log: 'NTEL' \n     

ns.sync()     
# log window: the timestamp ( the one provided by ms_localtime() )     
## ns.send_event('evt2', label="event2")


ns.StartRecording()
# I do not recommend to use this feature, as my experience is that Netstation
# [ the version _we_ use, may be not the latest one ] may sometimes crash
# on this command ; so I'd rather click the 'record' and 'stop' buttons manually.

time.sleep(5) # pretend we do sth very useful here ...
# for the version of the script without time.sleep(),
# Netstation [ the version we use ] seems to dislike short session files
# and silently removes it on exit .
# as in actual recording files are seldom shorter that at least a few seconds,
# this does not seem to be a big problem .     



#
# first let us send some "sample" events,
# then I'll show some more realistic examples     
#



# in the simplest form ( that we probably won't use in real experiment, though ),
# the send_event() method takes only a four-character event identifier --     
# -- in this case, it's "evt1" :     

ns.send_event('evt1')
# log window: shows event id in single quotes     
# ( there are also timestamps -- Netstation local time since the beginning of the session )

time.sleep(0.1)  # for the sake of example --
# -- force the events to arrive in the "correct" order :
# as Netstation re-sorts events according to their timestamp values,
# the events that have the same millisecond for the timestamp value,
# may change their order of appearance in the event list .
# so we introduce some additional short artificial delay 
# to help our events look nicely in the log and event list .     


# so we _must_ invent some ugly four-character code,
# but can also use some alias of variable length -- up to 256 characters, if I remember correctly :     
ns.send_event('evt2', label="event2")
# log window: label without quotes
# note that the label goes both to the log *and* to export later,
# in other words the label can be exported ( sth we expected to happen, right ? )     

time.sleep(0.1)  # force the events to arrive in the "correct" order


ns.send_event('evt3', label="event3", description="this is a description of event 3")
# the description, if exists, also goes to the log window --     
# -- but, at least for our version of NetStation,
# CAN NOT BE EXPORTED -- so it seems that it's main goal is pure amusement .
# If one is curious, this also has variable length ( up to 256 characters,
# if I am not mistaken )     

time.sleep(0.1)  # force the events to arrive in the "correct" order


# but what we really want is attach the information about the current time moment,
# or may be even some other moment back in time :     

ns.send_event('evt5', timestamp=egi.ms_localtime()) 
ns.send_event('evt6', description='back in time', timestamp=egi.ms_localtime() - 50)

# 1. At the moment we have to use the egi.ms_localtime() function, not some other
#    like time.time(), for two reasons :
#    (a) the timestamp should fit 32 bits ;
#    (b) the timestamps used internally in .sync() should be provided by the same function .

# What I probably should do here is make the egi.ms_localtime() call the default option .
# ( Actually, it *is* the default option -- it just happens then in a different thread
#   right before the actual communication. This is Ok for .sync(),
#   but should probably be changed for .send_event() . )

# 2. Note that in the Log Window the events appear in the order of posting,
#    but with "correct" timestamps ( i.e. last has a timestamp that is 50 ms "earlier" than the previous )     

time.sleep(0.1)  # force the events to arrive in the "correct" order



#
# now two real-life examples 
#


ns.send_event( 'evt_', timestamp=egi.ms_localtime() ) 

ns.send_event( 'evt_', timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} ) 

# log window: Now we have fields -- they may come in the 'wrong' order 
#  ... 1.  'fld2' : abc ,     
# but if the event identifiers are unique ( and they *should* be ), this is not important .     

time.sleep(0.1)  # force the events to arrive in the "correct" order

ns.send_event('stop') # just to have some "end of session" marker in the log     

time.sleep(5) # for symmetry )     

ns.StopRecording()

## ns.EndSession()     
## ns.disconnect()

ns.EndSession()     
ns.finalize()     

# Final notes: 

# 0. To view / export the event markers:
#    open session file -->
#    --> Events --> Event List -->
#    --> opt-click to "unwrap" all the field entries
#    --> File --> Save Events

# 1. Starting / stopping the recording automatically is not recommended ;

# 2. Maximum amount of entries in the table is 256 ;
#    the length (in bytes) of every value in the table should not exceed 65536 .


# 3. In our example events 5,6 would appear in the log window in the order of appearance,
#    but in the corrected order for the event list ;     
#    actually, for the event list *all* the events are sorted according to their timestamps,
#    so if some events arrive at the same millisecond, they may appear in the "wrong" order in the list .     
