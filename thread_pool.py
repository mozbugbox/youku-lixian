#!/usr/bin/python
# vim:fileencoding=utf-8:sw=4:et

from __future__ import print_function, unicode_literals, absolute_import
import sys
import os
import logging as log
import threading
import time

class ThreadPool:
    """Fake thread pool. Start new thread for each job"""
    def __init__(self, job_list, workers=5, timeout=1.0, daemon=True):
        """
        Construct a pool of thread with max `worker` threads.
        @job_list: a list of tuple looks like [(func, args, kwargs), ...]
        @timeout: sleep b/w checking new job once job list was empty
        """
        self.workers = workers
        self.timeout = timeout
        self.daemon = daemon
        self._job_list = job_list
        self._thread_list = set()
        self.job_list_lock = threading.Lock()

    def add_job(self, target, args=(), kwargs={}):
        """1st in last out?"""
        self.job_list_lock.acquire()
        self._job_list.append((target, args, kwargs))
        self.job_list_lock.release()

    def is_alive(self):
        """Check if there are jobs running or are waiting."""
        self.job_list_lock.acquire()
        ret = len(self._thread_list) > 0 and len(self._job_list) > 0
        self.job_list_lock.release()
        return ret

    def start(self):
        thread_list = self._thread_list
        job_list = self._job_list

        while len(thread_list) > 0 or len(job_list) > 0:
            # start some threads
            while len(thread_list) < self.workers and len(job_list) > 0:
                self.job_list_lock.acquire()
                job = job_list.pop()
                target = job[0]
                args = job[1] if len(job) > 1 else ()
                kwargs = job[2] if len(job) > 2 else {}

                t = threading.Thread(target=target, args=args, kwargs=kwargs)
                t.daemon = self.daemon
                thread_list.add(t)
                self.job_list_lock.release()

                t.start()

            # remove finished threads
            t_done = []
            for t1 in thread_list:
                t1.join(.1)
                if not t1.is_alive():
                    t_done.append(t1)
            for t1 in t_done:
                thread_list.remove(t1)

def main():
    log_level = log.INFO
    log.basicConfig(format="%(levelname)s>> %(message)s", level=log_level)

if __name__ == '__main__':
    main()

