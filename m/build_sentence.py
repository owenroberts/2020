# build sentence fragments
import random
import re
from nltk.stem import WordNetLemmatizer 
from tinydb import TinyDB, Query

from m.get_related_word import get_related_word
from m.completions import completions
from m.tag_and_anon import tag_and_anon

comps = completions()
wnl = WordNetLemmatizer()

db = TinyDB( 'db.json' )
q = Query()
pns = db.table( 'prop_noun_subs' )

# verbs commonly tagged as nouns
verbs_check = ['review', 'meet', 'prep', 'email']
# may need more checks, like in fragment with a NN
# call is verb sometimes (maybe if no other verb ... )

# abbreviations
abrv_check = [('w/', 'with'), ('.25', 'a little bit')]

# acronyms that are mis categorized as prop nouns 
acronyms = ['LOA', 'WFH']

# break down a sentence ... i need a verb and noun, subject and object

def build_sentence( text, beginning ):
	# print( 'text:', text )

	sentence = beginning
	events = [] # each things that happens during time period

	# get fragments of each time entry, usually one fragment is one "event"
	fragments = [f for f in text.split(',')]
	for frag in fragments:
		frag = frag.strip()

		# check for some common abbreviations
		for abrv, sub in abrv_check:
			if abrv in frag:
				r = re.compile( re.escape(abrv) )
				frag = re.sub( r, sub, frag )

		tagged = tag_and_anon( frag ) # get tagged, anonymize 

		# some fixes for tags before breaking down by pos
		for index, tag in enumerate( tagged ):
			word, pos = tag

			if word in acronyms:
				tagged[index] = ( word, pos.replace( 'P', '' ) )

			# check for words in db, some orgs are tagged incorrectly as JJ etc
			word_in_db = pns.search( q.word == word )
			if word_in_db:
				# if word has substitute (org, person etc.)
				if word_in_db[0]['word'] != word_in_db[0]['sub']:
					pos = 'NNP'

				# while we're checking, replace words that weren't replace by tag and anon
				if word != word_in_db[0]['sub']:
					word = word_in_db[0]['sub']
				tagged[index] = ( word, pos )

			# check for nouns incorrectly tagged as verbs
			if word.lower() in verbs_check and pos[0] != 'V':
				tagged[index] = ( word.lower(), 'VB' )

		print( 'tagged', tagged )

		# handle frags - list of parts of speech
		frag_pos = [t[1] for t in tagged] 

		verbs = [t for t in tagged if 'VB' in t[1]]
		nouns = [t for t in tagged if 'NN' in t[1]]

		preps = [t for t in tagged in 'IN' in t[1]]
		parts = [t for t in tagged in 'RP' in t[1]]

		# noun plural or singular add a or some following prep

		# if no verbs, generate a verb
		if not verbs:
			related = get_related_word( word.lower() if 'S' not in pos else wnl.lemmatize( word.lower(), 'n' ) )



		sent = f'{ " ".join( verbs ) }'
		if parts:
			sent += f' { " ".join( parts ) }'
		if preps:
			sent += f' { " ".join( preps ) }'
		sent +=  f' { " ".join( [n[0] for n in nouns] ) }'

		events.append( sent )



	# add events to sentence, separated by comma or and
	for index, event in enumerate(events):
		sentence += event
		if index < len( events ) - 2:
			sentence += ', '
		elif index < len( events ) - 1:
			sentence += ' and '

	# print( 'sent:', sentence )
	return sentence

def pos_in_frag( pos, frag ):
	# if any pos in array contains the pos string
	return True if [w for w in frag if re.match( pos, w ) ] else False