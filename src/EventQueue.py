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
        self.dimmer = None

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

    def runIn(self, time, evt):
        later = self.now()+time
        evt.sched = later
        #print("runin {} {}".format(time,evt))
        with self:
            self.pq.put_nowait((later,evt))
            self.wake()

    def runAt(self, time, evt):
        now = self.now()
        if time <= now:
            time = now
        with self:
            evt.sched = time
            self.pq.put_nowait((time,evt))
            self.wake()

    def mainLoop(self):
        self.dimmer = Event.DimScreenEvent(self.sda,"ScreenDimmer");
        self.dimmer.reschedule()
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
                if event.sched == when:
                    t = self.now()
                    if when > t:
                        delta = when - t
                        self.pq.put_nowait((when,event))
                        self.sleep(delta)   # can be interrupted via self.wake()
                    else:
                        event.run(self,t,when)
                elif not isinstance(event,Event.DimScreenEvent):
                    print(f"DROPPING {event}")

    async def execute(self,item):
        print(f'{item} executed')

    # def clock(self,now,dead):
    #     delta = now - dead
    #     print(f'{dead} executed at {now} delay {delta}')
    #     then = int(now/10)*10+10
    #     print(then)
    #     self.runAt(then,self.clock)

