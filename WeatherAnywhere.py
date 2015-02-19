#coding: utf-8

# Name: WeatherAnywhere.py
# Author: John Coomler
# v1.0: 02/07/2015 to 02/15/2015-Created
'''
This script provides current and multi day
weather forecasts for any city you name,
or coordinates you are currently located
in, using the api available from
www.openweathermap.org. The inspiration
for this script came from https://
github.com/cclaus/
weather_where_you_are.py.

Print out current weather at your
current location. Display geared for
iPhone in portrait mode.
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
# Number of days in advaced forecast
day_count=7

def place():
	# Retrieve lat & lon from current locale
	location.start_updates()
	# Delay sometimes improves accuracy
	#time.sleep(1)
	address_dict = location.get_location()
	location.stop_updates()
	lat = address_dict['latitude']
	lon = address_dict['longitude']
	return lat,lon

def city_ids():
	count=0
	ids=[]
	try:
		# Open csv file in same folder as this script
		with open('cities.csv') as f:
			# Read each line and store in list
			csv_f=csv.reader(f)
			for row in csv_f:
				ids.append(row)
				count=count+1
				# Align number spacing neatly in our list of cities
				if count<10:
					sp='     '
				else:
					sp='    '
				# Print city & country
				print sp+str(count)+'. '+row[0]+', '+row[1]
	
		ans=int(raw_input('\nEnter number of desired city: '))
	
		# Retrive our data from proper row, subtract 1 for zero based array
		city,country,id=ids[ans-1]
	except Exception as e:
		console.clear()
		msg='Error: '+str(e)
		sys.exit(msg)
	return city,country,id

def api(latitude,longitude,city,id):
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
		fmt_url = 'weather?lat={0}&lon={1}&type=accurate&units=imperial'.format (latitude, longitude)
	
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
		fmt_url='forecast/daily?lat={0}&lon={1}&type=accurate&units=imperial&cnt={2}'.format(latitude, longitude,day_count)
	
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
	if deg>=0 and deg<11.25:
		dir='N'
	elif deg>=11.25 and deg<33.75:
		dir='NNE'
	elif deg>=33.75 and deg<56.25:
		dir='NE'
	elif deg>=56.25 and deg<78.75:
		dir='ENE'
	elif deg>=78.75 and deg<101.25:
		dir='E'
	elif deg>=101.25 and deg<123.75:
		dir='ESE'
	elif deg>=123.75 and deg<146.25:
		dir='SE'
	elif deg>=146.25 and deg<168.75:
		dir='SSE'
	elif deg>=168.75 and deg<191.25:
		dir='S'
	elif deg>=191.25 and deg<213.75:
		dir='SSW'
	elif deg>=213.75 and deg<236.25:
		dir='SW'
	elif deg>=236.25 and deg<258.75:
		dir='WSW'
	elif deg>=258.75 and deg<281.25:
		dir='W'
	elif deg>=281.25 and deg<303.75:
		dir='WNW'
	elif deg>=303.75 and deg<326.25:
		dir='NW'
	elif deg>=326.25 and deg<348.75:
		dir='NNW'
	elif deg>=348.75 and deg<=360:
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

def print_w(w):
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
	
	# Print the reformated data
	print('''Today's Weather in {name}:
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


def print_f(f):
	# Extended forecast
	sp='     '

	print 'Extended '+day_count+' Day Forecast for '+str(f['city']['name'])+':'
	
	# Loop thru each day
	for i in range(day_count):
		ico=str(f['list'][i]['weather'][0]['icon'])+'.png'
		try:
			#Open, resize and show weather icon
			img=Image.open(ico).resize((25,25),Image.ANTIALIAS)
			img.show()
		except:
			 missing_icons.append(ico)
			 # Leave space between forecasts
			 print ''
			 pass
		# Timestamp of forecast day formatted to m-d-y
		print 'Forecast for '+datetime.datetime.fromtimestamp(int(f['list'][i]['dt'])).strftime('%A %m-%d-%Y')
	
		# Capitalize weather description
		print sp+str.title(str(f['list'][i]['weather'][0]['description']))
	
		# Get type of preciptation
		precip_type=f['list'][i]['weather'][0]['main']
		# Get measured amts of precip
		if precip_type=='Rain' or precip_type=='Snow':
			try:
				# Convert precip amt to inches
				print sp+'Expected '+precip_type+' Vol for 3 hrs: '+precip_inch(f['list'][i][precip_type.lower()])+' in'
			except:
				# Sometimes precip amts aren't listed
				pass
		elif precip_type=='Clouds':
				print sp+'No Rain Expected'
		
		# Cloudiness percentage
		print sp+'Clouds: '+str(f['list'][i]['clouds'])+'%'
		
		# High temp rounded to whole number
		print sp+'High: '+str(round(float(f['list'][i]['temp']['max']),0))+'° F'
		
		# Low temp rounded the same
		print sp+'Low: '+str(round(float(f['list'][i]['temp']['min']),0))+'° F'
		
		# Humidity
		print sp+'Humidity: '+str(f['list'][i]['humidity'])+'%'
		
		# Pressure formatted to inches
		print sp+'Barometric Pressure: '+str(pressure_inhg(f['list'][i]['pressure']))+' in'
		
		# Wind direction and speed
		print sp+'Wind: '+str(wind_dir(f['list'][i]['deg']))+' @ '+str(wind_mph(f['list'][i]['speed']))+' mph'
		#print '\n'

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
			lat,lon=place()
		elif ans==2:
			# Enter a city & country
			msg='Enter a city and country in format "'"New York, US"'": '
			ans=console.input_alert(msg)
			if ans:
				console.clear()
				print 'Gathering weather data for '+str.title(ans)
				city=ans.replace(' ','+')
				lat=0
				lon=0
				id=''		
		elif ans==3:
			# Pick from list
			theCity,country,id=city_ids()
			console.clear()
			if id:
				print 'Gathering weather data for '+theCity+', '+country
				city=''
				lat=0
				lon=0		
	except Exception as e:
		msg='Error: '+str(e)
		sys.exit(msg)
	
	# Call api from www.openweathermap.org
	w,f=api(lat,lon,city,id)
	
	console.clear()
	# Print current conditions to console
	print_w(w)
	# Print extended forecast to console
	print_f(f)
	
	print '\nWeather information provided by openweathermap.org'
	if missing_icons:
		print '\n*Some or all weather icons are missing. There are 18 in all but some are duplicates and not needed. Make sure all needed icons are in the same folder as this script. Weather icons are available at http://www.openweathermap.org/weather-conditions'
	
if __name__ == '__main__':
	main()
