# coding: utf-8
# Name: Search IMDB.py
# Author: John Coomler
# Creation Date: 11/18/2014
# Version: v1.0

'''
This Pythonista script uses the api
available at www.omdbapi.com to search
for your desired movie or TV series
title. The query will first return the
most popular result for what matches
that title. The script will display most
of the pertinent info on the console
screen about that movie/TV series
including release date, imdb rating, box
office returns, writers, director,
actors and plot. That may not be the
results you are looking for. You can
then refine your search and the query
will return a list of titles and their
release year that match or are close to
matching the desired title. When you
select a title from the list you will
get the same results as listed above.
You can keep refining your search until
you get the results you are looking for.
The info is displayed on the console
screen and formatted for Markdown and
copied to the clipboard so it can be
posted to your text editor or journal of
choice.
'''

import sys
import urllib2
import re
import json
import console
import string
import clipboard
import editor

# Initialize global variable
d='';
# Routine to capitialize first letter of each word
def titleCase(s):
	newText = re.sub(r"[A-Za-z]+('[A-Za-z]+)?",lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),s)
	return newText 
	
# Routine to query IMDB database
def queryData(s):
	request=urllib2.Request(s)
	response=json.load(urllib2.urlopen(request))
	console.clear()
	d=json.dumps(response,indent=-10)
	
	# Reformat data, stripping out extra spaces, quotation marks, commas, etc as necessary
	
	d=d.replace('"',' ');
	d=d.replace('{',' ');
	d=d.replace('}',' ');
	d=d.replace(' : ',':');
	d=d.replace(' ,',' ');
	d=d.replace('\u2013','-');
	d=d.replace('[',' ');
	d=d.replace(']',' ');
	d=d.replace('\\ ','');
	d=d.replace('&','and');
	d=d.replace('\u00','');
	
	# Uncomment for debugging
	#print d
	#sys.exit()
	
	# Trap errors in user input, if any
	error=re.search("(Error: .*)",d);
	if error:
		error=error.group(1)
		print error
		sys.exit()
	
	return d

# Function to return a Markdown list of actor(s) listed in d
def actorsMD(d):
	b=''
	a=re.findall(r"(Actors: .*)",d);
	a[0]=a[0].replace('Actors: ','').strip()
	theActors= a[0].split(',');
	
	# Loop through list of actors appending markdown syntax to each one
	for index, item in enumerate(theActors):
		theActors[index]=theActors[index].strip()
		theActors[index]='['+theActors[index]+'](http://www.imdb.com/find?ref_=nv_sr_fn&q='+theActors[index]+ '), '
		# If first actor in list...
		if index==0:
			# Append back the header
			theActors[index]='Actors: '+theActors[index]
		# Consecrate each markdown actor into a return variable
		b=b+theActors[index]
	#print b
	#sys.exit()
	return b

# Routine to mine data for desired strings
def mineData(d):
	#john=re.findall(r"(.*: .*)",d);
	
	# Create a list object of headers to search for in d
	headers=["(Title: .*)","(Type: .*)","(Released: .*)","(Year: .*)","(Genre: .*)","(imdbRating: .*)","(Rated: .*)","(Runtime: .*)","(imdbID: .*)","(Language: .*)","(Country: .*)","(Awards: .*)","(BoxOffice: .*)","(Production: .*)","(Director: .*)","(Writer: .*)","(Actors: .*)","(Plot: .*)","(tomatoÇonsensus: .*)","(Poster: .*)"]
	
	poster=''
	new_data=''
	
	print 'Results of your IMDB Search:\n'
	
	# Loop through list of headers
	for index, item in enumerate(headers):
		# Search for header string
		found=re.search(headers[index],d);
		if found:
			# Grab whole group and strip out blanks
			found=found.group(1).strip()
			# Look for any 'N/A's'
			na=re.search("(N/A)",found);
			if not na:
				if headers[index]=='(Title: .*)':
					title=found
				if headers[index]=='(imdbRating: .*)':
					found=found+'/10'
				if headers[index]=='(imdbID: .*)':
					imdb_ID=found
				print found + "\n"
				if headers[index]=='(Type: .*)':
					# Add hashtag and make type string proper case
					found=re.sub('Type: ','Type: #',found)
					found=titleCase(found)
				if headers[index]=='(Actors: .*)':
					# Return a Markdown list of actors
					found=actorsMD(d)
				# If this is poster info then add Markdown syntax
				if headers[index]=='(Poster: .*)':
					found='[Poster:]('+re.sub("Poster: ","",found)+")"
					poster=found
				# Append all data except title and poster info to variable
				if index<>0 and poster<>found:
					# Append a bold '**' Markdown to headers
					new_data=new_data+'**'+re.sub(": ",":** ",found)+'\n\n'
	# Append a title string and poster string in Markdown
	new_data='**Title:** [' +re.sub("Title: ","",title)+ '](http://www.imdb.com/title/' + re.sub("imdbID: ","",imdb_ID)+'/)\n\n' + new_data + poster
	
	# Clear clipboard, then add formatted info
	clipboard.set('')
	clipboard.set(new_data)
	
# Routine to give user more choices if not satisfied with the results of first query
def listData(d):
	# create list objects from the passed data d
	theTitles=re.findall(r"(Title: .*)",d);
	theYears=re.findall(r"(Year: .*)",d);
	theTypes=re.findall(r"(Type: .*)",d);
	theIds=re.findall(r"(imdbID: .*)",d);
	
	# Loop through all list objects to remove unwanted text and spaces
	for index, item in enumerate(theTitles):
		theTitles[index]=theTitles[index].replace('Title: ','').strip()
	
	for index, item in enumerate(theYears):
		theYears[index]=theYears[index].replace('Year: ','').strip()
		
	for index, item in enumerate(theTypes):
		theTypes[index]=theTypes[index].replace('Type: ','').strip()
	
	for index, item in enumerate(theIds):
		theIds[index]=theIds[index].replace('imdbID: ','').strip()
	
	# Initialize arrays	
	theFilm=[]
	theID=[]
	
	# Loop through list of types and select all but episodes
	for index, item in enumerate(theTypes):
		if theTypes[index]<>"episode":
			# Add title, year, and type to this array
			theFilm.append(theTitles[index]+', '+ theYears[index]+', '+theTypes[index])
			# Add imdbID to this array
			theID.append(theIds[index])
			
	# Print out a new list of film choices
	for index, item in enumerate(theFilm):
		print index, item
	try:
		print ''
		# Number of film selected will match the  index number of that film's imdbID in the id array
		idx=int(raw_input("Enter the number of your desired film or TV series: "))
	except ValueError:
		print ''
		print "Number doesn't exist."
		sys.exit()
	try:
		testID=theID[idx]
	except IndexError:
		print ''
		print "Try a number in range next time."
		print
		sys.exit()
		
	# Return the imdbID to the caller
	return theID[idx]
	
# Routine to refine your search if not happy with results of previous search
def refineData(s):
	clipboard.set('')
	# Use ?s for a query that yields multiple titles
	url="http://www.omdbapi.com/?s=" +s+ "&y=&plot=full&tomatoes=true&r=json"
	d=queryData(url)
	#print d
	id=listData(d)
	console.clear()
	print ''
	print "Retrieving data from new query..."
	if url<>' ':
		# Use ?i for an exact query on unique imdbID
		url="http://www.omdbapi.com/?i=" + id + "&y=&plot=full&tomatoes=true&r=json"
		d=queryData(url);
		mineData(d)
	else:
		sys.exit()

# Routine to append data to open doc
def writeData():
	console.clear()
	film=clipboard.get()
	if film=='':
		sys.exit()
	# Store contents of open doc in variable
	old_text=editor.get_text()
	# If open doc is not empty...
	if old_text<>'':
		'''
		Copy contents of the open doc to a new
		file. If back up file doesn't exist it
		will be created. If it exists, it will
		be overwritten.
		'''
		editor.set_file_contents('back_up.txt',old_text,'local')
		replacement = ''
		# Clear contents of current doc
		editor.replace_text(0,len(old_text), replacement)
		# Append new imdb data to text in current open doc
		concat=old_text +'\n'+'\n'+film
	else:
		# Query results only
		concat=film
	# Copy results to clipboard
	clipboard.set(concat)
	#editor.set_file_contents('Notepad.txt','','local')
	# Write results to open document in Editorial
	editor.replace_text(0,0,concat)
	
def main():
	console.clear()
	clipboard.set('')

	myTitle=raw_input("Please enter a movie or TV series title: ")

	print ''
	print "Connecting to server...wait"
	
	raw_string=re.compile(r' ')
	searchstring=raw_string.sub('+',myTitle)
	
	'''
	Use ?t to search for one item...this
	first pass will give you the most
	popular result for query, but not always
	the one you desire when there are
	multiple titles with the same name
	'''
	
	url="http://www.omdbapi.com/?t=" +searchstring + "&y=&plot=full&tomatoes=true&r=json"

	# Call subroutines
	d=queryData(url);
	mineData(d)

	while True:
		# Give user a choice to refine search
		print ''
		print "Refine your search? \n"
		print "[y] Yes"
		print "[n] No \n"
	
		choice=raw_input("Make a choice: ")

		if choice == 'y':
			refineData(searchstring)
		else:
			print''
			print 'Results of your search were copied\nto the clipboard in MD for use with\nthe MD text editor of your choice.'
			break

	sys.exit()

if __name__ == '__main__':
			main()
