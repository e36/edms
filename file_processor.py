import uuid
import os
import shutil
import logging
import config
import psycopg2
from wand.image import Image
from datetime import datetime


class FileProcessor:

    def __init__(self):

        #TODO add checks for the folders and permissions.  Add defs for this in utils.py?
        #TODO create error file for dump folder errors

        # logger
        self.log = logging.getLogger(__name__)
        self.l_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.l_handler = logging.FileHandler(config.processor_log_file)
        self.l_handler.setLevel(logging.INFO)
        self.l_handler.setFormatter(self.l_format)
        self.log.addHandler(self.l_handler)

        # the directory where new files will be dropped for processing
        self.consumedir = config.drop_directory

        # the directory where processed files will be stored
        self.storagedir = config.document_directory

        # the directory where thumbnail images will be stored
        self.thumbdir = config.thumnail_directory

        # temp directory
        self.tempdir = config.temp_directory

        # the list of files that are found in the consumedir
        self.consumefiles = []

        # the database connection.  Will need to create a cursor every time it's used
        try:
            self.dbconn = psycopg2.connect(
                dbname=config.database['database'],
                user=config.database['user'],
                password=config.database['password'],
                host=config.database['hostname']
            )
        except psycopg2.DatabaseError:
            self.log.error('Cannot connect to database ' + config.database['database'])

    def scan_consume_dir(self):
        """
        Scans the consume directory and populates self.consumefiles with the list
        :return: nothing
        """

        self.log.info('Beginning scan of ' + self.consumedir)
        self.log.info('Destination directory: ' + self.storagedir)

        try:
            # scan through and only add files to self.consumefiles
            dir_contents = os.scandir(self.consumedir)

            for item in dir_contents:
                if item.is_file():
                    self.consumefiles.append(item.name)
        except:
            self.log.error('Scan error')

    def process_file(self):
        """
        For each file in self.consumefiles:
        1. generate a new filename for the file
        2. copy the file to the storage location, and rename it
        3. add a database entry for the new file, and status = NEW
        :return:
        """

        for file in self.consumefiles:

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
                self.log.info('Copying ' + file + ' --> ' + new_filename)

                shutil.copy2(full_src_path, full_dst_path)

            except FileNotFoundError:
                self.log.error('Cannot copy ' + file + ' --> ' + new_filename + '. Check that the destination directory exists and is writable.')


            # TODO wrap this in some kind of exception
            if file_extension.lower() == 'pdf':
                # if the file is a PDF, then send it through make_pdf_thumbnail
                # it will return the new thumbnail filename, we'll insert that into the database
                thumbnail_filename = self.make_pdf_thumbnail(file, fuuid)
            elif file_extension.lower() in ['jpg', 'jpeg', 'gif', 'png', 'tif', 'tiff']:
                # if the file is an image then send it here
                thumbnail_filename = self.make_image_thumbnail(file, fuuid)

            try:
                print('fake db insert')
                # data = ('', '', new_filename, thumbnail_filename, file, 'NEW', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # c = self.dbconn.cursor()
                # c.execute('INSERT INTO documents VALUES(?,?,?,?,?,?,?)', data)
                # self.dbconn.commit()
            except:
                self.log.error('Cannot insert ' + new_filename + ' into the documents table.')

            try:
                os.remove(full_src_path)
            except:
                self.log.error('Cannot delete ' + full_src_path)

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

        # create thumbnail filename
        thumbfilename = uuid + '_thumbnail.png'
        thumbfilepath = self.thumbdir + thumbfilename

        # create temp file name
        temp_name = self.tempdir + thumbfilename

        # open the file
        pdf_file = Image(filename=filename + "[0]")

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

        # open the file
        image = Image(filename=filename)

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
