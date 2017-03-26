import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Monitor:
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self.stopped = False

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watch_dir, recursive=True)
        self.observer.start()
        try:
            while True:
                if self.stopped:
                    return
                time.sleep(5)
        except:
            self.observer.stop()
            print("[INFO] file monitor stopped...")

        self.observer.join()

    def stop(self):
        self.stopped = True


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # new file has been created, take action here
            print("Received create event")

        elif event.event_type == 'modified':
            # a file has changed, take action here
            print("Received modify event")
