import os
import sys
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from logging.handlers import TimedRotatingFileHandler

"""
To run this script
python watch_for_changes.py ../brands

You can check logs in watchdog/logs
"""

home = "/Users/PoojaNihalani"
#home = "/home/ec2-user"

SCRIPTS_DIR_NAME = "%s/watchdog/scripts" % home
FOLDER_TO_SCRIPT_MAP = {
  "kirklands" : "kirkland_format_file.py"
}


LOG_FILENAME = "%s/watchdog/logs/watchdog.log" % home
logger = logging.getLogger("watchdog log")

handler = TimedRotatingFileHandler(LOG_FILENAME,
                                       when="w0",
                                       interval=1,
                                       backupCount=7)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.xml", "*.lxml", "*.csv", "*.txt"]
    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        #print event.src_path, event.event_type
        #logger.info("%s,%s" % (event.src_path, event.event_type))  # print now only for debug
        try:
            #get brand name from folder
            brand_folder = ''
            folder_path, file_name = os.path.split(event.src_path)
            logger.info("Folder Path: %s" % folder_path)

            if folder_path:
                parts = os.path.split(folder_path)
                brand_folder = parts[1]

            logger.info("Brand folder name: %s" % brand_folder)
            if brand_folder and brand_folder != "processed":
                logger.info("%s,%s" % (event.src_path, event.event_type))  # print now only for debug
                if brand_folder in FOLDER_TO_SCRIPT_MAP.keys():
                    script_name = FOLDER_TO_SCRIPT_MAP[brand_folder]
                    script = "%s/%s" % (SCRIPTS_DIR_NAME, script_name)
                    output_filename = folder_path+'/processed/'+file_name+'.csv'
                    input_filename = event.src_path
                    if not os.path.exists(os.path.dirname(output_filename)):
                        logger.info("Making directories required to create %s" % output_filename)
                        os.makedirs(os.path.dirname(output_filename))
                    logger.info("Converting %s to %s" % (input_filename, output_filename))
                    subprocess.Popen(" %s %s %s %s %s %s" % ('python',
                      script, '-i', input_filename, '-o', output_filename), shell=True)
        except Exception as e:
            logger.exception("Exception occured %s" % e)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)



if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(MyHandler(), path=args[0] if args else '.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()