import sys
import os
import zipfile
from mutagen.easyid3 import EasyID3
import re
from icecream import ic

def sanitize_file_name(name):
    # Remove invalid characters and replace with underscore
    sanitized_name = re.sub(r'[<>:"/\|?*]', '_', name)
    return sanitized_name

def rename_directory(dest_dir):
    # Get a list of all files in the directory
    files = os.listdir(dest_dir)
    
    # Initialize variables for track number and track name
    track_number = None
    track_name = None
    
    # Iterate over the mp3 files to find common track number and track name
    for file in files:
        if file.endswith('.mp3'):
            # Get the full path of the mp3 file
            mp3_file = os.path.join(dest_dir, file)
            # Read the tags from the mp3 file
            audio = EasyID3(mp3_file)

            ic(audio.keys)
            
            # Get the track number from the tags
            current_track_number = audio.get('tracknumber', [''])[0].split('/')[0].zfill(2)
            # Get the track name from the tags
            current_track_name = audio.get('title', [''])[0]
            
            # Update track number and track name if they are empty or contradicting
            if track_number is None or track_number != current_track_number:
                track_number = ''
            if track_name is None or track_name != current_track_name:
                track_name = ''
    
    # Create the new directory name using heuristics
    new_dir_name = ''
    if track_number != '':
        new_dir_name += track_number
    if track_name != '':
        if new_dir_name != '':
            new_dir_name += '.'
        new_dir_name += sanitize_file_name(track_name)
    
    # Rename the directory
    if new_dir_name != '':
        new_dir_path = os.path.join(os.path.dirname(dest_dir), new_dir_name)
        os.rename(dest_dir, new_dir_path)

def unzip_and_rename_mp3(zip_file):
    ic(zip_file)
    # Extract the zip file
    with zipfile.ZipFile(zip_file, 'r') as z:
        # Create a directory with the same name as the zip file
        dest_dir = os.path.splitext(zip_file)[0]
        os.makedirs(dest_dir, exist_ok=True)
        z.extractall(dest_dir)
    
    # Get a list of all files in the extracted directory
    files = os.listdir(dest_dir)

    year = None 
    album = None
    artist = None
    albumartist = None
    
    for file in files:
        ic(file)
        # Check if the file is an mp3
        if file.endswith('.mp3'):
            # Get the full path of the mp3 file
            mp3_file = os.path.join(dest_dir, file)
            # Read the tags from the mp3 file
            audio = EasyID3(mp3_file)
            ic(audio.keys)
            
            # Get the track number from the tags
            track_number = audio.get('tracknumber', [''])[0].split('/')[0].zfill(2)
            # Get the track name from the tags
            track_name = audio.get('title', [''])[0]
            if not album: album = audio.get('album', [''])[0] 
            if not year: year = audio.get('date', [''])[0] 
            if not albumartist: albumartist = audio.get('albumartist', [''])[0] 
            if not artist: artist = audio.get('artist', [''])[0] 
            
            # Sanitize the track name
            sanitized_track_name = sanitize_file_name(track_name)
            
            # Create the new file name in the format "01. Track Name"
            new_file_name = f"{track_number}. {sanitized_track_name}.mp3"
            ic(new_file_name)
            
            # Rename the mp3 file
            os.rename(mp3_file, os.path.join(dest_dir, new_file_name))
            
        else:
            # Delete all non-mp3 files
            os.remove(os.path.join(dest_dir, file))

    ic(year)
    ic(album)
    ic(artist)
    ic(albumartist)

    if not albumartist:     
        albumartist = artist.split('&')[0].strip()

    ic(albumartist)

    new_dir_name = ''
    if albumartist:
        new_dir_name = f'{albumartist}. '
    if year:
        new_dir_name += f'{year}. '
    if album:
        new_dir_name += album

    new_dir_name = sanitize_file_name(new_dir_name)
    ic(new_dir_name)

    # Rename the directory
    if new_dir_name != '':
        new_dir_path = os.path.join(os.path.dirname(dest_dir), new_dir_name)
        os.rename(dest_dir, new_dir_path)

zip_files = sys.argv[1:]

for zip_file in zip_files:
    if zip_file.endswith('.zip'):
        ic(zip_file)
        unzip_and_rename_mp3(zip_file)

