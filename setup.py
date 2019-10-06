"""
Setup script for EDMS.
"""

import config
import os

# DIRECTORIES
# test that the directories exist, create them if not

if not os.path.isdir(config.drop_directory):
    os.mkdir(config.drop_directory)

if not os.path.isdir(config.document_directory):
    os.mkdir(config.document_directory)

if not os.path.isdir(config.thumbnail_directory):
    os.mkdir(config.thumbnail_directory)

if not os.path.isdir(config.temp_directory):
    os.mkdir(config.temp_directory)


# VIRTUAL ENVIRONMENT
