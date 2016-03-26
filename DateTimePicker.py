# coding: utf-8
'''
#---Script: DateTimePicker.py
#---Author: @coomlata1
#---Created: 03/23/16
#---Last Modified: 03/25/2016 @ 07:14PM

Script allows the selection of any date, time, or combination
therein using the Datepicker ui view. This works well for
logging entries in a diary or journal. The script can be run
stand alone or it can be called from apps such as 1Writer and
Drafts using their respective URL schemes as shown below.

Drafts: 'pythonista://DateTimePicker&action=run&argv=drafts4&argv=[[uuid]]'

1Writer:'pythonista://DateTimePicker?action=run&argv=onewriter'
'''
import ui
import datetime
import clipboard
import webbrowser
import sys

def change_date(self):
  # Sync label text with date picker to match selected date & time options
  the_date = self.date
  if not date_only.value and not time_only.value:
    # Format 'Wednesday Jan 1, 2016 03:15:00PM'
    the_date = the_date.strftime('%A %b %d, %Y %I:%M:%S%p')
  elif date_only.value:
    # Format 'Wednesday Jan 1, 2016'
    the_date = the_date.strftime('%A %b %d, %Y')
  elif time_only.value:
    # Format '03:15:00PM'
    the_date = the_date.strftime('%I:%M:%S%p')
  lbl.text = str(the_date)
  return str(the_date)

def date_toggled(self):
  if date_only.value:
    time_only.value = False
    # Pick dates only
    dp.mode = ui.DATE_PICKER_MODE_DATE
    lbl.text = change_date(dp)
  else:
    if time_only.value == False:
      # Pick date and time
      dp.mode = ui.DATE_PICKER_MODE_DATE_AND_TIME
      lbl.text = change_date(dp)

def time_toggled(self):
  if time_only.value:
    date_only.value = False
    # Pick times only
    dp.mode = ui.DATE_PICKER_MODE_TIME
    lbl.text = change_date(dp)
  else:
    if date_only.value == False:
      dp.mode = ui.DATE_PICKER_MODE_DATE_AND_TIME
      lbl.text = change_date(dp)

# Load pyui file
v = ui.load_view('date_time_picker')
v.background_color = 'cyan'

date_only = v['date_only']
time_only = v['time_only']

date_only.value = False
time_only.value = False

dp = v['datepicker1']
lbl = v['label1']

# Sync label display with date picker
lbl.text = change_date(dp)

# Display ui locked in portrait orientation and wait till user selects something from it.
v.present(orientations = ['portrait'])
v.wait_modal()

date_time = lbl.text

# Send date_time text to clipboard
clipboard.set('')
clipboard.set(date_time)
'''
Allow to run script stand alone or from another
app using command line arguments via URL's.
'''
try:
  # No error if this script was called from a app using URL
  app = sys.argv[1]

  if app == 'onewriter':
    import urllib
    quoted_output = urllib.quote(date_time, safe = '')
    cmd = 'onewriter://x-callback-url/append?path=/Documents%2F&name=Notepad.txt&type=Local&text={}'.format(quoted_output)
  elif app == 'drafts4':
    '''
    Append nothing to open Draft doc using the 2nd
    argument from calling URL as the UUID of the
    open doc and then run a Drafts action to copy contents
    of clipboard to open draft at the cursor position. If
    any text is appended to open draft it is inserted at the
    bottom of the existing text. I prefer to insert the text at
    the cursor, which requires the Drafts action
    'ClipboardAtCursor' available at 'https://drafts4-actions.agiletortoise.com/a/1j7'
    '''
    cmd = 'drafts4://x-callback-url/append?uuid={}&text={}&action=ClipboardAtCursor'.format(sys.argv[2],'')
  else:
    cmd = '{}://'.format(app)

  webbrowser.open(cmd)
  msg = 'Back to caller app, {}.'.format(app)
  sys.exit(msg)
except IndexError:
  # Initiated stand alone so just display results &  exit
  print 'Date-Time Selected: {}\n'.format(date_time)
  sys.exit('Finished')
