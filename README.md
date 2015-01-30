# pythonista-scripts
Useful scripts to be run in Pythonista for iOS

- **Search IMDB.py** - A script that I find useful to quickly look up info on a movie title or a TV series.  The results of the query are displayed on the console screen and a Markdown version is copied to the clipboard for pasting to a text editor, etc.

- **PhotosToDropbox.py** - A script that takes photos from the iPhone camera roll, resizes them, renames and organizes them based on the date and time the photo was taken, and then uploads them to Dropbox.  The cool part is that the script will preserve the metadata of the original photo if desired using the Pexif module to read the metadata from the original and write it back to the resized copy.  The Pexif module can be imported into Pythonista by simply copying pexif.py into the Pythonista script directory. The Pexif module can be found here: https://github.com/bennoleslie/pexif
