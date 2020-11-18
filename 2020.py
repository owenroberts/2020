import datetime
import random

from os import listdir
from os.path import isfile, join

from m.get_time_and_text import get_time_and_text
from m.build_sentence import build_sentence
from m.completions import completions

comps = completions()
time_sheets_path = 'time_sheets/'
# load all timesheets 
# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
onlyfiles = [f for f in listdir(time_sheets_path) if isfile(join(time_sheets_path, f))]
onlyfiles.sort()

full_text = ''

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def read_file( file ):
	global full_text

	# each day starts here
	current_hour = 0
	track_the_time = '' # keep track of morning/afternoon
	date = file.split(' ')[0].split('_') # get date from file name

	# get weekday string from date
	weekday = days[datetime.date(2020, int(date[0]), int(date[1])).weekday()] 

	full_text += random.choice( comps['first_sent'][weekday] ) + " "
	
	lines = open(time_sheets_path + file, 'r').readlines()
	for line in lines:

		line = line.rstrip()

		if len(line) > 0:
			
			time_stamp, duration, text, current_hour = get_time_and_text( line, current_hour )

			current_time = 'afternoon' if current_hour >= 12 else 'morning'
			if not track_the_time or current_time is not track_the_time:
				beginning = f'In the { current_time }, I '
				track_the_time = current_time
			else:
				beginning = 'Then, I '

			sentence = build_sentence( text, beginning )

			# add random/multi sentence structures
			full_text += f'{ sentence } for { duration }. '

	# new line after day
	full_text += '\n\n'


# for file in onlyfiles:
	# print( file )
read_file( onlyfiles[0] )

# output file
o = open('full_text.txt', 'w')
o.write( full_text )
o.close()