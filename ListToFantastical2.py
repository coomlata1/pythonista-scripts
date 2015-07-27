#coding: utf-8
'''
ListToFantastical2.py

Parses BOTH reminders and events from comma
seperated text passed from URL's in LCP, 1Writer,
or Drafts and posts them in Fantastical.

Thanks to Fantastical's natural language parsing,
your 'tasks' can be reminders or events.  The
reminders must start with a 'Task', 'Todo',
'Reminder', or 'Remind me' pre-text followed by the
todo itself.  Events don't need the pre-text. For
more on this see:
   http://www.geekswithjuniors.com/note/5-awesome-things-from-fantastical-2-that-can-improve-your-wo.html
and:
   http://plobo.net/recursive-actions-with-launchcenterpro-and-pythonista
for well documented intros to the proper syntax.

Example caller URL's:
  1Writer:
    pythonista://ListToFantastical2?action=run&argv=[text]&argv=onewriter
  Drafts:
    pythonista://ListToFantastical2?action=run&argv=[[draft]]&argv=drafts4
  LCP:
    pythonista://{{ListToFantastical2}}?action=run&argv=[prompt-list:Enter Todos, Reminders, Events:]&argv=launch

Credit Due:
list2Fantastical.py
https://gist.github.com/pslobo/25af95742e1480210e2e
Thanks to @pslobo for his contribution to GitHub
'''
import urllib2
import webbrowser
import sys

'''
The first arg is a comma seperated list of items
received from user input prompt in LCP or comma
separated text in 1Writer, or Drafts. The second
arg is the caller app.
'''
try:
  tasks = sys.argv[1]
  caller = sys.argv[2]
except IndexError:
  sys.exit('Error: Command line args are missing.')

# Initialize the x-callback-url
url_str = ''
'''
Default is for any added tasks to be saved
automatically. Set the 'save' variable to '0' to
manually save or cancel each new task as it is
being processed in Fantastical.
'''
save = '1'

# Split the list by commas and iterate over each resulting item
for task in tasks.split(','):
  '''
  Check to see if there is already an item in the
  x-callback-url. If not, create it, allowing for a
  return to calling app, which is argv[2], upon
  success. If there is, then add task_str + &x
  success followed by the URL-encoded url_str. This
  respects the needed encoding of nested.
  '''
  if url_str == '':
    url_str += 'fantastical2://x-callback-url/parse?sentence={}&add={}&x-success={}://'.format(urllib2.quote(task,''), save, caller)

  else:
    url_str = 'fantastical2://x-callback-url/parse?sentence={}&add={}&x-success={}'.format(urllib2.quote(task,''), save, urllib2.quote(url_str,''))

# Check to see if Fantastical is installed and open the URL if it is.
if webbrowser.can_open("fantastical2://"):
  webbrowser.open(url_str)
else:
  print "Fantastical not installed"
