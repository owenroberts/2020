# read through all the time sheets and add them to the main text

import datetime
from random import choice

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
busy_range = []


def read_file( file, go_backwards ):
	global current_month
	global current_day
	
	# each day starts here
	current_hour = 0
	track_the_time = '' # keep track of morning/afternoon
	date = file.split(' ')[0].split('_') # get date from file name
	was_busy = 0

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

	o.write( choice( comps['first_sent'][days[weekday]] ) + " " )
	
	lines = open( time_sheets_path + file, 'r' ).readlines()
	if go_backwards:
		lines = reversed( lines )
	for line in lines:

		line = line.rstrip()

		if len( line ) > 0:
			# print( 'line:', line )
			
			time_stamp, duration, text, current_hour = get_time_and_text( line, current_hour )

			if text:
				sentence = build_sentence( text )
			else:
				sentence = choice( comps['end'] ) # time stamp with nothing after

			if not duration:
				duration = "I don't remember how long" # no matching time stamp

			current_time = 'afternoon' if current_hour >= 12 else 'morning'
			if go_backwards:
				current_time = 'afternoon' if current_hour < 12 else 'morning'
			
			if not track_the_time or current_time is not track_the_time:
				time_change = True
				track_the_time = current_time
			else:
				time_change = False

			sent_type = choice( [0, 1, 2] )
			if sent_type == 0:
				beginning = f'In the { current_time },' if time_change else 'Then,'
				s = f'{ beginning } I { sentence } for { duration }. '
			elif sent_type == 1:
				s = '' if time_change else 'Then, '
				s += f'I { sentence } for { duration }'
				s += f' in the { current_time }. ' if time_change else '. '
			else:
				if time_change:
					beginning = f'For { duration } in the { current_time },'
				else:
					beginning = f'Then, for { duration }'
				s = f'{ beginning } I { sentence }. '
			
			was_busy += len( s ) # business counter
			o.write( '%s' % s )

	
	# end of the day
	# track relative 'business'
	b = int( was_busy / 100 ) # range 0 - 24 ish
	busy_range.append( b )
	busy_avg = int( sum( busy_range ) / len( busy_range ) )
	if b < busy_avg:
		o.write( comps['busy']['0'] )
	elif b == busy_avg:
		o.write( comps['busy']['1'] )
	else:
		o.write( comps['busy']['2'] )

	o.write( comps['eod'][str( current_hour )] )

	# new line after day
	# print( '\n\n' )
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
\parindent 0pt
\parskip \baselineskip
\textcopyright{} 2020 Owen Roberts \\
All rights reserved.

This work is licensed with Creative Commons Attribution-ShareAlike 4.0
International.(CC BY-SA 4.0)

http://creativecommons.org/licenses/by-sa/4.0/

The names of people, places, organizations and other named entities in this document have been replaced with randomly generated names.  Any resemblance to actual persons, organizations, places, etc. is coincidental.

\endgroup
\clearpage

\mainmatter

\section*{\hfil Part 1\hfil}
\clearpage

""" )

# for file in onlyfiles:
	# read_file( file, False )
# for i in range(0, 5):
	# read_file( onlyfiles[i], False )
# read_file( onlyfiles[0] )

o.write( r"""\section*{\hfil Part 2\hfil}
\clearpage

""" )

# do it again in reverse
count = 0
for file in reversed( onlyfiles ):
	read_file( file, True )
	count = count + 1
	if count == 5:
		break



o.write( r'\end{document}' )

o.close()