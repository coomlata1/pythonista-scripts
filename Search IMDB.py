#coding: utf-8
# Name: Search IMDB.py
# Author: John Coomler
# v1.0: 11/18/2014-Created
# v1.1: 02/01/2015-Added 'getNameID'
# function to return IMDB name id's for
# use with director & actor hypertexts.
# Added 'while True' loops for user input.
# v1.2: 02/09/2015-Many thanks to cclaus
# for code cleanup & great comments.
# v2.0: 02/25/2015-Complete rewrite of
# code, based on @cclauss's suggestions,
# to use Python dictionary for mining data
# rather than converting query results to
# strings and searching for substrings
# v2.1: 03/26/2015-Added code to account
# for apostrophes in actor/director's
# names during ID searches.
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
import requests
import string
import sys

# Initialize global variables
d = ''
url_fmt = 'http://www.omdbapi.com/?{}={}&y=&plot=full&tomatoes=true&r=json'

# Function that returns a query to IMDB database
def queryData(url):
  return requests.get(url).json()

'''
Function that returns a Markdown list of
names(actors & directors) listed in query.
'''
def names_md(names):
  fmt = '[{}](http://www.imdb.com/name/{})'
  return ', '.join(fmt.format(name.strip(),
    get_imdbID_name(name.strip())) for name in names)

'''
Function to return the IMDB id number of a
director or actors name
'''
def get_imdbID_name(name):
  url = 'http://www.imdb.com/xml/find?json=1&nr=1&nm=on&q=' + name.replace(' ', '+')
  d = queryData(url)
  #print ''
  #print d

  try:
    '''
    If 'name_popular' does not appear in
    query results then error will cause a
    jump to the except to try for
    'name_exact' and so on down the line
    '''
    name_id = d['name_popular'][0]['id']
    '''
    If we get hit but it doesn't match
    name we want then raise an error to
    try 'name_exact'' and so on down the
    line
    '''
    # Take care of apostrophe in a name, like "Jack O'Donnell"
    if d['name_popular'][0]['name'].replace('&#x27;',"'") <> name:
      raise Exception
    #print '{} popular'.format(name)
  except:
    try:
      name_id = d['name_exact'][0]['id']
      if d['name_exact'][0]['name'].replace('&#x27;',"'") <> name:
        raise Exception
      #print '{} exact'.format(name)
    except:
      try:
        name_id = d['name_approx'][0]['id']
        #print '{} approx'.format(name)
      except KeyError:
        print '{} name not found'.format(name)
        name_id = ''
        pass
  #print '{} IMDB Id: {}'.format(name, name_id)
  return name_id

# Strip any 'N/A's from data mining
def strip_nas(data):
  data = data.split('\n')
  new_data = ''

  for line in data:
    # Look for any 'N/A's'
    na = re.search("(N/A)", line)
    if na:
      # Clear them out
      line = ''
      #line = line.replace('\n','')
    else:
      new_data += '{}\n\n'.format(line)
  return new_data

'''
Function to mine query results for desired
movie info & return a text of those
results to the caller for printing to the
console.
'''
def mine_console_data(d):
  try:
    type = str.title(str(d['Type']))
  except KeyError:
    sys.exit('No useable query results')

  data = ('''Results of your IMDB Search:
Title: {Title}
Type: {}
Release Date: {Released}
Year: {Year}
Genre: {Genre}
IMDB Rating: {imdbRating}/10
Rating: {Rated}
Runtime: {Runtime}
IMDB Id: {imdbID}
Language: {Language}
Country: {Country}
Awards: {Awards}
Box Office: {BoxOffice}
Production: {Production}
Director: {Director}
Writers: {Writer}
Actors: {Actors}
Plot: {Plot}
Rotten Tomatoes Review: {tomatoConsensus}
  ''').format(type, **d)

  # Call function to remove any N/A's
  new_data = strip_nas(data)
  return new_data

'''
Function to mine query results for desired
movie info & return a Markdown text of
those results for copying to the
clipboard.
'''
def mine_md_data(d):
  title = d['Title']
  imdb_id = d['imdbID']

  print '\nGathering director & actor ids for MarkDown text on clipboard'
  md_directors = d['Director'].split(',')
  md_directors = names_md(md_directors)
  #print md_directors

  md_actors = d['Actors'].split(',')
  md_actors = names_md(md_actors)
  #print md_actors

  md_data = ('''
**Type:** #{Type}
**Release Date:** {Released}
**Year:** {Year}
**Genre:** {Genre}
**IMDB Rating:** {imdbRating}/10
**Rating:** {Rated}
**Runtime:** {Runtime}
**IMDB Id:** {}
**Language:** {Language}
**Country:** {Country}
**Awards:** {Awards}
**Box Office:** {BoxOffice}
**Production:** {Production}
**Director:** {}
**Writers:** {Writer}
**Actors:** {}
**Plot:** {Plot}
**Rotten Tomatoes Review:** {tomatoConsensus}
[Poster]({Poster})
''').format(imdb_id, md_directors, md_actors, **d)

  # Append a title string in Markdown
  fmt = '**Title:** [{}](http://www.imdb.com/title/{}/){}'
  md_data = fmt.format(title, imdb_id,  md_data)

  # Call function to remove any N/A's
  new_md_data = strip_nas(md_data)
  return new_md_data

'''
Funtion that provides list of multiple
title choices if not satisfied with
results of 1st query & returns the IMDB id
for the movie title chosen.
'''
def listData(d):
  #print d
  #sys.exit()

  the_films = []
  the_ids = []

  # Loop through list of titles and append all but episodes to film array
  for i in xrange(len(d['Search'])):
    if d['Search'][i]['Type'] <> 'episode':
      the_films.append(', '.join([d['Search'][i]['Title'],d['Search'][i]['Year'], d['Search'][i]['Type']]))
      # Add film's imdbID to the ids array
      the_ids.append(d['Search'][i]['imdbID'])

  while True:
    # Print out a new list of film choices
    for index, item in enumerate(the_films):
      print index, item
    try:
      '''
      Number of film selected will
      match the  index number of that
      film's imdbID in the ids array.
      '''
      film_idx = int(raw_input("\nEnter the number of your desired film or TV series: "))
      film_id = the_ids[film_idx]
      break
    except (IndexError, ValueError):
      choice = raw_input('\nInvalid entry...Continue? (y/n): ')
      console.clear()
      if not choice.upper().startswith('Y'):
        sys.exit('Process cancelled...Goodbye')

  # Return the film's imdbID to the caller
  return film_id

def main(args):
  console.clear()
  clipboard.set('')
  '''
  Tap-and-hold on Pythonista run button to
  enter movie name as commandline
  arguments
  '''
  myTitle = ' '.join(args) or raw_input('Please enter a movie or TV series title: ')

  print "\nConnecting to server...wait"

  s = myTitle.replace(' ', '+')
  '''
  Use ?t to search for one item...this
  first pass will give you the most
  popular result for query, but not always
  the one you desire when there are
  multiple titles with the same name
  '''
  # Call subroutines
  d = queryData(url_fmt.format('t', s));
  print('='*20)
  print(mine_console_data(d))

  while True:
    # Give user a choice to refine search
    msg = 'Refine your search? (y/n/c): '
    choice = raw_input(msg)
    # Accept 'Yes', etc.
    if choice.upper().startswith('Y'):
      print('='*20)
      # Use ?s for a query that yields multiple titles
      url = url_fmt.format('s', s)
      d = queryData(url)
      '''
      Call function to list all the titles
      in the query and return IMDB id
      for title chosen from list
      '''
      id = listData(d)
      print "\nRetrieving data from new query..."
      # Use ?i for an exact query on unique imdbID
      d = queryData(url_fmt.format('i', id));
      print('='*20)
      print(mine_console_data(d))
    elif choice.upper().startswith('N'):
      # Clear clipboard, then add formatted text
      clipboard.set('')
      clipboard.set(mine_md_data(d))

      print '\nResults of your search were copied\nto the clipboard in MD for use with\nthe MD text editor or journaling app\nof your choice.\n\n'
      break
    else:
      sys.exit('Search Cancelled')

if __name__ == '__main__':
  main(sys.argv[1:])  # strip off script name
