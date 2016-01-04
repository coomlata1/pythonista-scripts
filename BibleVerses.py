# coding: utf-8
'''
BibleVerses.py
@coomlata1

This Pythonista script will retrieve any bible verse or
verses and copy them to the clipboard or 1Writer,
Editorial, or Drafts via a url. The script uses the
getBible.net api as the query source for scripture.
More info is available at https://getbible.net/api.

The script can be initialized stand alone from
Pythonista or from a url action in 1Writer,
Editorial, or Drafts. 

If run stand alone, the script will copy the
verse(s) returned from the query to the clipboard
and print them to the console. You can then copy
the verses to any application you wish using the
clipboard. 

If the script is called from one of the 3 text
editors mentioned above via a url, the scripture
will be appended to the calling editor's open doc.

Examples of the calling URLs:
From 1Writer: pythonista://
{{BibleVerses.py}}?action=run&argv=onewriter
  
From Editorial: pythonista://
BibleVerses.py?action=run&argv=editorial

From Drafts: pythonista://
{{BibleVerses.py}}?action=run&argv={{drafts4}}
&argv={{[[uuid]]}}

The script will prompt you for the desired verse
references. Possible formats for the references
include:
  Multiple books with consecutive or single verses:
  1 John 5:3-5,7-10,14;Mark 7:4-6;8:3-6,10
  1 John 5:3-5,7-10,14;Mark 7:4-6;Mark 8:3-6,10
  Consecutive verses:
  Mark 7:4-6
  Single verse:
  Mark 7:4

Seperate different books or chapters with a
semicolon. Seperate verses in same book with a
comma. List verses in numerical order, lowest to
highest. Seperate the book and it's verse
references with a space. Book names with both
numeric and alpha characters(1 John), can be listed
as 1John or 1 John and the script will handle it.

The script allows you to select between 10
different English language bible versions. The
default setting is the New American Standard.
  
Inspiration for this script came from 
@pfcbenjamin and his script, 'BibleDraft.py'.
More info on his projects is available at:
http://sweetnessoffreedom.wordpress.com/projects
'''
import requests
import urllib
import sys
import re
import webbrowser
import console
import clipboard

def passage_query(ref, version):
  ref = ref.replace(' ','%20')
  url = 'https://getbible.net/json?p={}&v={}'.format(ref, version)
  r = requests.get(url)
  t = r.text
  return t

def check_book(ref):
  book = ''
  # Make sure we have space between end of book name and chapter number and fix if necessary
  # Loop backwards through each character in ref
  for i in reversed(xrange(len(ref))):
    # If a letter
    if ref[i].isalpha():
      # Last letter of book so mark it's place in ref
      pos = ref.rfind(ref[i])
      break
  '''
  Book name is all characters from start of ref to
  position of last letter of book plus 1 for zero
  based array
  '''
  # Strip out any white spaces in book & verses...
  # ie '1 John 5:4- 7'
  book = ref[:pos + 1].strip().replace(' ','')
  verses = ref[pos + 1:].strip().replace(' ','')
  
  # Add unwhitened book & verses back to ref
  ref = '{} {}'.format(book, verses).title()
  
  return ref, book
  
def replace_all(t, dic):
  for j, k in dic.iteritems():
    t = t.replace(j, k)
  return t

def cleanup(t, ref, version):
  # Chapter number is between space and colon
  chapter = ref[ref.find(' ') + 1:ref.find(':')]
  # If comma(s) in ref
  if ref.find(',') != -1:
    # First passage is between colon & 1st comma
    fp = ref[ref.find(':') + 1:ref.find(',')].strip()
    # Last passage is between last comma and end
    lp = ref[ref.rfind(',', 0, len(ref)) + 1:].strip()
    
    # If dash in first passage
    if fp.find('-') != -1:
      # First verse between colon & dash
      first_verse = fp[fp.find(':') + 1:fp.find('-')].strip()
    else:
      # No dash so first verse is first passage
      first_verse = fp
    
    # If dash in last passage
    if lp.find('-') != -1:
      # Last verse is everything after dash
      last_verse = lp[lp.find('-') + 1:].strip()
    else:
      # No dash so last verse is last passage
      last_verse = lp
  # No commas in ref
  else:
    # If dash in ref
    if ref.find('-') != -1:
      # First verse is between colon & dash
      first_verse = ref[ref.find(':') + 1:ref.find('-')].strip()
      # Last verse is everything after dash
      last_verse = ref[ref.find('-') + 1:].strip()
    else:
      # First verse & last verse are same...everything after colon
      first_verse = ref[ref.find(':') + 1:].strip()
      last_verse = first_verse
    
  # Create dictionaries to clean up passages
  dic_c = {'{':'', '}':'', '"':'', '\\':'', '*': ''}
  dic_w = {'verse:':'', ':verse_nr:':'verse '}

  # Replace unwanted characters
  t = replace_all(t, dic_c)
  # Replace unwanted words
  t = replace_all(t, dic_w)
  
  # More cleaning...
  for i in range(int(last_verse)):
    t = t.replace(',{0}verse {0},'.format(i + 1),' [{}] '.format(i + 1))
    if int(first_verse) == i + 1:
      t = t.replace('chapter_nr:{0},chapter:{1}verse {1},'.format(chapter, i + 1), '[{}:{}] '.format(chapter, i + 1))
    else:
      t = t.replace('chapter_nr:{0},chapter:{1}verse {1},'.format(chapter, i + 1), ' [{}] '.format(i + 1))
       
  t = t.replace('],direction:LTR,type:verse,version:{});'.format(version),'')

  header_end_pos = t.find('[{}:{}]'.format(chapter, first_verse))
  header = t[:header_end_pos]
  # Uncomment to debug
  #print header
  t = t.replace(header, '')
  header = header.replace('(book:', '').replace('[', '')
  header = ',{}'.format(header)
  # Uncomment to debug
  #print header
  t = t.replace(header, '')
  return t

def get_url(app, fulltext):
  if app == 'drafts4':
    # Write scripture to new draft
    #url = '{}://x-callback-url/create?text={}'.format(app, urllib.quote(fulltext))
  
    # Append scripture to existing open draft
    url = '{}://x-callback-url/append?uuid={}&text={}'.format(app, sys.argv[2], urllib.quote(fulltext))
  elif app == 'onewriter':
    # Append scripture to open 1Writer doc
    url = '{}://x-callback-url/append?path=/Documents%2F&name=Notepad.txt&type=Local&text={}'.format(app, urllib.quote(fulltext))
  elif app == 'editorial':
    # Copy scripture to clipboard
    clipboard.set('')
    clipboard.set(fulltext)
    '''
    Append scripture to open Editorial doc. Calls
    the 'Append Open Doc' Editorial workflow
    available at http://www.editorial-
    workflows.com/workflow/
    5278032428269568/g2tYM1p0OZ4
    '''
    url = '{}://?command=Append%20Open%20Doc'.format(app)
  
  return url

def main(ref):
  user_input = 'Verse(s): {}'.format(ref.title())
  console.hud_alert('Quering For Verses...')
  '''
  Allow to run script stand alone or from another
  app using command line arguments via URL's.
  '''
  try:
    app = sys.argv[1]
  except IndexError:
    app = ''
    #print 'Query on:\n{}'.format(ref.title())
  
  # Handle multiple references
  alt_line_split = re.search(';',ref)
  if alt_line_split:
    ref = re.sub(';','\n',ref)
  # Converts Unicode to String
  ref = ref.encode()
  # Convert to title case
  ref = ref.title()

  # Count lines in ref
  lines = str.splitlines(ref)
  # Make list to spit multiple passages into
  fulltext = []
  # Make list for multiple book references
  books = []
  
  # Pick your desired Bible version & uncomment it
  #version = 'amp' # Amplified Version
  #version = 'akjv' # KJV Easy Read
  #version = 'asv' # American Standard Version
  #version = 'basicenglish' # Basic English Bible
  #version = 'darby' # Darby
  #version = 'kjv' # King James Version
  version = 'nasb' # New American Standard
  #version = 'wb' # Webster's Bible
  #version = 'web' # World English Bible
  #version = 'ylt' # Young's Literal Translation

  # Loop each reference and check book names to insure proper syntax
  for ref in lines:
    # Strip any blank spaces at front & back of ref
    ref = ref.strip()
    # If alpha characters in ref then we have a bible book in ref
    if re.search('[a-zA-Z]', ref):
      # Check book for syntax errors
      ref, book = check_book(ref)
      # Append book to list of books
      books.append(book)
    
    # If no letters in this ref...
    else:
      # Eliminate blank spaces in verse
      ref = ref.replace(' ','')
      # Add book from last ref that had a book
      ref = '{} {}'.format(books[len(books) - 1], ref)
    
    # Query passage
    t = passage_query(ref, version)
    # Uncomment to debug
    #print t
    # Pretty up query results
    bibletext = cleanup(t, ref, version)
    # Add markdown syntax to highlight verse ref
    bibletext = '**{} ({})** {}'.format(ref, version.upper(), bibletext)
    # Add scripture to list
    fulltext.append(bibletext)

  # Converts list to string
  fulltext = '\n\n'.join(fulltext)
  # Prepend verses and line feeds to scripture
  fulltext = '{}\n\n{}'.format(user_input, fulltext)
  fulltext = fulltext.encode()
  # Uncomment to debug
  #print fulltext

  # Return scripture to caller app, if any
  if app:
    url = get_url(app, fulltext)
    webbrowser.open(url)
  else:
    # Clear clipboard, then add formatted text
    clipboard.set('')
    clipboard.set(fulltext)
    print('''
The results of the scripture query are
shown below and copied to the clipboard
for pasting into the MD text editor or
journaling app of your choice.\n''')
    print fulltext

if __name__ == '__main__':
  try:
    ref = console.input_alert('Bible Verses', 'Please enter bible verse(s) in the following format: Luke 3:1-3,5,6;1 John 2:1-4,6 to query scripture and return desired passages:\n\n', '', 'Go').strip()
  except:
    # Cancel back to calling app if applicable
    try:
      app = sys.argv[1]
      webbrowser.open('{}://'.format(app))
      sys.exit()
    except:
      # Initiated stand alone so just exit
      sys.exit('Script cancelled!')

  main(ref)
