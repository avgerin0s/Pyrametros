from shutil import copy
import os

def static_path(filename):
    """Get a full path to the filename in ./static/"""
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./static/")
    return os.path.join(dir, filename)

def backup(filename):
    """Backup file that can be found in static/"""
    filename = static_path(filename)
    copy(filename, filename + ".backup")

def restore(filename):
    """Restor backed up file in static/. Use original filename"""
    filename = static_path(filename)
    copy(filename + ".backup", filename)
