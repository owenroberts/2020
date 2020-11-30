# find named entities and proper nouns to add to the databse

from m import db
import nltk
from nltk.tokenize import word_tokenize
from nltk.tree import Tree
import re

nones = [] # save things that are nones in given session

def add_subs( text ):

	tokens = word_tokenize( text )
	tagged = nltk.pos_tag( tokens )

	# look for named entity in text fragment 
	chunked = nltk.ne_chunk( tagged )
	current_chunk = []
	continuous_chunk = []

	for i in chunked:
		if type(i) == Tree:
			current_chunk.append( " ".join([token for token, pos in i.leaves()]))
		if current_chunk:
			ne = " ".join( current_chunk )
			if ne not in continuous_chunk:
				continuous_chunk.append( ne )
				current_chunk = []
			else:
				continue;

	for index, tag in enumerate( tagged ):
		word, pos = tag
		if 'NNP' in pos: # only care about NNP/S

			# if word is in ne chunk
			terms = [s for s in continuous_chunk if word in s] # why terms? idk 

			# if not in ne list and proper noun
			if len( terms ) == 0:
				terms.append( word )

			for term in terms:
				sub = '' # empty sub

				# check db first 
				word_in_db = db.pns_has_word( term )

				if word_in_db:
					sub = word_in_db[0]['sub']
				
				# add to db (only when add to db flagged true)
				elif add_to_db and term not in nones: 
					
					# manually assign entity type
					print( text ) # print so i know what the context is 
					ne_type = input("What type is " + term + "? ")
					
					if ne_type == 'None' or ne_type == '': # don't do a sub
						sub = ''
						nones.append( term )

					elif ne_type == 'Self': # if not proper, sub with itSelf
						sub = term

					# if proper count the type and add new name
					else:
						# get length of documents with the type in sub and add one
						# n = len([r for r in pns.all() if ne_type in r['sub']])
						n = db.get_type_length( ne_type )
						sub = f"{ne_type}-{n + 1}"
						pos = 'NNP' # what about special things like DSP?

					# if there's a new sub add it to the db
					if sub:	
						# way to tell the program to add to existing record?
						db.pns.insert( { 'word': [term], 'sub': sub } )

				if sub:
					# substitue tagged word with new text
					# print( term, sub, tagged )
					tagged[index] = ( sub, pos )