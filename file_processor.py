import uuid
import os
import shutil
from utils import get_now_utc_epoch
import logging

# CREATE TABLE "documents" (
# 	`filename`	TEXT UNIQUE,
# 	`status`	TEXT,
# 	`created_utc`	INTEGER,
# 	`originalfilename`	TEXT,
#   `title` TEXT
# )


class FileProcessor:

    def __init__(self, dbconn):

        # the directory where new files will be dropped for processing
        self.consumedir = ''

        # the directory where processed files will be stored
        self.storatedir = ''

        # the list of files that are found in the consumedir
        self.consumefiles = []

        # the database connection.  Will need to create a cursor every time it's used
        self.dbconn = dbconn

        # optional logger
        self.logger = None

    def scan_consume_dir(self):
        """
        Scans the consume directory and populates self.consumefiles with the list
        :return: nothing
        """

        self.log('Beginning scan of ' + self.consumedir, 'info')
        self.log('Destination directory: ' + self.storatedir, 'info')

        try:
            # scan through and only add files to self.consumefiles
            dir_contents = os.scandir(self.consumedir)

            for item in dir_contents:
                if item.is_file():
                    self.consumefiles.append(item.name)
        except:
            self.log('Scan error', 'error')

    def process_file(self):
        """
        For each file in self.consumefiles:
        1. generate a new filename for the file
        2. copy the file to the storage location, and rename it
        3. add a database entry for the new file, and status = NEW
        :return:
        """

        for file in self.consumefiles:

            file_extension = file.split('.')[-1]

            new_filename = uuid.uuid4().hex + '.' + file_extension

            full_src_path = self.consumedir + file
            full_dst_path = self.storatedir + new_filename

            try:
                self.log('Copying ' + file + ' --> ' + new_filename, 'info')

                shutil.copy2(full_src_path, full_dst_path)

            except FileNotFoundError:
                self.log('Cannot copy ' + file + ' --> ' + new_filename + '. Check that the destination directory exists and is writable.', 'error')

            try:
                data = (new_filename, 'NEW', get_now_utc_epoch(), file)
                c = self.dbconn.cursor()
                c.execute('INSERT INTO documents VALUES(?,?,?,?)', data)
                self.dbconn.commit()
            except sqlite3.Error as err:
                self.log('Cannot insert ' + new_filename + ' into the documents table.' + err, 'error')

            try:
                os.remove(full_src_path)
            except:
                self.log('Cannot delete ' + full_src_path, 'error')

    def log(self, text, level='error'):
        """
        Either prints or logs a bit of text.
        :param text: the text message to be logged
        :param level: info, warn, error
        :return: nothing
        """

        if not self.logger:
            print(level + ': ' + text)
        elif level == 'info':
            self.logger.info(text)
        elif level == 'warn':
            self.logger.warn(text)
        elif level == 'error':
            self.logger.error(text)
        elif level == 'critical':
            self.logger.critical(text)


if __name__ == '__main__':
    import sqlite3
    dbc = sqlite3.connect('C:\\Users\\azl6rw0\\Documents\\Personal\\docs\\docsdb.db')

    logr = logging.getLogger(__name__)
    l_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    l_handler = logging.FileHandler('log.log')
    l_handler.setLevel(logging.INFO)
    l_handler.setFormatter(l_format)
    logr.addHandler(l_handler)

    fp = FileProcessor(dbc)

    # fp.logger = logr

    fp.consumedir = "C:\\Users\\azl6rw0\\Documents\\Personal\\docs\\consumption\\"
    fp.storatedir = "C:\\Users\\azl6rw0\\Documents\\Personal\\docs\\storage\\"
    fp.scan_consume_dir()
    fp.process_file()
