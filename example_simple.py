# import egi

"""
   The only real difference in the code between this example and the "multi-threaded" one
   are three lines:

   
   1. "import egi.simple as egi" vs "import egi.threaded as egi"
   2. "ns.connect('11.0.0.42', 55513)" vs. "ns.initialize('11.0.0.42', 55513)"

   -- in the beginning

   and
   3. "ns.disconnect()" vs "ns.finalize()"

   -- in the end of the file .

   The two last differences are left intentionally,
   to make a little bit more difficult to mix up the two variants of usage of the module .     

"""

import egi.simple as egi
## import egi.threaded as egi
# make the script reenterable )     
reload(egi)     

import sys # sys.argv[]     
import time # time.time()     

# ms_localtime = egi.egi_internal.ms_localtime     
ms_localtime = egi.ms_localtime     

#
# Panels / Multi-Port ECI --> log
# or just Panels --> Log (I assume you have selected 'Long Form')
#

ns = egi.Netstation()
ns.connect('11.0.0.42', 55513) # sample address and port -- change according to your network settings
## ns.initialize('11.0.0.42', 55513)
ns.BeginSession()     

# "Connected to PC" 
# log: 'NTEL' \n     

ns.sync()     

# log: the timestamp     

ns.StartRecording()

time.sleep(5) # NS removes "too short" session files on exit     


#
# "tutorial part"
#

ns.send_event('evt1')
time.sleep(0.1)  # force the events to arrive in the "correct" order

# log: tag in single quotes     
## timestamps : NS time since the moment of recording     

ns.send_event('evt2', label="event2")
time.sleep(0.1)  # force the events to arrive in the "correct" order

# log: label without quotes     

ns.send_event('evt3', label="event3", description="this will appear")
time.sleep(0.1)  # force the events to arrive in the "correct" order

# description on the next line     

ns.send_event('evt5', timestamp=egi.ms_localtime()) 
ns.send_event('evt6', description='back in time', timestamp=egi.ms_localtime() - 50)

time.sleep(0.1)  # force the events to arrive in the "correct" order

# appear in the order of posting, but with "correct" timestamps ( i.e. last has a timestamp that is 50 ms "earlier" than the previous )     


#
# two real-life examples 
#

ns.send_event( 'evt_', timestamp=egi.ms_localtime() ) 
time.sleep(0.1)  # force the events to arrive in the "correct" order

ns.send_event( 'evt_', timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} ) 
time.sleep(0.1)  # force the events to arrive in the "correct" order

# log: ... 1.  'fld2' : abc     


ns.send_event('stop')

time.sleep(5)

ns.StopRecording()

ns.EndSession()     
ns.disconnect()

## ns.EndSession()     
## ns.finalize()     

# 0. open file -- Events -- Event List -- opt-click -- File -- Save Events     
# 1. auto rec is not recommended ;  
# 2. in our version of NetStation software, the 'Label' filed shows up and gets exported ;     
#     the 'description' appears only in the log file, so it seems to exist for amusement mostly .     
# 3. evt5,6 would appear in the corrected order ;     
#     actually, *all* the events get sorted, so if som events arrive at the same millisecond, they may appear in the "wrong" order in the list     

