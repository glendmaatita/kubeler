import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WatchHandler(FileSystemEventHandler):
    def __init__(self, handler):
        self.handler = handler

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            commands = self.handler.load_file(event.src_path)
            self.handler.execute(commands)

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")

def watch_directory(handler, path="."):
    event_handler = WatchHandler(handler)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
