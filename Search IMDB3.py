# coding: utf-8
'''
#---Script: Search IMDB.py
#---Author: @coomlata1
#---Created: 11/18/2014
#---Last Modified: 01/30/2017

This Pythonista script uses the api available at www.omdbapi.com to search for your desired movie, TV series, or actor-actress information.

The movie-tv query will first return the most popular result for what matches that title. The script will display most of the pertinent info in a ui.TextView screen about that movie/TV series including release date, imdb rating, box office returns, writers, director, actors and plot.

That may not be the results you are looking for. You can then refine your search and the query will return a list of titles and their release year that match or are close to matching the desired title. When you select a title from the list you will get a new set of results for that title. You can keep refining your search until you get the results you are looking for. The info is displayed in a ui TextView screen and formatted for Markdown.

There is also an option button available which displays the query results directly from the imdb web site on a WebView screen.

The actor-actress query results will display on a Webview page directly from the imdb website. The results here are for viewing only. There is no option provided in the script to export the results.

You can export the results of the movie-tv queries to 1Writer, DayOne, Drafts, Editorial or the clipboard. The results can also be imported to these apps if this script is called via a url from the app itself.

When exported to a Markdown capable editor the movie title & poster appear in hypertext with a direct link to the IMDB database if more info is desired.

This script is also capable of displaying the query results in markdown TextView as a result of MarkdownView.py, a script placed in the site-packages folder, and called as a module in this script.

Requirements: Markdown.py which is available at:
https://github.com/mikaelho/pythonista-markdownview. Be sure to read the readme.md file for installation instructions.

Optional: The tmdb api at https://www.themoviedb.or/en provides a more detailed overview of cast, crew, and plot. To use the api you will need to register, whereupon you will receive an api key.

A pure python wrapper for the tmdb api, 'tmdbsimple', allows for an easy way to code your tmdb api queries. It is available at https://pypi.python.org/pypi/tmdbsimple. I installed it into Pythonista using Stash by typing 'pip install tmdbsimple' at the Stash command line. Further instructions and information are available on the tmdbsimple webpage.
'''
#from __future__ import (absolute_import, division, print_function, unicode_literals)
import clipboard
import console
import requests
import urllib
import sys
import re
import unicodedata
import ui
import dialogs
import MarkdownView as mv

# The url template for the IMDB api queries
url_fmt = 'http://www.omdbapi.com/?{}={}&y={}&plot=full&tomatoes=true&r=json'
tmdb_simple_imported = True

# Test for existence of tmdbsimple module.
try:
  import tmdbsimple as tmdb
  # Enter your registered tmdb api key...
  tmdb.API_KEY ='ac6091c3fc2e0b58a399eb0b158777b9'
except ImportError:
  tmdb_simple_imported = False
  
# Action called when a selection change is made on segmented control in ui
def seg1_selected(sender):
  if sender.selected_index == 0:
    sender.superview.lb1.text = 'Enter A Movie Or TV Series Title:'
    sender.superview.lb2.text = 'Enter Year Of Release If Known:'
    sender.superview.tf2.hidden= False
    sender.superview.tf1.text = ''
    sender.superview.tf2.text = ''
    sender.superview.right_button_items = []
  elif sender.selected_index == 1:
    sender.superview.lb1.text = 'Enter Actor-Actress Name:'
    sender.superview.lb2.text = ''
    sender.superview.tf2.hidden= True
    sender.superview.tf1.text = ''
    sender.superview.tf2.text = ''
    sender.superview.right_button_items = []

# The ui
class MyView(ui.View):
  def __init__(self):
    self.width, self.height = ui.get_screen_size()
    #self.frame = (0, 0, 424, 736)
    self.background_color = 'orange'
    self.flex = 'WHLRTB'
    b1 = ui.ButtonItem('Quit', action = self.cancel, tint_color = 'black')
    
    self.left_button_items = [b1]

    # Accomodate iPhone 6p and smaller phones as well
    if is_iP6p():
      self.sc = ui.SegmentedControl(frame = (20,30,380,50))
      self.tf1 = ui.TextField(frame = (20, 130, 380, 50))
      self.tf2 = ui.TextField(frame = (70, 240, 275, 50))
      self.lb1 = ui.Label(frame = (70, 80, 275, 50))
      self.lb2 = ui.Label(frame = (70, 190, 275, 50))
      self.iv = ui.ImageView(frame = (55, 290, 300, 300))
      self.sc.segments = ('Search For Movie-TV Series', 'Search For Actor-Actress')
    else:
      self.sc = ui.SegmentedControl(frame = (20,15,280,50))
      self.tf1 = ui.TextField(frame = (20, 105, 280, 50))
      self.tf2 = ui.TextField(frame = (70, 200, 175, 50))
      self.lb1 = ui.Label(frame = (25, 60, 275, 50))
      self.lb2 = ui.Label(frame = (20, 150, 275, 50))
      self.iv = ui.ImageView(frame = (45, 235, 225, 225))
      self.sc.segments = ('Search Movies-TV', 'Search Actor')
    
    self.sc.bordered = True
    self.sc.border_width = 2
    self.sc.background_color = 'cyan'
    self.sc.tint_color = 'black'
    self.sc.corner_radius = 10
    self.sc.flex = "WHLRTB"
    # Default to a title search
    self.sc.selected_index = 0
    self.sc.action = seg1_selected
  
    self.tf1.bordered = False
    self.tf1.background_color = 'cyan'
    self.tf1.corner_radius = 10
    self.tf1.font = ('<system-bold>', 16)
    self.tf1.flex = "WHLRTB"
    self.tf1.clear_button_mode = 'while_editing'
    self.tf1.delegate = self
    # Displays keyboard
    #self.tf1.begin_editing()

    self.tf2.bordered = False
    self.tf2.background_color = 'cyan'
    self.tf2.corner_radius = 10
    self.tf2.font = ('<system-bold>', 16)
    self.tf2.flex = 'WHLRTB'
    self.tf2.clear_button_mode = 'while_editing'
    self.tf2.keyboard_type = ui.KEYBOARD_NUMBER_PAD

    self.lb1.alignment = ui.ALIGN_CENTER
    self.lb1.text = 'Enter A Movie Or TV Series Title:'
    self.lb1.name = 'text_field'
    self.lb1.font = ('<system-bold>', 18)
    self.lb1.flex = 'WHLRTB'

    self.lb2.alignment = ui.ALIGN_CENTER
    self.lb2.text = 'Enter Year Of Release If Known:'
    self.lb2.font = ('<system-bold>', 18)
    self.lb2.flex = 'WHLRTB'
    
    # Gif file needs to be in the same directory as this script
    self.iv.image = ui.Image.named('thin_blue_line.gif')
    
    # Load controls into ui
    self.add_subview(self.sc)
    self.add_subview(self.tf1)
    self.add_subview(self.tf2)
    self.add_subview(self.lb1)
    self.add_subview(self.lb2)
    self.add_subview(self.iv)
  
  def cancel(self, sender):
    global app
    
    # If this script is called from a url in another app...
    if app:
      if app == '1Writer':
        app = 'onewriter'
      app = app.lower()
      cmd = '{}://'.format(app)
      import webbrowser
      webbrowser.open(cmd)
    # Exit ui
    self.close()
    
  def textfield_did_change(self, tf1):
    tf1.text = tf1.text.title()
    if tf1.text:
      self.right_button_items = []
      b2 = ui.ButtonItem('Run Query', action = self.query, tint_color = 'green')
      self.right_button_items = [b2]
    else:
      self.right_button_items = []

  def query(self, sender):
    global d

    # Clear keyboard from screen
    self.tf1.end_editing()
    self.tf2.end_editing()
    
    if self.sc.selected_index == 0:
      # Searching movie-tv title
      my_title = self.tf1.text
      my_year = self.tf2.text

      t = my_title.strip().replace(' ', '+')
      y = my_year.strip()

      console.hud_alert('Querying IMDB for {}'.format(my_title))
      '''
      Use ?t to search for one item. This first pass will give you the most popular result for query, but not always the one you desire when there are multiple titles that are the same or similar to the title you are looking for.
      '''
      # Call subroutines
      d = query_data(url_fmt.format('t', t, y))
      results = mine_console_data(d)
      sender.enabled = False
      self.load_textview(results)
    else:
      # Searching for a actor-actress name
      name = self.tf1.text
      name = name.strip()
      id = get_imdbID_name(name)
      #print id
      url = 'http://www.imdb.com/{}'.format(id)
      self.load_webview(url)
      
  def load_textview(self, results):
    #self.mv = ui.TextView()
    self.mv = mv.MarkdownView()
    self.mv.editable = False
    self.mv.background_color = 'orange'
    self.mv.width, self.mv.height = ui.get_screen_size()
    self.mv.font = ('<system-bold>', 15)
    self.mv.flex = 'HLRTB'
    self.right_button_items = []
    b3 = ui.ButtonItem('Refine Query?', tint_color = 'black')
    b4 = ui.ButtonItem('Yes', action = self.refine, tint_color = 'green')
    b5 = ui.ButtonItem('No', action = self.no_refine, tint_color = 'red')
    self.right_button_items = [b5, b4, b3]
    self.add_subview(self.mv)
    self.mv.text = results
  
  def refine(self, sender):
    global d

    # Use ?s for a query that yields multiple titles
    s = self.tf1.text.strip().replace(' ', '+')
    y = ''
    url = url_fmt.format('s', s, y)
    rd = query_data(url)
    '''
    Call function to list all the titles in the query & a list of their respective IMDB ids.
    '''
    the_films, the_ids = list_data(rd)

    items = the_films
    id = ''
    
    # If more than one item in query results...
    if len(items) != 1:
      movie_pick = dialogs.list_dialog('Pick Your Desired Movie Or TV Show:', items)
      
      if movie_pick is not None:
        #console.hud_alert('Now quering for {}'.format(movie_pick))
        for i, item in enumerate(items):
          if item.strip() == movie_pick.strip():
            id = the_ids[i].strip()
            break

        # Use ?i for an exact query on unique imdbID
        rd = query_data(url_fmt.format('i', id, y))
        results = mine_console_data(rd)
        d = rd
        self.mv.text = results
      else:
        console.hud_alert('Nothing Selected')
    else:
      console.hud_alert('Only One Film-TV Series In Query')
    return

  def no_refine(self, sender):
    global app
    # Clear clipboard, then add formatted text
    clipboard.set('')
    clipboard.set(mine_md_data(d))
    #self.mv.text = mine_md_data(d)
    self.mv.text = clipboard.get()
    b6 = ui.ButtonItem('Webview?:', tint_color = 'black')
    b7 = ui.ButtonItem('Yes', action = self.web, tint_color = 'green')
    b8 = ui.ButtonItem('No', action = self.no_web, tint_color = 'red' )
    self.right_button_items = [b8, b7, b6]
  
  def web(self, sender):
    imdb_id = d['imdbID']
    url = 'http://www.imdb.com/title/{}/'.format(imdb_id)
    self.load_webview(url)
      
  def no_web(self, sender):
    global app
    # Clear clipboard, then add formatted text
    clipboard.set('')
    clipboard.set(mine_md_data(d))
    self.mv.text = clipboard.get()
    # Set up buttons on title bar for export
    b9 = ui.ButtonItem('Export Query Results?:', tint_color = 'black')
    b10 = ui.ButtonItem('Yes', action = self.export, tint_color = 'green')
    b11 = ui.ButtonItem('No', action = self.no_export, tint_color = 'red' )
    self.right_button_items = [b11, b10, b9]

    # If script called from another app...
    if app:
      cmd = get_url(app, source = 'called', title = '')
      import webbrowser
      webbrowser.open(cmd)
      self.close()
      sys.exit('Returning to caller')
      
  def export(self, sender):
    the_apps = ['DayOne', 'Drafts4', 'Editorial', '1Writer', 'Clipboard']
    app_pick = dialogs.list_dialog('Pick An App To Export Query Results To:', the_apps)
    if app_pick is not None:
      cmd = get_url(app_pick, source = 'picked', title = self.tf1.text.strip())
      if cmd:
        import webbrowser
        webbrowser.open(cmd)
        self.close()
        sys.exit('Exporting query results to chosen app.')
      else:
        msg = 'Results of your search were copied to the clipboard in MD for use with the MD text editor or journaling app of your choice.' + '\n\n'
        self.mv.text = self.mv.text + msg
        self.no_export(self)

  def no_export(self, sender):
    b12 = ui.ButtonItem('New Query', action = self.new_query, tint_color = 'green' )
    self.right_button_items = [b12]
  
  def load_webview(self, url):
    self.wv = ui.WebView()
    self.wv.frame = self.bounds
    self.wv.border_color='grey'
    self.wv.border_width = 3
    self.wv.scales_page_to_fit = True
    self.wv.load_url(url)
    self.right_button_items = []
    self.closebutton(self.wv)
    self.add_subview(self.wv)
       
  # Create close button('X') for webview
  def closebutton(self, view):
    if is_iP6p():
      l_pos = 377
    else:
      l_pos = 285
    # Position x button coordinate based on screen size
    closebutton = ui.Button(frame = (l_pos,0,35,35), bg_color = 'grey')
    closebutton.image = ui.Image.named('ionicons-close-round-32')
    closebutton.flex = 'bl'
    closebutton.action = self.closeview
    view.add_subview(closebutton)

  # Assigned action for closebutton...closes webview
  def closeview(self, sender):
    # Close webview subview
    sender.superview.superview.remove_subview(sender.superview)
    
    # Title search
    if self.sc.selected_index == 0:
      # Reshow export buttons on title bar
      b9 = ui.ButtonItem('Export Query Results?:', tint_color = 'black')
      b10 = ui.ButtonItem('Yes', action = self.export, tint_color = 'green')
      b11 = ui.ButtonItem('No', action = self.no_export, tint_color = 'red' )
      self.right_button_items = [b11, b10, b9]
    # Name Search
    else:
      self.tf1.text = ''
        
  def new_query(self, sender):
    self.remove_subview(self.mv)
    self.right_button_items = []
    self.tf1.text = ''
    self.tf2.text = ''
    #self.tf1.begin_editing()

# Determine which device by screen size
def is_iP6p():
  iP6p = True
  min_screen_size = min(ui.get_screen_size())

  #print min_screen_size
  #iphone6 min = 414
  #iphone6 max = 736
  #iphone5 min = 320
  #iphone5 max = 568

  if min_screen_size < 414:
    iP6p = False
  return iP6p

# Function that returns a query to IMDB database
def query_data(url):
  return requests.get(url).json()

# Strip out lines containing '(N/A)'
def strip_na_lines(data):
  return '\n\n'.join(line for line in data.split('\n')
                     if 'N/A' not in line) + '\n'

def tmdb_movie_query(d):
  search = tmdb.Search()
  found = False
  # Query for movies
  response = search.movie(query = '{}'.format(d['Title']))
  # Loop query results
  for s in search.results:
    found == False
    if s['title'].upper() == d['Title'].upper():
      # Get each movie's tmdb movie id
      id = s['id']
      # Initialize query for this specific movie's data
      movie = tmdb.Movies(id)
      # Allow for search on info
      response = movie.info()
      # Get imdb id for this movie
      imdb_id = movie.imdb_id
  
      # If there is an imdb id...
      if imdb_id == d['imdbID']:
        found = True
        break
  
  if found:
    the_movie_plot = movie.overview
    # Format for millions of dollars with no cents
    if movie.budget > 0:
      budget = '${:7,.0f}'.format(movie.budget)
    else:
      budget = 'N/A'
  
    if movie.revenue > 0:
      revenue = '${:7,.0f}'.format(movie.revenue)
    else:
      revenue = 'N/A'
    
    response = movie.credits()
    the_producers = []
    the_movie_cast = []
    
    for s in movie.production_companies:
      the_producers.append('{}'.format(s['name']))
    
    for s in movie.cast:
      # Debug
      #print (s['name'], s['character'])
      the_movie_cast.append('{} as {}'.format(s['name'], s['character']))
  else:
    budget = 'N/A'
    revenue = 'N/A'
    the_producers = ''
    the_movie_cast = ''
    the_movie_plot = ''
  
  return budget, revenue, the_producers, the_movie_cast, the_movie_plot
  
def tmdb_tv_query(d):
  search = tmdb.Search()
  found = False
  # Query for tv
  response = search.tv(query = '{}'.format(d['Title']))
  # Loop query results
  for s in search.results:
    #print s
    found == False
    if s['name'].upper() == d['Title'].upper():
      # Get each tv show's tmdb movie id
      id = s['id']
      # Initialize query for this specific tv series data
      tv = tmdb.TV(id)
      
      # Allow for search on id
      response = tv.external_ids()
      # Get imdb id for this tv show
      imdb_id = tv.imdb_id
  
      # If there is an imdb id...
      if imdb_id == d['imdbID']:
        found = True
        break
  
  if found:
    response = tv.credits()
    the_tv_cast = []
    
    for s in tv.cast:
      # Debug
      #print (s['name'], s['character'])
      if s['character']:
        the_tv_cast.append('{} as {}'.format(s['name'], s['character']))
      else:
        the_tv_cast.append('{}'.format(s['name']))
        
    response = tv.info()
    seasons = tv.number_of_seasons
    episodes = tv.number_of_episodes
    the_tv_plot = tv.overview
  else:
    seasons = ''
    episodes = ''
    the_tv_cast = ''
    the_tv_plot = ''
  
  return seasons, episodes, the_tv_cast, the_tv_plot

'''
Function to return the IMDB id number for actor's name
'''
def get_imdbID_name(name):
  new_name = name
 
  url = 'http://www.imdb.com/xml/find?json=1&nr=1&nm=on&q={}'.format(new_name.replace(' ', '+'))
  
  url = urllib.unquote(url).decode('utf-8')
  #print(url)
  d = query_data(url)
  
  #print (len(d))
  #print(d)
  try:
    '''
    If 'name_popular' does not appear in
    query results then error will cause a
    jump to the exception to try for
    'name_exact' and so on down the line
    '''
    name_id = d['name_popular'][0]['id']
    #print('{} popular'.format(name))
  except:
    try:
      name_id = d['name_exact'][0]['id']
      #print('{} exact'.format(name))
    except:
      try:
        name_id = d['name_approx'][0]['id']
        #print('{} approx'.format(name))
      except KeyError:
        print('\nAn Imdb id for {} was not found.'.format(name))
        name_id = ''
        pass

  # If no id returned then return text for a url to run a general query on name...
  if len(name_id) == 0:
    name_id = 'find?ref_=nv_sr_fn&q={}&s=all'.format(name.replace(' ', '+'))
  else:
    # Otherwise return text for a url to query on actual id.
    #print('\nName:{} Id:{} found.'.format(name, name_id))
    name_id = 'name/{}'.format(name_id)
  return name_id

'''
Function to mine query results for desired movie info & return a text of those results to the caller for display in a TextView.
'''
def mine_console_data(d):
  #print d
  try:
    d['Type'] = d['Type'].title()
  except KeyError:
    msg = 'No useable query results'
    console.hud_alert(msg)
    sys.exit(msg)
    
  # If you have installed the tmdbsimple python module and you have a tmdb api key then you can mine more data
  if tmdb_simple_imported:
    if tmdb.API_KEY:
      if d['Type'] == 'Movie':
        budget, revenue, the_producers, the_movie_cast, the_movie_plot = tmdb_movie_query(d)
    
        d['Response'] = budget
        d['BoxOffice'] = revenue
    
        if the_producers:
          d['Production'] = ', '.join(the_producers)
    
        if the_movie_cast:
          d['Actors'] = ', '.join(the_movie_cast)
    
        if the_movie_plot:
          if len(the_movie_plot) > len(d['Plot']):
            d['Plot'] = the_movie_plot
    
      if d['Type'] == 'Series':
        seasons, episodes, the_tv_cast, the_tv_plot = tmdb_tv_query(d)
      
        if seasons and episodes:
          d['Year'] = '{}...{} Seasons...{} Episodes'.format(d['Year'], seasons, episodes)
    
        if the_tv_cast:
          d['Actors'] = ', '.join(the_tv_cast)
      
        if the_tv_plot:
          if len(the_tv_plot) > len(d['Plot']):
            d['Plot'] = the_tv_plot
        d['Response'] = 'N/A'
    else:
      d['Response'] = 'N/A'
    
  return strip_na_lines('''Results of your IMDB Search:
Title: {Title}
Type: {Type}
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
Budget: {Response}
Box Office: {BoxOffice}
Production: {Production}
Director: {Director}
Writers: {Writer}
Cast: {Actors}
Plot: {Plot}
Rotten Tomatoes Review: {tomatoConsensus}
'''.format(**d))

'''
Function to mine query results for desired movie info & return a Markdown text of those results for copying to the
clipboard.
'''
def mine_md_data(d):
  return strip_na_lines('''**Title:** [{Title}](http://www.imdb.com/title/{imdbID}/)
**Type:** #{Type}
**Release Date:** {Released}
**Year:** {Year}
**Genre:** {Genre}
**IMDB Rating:** {imdbRating}/10
**Rating:** {Rated}
**Runtime:** {Runtime}
**IMDB Id:** {imdbID}
**Language:** {Language}
**Country:** {Country}
**Awards:** {Awards}
**Budget:** {Response}
**Box Office:** {BoxOffice}
**Production:** {Production}
**Director:** {Director}
**Writers:** {Writer}
**Cast:** {Actors}
**Plot:** {Plot}
**Rotten Tomatoes Review:** {tomatoConsensus}
[Poster]({Poster})
'''.format(**d))

'''
Function that returns a list of multiple titles that contain the film-tv name if not satisfied with results of 1st query, and a list of each title's respective IMDB id.
'''
def list_data(d):
  # For debug
  #print(d)
  #sys.exit()

  the_films = []
  the_sorted_films = set()
  the_ids = []
  
  # Loop through query results & add the year, title, type, and IMDB id of every media but 'episodes' to film-tv set.
  for title in d['Search']:
    if title['Type'] != 'episode':
      #the_films.append(', '.join([title['Title'], title['Year'], title['Type']]))
      # Add film-tv shows to a set for sorting by year made
      the_sorted_films.add(','.join([title['Year'], title['Title'], title['Type'], title['imdbID']]))
  
  # Loop sorted media & append it back into a list in sorted chronological order...oldest to newest
  for film in sorted(the_sorted_films):
    film = film.split(',')
    the_films.append(', '.join([film[1], film[0], film[2]]))
    # Add film's imdbID to the ids list
    the_ids.append(film[3])  
      
  return the_films, the_ids

'''
Function to return a url cmd to send query results to the app, either named in the arg that called this script, or picked from export app list in this script
'''
def get_url(app, source, title):
  import urllib

  # Retrieve query from clipboard
  b = clipboard.get()

  # Replace unicode characters when necessary
  if len(re.sub('[ -~]', '', b)) != 0:
    b = unicodedata.normalize('NFD', u'{}'.format(b)).encode('ascii', 'ignore')

  quoted_output = urllib.quote(b, safe = '')

  if app == 'DayOne':
    # Post query results to a DayOne journal entry
    cmd = 'dayone://post?journal={}&entry={}&tags={}'.format('Movies', quoted_output, 'movie')

  if app == '1Writer':
    if source == 'called':
      # Append query to open 1Writer doc
      cmd = 'onewriter://x-callback-url/append?path=/Documents%2F&name=Notepad.txt&type=Local&text={}'.format(quoted_output)
    else:
      title = title.replace(' ','%20')
      # Write query results to a new 1Writer markdown doc named by title of movie
      cmd = 'onewriter://x-callback-url/create?path=/Documents&name={}.md&text={}'.format(title, quoted_output)

  if app == 'Editorial':
    if source == 'called':
      # Append query to open Editorial doc
      cmd = 'editorial://?command=Append%20Open%20Doc'
    else:
      # Write query results to a new Editorial markdown doc named by title of film-tv show
      cmd = 'editorial://new/{}.md?root=local&content={}'.format(title, quoted_output)

  if app == 'Drafts4':
    if source == 'called':
      '''
      Append query to open Draft doc using the 2nd
      argument from calling URL as the UUID of the
      open doc
      '''
      cmd = 'drafts4://x-callback-url/append?uuid={}&text={}'.format(sys.argv[2], quoted_output)
    else:
      # Write query results to a new draft text
      cmd = 'drafts4://x-callback-url/create?text={}'.format(quoted_output)

  if app == 'Clipboard':
    cmd = ''

  return cmd

def main():
  global app
  
  v = MyView()
  
  '''
  Allow to run script stand alone or from another app using command line arguments via URL's.
  '''
  try:
    app = sys.argv[1]
  except IndexError:
    app = None
     
  # Lock screen and title bar in portrait orientation and wait for view to close
  v.present(style = 'full_screen', title_bar_color = 'cyan', orientations = ['portrait'])
  v.wait_modal()

  '''
  If view was closed with the 'X' on title bar & script was called from another app, then return to calling app & exit script, otherwise just cancel script.
  '''
  #if app:
    #if app == '1Writer':
      #app = 'onewriter'
    #app = app.lower()
    #cmd = '{}://'.format(app)
    #import webbrowser
    #webbrowser.open(cmd)
    #sys.exit('Returning to caller.')
  #else:
    #sys.exit('Cancelled')
if __name__ == '__main__':
  main()
