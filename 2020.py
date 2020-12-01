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
		o.write( r'\vspace{2ex}' )
		o.write( '\n' )
		o.write( r'\noindent ' )
		current_day = weekday

	month = months[datetime.date(2020, int(date[0]), int(date[1])).month - 1]

	if month != current_month:
		o.write( r'\chapter*{%s}' % month )
		o.write( '\n' )
		# o.write( month )
		o.write( r'\vspace{2ex}' )
		o.write( '\n' )
		current_month = month

	sents = []
	sents.append( choice( comps['first_sent'][days[weekday]] ) )
	
	lines = open( time_sheets_path + file, 'r' ).readlines()
	
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
			
			if not track_the_time or current_time is not track_the_time:
				time_change = True
				track_the_time = current_time
			else:
				time_change = False

			sent_type = choice( [0, 1, 2] )
			if sent_type == 0:
				beginning = f'In the { current_time },' if time_change else 'Then,'
				s = f'{ beginning } I { sentence } for { duration }.'
			elif sent_type == 1:
				s = '' if time_change else 'Then, '
				s += f'I { sentence } for { duration }'
				s += f' in the { current_time }. ' if time_change else '.'
			else:
				if time_change:
					beginning = f'For { duration } in the { current_time },'
				else:
					beginning = f'Then, for { duration }'
				s = f'{ beginning } I { sentence }.'
			
			was_busy += len( s ) # business counter
			# o.write( '%s' % s )
			sents.append( s )
	
	# end of the day
	# track relative 'business'
	b = int( was_busy / 100 ) # range 0 - 24 ish
	busy_range.append( b )
	busy_avg = int( sum( busy_range ) / len( busy_range ) )
	if b < busy_avg:
		sents.append( comps['busy']['0'] )
	elif b == busy_avg:
		sents.append( comps['busy']['1'] )
	else:
		sents.append( comps['busy']['2'] )

	sents.append( comps['eod'][str( current_hour )] )

	if go_backwards:
		sents = reversed( sents )
	o.write( " ".join( sents ) )

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

\frontmatter
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

\chapter*{\hfil Part 1\hfil}
\clearpage

\pagestyle{myheadings}

""" )

for file in onlyfiles:
	read_file( file, False )
# for i in range(0, 5):
	# read_file( onlyfiles[i], False )
# read_file( onlyfiles[0] )

o.write( r"""\clearpage

\chapter*{\hfil Part 2\hfil}
\clearpage

""" )

# do it again in reverse
for file in reversed( onlyfiles ):
	read_file( file, True )

# license info 


o.write( r'''\clearpage

This work includes data from ConceptNet 5, which was compiled by the
Commonsense Computing Initiative. ConceptNet 5 is freely available under
the Creative Commons Attribution-ShareAlike license (CC BY SA 3.0) from
http://conceptnet.io.

The included data was created by contributors to Commonsense Computing
projects, contributors to Wikimedia projects, DBPedia, OpenCyc, Games
with a Purpose, Princeton University's WordNet, Francis Bond's Open
Multilingual WordNet, and Jim Breen's JMDict.

WordNet Release 3.0 This software and database is being provided to you, the LICENSEE, by Princeton University under the following license. By obtaining, using and/or copying this software and database, you agree that you have read, understood, and will comply with these terms and conditions.: Permission to use, copy, modify and distribute this software and database and its documentation for any purpose and without fee or royalty is hereby granted, provided that you agree to comply with the following copyright notice and statements, including the disclaimer, and that the same appear on ALL copies of the software, database and documentation, including modifications that you make for internal use or for distribution. WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT- ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS. The name of Princeton University or Princeton may not be used in advertising or publicity pertaining to distribution of the software and/or database. Title to copyright in this software, database and any associated documentation shall at all times remain with Princeton University and LICENSEE agrees to preserve same.

The code for this project is availabe at
https://github.com/owenroberts/2020

It is distributed under the MIT license.

Copyright 2020 Owen Roberts

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

\end{document}''' )

o.close()