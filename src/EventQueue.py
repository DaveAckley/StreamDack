import asyncio
import time
from abc import ABC, abstractmethod
import threading

import Event

class EventQueue:
    def __init__(self, sda, name):
        self.sda = sda
        self.name = name
        self.pq = asyncio.PriorityQueue()
        self.updateLock = threading.RLock()
        self.conditionObject = threading.Condition(self.updateLock)

    def __str__(self):
        return "EQ:"+self.name

    def __repr__(self):
        return "EQ:"+self.name+"DONG"

    def __enter__(self):
        self.updateLock.acquire()

    def __exit__(self, type, value, traceback):
        self.updateLock.release()

    def wake(self):
        self.conditionObject.notify()

    def sleep(self,timeout):
        with self:
            self.conditionObject.wait(timeout)

    def now(self):
        return time.time()

    def runIn(self, time, func):
        later = self.now()+time
        #print("runin {} {}".format(time,func))
        with self:
            self.pq.put_nowait((later,func))
            self.wake()

    def runAt(self, time, func):
        now = self.now()
        if time <= now:
            time = now
        with self:
            self.pq.put_nowait((time,func))
            self.wake()

    def mainLoop(self):
        #clock = Event.ClockEvent(self.sda,"DemoClock");
        #self.runIn(1,clock)
        #sleepy = Event.SleepEvent("DemoThread");
        #self.runIn(3,sleepy)
        #shelly = Event.ShellEvent("DemoShell","ls","-a", "-l");
        #self.runIn(4,shelly)
        while (True):
            if self.pq.empty():
                self.sleep(1)
            else:
                (when,event) = self.pq.get_nowait()
                t = self.now()
                if when > t:
                    delta = when - t
                    self.pq.put_nowait((when,event))
                    self.sleep(delta)   # can be interrupted via self.wake()
                elif event:
                    event.run(self,t,when)
                else:
                    print("NO EVENT?",when,event)
                    
        
    async def execute(self,item):
        print(f'{item} executed')

    # def clock(self,now,dead):
    #     delta = now - dead
    #     print(f'{dead} executed at {now} delay {delta}')
    #     then = int(now/10)*10+10
    #     print(then)
    #     self.runAt(then,self.clock)

