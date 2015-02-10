# coding: utf-8
# Name: Search IMDB.py
# Author: John Coomler
# v1.0: 11/18/2014-Created
# v1.1: 02/01/2015-Added 'getNameID'
# function to return IMDB name id's for
# use with director & actor hypertexts.
# Added 'while True' loops for user input.
# v1.2: 02/09/2015-Many thanks to cclaus
# for code cleanup & great comments.
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
get a new set of results for that title.
You can keep refining your search until
you get the results you are looking for.
The info is displayed on the console
screen and formatted for Markdown and
copied to the clipboard so it can be
posted to your text editor or journal of
choice. When copied to a Markdown
capable editor, the movie title, director,
stars, and poster all appear in hypertext
with a direct link to the IMDB database if
more info is desired.
'''
import clipboard
import console
import json
import re
import requests  # use requests to simplify
import string
import sys
#import urllib2

# Initialize global variables
d=''  # ccc: trailing ';' is not required
url_fmt='http://www.omdbapi.com/?{}={}&y=&plot=full&tomatoes=true&r=json'

# ccc: just use str.title()
# Funtion that returns a string with first letter of each word capitalized.
#def titleCase(s):
#    newText = re.sub(r"[A-Za-z]+('[A-Za-z]+)?",lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),s)
#    return newText

# Function that returns a query to IMDB database
def queryData(url):
    #request=urllib2.Request(s)
    #response=json.load(urllib2.urlopen(request))
    response = requests.get(url).json()  # use requests module to simplify

    d=json.dumps(response,indent=-10)
    '''
    Reformat data, stripping out extra
    spaces, quotation marks, commas, etc as
    necessary
    '''
    # ccc: chain multiple functions
    d=d.replace('"',' ').replace('{',' ').replace('}',' ').replace(' : ',':')
    d=d.replace(' ,',' ').replace('\u2013','-').replace('[',' ').replace(']',' ')
    d=d.replace('\\ ','').replace('&','and').replace('\u00','')

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

# Function that returns a Markdown list of movie names(actors & directors) listed in query
def movieNamesMD(d,header):
    b=''
    a=re.findall(r'('+header+' .*)',d);
    a[0]=a[0].replace(header+' ','').strip()
    theNames= a[0].split(',');

    # Loop through list of movie names, appending markdown syntax to each one
    #for index, item in enumerate(theNames):  # ccc: use enumerate() when you want both index and item
    for index in xrange(len(theNames)):       # ccc: use xrange(len()) when you only want index
        theNames[index]=theNames[index].strip()

        # Call function to return the IMDB name ID for this name
        nameID=getNameID(theNames[index])

        # Append Markdown code
        # The old way
        #theNames[index]='['+theNames[index]+'](http://www.imdb.com/find?ref_=nv_sr_fn&q='+theNames[index]+ '), '
        # The new way with name ids
        theNames[index]='[{}](http://www.imdb.com/name/{}), '.format(theNames[index], nameID)

        # If first movie name in list...
        if index==0:
            # Append back the header
            theNames[index]=header+' ' +theNames[index]
        # Consecrate each markdown movie name into a return variable
        b+=theNames[index]  # ccc: +=
    #print b
    #sys.exit()
    return b

# Function to return the IMDB id number of a director or actors name
def getNameID(name):
    raw_string=re.compile(r' ')
    searchstring=raw_string.sub('+',name)

    url='http://www.imdb.com/xml/find?json=1&nr=1&nm=on&q='+searchstring

    d=queryData(url).replace("\n","")  # ccc: chain multiple functions, ';' not required
    nameID=re.findall(r"(name_popular:.*)",d) or re.findall(r"(name_exact:.*)",d)
    nameID=re.findall(r"(nm.*)",nameID[0])  # ccc: chain multiple functions, ';' not required

    nameID=nameID[0].split()[0].strip()  # ccc: chain multiple functions

    print name+' IMDB Id: '+nameID
    return nameID

# Routine to mine query results for desired strings & copies a Markdown text of those strings to the clipboard.
def mineData(d):
    #john=re.findall(r"(.*: .*)",d);

    # Create a list object of headers to search for in d

    headers='''Title Type Released Year Genre imdbRating Rated Runtime imdbID
               Language Country Awards BoxOffice Production Director Writer
               Actors Plot tomatoÇonsensus Poster'''.split()
    headers= ['({}: .*)'.format(x) for x in headers]  # ccc: list comprehension

    poster=new_data=''

    print 'Results of your IMDB Search:\n'

    # Loop through list of headers
    #for index, item in enumerate(headers):  # ccc: use enumerate() when you want both index and item
    for index in xrange(len(headers)):       # ccc: use xrange(len()) when you only want index
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
                    found+='/10'  # ccc: +=
                if headers[index]=='(imdbID: .*)':
                    imdb_ID=found
                print found + "\n"
                if headers[index]=='(Type: .*)':
                    # Add hashtag and make type string proper case
                    found=re.sub('Type: ','Type: #',found).title()  # ccc: use str.title()
                    #found=titleCase(found)
                if headers[index]=='(Director: .*)':
                    # Return a Markdown list of director(s)
                    found=movieNamesMD(d,'Director:')
                    print ''
                if headers[index]=='(Actors: .*)':
                    # Return a Markdown list of actors
                    found=movieNamesMD(d,'Actors:')
                    print ''
                # If this is poster info then add Markdown syntax
                if headers[index]=='(Poster: .*)':
                    found='[Poster:]('+re.sub("Poster: ","",found)+")"
                    poster=found
                # Append all data except title and poster info to variable
                if index and poster<>found:  # ccc: '<>0' not required
                    # Append a bold '**' Markdown to headers
                    new_data+='**'+re.sub(": ",":** ",found)+'\n\n'  # ccc: +=
    # Append a title string and poster string in Markdown
    fmt = '**Title:** [{}](http://www.imdb.com/title/{}/)\n\n{}{}'
    new_data=fmt.format(re.sub("Title: ","",title), re.sub("imdbID: ","",imdb_ID), new_data, poster)

    # Clear clipboard, then add formatted text
    clipboard.set('')
    clipboard.set(new_data)

# Funtion that provides list of multiple title choices if not satisfied with results of 1st query & returns the IMDB id for the movie title chosen.
def listData(d):
    # Create list objects from the query results
    #theTitles=re.findall(r"(Title: .*)",d);
    #theYears=re.findall(r"(Year: .*)",d);
    #theTypes=re.findall(r"(Type: .*)",d);
    #theIds=re.findall(r"(imdbID: .*)",d);

    # Loop through all list objects to remove unwanted text and spaces
    #for index, item in enumerate(theTitles):
    #    theTitles[index]=theTitles[index].replace('Title: ','').strip()
    # ccc: use list comprehensions for rapid conversions
    theTitles = [x.replace('Title: ','').strip() for x in re.findall(r"(Title: .*)",d)]

    #for index, item in enumerate(theYears):
    #    theYears[index]=theYears[index].replace('Year: ','').strip()
    theYears  = [x.replace('Year: ','').strip() for x in re.findall(r"(Year: .*)",d)]

    #for index, item in enumerate(theTypes):
    #    theTypes[index]=theTypes[index].replace('Type: ','').strip()
    theTypes = [x.replace('Type: ','').strip() for x in re.findall(r"(Type: .*)",d)]

    #for index, item in enumerate(theIds):
    #    theIds[index]=theIds[index].replace('imdbID: ','').strip()
    theIds = [x.replace('imdbID: ','').strip() for x in re.findall(r"(imdbID: .*)",d)]

    # Initialize arrays
    theFilm=[]
    theID=[]

    # Loop through list of types and select all but episodes
    #for index, item in enumerate(theTypes):  # ccc: use enumerate() when you want both index and item
    for index in xrange(len(theTypes)):       # ccc: use xrange(len()) when you only want index
        if theTypes[index]<>"episode":
            # Add title, year, and type to this array  # ccc: use str.join()
            theFilm.append(', '.join([theTitles[index], theYears[index], theTypes[index]]))
            # Add imdbID to this array
            theID.append(theIds[index])

    while True:
        # Print out a new list of film choices
        for index, item in enumerate(theFilm):
            print index, item
        try:
            print ''
            '''
            Number of film selected will
            match the  index number of that
            film's imdbID in the id array.
            '''
            idx=int(raw_input("Enter the number of your desired film or TV series: "))
            testID=theID[idx]
            break
        except:  # ccc: add the error(s) that you are expecting?
            print ''
            msg='Invalid entry...Continue? (y/n): '
            choice=raw_input(msg)
            console.clear()
            if not choice.upper().startswith('Y'):  # ccc: accept 'Yes', etc.
                sys.exit('Process cancelled...Goodbye')

    # Return the imdbID to the caller
    return theID[idx]

# Routine to refine query for mulitple titles if not happy with results of previous query
def refineData(s):
    clipboard.set('')
    # Use ?s for a query that yields multiple titles
    #url="http://www.omdbapi.com/?s=" +s+ "&y=&plot=full&tomatoes=true&r=json"
    url=url_fmt.format('s', s)
    d=queryData(url)
    #print d
    # List all the titles that match query and return IMDB id for movie title chosen from list
    id=listData(d)
    print "\nRetrieving data from new query..."
    if url==' ':    # ccc: how could this ever happen?
        sys.exit()  # ccc: no message to user?
    # Use ?i for an exact query on unique imdbID
    #url="http://www.omdbapi.com/?i=" + id + "&y=&plot=full&tomatoes=true&r=json"
    d=queryData(url_fmt.format('i', id));
    console.clear()
    mineData(d)

def main(args):
    console.clear()
    clipboard.set('')  # ccc: why clear the clipboard before you need to?  User might want its contents.

    # ccc: tap-and-hold on Pythonista run button to enter movie name as commandline arguements
    myTitle=' '.join(args) or raw_input('Please enter a movie or TV series title: ')

    print "\nConnecting to server...wait"

    #raw_string=re.compile(r' ')
    #searchstring=raw_string.sub('+',myTitle)
    searchstring=myTitle.replace(' ', '+')
    '''
    Use ?t to search for one item...this
    first pass will give you the most
    popular result for query, but not always
    the one you desire when there are
    multiple titles with the same name
    '''
    #url='http://www.omdbapi.com/?t={}&y=&plot=full&tomatoes=true&r=json'.format(myTitle)

    # Call subroutines
    d=queryData(url_fmt.format('t', searchstring));
    console.clear()
    mineData(d)

    while True:
        # Give user a choice to refine search
        msg='Refine your search? (y/n): '
        choice=raw_input(msg)
        if choice.upper().startswith('Y'):  # ccc: accept 'Yes', etc.
            console.clear()
            refineData(searchstring)
        else:
            print '\nResults of your search were copied\nto the clipboard in MD for use with\nthe MD text editor or journaling app\nof your choice.\n\n'
            break
    
if __name__ == '__main__':
    main(sys.argv[1:])  # strip off script name
