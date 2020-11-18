# tag the text and anonymize proper nouns and such

from tinydb import TinyDB, Query
import nltk
from nltk.tokenize import word_tokenize
from nltk.tree import Tree

# save  substitutions for proper nouns
db = TinyDB( 'db.json' )
q = Query()
pns = db.table( 'prop_noun_subs' ) # pns is abbreivation for proper noun substitute table
add_to_db = False # true when manually tagging new data

def tag_and_anon( text ):
	# print( text )

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
			if len(terms) == 0:
				terms.append(word)

			for term in terms:
				sub = '' # empty sub

				# check db first 
				word_in_db = pns.search( q.word == term )
				
				if word_in_db:
					sub = word_in_db[0]['sub']
				
				elif add_to_db: # add to db (only when add to db flagged true)
					
					# manually assign entity type
					print( text ) # print so i know what the context is 
					ne_type = input("What type is " + term + "? ")
					
					if ne_type == 'None' or ne_type == '': # don't do a sub
						sub = ''

					elif ne_type == 'Self': # if not proper, sub with itSelf
						sub = term

					# if proper count the type and add new name
					else:
						# get length of documents with the type in sub and add one
						sub = f"{ne_type} {str(len( [doc for doc in pns.all() if ne_type in doc['sub']] + 1 ))}"

					# if there's a new sub add it to the db
					if sub:	
						prop_noun_subs.insert( { 'word': term, 'sub': sub } )

				if sub:
					# substitue tagged word with new text
					# print( term, sub, tagged )
					tagged[index] = (sub, tagged[index][1])

	# clear duplicates created by chunks						
	new_tagged = [] 
	[new_tagged.append(t) for t in tagged if t not in new_tagged]
	
	return new_tagged