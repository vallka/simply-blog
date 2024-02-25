import sys
import os
from icecream import ic
import pyexiv2




def process_file(file_path):
    basename = os.path.basename(file_path)
    dir = os.path.dirname(file_path)
    if '.jpg' in basename and 'JPEG-2048' in dir:
        ic(file_path)
        exif = pyexiv2.Image(file_path)
        ic(exif.read_exif())
        ic(exif.read_iptc())
        ic(exif.read_xmp())

        exif.close()

def walk_directory(directory_path, process_function):
    # Ensure the directory path is valid
    if not os.path.isdir(directory_path):
        raise ValueError("Invalid directory path")

    # Get a list of all entries in the directory (files and subdirectories)
    entries = os.listdir(directory_path)

    # Sort entries alphabetically
    entries.sort()

    for entry in entries:
        entry_path = os.path.join(directory_path, entry)
        if os.path.isfile(entry_path):
            process_function(entry_path)
        elif os.path.isdir(entry_path):
            walk_directory(entry_path, process_function)


def run(dir):
        ic (dir)

        #directory_path = p_dir + root_dir + start_dir
        walk_directory(dir, process_file)

        print ("DONE!")

run(sys.argv[1])
