# coding: utf-8
# Name: PhotoToDropbox2.py
# Author: John Coomler
# v1.0: 01/28/2015-Created
# v1.1: 02/01/2015-Fixed bug in
# 'GetDimensions()' function for square
# photos.
'''
This Pythonista script will RESIZE,
RENAME, & UPLOAD all selected photos in
the iPhone camera roll to new folders
in your Dropbox account. The main folder
will be named after the year the photo was
taken in the format 'yyyy', & the
subfolders will be named for the date the
photo was taken in the format mm.dd.yyyy.
The photos themselves will have the exact
time the photo was taken amended to the
front of their names in the format
hh.mm.ss.XXXX.jpg, where XXXX is the
original name. All metadata in the
original photo will be copied to the
resized & renamed copy if desired. The
script allows you to select your desired
photo scaling options.

Script requires that the pexif module,
available at https://github.com
bennoleslie/pexif, be imported into
Pythonista. Just copy pexif.py into the
Pythonista script dir. Pexif allows for
both reading from and writing to the
metadata of image files. Many thanks to
Ben Leslie for maintaining the pexif
module at github.
'''
import photos
import time
import Image
import sys
import console
import PIL
import string
import re
import pexif
from DropboxLogin import get_client

# Global arrays for photos that will require manual processing
no_exif=[]
no_resize=[]

# Global processing flags
resizeOk=True

# Set this flag to false to resize photos without the metadata
keepMeta=True

def GetDateTimeInfo(meta):
	old_filename=str(meta.get('filename'))
	exif=meta.get('{Exif}')
	try:
		if not exif=='None':
			theDatetime=str(exif.get('DateTimeOriginal'))
			
			theDatetime=theDatetime.split(" ")
		
			theDate=theDatetime[0]
			theDate=theDate.split(':')
		
			theTime=theDatetime[1]
			theTime=theTime.replace(':','.')+'.'
			folder_name=theDate[0]+'/'+theDate[1]+'.'+theDate[2]+'.'+theDate[0]
			new_filename=theTime+old_filename
	except:
		new_filename=old_filename
		folder_name='NoDates'
		no_exif.append(old_filename)
	
	return old_filename,new_filename,folder_name

def GetDimensions(meta,resize,img_name,min):
	# Original size
	exif=meta.get('{Exif}')
	new_width=0
	new_height=0
	img_width=int(exif.get('PixelXDimension'))
	img_height=int(exif.get('PixelYDimension'))
	
	if min:
		min_width=1600
		min_height=1200
	else:
		min_width=0
		min_height=0
	
	if resize==1:
		# If scaled at 100%...no change
		new_width=img_width
		new_height=img_height
		no_resize.append(img_name)
		resizeOk=False
	# Don't resize a non-square photo smaller than the desired minumum size.
	elif img_width<>img_height and int(resize*(img_width))*int(resize*(img_height))<int(min_width*min_height):
		new_width=img_width
		new_height=img_height
		no_resize.append(img_name)
		resizeOk=False	
	# Square
	elif img_width==img_height:
		# Don't resize square photos with a height smaller than height of desired minumum size
		if img_width<min_height:
			new_width=img_width
			new_height=img_height
			no_resize.append(img_name)
			resizeOk=False
		else:
			new_width=int(resize*img_width)
			new_height=int(resize*img_height)
			resizeOk=True
	else:
		new_width=int(resize*img_width)
		new_height=int(resize*img_height)
		resizeOk=True
		
	# Return resize dimensions...new & old	
	return (new_width,new_height,img_width,img_height,resizeOk)

def CopyMeta(meta_src,meta_dst,x,y):
	'''
	Copy metadata from original photo to a
	resized photo that has no media
	metadata and write the results to a
	new photo that is resized with the
	media metadata.
	'''
	# Source photo
	img_src=pexif.JpegFile.fromFile(meta_src)
	# Destination photo
	img_dst=pexif.JpegFile.fromFile(meta_dst)
	img_dst.import_metadata(img_src)
		
	# Results photo
	'''
	After importing metadata from source
	we need to update the metadata to the
	new resize dimensions. Thanks to Ben
	Leslie for updating Pexif to
	accomodate this. 
	'''
	img_dst.exif.primary.ExtendedEXIF.PixelXDimension = [x]
	img_dst.exif.primary.ExtendedEXIF.PixelYDimension = [y]
		
	# Now write the updated metadata to the resized photo
	img_dst.writeFile('meta_resized.jpg')
		
	img_src=''
	img_dst=''

def main():
	console.clear()
	
	try:
		'''
		Here we are picking photos from the
		camera roll which, in Pythonista,
		allows us access to extra media data
		in photo's metafile. Because raw data
		is set to true, the image is a string
		representing the image object, not the
		object itself.
		'''
		choose=photos.pick_image(show_albums=True, multi=True,original=True,raw_data=True,include_metadata=True)
	except:
		print 'No photos choosen...exiting.'
		sys.exit()
	
	minumum_size=True
	resizePercent=0
	
	# Pick a scaling percent for selected photo(s)
	try:
		ans=console.alert('Reduce the selected photo(s) by what percent of their original size?','','50% with a 1600x1200 minumum','Custom without a minumum','None')
		
		if ans==1:
			resizePercent=float(50) /100
		elif ans==2:
			resizePercent=float(console.input_alert('Enter desired reduction percent for selected photo(s): ','Numbers only','35')) /100
			# No minumums here...reduce all photos no matter what their size.
			minumum_size=False
		elif ans==3:
			# Don't resize
			resizePercent=1
	except:
		print 'No valid entry...Process cancelled.'
		sys.exit()

	# Create an instance of Dropbox client
	drop_client=get_client()
	
	ans=''
	count=0
	dest_dir='/Photos'
	
	'''
	When metadata is returned with photo the
	photo is a tuple, with one the image,
	and the other the media metadata.
	'''
	
	for photo in choose:
		print ''
		print 'Processing photo...'
		# Raw data string
		img=photo[0]
		# Metadata
		meta=photo[1]
		#print meta
		#sys.exit()
		
		# Get date and time info of photo
		old_filename,new_filename,folder_name=GetDateTimeInfo(meta)
		
		# Use info to rename photo
		new_filename=dest_dir+'/'+folder_name+'/'+new_filename
		
		# Get dimensions for resize based on size of original photo
		new_width,new_height,old_width,old_height,resizeOk=GetDimensions(meta,resizePercent,old_filename,minumum_size)
		
		print ''
		print 'Original Name: '+old_filename
		print 'New Name: '+new_filename
		
		print ''
		print 'Original Size: '+str(old_width)+'x'+str(old_height)
		print 'New Size: '+str(new_width)+'x'+str(new_height)
		
		if keepMeta:
			addToMsg='with'
		else:
			addToMsg='without'
		
		if resizeOk:
			msg='Creating resized copy of original photo '+addToMsg+' the metadata from original.'
		else:
			msg='Creating copy of original photo '+addToMsg+' the metadata from original.'
				
		print ''
		print msg
		
		msg=''
		addToMsg=''
		
		# Write string image of original photo to Pythonista script dir
		with open('meta_with.jpg', 'wb') as out_file:
			out_file.write(img)
		
		# Open image, resize it, and write new image to scripts dir
		img=Image.open('meta_with.jpg')
		resized=img.resize((new_width,new_height),Image.ANTIALIAS)
		resized.save('meta_without.jpg')
		resized=''
		
		if keepMeta:
			'''
			Copy metadata from 'meta_with.jpg'
			to 'meta_without.jpg and call this
			reprocessed image file
			'meta_resized.jpg'. 
			'''
			CopyMeta('meta_with.jpg','meta_without.jpg',new_width,new_height)
		
			jpgFile='meta_resized.jpg'
		else:
			# Use resized photo that has not had metadata added back into it
			jpgFile='meta_without.jpg'
			
		print ''
		print 'Uploading photo to Dropbox...'
		
		'''
		Upload resized photo with or without
		original metadata to Dropbox...use
		with statement to open file so file
		closes automatically at end of with.
		'''
		
		with open(jpgFile,'r') as img:
			response=drop_client.put_file(new_filename,img)
		
		# Give Dropbox server time to process
		time.sleep(5)
		response=''
		jpgFile=''
		
		print ''
		print 'Upload successful.'
		count=count+1
		
	print ''
	print str(count) + ' photos processed.'

	if len(no_exif)>0:
		print ''
		print 'Photos with no DateTimeOriginal tag in their metadata and will need categorizing manually:'
		print '\n'.join(no_exif)
	
	if len(no_resize)>0:
		print ''
		print 'Photos that did not get resized because either you chose not to resize, or they were smaller than the minumum size of 1600x1200:'
		print '\n'.join(no_resize)

	sys.exit()
if __name__ == '__main__':
			main()
