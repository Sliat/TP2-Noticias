from datetime import datetime, timedelta
import threading
import time


class CronTab(object):

    def __init__(self, interval, eventos = []):
        self.events = eventos
        self.interval = interval
        print(self.interval)
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def add_event(self, event):
        self.events.append(event)


    def run(self):
        while True:
            # Do something
            for e in self.events:
                e.iniciar()
            time.sleep(self.interval)
