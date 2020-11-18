# for looking at pos trends

from os import listdir
from os.path import isfile, join
from tinydb import TinyDB, Query
from get_time_and_text import get_time_and_text
from tag_and_anon import tag_and_anon

time_sheets_path = 'time_sheets/'
onlyfiles = [f for f in listdir(time_sheets_path) if isfile(join(time_sheets_path, f))]
onlyfiles.sort()

db = TinyDB( 'db.json' )
q = Query()
pos_stats = db.table( 'pos_stats' )

def get_stats( file ):

	current_hour = 0
	
	lines = open(time_sheets_path + file, 'r').readlines()
	for line in lines:

		line = line.rstrip()
		time_stamp, duration, text, current_hour = get_time_and_text( line, current_hour )
		
		fragments = [frag for frag in text.split(',')]
		for frag in fragments:
			frag = frag.strip()
			tagged = tag_and_anon( frag )

			for tag in tagged:
				word = tag[0]
				pos = tag[1]
				word_in_db = pos_stats.search( q.word == word )
				if word_in_db:
					if word_in_db[0]['pos'] != pos:
						pos_stats.insert( { 'word': word, 'pos': pos } )
				else:
					pos_stats.insert( { 'word': word, 'pos': pos } )

		


for file in onlyfiles:
	get_stats( file )
