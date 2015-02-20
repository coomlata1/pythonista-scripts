#coding: utf-8

# Name: WeatherAnywhere.py
# Author: John Coomler
# v1.0: 02/07/2015 to 02/15/2015-Created
# v1.1: 02/19/2015-Tightened up code and
# made function calls to retrieve weather
# data for printing from main(). Many
# thanks to @cclauss for his continued
# expertise, input, & support in sorting
# out and improving the code.
'''
This script provides current and multi day
weather forecasts for any city you name,
or coordinates you are currently located
in, using the api available from
www.openweathermap.org. The inspiration
for this script came from https://
github.com/cclaus/weather_where_you_are/
weather_where_you_are.py. The conversion
functions used here were found at http://
jim-easterbrook.github.io/pywws/doc/en/
html/_modules/pywws/conversions.html
'''
import location
import requests
#import time
import datetime
import console
import sys
import csv
from PIL import Image

# Global variables
missing_icons=[]
icons=[]
# Number of days in advaced forecast
day_count=7

def get_current_lat_lon():
	# Retrieve lat & lon from current locale
	location.start_updates()
	# Delay sometimes improves accuracy
	#time.sleep(1)
	address_dict = location.get_location()
	location.stop_updates()
	lat = address_dict['latitude']
	lon = address_dict['longitude']
	return lat,lon

def city_ids(filename='cities.csv'):
	try:
		with open(filename) as in_file:
			ids = [row for row in csv.reader(in_file)]
	except IOError as e:
		sys.exit('IOError in city_ids(): {}'.format(e))
	if not ids:
		sys.exit('No cities found in: {}'.format(filename))
	for i, id in enumerate(ids):
		print('{:>7}. {}, {}'.format(i, id[0], id[1]))
	while True:
		try:
			ans = int(raw_input('\nEnter number of desired city: '))
			city, country, id = ids[ans]
			return city, country, id
		except (IndexError, ValueError):
			pass
			print('Please enter a vaild number.')

def get_weather_dicts(lat,lon,city,id):
	base_url='http://api.openweathermap.org/data/2.5/'
	
	# Current weather conditions
	if city:
		# From entered city
		fmt_url = 'weather?q='+city+'&type=accurate&units=imperial'
	elif id:
		# From list
		fmt_url = 'weather?id='+id+'&type=accurate&units=imperial'
	else:
		# From where you are now
		fmt_url = 'weather?lat={0}&lon={1}&type=accurate&units=imperial'.format (lat,lon)
	
	url=base_url+fmt_url
	try:
		w = requests.get(url).json()
		#import pprint;pprint.pprint(w)
		#See: http://bugs.openweathermap.org/projects/api/wiki
		#sys.exit()
	except:
		console.clear()
		sys.exit('Weather servers are busy. Try again in 5 minutes...')
	
	# Extended forecast
	if city:
		# From an entered city
		fmt_url = 'forecast/daily?q='+city+'&units=imperial&cnt={}'.format(day_count)
	elif id:
		# From list
		fmt_url = 'forecast/daily?id='+id+'&units=imperial&cnt={}'.format(day_count)
	else:
		# From where you are now
		fmt_url='forecast/daily?lat={0}&lon={1}&type=accurate&units=imperial&cnt={2}'.format(lat,lon,day_count)
	
	url=base_url+fmt_url
	
	try:
		f=requests.get(url).json()
		#import pprint;pprint.pprint(f)
		#sys.exit()
	except:
		console.clear()
		sys.exit('Weather servers are busy. Try again in a minute...')
	
	return w,f

def precip_inch(mm):
	# Convert rain or snowfall from mm to in
	return str(round(float(mm/25.4),2))

def wind_dir(deg):
	# Convert degrees to wind direction
	if 0<=deg<11.25:
		dir='N'
	elif 11.25<=deg<33.75:
		dir='NNE'
	elif 33.75<=deg<56.25:
		dir='NE'
	elif 56.25<=deg<78.75:
		dir='ENE'
	elif 78.75<=deg<101.25:
		dir='E'
	elif 101.25<=deg<123.75:
		dir='ESE'
	elif 123.75<=deg<146.25:
		dir='SE'
	elif 146.25<=deg<168.75:
		dir='SSE'
	elif 168.75<=deg<191.25:
		dir='S'
	elif 191.25<=deg<213.75:
		dir='SSW'
	elif 213.75<=deg<236.25:
		dir='SW'
	elif 236.25<=deg<258.75:
		dir='WSW'
	elif 258.75<=deg<281.25:
		dir='W'
	elif 281.25<=deg<303.75:
		dir='WNW'
	elif 303.75<=deg<326.25:
		dir='NW'
	elif 326.25<=deg<348.75:
		dir='NNW'
	elif 348.75<=deg<=360:
		dir='N'
	return dir

def wind_mph(mps):
	# Convert wind from meters/sec to mph
	return str(round(float(mps*3.6/1.609344),0))

def wind_chill(temp,wind):
	'''
	Compute wind chill using formula from
	http://en.wikipedia.org/wiki/wind_chill
	'''
	temp=float(temp)
	wind=float(wind)
	if wind<=3 or temp>50:
		return temp
	return str(round(float(min(35.74+(temp*0.6215) + (((0.3965*temp)-35.75)*(wind**0.16)),temp)),0))

def pressure_inhg(hPa):
	# Convert pressure from hectopascals/millibar to inches of mecury
	return str(round(float(hPa/33.86389),2))

def Timer(start, end):
	"""
	Calculates the time it takes to run
	process, based on start and finish
	"""
	elapsed = end - start
	# Convert process time, if needed
	if elapsed < 60:
		time = str(round(elapsed,2)) + " seconds\n"
	
	if 60 <= elapsed <= 3599:  # ccc: slightly faster to state the variable only once
		min = elapsed / 60
		time = str(round(min,2)) + " minutes\n"
	
	if elapsed >= 3600:        # ccc: what happens if elapsed is 3591, 3592, 3593, etc.?
		hour = elapsed / 3600
		time = str(round(hour,2)) + " hours\n"
	
	return time


def get_current_weather(w):
	# Current weather conditions
	#for item in ('temp_min', 'temp_max'):
		#if item not in w['main']:
			#w['main'][item] = None # create values if they are not present
	
	#if 'weather' not in w:
		#w['weather']=[{'description' : 'not available'}]
	
	# Round current temp to whole number
	w['main']['temp']=str(round(float(w['main']['temp']),0))
	
	# Pressure & convert to inches
	w['main']['pressure']=pressure_inhg(w['main']['pressure'])
	
	# Capitalize weather description
	w['weather'][0]['description']=str.title(str(w['weather'][0]['description']))
	
	# Conver wind degrees to wind direction
	w['wind']['deg']=wind_dir(w['wind']['deg'])
	
	# Convert wind speed to mph
	w['wind']['speed']=wind_mph(w['wind']['speed'])
	
	# Get wind chill factor using temp & wind speed
	chill=wind_chill(w['main']['temp'],w['wind']['speed'])
	
	try:
		# Get wind gusts and covert to mph, although they aren't always listed'
		w['wind']['gust']=float(wind_mph(w['wind']['gust']))+float(w['wind']['speed'])
		gusts='Gusts to '+w['wind']['gust']
	except:
		gusts=''
	# Convert timestamp to date of weather
	w['dt']=datetime.datetime.fromtimestamp(int(w['dt'])).strftime('%A\n  %m-%d-%Y @ %I:%M %p:')
	# Do same for sunrise,sunset timestamps
	
	for item in ('sunrise', 'sunset'):
		w['sys'][item]=datetime.datetime.fromtimestamp(int(w['sys'][item])).strftime('%I:%M %p')
	
	# Find icon name in data
	ico=w['weather'][0]['icon']+'.png'
	#Open, resize and show weather icon
	try:
		i=Image.open(ico).resize((25,25),Image.ANTIALIAS)
		i.show()
	except:
		# Maybe no icons or some missing
		missing_icons.append(ico)
		# Don't stop the show for missing icons
		pass
	
	# Return the reformated data
	weather=('''Today's Weather in {name}:\n
  Current Conditions for {dt}
  	{weather[0][description]}
  	Clouds: {clouds[all]}%
  	Temperature: {main[temp]}° F
  	Humidity: {main[humidity]}%
  	Barometric Pressure: {main[pressure]} in
  	Wind: {wind[deg]} @ {wind[speed]} mph {}
  	Feels Like: {}° F
  	Sunrise: {sys[sunrise]}
  	Sunset: {sys[sunset]}\n'''.format(gusts,chill,**w))
	return weather

def get_forecast(f):
	# Extended forecast
	sp='     '

	forecast= 'Extended '+str(day_count)+' Day Forecast for '+str(f['city']['name'])+':\n'
	
	# Loop thru each day
	for i in range(day_count):
		ico=str(f['list'][i]['weather'][0]['icon'])+'.png'
		icons.append(ico)
		
		# Timestamp of forecast day formatted to m-d-y
		forecast=forecast+'\nForecast for '+datetime.datetime.fromtimestamp(int(f['list'][i]['dt'])).strftime('%A %m-%d-%Y')
	
		# Capitalize weather description
		forecast=forecast+'\n'+sp+str.title(str(f['list'][i]['weather'][0]['description']))
	
		# Get type of preciptation
		precip_type=f['list'][i]['weather'][0]['main']
		# Get measured amts of precip
		if precip_type=='Rain' or precip_type=='Snow':
			try:
				# Convert precip amt to inches
				forecast=forecast+'\n'+sp+'Expected '+precip_type+' Vol for 3 hrs: '+precip_inch(f['list'][i][precip_type.lower()])+' in'
			except:
				# Sometimes precip amts aren't listed
				pass
		elif precip_type=='Clouds':
				forecast=forecast+'\n'+sp+'No Rain Expected'
		
		# Cloudiness percentage
		forecast=forecast+'\n'+sp+'Clouds: '+str(f['list'][i]['clouds'])+'%'
		
		# High temp rounded to whole number
		forecast=forecast+'\n'+sp+'High: '+str(round(float(f['list'][i]['temp']['max']),0))+'° F'
		
		# Low temp rounded the same
		forecast=forecast+'\n'+sp+'Low: '+str(round(float(f['list'][i]['temp']['min']),0))+'° F'
		
		# Humidity
		forecast=forecast+'\n'+sp+'Humidity: '+str(f['list'][i]['humidity'])+'%'
		
		# Pressure formatted to inches
		forecast=forecast+'\n'+sp+'Barometric Pressure: '+str(pressure_inhg(f['list'][i]['pressure']))+' in'
		
		# Wind direction and speed
		forecast=forecast+'\n'+sp+'Wind: '+str(wind_dir(f['list'][i]['deg']))+' @ '+str(wind_mph(f['list'][i]['speed']))+' mph'
		forecast=forecast+'\n'
		
	return forecast

def main():
	console.clear()
	# Pick a weather source
	try:
		ans=console.alert('Choose Your Weather Source:','','From Your Current Location','From Entering a City Name','From A Pick List of Cities')
		if ans==1:
			# Weather where you are
			print 'Gathering weather data from where you are...'
			city=''
			country=''
			id=''
			# Get lat & lon of where you are
			lat,lon=get_current_lat_lon()
		elif ans==2:
			# Enter a city & country
			msg='Enter a city and country in format "'"New York, US"'": '
			ans=console.input_alert(msg)
			if ans:
				#console.clear()
				print('='*20)
				print 'Gathering weather data for '+str.title(ans)
				city=ans.replace(' ','+')
				lat=0
				lon=0
				id=''		
		elif ans==3:
			# Pick from list
			theCity,country,id=city_ids()
			#console.clear()
			print('='*20)
			if id:
				print 'Gathering weather data for '+theCity+', '+country
				city=''
				lat=0
				lon=0		
	except Exception as e:
		msg='Error: '+str(e)
		sys.exit(msg)
	
	# Call api from www.openweathermap.org
	w,f=get_weather_dicts(lat,lon,city,id)
	
	#start = time.clock()
	#console.clear()
	print('='*20)
	# Print current conditions to console
	print(get_current_weather(w))
	'''
	Printing the extended forecast to the
	console involves a bit more code because
	we are inserting a weather icon at each
	blank line.
	'''
	extended_f=get_forecast(f).split('\n')
	count=0
	for line in extended_f:
		'''
		Look for blank lines and don't exceed
		the number of forecasted days -1 for
		zero base in array holding icon names
		'''
		if not line and count<=(day_count-1):
			ico=icons[count]
			try:
				# Open, resize and show weather icon
				img=Image.open(ico).resize((25,25),Image.ANTIALIAS)
			
				img.show()
			except:
			 	missing_icons.append(ico)
			 	pass
			count=count+1
		print line
	
	print 'Weather information provided by openweathermap.org'
	if missing_icons:
		print '\n*Some or all weather icons are missing. There are 18 in all but some are duplicates and not needed. Make sure all needed icons are in the same folder as this script. Weather icons are available at http://www.openweathermap.org/weather-conditions'
	
	#finish = time.clock()
	#print Timer(start, finish)

if __name__ == '__main__':
	main()
