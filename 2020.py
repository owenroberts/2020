# read through all the time sheets and add them to the main text

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

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

current_month = 'None'
current_day = 0

def read_file( file ):
	global current_month
	global current_day
	
	# each day starts here
	current_hour = 0
	track_the_time = '' # keep track of morning/afternoon
	date = file.split(' ')[0].split('_') # get date from file name

	# get weekday string from date
	weekday = datetime.date(2020, int(date[0]), int(date[1])).weekday()
	if weekday >= current_day:
		current_day = weekday
	else:
		o.write( r'\vspace{1ex}' )
		o.write( '\n' )
		o.write( r'\noindent ' )
		current_day = weekday

	month = months[datetime.date(2020, int(date[0]), int(date[1])).month - 1]

	if month != current_month:
		o.write( r'\section*{%s}' % month )
		o.write( '\n' )
		# o.write( month )
		o.write( r'\vspace{1ex}' )
		o.write( '\n' )
		current_month = month



	o.write( random.choice( comps['first_sent'][days[weekday]] ) + " " )
	
	lines = open( time_sheets_path + file, 'r' ).readlines()
	for line in lines:

		line = line.rstrip()

		if len( line ) > 0:
			# print( 'line:', line )
			
			time_stamp, duration, text, current_hour = get_time_and_text( line, current_hour )

			current_time = 'afternoon' if current_hour >= 12 else 'morning'
			if not track_the_time or current_time is not track_the_time:
				beginning = f'In the { current_time }, I '
				track_the_time = current_time
			else:
				beginning = 'Then, I '

			if text:
				sentence = beginning + build_sentence( text )
			else:
				sentence = beginning + random.choice( comps['end'] ) # time stamp with nothing after

			# print( 'duration:', duration )
			if not duration:
				duration = "I don't remember how long" # no matching time stamp

			# print( f'{ sentence } for { duration }. ' )
			# add random/multi sentence structures
			# o.write( f'{ sentence } for { duration }. ' )
			o.write( '%s' % f'{ sentence } for { duration }. ' )

	# new line after day
	o.write( '\n\n' )

o = open( 'tex/2020.tex', 'w' ) # output file

o.write( r"""\documentclass[oneside,12pt]{book}
\frenchspacing
\usepackage{makeidx}
\makeindex
\begin{document}
\title{\textit{2020} by James}
\author{Owen Ribbit}
\date{November 2020}
\maketitle

\pagestyle{empty}
%% copyrightpage
\begingroup
\footnotesize
\parindent 0pt
\parskip \baselineskip
\textcopyright{} 2020 Owen Roberts \\
All rights reserved.

This work is licensed with Creative Commons Attribution-ShareAlike 4.0
International.(CC BY-SA 4.0)

http://creativecommons.org/licenses/by-sa/4.0/

\endgroup
\clearpage

\mainmatter

""" )

for file in onlyfiles:
	read_file( file )
# read_file( onlyfiles[0] )

o.write( r'\end{document}' )

o.close()