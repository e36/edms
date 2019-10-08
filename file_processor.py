import uuid
import os
import shutil
import logging
import config
import psycopg2
import sys
from wand.image import Image
from datetime import datetime


class FileProcessor:

    def __init__(self):

        # TODO create error file for dump folder errors

        self.version = 1.2

        # logger
        # logging = logging.getLogger(__name__)
        # self.l_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # self.l_handler = logging.FileHandler(config.processor_log_file)
        # self.l_handler.setLevel(logging.INFO)
        # self.l_handler.setFormatter(self.l_format)
        # logging.addHandler(self.l_handler)
        logging.basicConfig(filename=config.processor_log_file,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)

        logging.info("Starting file processor version " + str(self.version))

        # the directory where new files will be dropped for processing
        self.consumedir = config.drop_directory

        # the directory where processed files will be stored
        self.storagedir = config.document_directory

        # the directory where thumbnail images will be stored
        self.thumbdir = config.thumbnail_directory

        # temp directory
        self.tempdir = config.temp_directory

        # the list of files that are found in the consumedir
        self.consumefiles = []

        # the number of files found
        self.number_of_files = 0

        # the database connection.  Will need to create a cursor every time it's used
        try:
            self.dbconn = psycopg2.connect(
                dbname=config.database['database'],
                user=config.database['user'],
                password=config.database['password'],
                host=config.database['hostname']
            )
        except psycopg2.DatabaseError:
            logging.error('Cannot connect to database ' + config.database['database'])

        # check and see if the directories exist
        self.validate_directories()

    def validate_directories(self):
        """
        Validates that the necessary directories exist.
        :return: nothing
        """

        logging.info("Validating directories.")

        if os.path.exists(self.storagedir):
            logging.info("Storage directory at " + self.storagedir + " is found.")
        else:
            logging.error("Storage directory at " + self.storagedir + " cannot be found.")
            sys.exit()

        if os.path.exists(self.consumedir):
            logging.info("Drop directory at " + self.consumedir + " is found.")
        else:
            logging.error("Drop directory at " + self.consumedir + " cannot be found.")
            sys.exit()

        if os.path.exists(self.thumbdir):
            logging.info("Thumbnail directory at " + self.thumbdir + " is found.")
        else:
            logging.error("Thumbnail directory at " + self.thumbdir + " cannot be found.")
            sys.exit()

        if os.path.exists(self.tempdir):
            logging.info("Temp directory at " + self.tempdir + " is found.")
        else:
            logging.error("Temp directory at " + self.tempdir + " cannot be found.")
            sys.exit()

    def scan_consume_dir(self):
        """
        Scans the consume directory and populates self.consumefiles with the list
        :return: nothing
        """

        logging.info('Beginning scan of ' + self.consumedir)
        logging.info('Destination directory: ' + self.storagedir)

        try:
            # scan through and only add files to self.consumefiles
            dir_contents = os.scandir(self.consumedir)

            for item in dir_contents:
                if not item.name.startswith('.') and item.is_file():
                    self.consumefiles.append(item.name)
        except Exception as e:
            logging.error(f'Scan error: {str(e)}')
            sys.exit()

        # capture the number of files
        self.number_of_files = len(self.consumefiles)
        logging.info(f"{self.number_of_files} files found.")

    def process_file(self):
        """
        For each file in self.consumefiles:
        1. generate a new filename for the file
        2. copy the file to the storage location, and rename it
        3. add a database entry for the new file, and status = NEW
        :return:
        """

        for file in self.consumefiles:

            logging.info("Processing " + file)

            # split the file so we can get just the extension
            file_extension = file.split('.')[-1]

            # generate a uuid that will be used for the new filename
            fuuid = uuid.uuid4().hex

            # create the new file name with extension
            new_filename = fuuid + '.' + file_extension

            # create file paths
            full_src_path = self.consumedir + file
            full_dst_path = self.storagedir + new_filename

            thumbnail_filename = ''

            try:
                # copy the original document to the storage location, with the new filename
                logging.info('Copying ' + file + ' --> ' + new_filename)

                shutil.copy2(full_src_path, full_dst_path)

            except FileNotFoundError:
                logging.error('Cannot copy ' + file + ' --> ' + new_filename + '. Check that the destination directory exists and is writable.')

            # TODO wrap this in some kind of exception
            if file_extension.lower() == 'pdf':
                # if the file is a PDF, then send it through make_pdf_thumbnail
                # it will return the new thumbnail filename, we'll insert that into the database
                thumbnail_filename = self.make_pdf_thumbnail(file, fuuid)
            elif file_extension.lower() in config.supported_file_types:
                # if the file is an image then send it here
                thumbnail_filename = self.make_image_thumbnail(file, fuuid)

            try:
                data = ('New Title', 'New Description', new_filename, thumbnail_filename, file, 'NEW', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fuuid, file_extension.lower())
                print("inserting " + str(data))
                c = self.dbconn.cursor()
                c.execute("INSERT INTO document (title, description, document_filename, thumbnail_filename, original_filename, status, created, document_id ,file_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);", data)
                self.dbconn.commit()
            except psycopg2.OperationalError as err:
                logging.error('Cannot insert ' + new_filename + ' into the documents table. ' + str(err))

            try:
                os.remove(full_src_path)
            except:
                logging.error('Cannot delete ' + full_src_path)

    def make_pdf_thumbnail(self, filename, uuid):
        """
        Creates a thumbnail of the first page of a PDF file, and saves it to the thumb directory with the same uuid
        filename as the original document.
        :param filename: the filename of the original document
        :param uuid: the uuid of the new file name
        :return: the filename of the thumbnail
        """

        # this is the factor by which the height and width will be multipled to get to the desired thumbnail target
        factor = 1

        # create full filepath
        full_filepath = self.consumedir + filename

        # create thumbnail filename
        thumbfilename = uuid + '_thumbnail.png'
        thumbfilepath = self.thumbdir + thumbfilename

        # create temp file name
        temp_name = self.tempdir + thumbfilename

        # open the file
        pdf_file = Image(filename=full_filepath + "[0]")

        # get the first page
        # page_one = pdf_file.sequence[0]

        # save to temp directory
        pdf_file.save(filename=temp_name)

        img = Image(filename=temp_name)

        # figure out the height and width, and resize it down to around width 160, height 160
        width = img.width
        height = img.height

        if width >= height:
            factor = config.thumbnail_width_target / width
        else:
            factor = config.thumbnail_height_target / height

        img.resize(int(img.width * factor), int(img.height * factor))
        img.save(filename=thumbfilepath)

        os.remove(temp_name)

        return thumbfilename

    def make_image_thumbnail(self, filename, uuid):
        """
        Creates a thumbnail of the first page of an image file, and saves it to the thumb directory with the same uuid
        filename as the original document.
        :param filename: the filename of the original document
        :param uuid: the uuid of the new file name
        :return: the filename of the thumbnail
        """

        # create thumbnail filename
        thumbfilename = uuid + '_thumbnail.png'
        thumbfilepath = self.thumbdir + thumbfilename

        # this is the factor by which the height and width will be multipled to get to the desired thumbnail target
        factor = 1

        # create full filepath
        full_filepath = self.consumedir + filename

        # open the file
        image = Image(filename=full_filepath)

        # figure out the height and width, and resize it down to around width 160, height 160
        width = image.width
        height = image.height

        if width >= height:
            factor = config.thumbnail_width_target / width
        else:
            factor = config.thumbnail_height_target / height

        image.resize(int(image.width * factor), int(image.height * factor))
        image.save(filename=thumbfilepath)

        return thumbfilename


if __name__ == '__main__':

    print(config.processor_log_file)

    fp = FileProcessor()

    fp.scan_consume_dir()
    fp.process_file()
