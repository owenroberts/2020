# separate timestamp from text 
# rerturn timestamp, or none, duration, time

import re
import math
from datetime import datetime
TIME_FMT = "%H:%M"

number_strings = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']

def get_time_and_text( line, current_hour ):
	# print( line )
	
	time_stamp = ''
	duration = '' 
	text = ''

	has_time_stamp = re.search( r'(\d+:\d+-*(\d+:\d+)*)(\s+)*(.*)$', line )
	
	if has_time_stamp:
		time_stamp = has_time_stamp.groups()[0]
		text = has_time_stamp.groups()[3]
		t1, t2 = re.search( r'(\d+:\d+)-*(\d+:\d+)*', time_stamp ).groups()
		
		# get morning vs afternoon, needs to go in order
		t1, current_hour = adjust_afternoon( t1, current_hour )
		if t2:
			t2, current_hour = adjust_afternoon( t2, current_hour )

		# if two time stamps available, get duration
		if t2:
			td = datetime.strptime(t2, TIME_FMT) - datetime.strptime(t1, TIME_FMT)
			duration = duration_to_string( td.seconds / 60 / 60 )
		else:
			duration = ''

	else:
		has_time = re.search( r'(\d*\.*\d+\s*([Hh]our)*)(\s+)*(.*)$', line )
		if has_time:
			time_value = has_time.groups()[0]
			duration = duration_to_string( time_value ) # format somehow
			text = has_time.groups()[3]

	return time_stamp, duration, text, current_hour

# if this is the first instance of 12 it is no longer morning
# if it is no longer morning, hours must add 12 to get correct duration
# passing current hour around seems nuts ... 
def adjust_afternoon( time, current_hour ):
	h, m = time.split(':')
	if int(h) > current_hour:
		current_hour = int(h)
	if int(h) < current_hour and int(h) < 12:
		current_hour = int(h) + 12
	
	# special case 
	if int(h) == 12 and current_hour > 12:
		return f'{int(h) - 12}:{m}', current_hour	
	
	if current_hour >= 12 and h != '12':
		return f'{int(h) + 12}:{m}', current_hour
	else:
		return time, current_hour
		

def duration_to_string( duration ):

	hours = 0
	mins = 0

	if isinstance(duration, float):
		mins, hours = math.modf(duration)
	else:
		h, m = re.search( r'(\d*)(\.*\d*)', duration ).groups()
		if h:
			hours = int(h)
		if m:
			m = float(m)

	min_string = '15 minutes' if mins == 0.25 else '45 minutes' # only for .25 and .75

	if hours == 0:
		if mins == 0.5:
			return 'half an hour'
		else:
			return min_string
	
	elif hours == 1:
		if mins == 0.5:
			return 'an hour and a half'
		else:
			return f'an hour and { min_string }'
	else:
		h = int( hours )
		hour_string = number_strings[h] if h < len( number_strings ) else hours

		if mins == 0:
			return f'{ hour_string } hours'
		if mins == 0.5:
			return f'{ hour_string } and a half hours'
		else:
			return f'{ hour_string } hours and { min_string }'

	# jesus christ



