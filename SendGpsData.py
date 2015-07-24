# coding: utf-8
'''
SendGpsData.py

A Pythonista script for texting your GPS location &
current weather using clipboard, email, or SMS
messaging. Requires Launch Center Pro to provide
ability to email and SMS msg the text. The script
can be run stand alone from Pythonista or be
called from 1Writer, Editorial, or Drafts via a
URL, in which case the text will be appended to the
caller's open doc for use in journaling, logs, etc.

Examples of the calling URLs:
From 1Writer: pythonista://{{SendGpsData.py}}?action=run&argv={{onewriter}}
From Editorial: pythonista://SendGpsData.py?action=run&argv=editorial
From Drafts: pythonista://SendGpsData.py?action=run&argv=drafts4&argv=[[uuid]]

Used code and ideas from:
  location.py at:
  https://gist.github.com/drdrang/8329584

  insert_location.py at:
  https://gist.github.com/hiilppp/8268816

  gps.py at:
  https://gist.github.com/n8henrie/60b2e9390355bc8e24dd

  py_forecast.py at:
  https://gist.github.com/miklb/8346411

Many thanks to @drdrang, @hiilppp, @n8henrie, and
@miklb for their inspiration.
'''
import location
import time
import console
import datetime
import webbrowser
import urllib
import sys
import json
import requests
import clipboard

console.clear()
console.show_activity()

# Initialize global variables
arg = ''
quoted_output = ''
output = ''
cmd = ''

# Procedure for getting weather from lat & lon
def get_weather(lat, lon, bold):
  err = ''
  '''
  You will need an to replace the empty quotes
  below with an API key to get weather data.
  Register for your free key at
  http://www.wunderground.com
  '''
  api_key = ''

  # Change to 'metric' if desired
  imperial_or_metric = 'imperial'

  # Conversion units
  if imperial_or_metric == 'imperial':
    unit = 'f'
  else:
    unit = 'c'

  url_fmt = 'http://api.wunderground.com/api/{}/{}/q/{}.json'

  # Weather from where you are now
  fmt = '{},{}'
  query = fmt.format(lat, lon)

  w_url = url_fmt.format(api_key, 'conditions/', query)

  try:
    w = requests.get(w_url).json()
    #import pprint;pprint.pprint(w)

  # Servers down or no internet
  except requests.ConnectionError:
    err = True
    w_data = '\n\nWeather servers are busy. Try again in a few minutes...'

  # If no errors...continue
  if not err:
    try:
      current = w['current_observation']
    # If no api key...
    except KeyError:
      err = True
      w_data = '\n\nNo weather data was returned. You will need to register for a free API key @  http://www.wunderground.com to access the weather stats.'
    # And on we go...
    if not err:
      # Apply conversion units to temperature
      temp = int(current['temp_' + unit])
      temp = '{}°{}'.format(temp, unit.title())

      current_weather = w['current_observation']['weather'].lower()
      humidity = w['current_observation']['relative_humidity']

      w_data = '\n\nCurrent weather here is {}{}{}, {}{}{}, with {}{} humidity{}.'.format(bold, current_weather, bold, bold, temp, bold, bold, humidity, bold)

  return w_data

# Procedure to return to calling apps
def do_args(arg, quoted_output, output):
  if not quoted_output:
    cmd = '{}://x-callback-url/'.format(arg)
  else:
    if arg == 'onewriter':
      cmd = '{}://x-callback-url/append?path=Documents%2F&name=Notepad.txt&type=Local&text={}'.format(arg, quoted_output)
    if arg == 'editorial':
      clipboard.set('')
      clipboard.set(output)
      cmd = "{}://?command=Append%20Open%20Doc".format(arg)
    if arg == 'drafts4':
      '''
      Append gps data to open Draft doc using the
      2nd argument from calling URL as the UUID of
      the open doc
      '''
      cmd = 'drafts4://x-callback-url/append?uuid={}&text={}'.format(sys.argv[2], quoted_output)

  webbrowser.open(cmd)
  sys.exit('Finished!')

def main():
  # Allow to run script stand alone
  try:
    arg = sys.argv[1]
  except IndexError:
    arg = ''

  print '\nThis script is now gathering your current GPS coordinates, allowing you to text your location and current weather.\n'

  # Start getting the location
  location.start_updates()

  for i in range(4):
    time.sleep(5)
    my_loc = location.get_location()
    acc = my_loc['horizontal_accuracy']

    # First run
    if i == 0:
      best_loc = my_loc
      best_acc = my_loc['horizontal_accuracy']

      # Setup alert box
      title = 'Accuracy: {} meters.'.format(acc)
      msg = "Take more time to try to improve accuracy?"
      butt1 = "Good enough."
      butt2 = "Try harder (~25 secs)."
      # Allow a cancel
      try:
        answer = console.alert(title, msg, butt1, butt2)
      except:
        console.clear()
        # Call procedure if script called from another app
        if arg:
          do_args(arg, quoted_output, output)
        else:
          sys.exit('Cancelled')

      # If initial accuracy is good enough, give user the chance to break
      if answer == 1:
        break

      # If initial accuracy is not good enough, loop 4 more times and try to improve.
      elif answer == 2:
        pass

    if acc < best_acc:
      best_loc = my_loc
      best_acc = my_loc['horizontal_accuracy']

    print('Best accuracy is now {} meters.'.format(best_acc))

  location.stop_updates()

  lat = best_loc['latitude']
  lon = best_loc['longitude']

  # Setup alert box
  title = 'Select Type of GPS Data To Send:'
  butt1 = "Address"
  butt2 = "Coordinates"

  # Allow a cancel
  try:
    ans = console.alert(title,'', butt1, butt2)
  except:
    console.clear()
    # Call procedure if script called from another app
    if arg:
      do_args(arg, quoted_output, output)
    else:
      sys.exit('Cancelled')

  # Set up for Markdown if called from apps
  if arg:
    bold = '**'
  else:
    bold = ''

  w_data = get_weather(lat, lon, bold)

  if ans == 1:
    data_type = 'address was'
    a = location.reverse_geocode({'latitude': lat,'longitude': lon})

    b = '{}{}, {} {} {}{}, {}'.format(bold, a[0]['Street'], a[0]['City'], a[0]['State'], a[0]['ZIP'], bold, a[0]['Country'])

    datestamp = datetime.datetime.fromtimestamp(best_loc['timestamp'])
    d = datestamp.strftime('%m-%d-%Y @ %I:%M:%S %p')

    output = 'My location as of {} is {}, with an accuracy of about {} meters.'.format(d, b, str(best_acc))

  if ans == 2:
    data_type = 'coordinates were'
    output = 'Click on http://maps.apple.com/?q={},{} for a map to my current location.'.format(str(lat), str(lon))

  quoted_output = urllib.quote(output + w_data, safe = '')

  # Call procedure if script called from another app
  if arg:
    do_args(arg, quoted_output, output + w_data)

  # Setup alert box if called as stand alone script
  title = 'Send Your GPS & Weather Data To:'
  butt1 = "Clipboard"
  butt2 = "SMS msg"
  butt3 = "Email"

  # Allow a cancel
  try:
    ans = console.alert(title, '', butt1, butt2, butt3)
  except:
    console.clear()
    sys.exit('Cancelled')

  if ans == 1:
    clipboard.set('')
    clipboard.set(output)
    console.clear()
    print 'Your GPS {} copied to the clipboard.'.format(data_type)

  if ans == 2:
    cmd = 'launch://messaging?body={}'.format(quoted_output)
    webbrowser.open(cmd)
    console.clear()

  if ans == 3:
    cmd = 'launch://email?body={}'.format(quoted_output)
    webbrowser.open(cmd)
    console.clear()

  sys.exit('Finished!!')

if __name__ == '__main__':
  main()
