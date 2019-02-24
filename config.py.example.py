# APP CONFIG
SECRET_KEY = "type a long random string"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# set up the database engine information here
database = {
    'engine': 'postgresql',
    'hostname': 'localhost',
    'port': '5432',
    'database': 'test',
    'user': 'testuser',
    'password': 'password'
}

# postgresql://scott:tiger@localhost/mydatabase
SQLALCHEMY_DATABASE_URI = database['engine'] + "://" + database['user'] + ":" + database['password'] + "@" + database['hostname'] + "/" + database['database']

# the drop directory, where files will be picked up by the file processor job
drop_directory = 'drop/'

# the storage directory, where the documents will be saved to once they've been processed
document_directory = 'static/documents/'

# thumbnail directory, where the document thumbnails will be saved
thumbnail_directory = 'static/thumbnails/'

# file processor logging file
processor_log_file = 'processorlog.log'

# temp folder
temp_directory = 'temp/'

# thumbnail height and width targets.  The processor will attempt to get as close to this as possible
thumbnail_height_target = 160
thumbnail_width_target = 160
