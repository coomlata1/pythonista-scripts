# pythonista-scripts
Useful scripts to be run in Pythonista for iOS.  Kudos to @cclauss for line by line code cleanup and helpful comments on improving these scripts.

- **Search IMDB.py** - A script that I find useful to quickly look up info on a movie title or a TV series.  The results of the query are displayed on the console screen and a Markdown version is copied to the clipboard for pasting to a text editor, etc.

- **PhotosToDropbox.py** - A script that lets you select multiple photos from the iPhone camera roll, resize & geo-tag them, and upload them to Dropbox where they are renamed and organized based on the date and time they were taken.  The cool part is that the script will preserve the metadata of the original photo if desired, using the Pexif module to read the metadata from the original and write it back to the resized copy.  The Pexif module can be imported into Pythonista by simply copying pexif.py into the Pythonista script directory. The Pexif module can be found [here](https://github.com/bennoleslie/pexif).
