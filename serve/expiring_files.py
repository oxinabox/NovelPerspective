##########################
# This is apparently threadsafe
# see list of atomic operations:
# http://effbot.org/zone/thread-synchronization.htm
# modifying a list in place is fine

import time
import tempfile
import atexit

to_expire=[]

def mark_to_expire(vv):
    to_expire.append((time.time(), vv))
    return vv

def expiring_temp_file(name_base):
    vv = tempfile.NamedTemporaryFile(suffix=name_base, delete=False)
    mark_to_expire(vv)
    return vv


@atexit.register
def check_expires(timeout = 2*60*60): # 2 hours
    # I don't have to really worry too much about how the deletion happens
    # User will be well and truely done with the files by the time it does
    # This is a bit hacky, but I got research work to do.

    now = time.time()
    keep_after = 0
    for ii,(create_time, fh) in enumerate(to_expire):
        if create_time - now > timeout:
            fh.delete=True # let it auto delete
            keep_after = ii
        else:
            # Have found first that it not too old
            break
    for ii in range(0, keep_after):
        to_expire.pop(ii)



