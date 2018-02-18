# coding: utf-8
'''
#---Filename: TimeClock.py
#---Author: coomlata1
#---Created: 02-17-2018
#---Last Updated: 02-18-2018

#---Description: Calculates the time elapsed between
two user selected times. Ideal for calculating hours
in shift work. Code includes time deductions for
lunches if applicable.

#---Contributors: Time arithmetic info gathered from:
https://stackoverflow.com/questions/3096953/how-to-
calculate-the-time-interval-between-two-time-strings

https://stackoverflow.com/questions/46402022/subtract-
hours-and-minutes-from-time
'''
import ui
import datetime
from datetime import timedelta
import time

# Action for Start Time DatePicker
def change_start_time(self):
  # Sync label text with DatePicker to match selected start time
  lbl_pick_start.text = self.date.strftime('%I:%M %p')

# Action for End Time TimePicker
def change_end_time(self):
  # Sync label text with DatePicker to match selected end time
  lbl_pick_end.text = self.date.strftime('%I:%M %p')
  
# Action for title bar 'Select' button on ui DatePicker title  bar
def select(self):
  # Formst for 12 hour clock with AM-PM syntax
  FMT = '%I:%M %p'

  # Assign start & end times as selected on the respective DatePickers
  start = dp_start.date.strftime(FMT)
  end = dp_end.date.strftime(FMT)
  
  # Lunch time in minutes...set to zero if not applicable.
  lunch = 30
  
  tdelta = datetime.datetime.strptime(end, FMT) - datetime.datetime.strptime(start, FMT) - timedelta(hours = 0, minutes = lunch)
  
  '''
  If you want the code to assume the interval crosses midnight (i.e. it should assume the end time is never earlier than the start time), you add the following lines to the above code:
  '''
  if tdelta.days < 0:
    tdelta = timedelta(days = 0,
                seconds = tdelta.seconds, microseconds = tdelta.microseconds)
                
  lbl_tpassed.text = '{}'.format(tdelta)

# DatePicker ui
dp = ui.View(name = 'Pick Start & End Times', frame = (0, 0, 414, 736))
dp.flex = 'HLRTB'
dp.background_color = 'cyan'
b1 = ui.ButtonItem('Select', action = select, tint_color = 'green')
dp.right_button_items = [b1]

dp_lb1 = ui.Label(frame = (130, 6, 160, 24))
dp_lb1.flex = 'HLRTB'
dp_lb1.font = ('<system>', 14)
dp_lb1.alignment = ui.ALIGN_CENTER
dp_lb1.text = 'Start Time:'
dp.add_subview(dp_lb1)

dp_lb2 = ui.Label(frame = (130, 325, 160, 24))
dp_lb2.flex = 'HLRTB'
dp_lb2.font = ('<system>', 14)
dp_lb2.alignment = ui.ALIGN_CENTER
dp_lb2.text = 'End Time:'
dp.add_subview(dp_lb2)

dp_lb3 = ui.Label(frame = (80, 645, 265, 24))
dp_lb3.flex = 'HLRTB'
dp_lb3.font = ('<system>', 14)
dp_lb3.alignment = ui.ALIGN_CENTER
dp_lb3.text = 'Time Passed...Click \'Select\' To Calculate:'
dp.add_subview(dp_lb3)

lbl_pick_start = ui.Label(frame = (105, 35, 200, 35))
lbl_pick_start.flex = 'HLRTB'
lbl_pick_start.font = ('<system-bold>', 14)
lbl_pick_start.alignment = ui.ALIGN_CENTER
lbl_pick_start.border_width = 2
lbl_pick_start.corner_radius = 10
lbl_pick_start.background_color = 'yellow'
lbl_pick_start.text = 'Time'
dp.add_subview(lbl_pick_start)

lbl_pick_end = ui.Label(frame = (105, 355, 200, 35))
lbl_pick_end.flex = 'HLRTB'
lbl_pick_end.font = ('<system-bold>', 14)
lbl_pick_end.alignment = ui.ALIGN_CENTER
lbl_pick_end.border_width = 2
lbl_pick_end.corner_radius = 10
lbl_pick_end.background_color = 'yellow'
lbl_pick_end.text = 'Time'
dp.add_subview(lbl_pick_end)

lbl_tpassed = ui.Label(frame = (105, 675, 200, 35))
lbl_tpassed.flex = 'HLRTB'
lbl_tpassed.font = ('<system-bold>', 14)
lbl_tpassed.alignment = ui.ALIGN_CENTER
lbl_tpassed.border_width = 2
lbl_tpassed.corner_radius = 10
lbl_tpassed.background_color = 'yellow'
lbl_tpassed.text_color = 'red'
lbl_tpassed.text = '00:00:00'
dp.add_subview(lbl_tpassed)

dp_start = ui.DatePicker(frame = (48, 85, 320, 225))
dp_start.flex = 'HLRTB'
dp_start.border_width = 2
dp_start.corner_radius = 10
dp_start.background_color = 'yellow'
dp_start.mode = ui.DATE_PICKER_MODE_TIME
dp_start.action = change_start_time
dp.add_subview(dp_start)

dp_end = ui.DatePicker(frame = (48, 405, 320, 225))
dp_end.flex = 'HLRTB'
dp_end.border_width = 2
dp_end.corner_radius = 10
dp_end.background_color = 'yellow'
dp_end.mode = ui.DATE_PICKER_MODE_TIME
dp_end.action = change_end_time
dp.add_subview(dp_end)

# Pick times...Default times on start and end picker is current time.
dp_start.date = datetime.datetime.now()
dp_end.date = datetime.datetime.now()
# Format today's time as '%I:%M %p' and put them on labels
lbl_pick_start.text = dp_start.date.strftime('%I:%M %p')
lbl_pick_end.text = dp_end.date.strftime('%I:%M %p')

# Show the DatePicker ui
dp.present(orientations = ['portrait'])
