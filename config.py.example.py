# set up the database engine information here
database = {
    'engine':'postgresql',
    'hostname':'localhost',
    'port':'5432',
    'database':'test',
    'user':'testuser',
    'password':'password'
}

# the drop directory, where files will be picked up by the file processor job
drop_directory='~/Projects/edms/drop/'

# the storage directory, where the documents will be saved to once they've been processed
document_directory='~/Projects/edms/documents/'

# thumbnail directory, where the document thumbnails will be saved
thumnail_directory='~/Projects/edms/thumbnails/'

# file processor logging file
processor_log_file='~/Projects/edms/processorlog.log'