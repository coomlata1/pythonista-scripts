# coding: utf-8
'''
BibleVerses.py
@coomlata1

This Pythonista script will retrieve any bible
verse or verses and copy them to the clipboard or
1Writer, Editorial, or Drafts via a url. The script
uses the getBible.net api as the query source for
scripture. More info is available at https://
getbible.net/api.

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
  Book or multiple books:
    Matthew
    Luke;Mark
  Chapters or multiple chapters:
    Luke 3;Mark 4
    Luke 3;4
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

Examples:
    Luke 2;4;1:2-7,9
      This would return Chapters 2 & 4 of Luke;
      Chapter 1 verses 2 to 7 & verse 9 from Luke

    Matthew 1:2-8;5;Genesis 1;3:4-8;6:2;Mark
      This would return Matthew chapter 1; Matthew
      chapter 2 verses 2 to 8; Matthew chapter 5;
      Genesis chapter 1; Genesis chapter 3 verses 4
      to 8; Genesis chapter 6 verse 2; the entire
      book of Mark.

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
import difflib

def passage_query(ref, version):
  ref = ref.replace(' ','%20')
  url = 'https://getbible.net/json?p={}&v={}'.format(ref, version)
  r = requests.get(url)
  t = r.text
  return t

def check_book(ref, err):
  books = ['1 Chronicles', '1 Corinthians', '1 John', '1 Kings', '1 Peter',
'1 Samuel', '1 Thessalonians', '1 Timothy', '2 Chronicles', '2 Corinthians',
'2 John', '2 Kings', '2 Peter', '2 Samuel', '2 Thessalonians', '2 Timothy',
'3 John', 'Acts', 'Amos', 'Colossians', 'Daniel', 'Deuteronomy', 'Ecclesiastes',
'Ephesians', 'Esther', 'Exodus', 'Ezekiel', 'Ezra' 'Galatians', 'Genesis',
'Habakkuk', 'Haggai', 'Hebrews', 'Hosea', 'Isaiah', 'James', 'Jeremiah', 'Job',
'Joel', 'John', 'Jonah', 'Joshua', 'Jude', 'Judges', 'Lamentations', 'Leviticus',
'Luke', 'Malachi', 'Mark', 'Matthew', 'Micah', 'Nahum', 'Nehemiah', 'Numbers',
'Obadiah', 'Philemon', 'Philippians', 'Proverbs', 'Psalms', 'Revelation',
'Romans', 'Ruth', 'Song of Solomon', 'Titus', 'Zechariah', 'Zephaniah']

  book = ''

  '''
  Make sure we have space between end of book name
  and chapter number and fix if necessary.  Loop
  backwards through each character in ref.
  '''
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
  # Check for spelling...return the closest match
  the_book = difflib.get_close_matches(book, books, 1)

  # Convert list to text and strip out white spaces
  try:
    the_book = the_book[0].title().replace(' ', '')
  except IndexError:
    err = True
    the_book = book

  verses = ref[pos + 1:].strip().replace(' ','')

  # If verse has no colon, but contains a dash...
  if not ':' in verses and '-' in verses:
    # Syntax error
    err = True

  if not err:
    # Add unwhitened book & verses back to ref
    ref = '{} {}'.format(the_book, verses)
  return ref, the_book, err

def replace_all(t, dic):
  for j, k in dic.iteritems():
    t = t.replace(j, k)
  return t

def cleanup(t, ref, version):
  if ':' in ref:
    verses_in_ref = True
    # Chapter number is between space and colon
    chapter = ref[ref.find(' ') + 1:ref.find(':')]
    # If comma(s) in ref
    if ',' in ref:
      # First passage is between colon & 1st comma
      fp = ref[ref.find(':') + 1:ref.find(',')].strip()
      # Last passage is between last comma and end
      lp = ref[ref.rfind(',', 0, len(ref)) + 1:].strip()

      # If dash in first passage
      if '-' in fp:
        # First verse between colon & dash
        first_verse = fp[fp.find(':') + 1:fp.find('-')].strip()
      else:
        # No dash so first verse is first passage
        first_verse = fp

      # If dash in last passage
      if '-' in lp:
        # Last verse is everything after dash
        last_verse = lp[lp.find('-') + 1:].strip()
      else:
        # No dash so last verse is last passage
        last_verse = lp
    # No commas in ref
    else:
      # If dash in ref
      if '-' in ref:
        # First verse is between colon & dash
        first_verse = ref[ref.find(':') + 1:ref.find('-')].strip()
        # Last verse is everything after dash
        last_verse = ref[ref.find('-') + 1:].strip()
      else:
        # First verse & last verse are same...everything after colon
        first_verse = ref[ref.find(':') + 1:].strip()
        last_verse = first_verse
  else:
    verses_in_ref = False
    if ' ' in ref:
      book = ref[:ref.find(' ')].strip()
      chapter = ref[ref.find(' ') + 1:]
    else:
      book == ref
      chapter == ''

  # Create dictionaries to clean up passages
  dic_c = {'{':'', '}':'', '"':'', '\\':'', '*': ''}
  dic_w = {'verse:':'', ':verse_nr:':'verse '}

  # Replace unwanted characters
  t = replace_all(t, dic_c)
  # Replace unwanted words
  t = replace_all(t, dic_w)

  # More cleaning...
  if verses_in_ref:
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
  else:
    first_verse = 1
    # Covers Psalms 119, the largest chapter in Bible
    last_verse = 176

    for i in range(int(last_verse)):
      t = t.replace(',{0}verse {0},'.format(i + 1),' [{}] '.format(i + 1))

      t = t.replace(',{0}:chapter_nr:{0},chapter:1verse 1,'.format(i + 1), '\n\n**[{}:1]** '.format(i + 1))

    # With book & chapter
    if len(chapter) != 0:
      t = t.replace('chapter:1verse 1,', ' [{}:1] '.format(chapter))
      header_end_pos = t.find('[{}:1]'.format(chapter))
    else:
      # With book only
      t = t.replace('1:chapter_nr:1,chapter:1verse 1,', ' [1:1] ')
      header_end_pos = t.find('[1:1]')

    header = t[:header_end_pos]
    t = t.replace(header, '')

  t = t.replace('\\', '')
  return t

def get_url(app, fulltext):
  if app == 'drafts4':
    # Write scripture to new draft
    #url = '{}://x-callback-url/create?text={}'.format(app, urllib.quote(fulltext))

    # Append scripture to existing open draft
    fmt = '{}://x-callback-url/append?uuid={}&text={}'
    url = fmt.format(app, sys.argv[2], urllib.quote(fulltext))
  elif app == 'onewriter':
    # Append scripture to open 1Writer doc
    fmt = '{}://x-callback-url/append?path=/Documents%2F&name=Notepad.txt&type=Local&text={}'
    url = fmt.format(app, urllib.quote(fulltext))
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
  '''
  Allow to run script stand alone or from another
  app using command line arguments via URL's.
  '''
  try:
    app = sys.argv[1]
  except IndexError:
    app = ''

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
  # Make list for multiple books
  books = []

  # List of Bible versions
  versions = 'amp akjv asv basicenglish darby kjv nasb wb web ylt'.split()

  # Pick your desired Bible version by number
  #0 = amp...Amplified Version
  #1 = akjv...KJV Easy Read
  #2 = asv...American Standard Version
  #3 = basicenglish...Basic English Bible
  #4 = darby...Darby
  #5 = kjv...King James Version
  #6 = nasb...New American Standard Bible
  #7 = wb...Webster's Bible
  #8 = web...World English Bible
  #9 = ylt...Young's Literal Translation

  # Change number to match desired version
  version = versions[6]

  # Loop each reference and check book names to insure proper syntax and spelling
  for ref in lines:
    # Default for error flag
    err = False
    # Strip any blank spaces at front & back of ref
    ref = ref.strip()
    # If alpha characters in ref then we have a bible book in ref
    if re.search('[a-zA-Z]', ref):
      # Check book for syntax & spelling errors
      ref, book, err = check_book(ref, err)
      # Append book to list of books
      books.append(book)

    # If no letters in this ref...
    else:
      # Eliminate blank spaces in verse
      ref = ref.replace(' ','')
      # Add book from last ref that had a book
      try:
        ref = '{} {}'.format(books[len(books) - 1], ref)
        # Check syntax
        ref, book, err = check_book(ref, err)
      except IndexError:
        err = True

    err_msg = 'No scripture found for "{}"...Check syntax.'.format(ref)

    if not err:
      # Query passage
      console.hud_alert('Querying For {}...'.format(ref))
      t = passage_query(ref, version)
      # If query returned scripture...
      if t != 'NULL':
        # Pretty up query results
        bibletext = cleanup(t, ref, version)
      else:
        bibletext = err_msg
    else:
      bibletext = err_msg
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
    msg = 'Please enter bible verse(s) in the following format: Luke 3:1-3,5,6;1 John 2:1-4,6 to query scripture and return desired passages:\n\n'
    ref = console.input_alert('Bible Verses', msg, '', 'Go').strip()
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
