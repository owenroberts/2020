# read through timesheets and format them to prep for james review

import datetime
from os import listdir
from os.path import isfile, join

from m.get_time_and_text import get_time_and_text
from m.get_anon_subs import get_subs

time_sheets_path = 'time_sheets/'

onlyfiles = [f for f in listdir(time_sheets_path) if isfile(join(time_sheets_path, f))]
onlyfiles.sort()

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

o = open('anonymized_timesheets.txt', 'w')
current_month = 'None'

def read_file( file ):
	global current_month

	date = file.split(' ')[0].split('_') # get date from file name
	# weekday = days[datetime.date(2020, int(date[0]), int(date[1])).weekday()] 
	month = months[datetime.date(2020, int(date[0]), int(date[1])).month - 1] 

	if month != current_month:
		o.write(month)
		o.write('\n\n')
		current_month = month

	o.write( f'{date[0]}/{date[1]}/2020' )
	o.write('\n\n')

	lines = open(time_sheets_path + file, 'r').readlines()
	for line in lines:
		time_stamp, duration, text, current_hour = get_time_and_text( line, 0 )
		text = get_subs( text )
		o.write( text )
		o.write('\n')

for file in onlyfiles:
	read_file( file )
	o.write('\n\n')

o.close()