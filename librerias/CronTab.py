from datetime import datetime, timedelta
import time


class CronTab(object):
    def __init__(self, *events):
        self.events = events

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])
        while 1:
            for e in self.events:
                e.check(t)

            t += timedelta(minutes=1)
            while datetime.now() < t:
                time.sleep((t - datetime.now()).seconds)
