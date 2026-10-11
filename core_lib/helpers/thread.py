import threading
import time
from datetime import timedelta


class LockGroup(object):
    def __init__(self, max_age: timedelta):
        self.lock_dict = {}
        self.lock = threading.Lock()
        self.max_age = max_age

    # Returns a lock object, unique for each unique value of param.
    # The first call with a given value of param creates a new lock, subsequent
    # calls return the same lock.
    def get_lock(self, param) -> object:
        with self.lock:
            current_time = int(round(time.time() * 1000))
            if param not in self.lock_dict:
                self.lock_dict[param] = {'time': current_time, 'lock': threading.Lock()}
            lock_item = self.lock_dict[param]
            lock_item['time'] = current_time
            return lock_item['lock']

    # Removes locks not requested for longer than max_age.
    # A lock that is currently held is never removed, otherwise the next
    # get_lock() for the same param would hand out a second, different lock.
    def clear(self):
        with self.lock:
            current_time = int(round(time.time() * 1000))
            for group in list(self.lock_dict.keys()):
                value = self.lock_dict[group]
                is_expired = timedelta(milliseconds=(current_time - value['time'])) > self.max_age
                if is_expired and not value['lock'].locked():
                    del self.lock_dict[group]
