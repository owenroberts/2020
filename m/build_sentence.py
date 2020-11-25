# build sentence fragments
import random
import re
import nltk
from nltk.stem import WordNetLemmatizer 
from tinydb import TinyDB, Query

from m.get_related_word import get_related_word
from m.completions import completions
from m.tag_and_anon import tag_and_anon

from m import subs # substitions
subs = subs.subs()

comps = completions()
wnl = WordNetLemmatizer()

db = TinyDB( 'db.json' )
q = Query()
pns = db.table( 'prop_noun_subs' )
rv = db.table( 'related_verbs' ) # save related verbs from concept net to speed up commons verbs


def build_sentence( text, beginning ):
	print( 'text:', text )

	sentence = beginning
	events = [] # each things that happens during time period

	# get fragments of each time entry, usually one fragment is one "event"
	fragments = [f for f in text.split(',')]
	for frag in fragments:
		frag = frag.strip()
		frag = sub_text( frag, 'abbreviations' ) # sub common abbreviations for full words
		frag = sub_text( frag, 'acronyms' ) # sub common acronyms for full words
		# print( 'frag:', frag )

		tagged = tag_and_anon( frag,  ) # get tagged, anonymize 
		# print( 'tagged', tagged )

		# lower case non-prop nouns
		if any( t[1].isalpha() for t in tagged ):
			props = [t for t in tagged if 'NNP' in t[1]] # prop nouns
			nouns = [t for t in tagged if re.match( r'NNS?$', t[1])] # regular noun
			verbs = [t for t in tagged if 'VB' in t[1]] # verbs

			# these are still tuples with word, pos
			p = random.choice( props ) if props else ''
			n = random.choice( nouns ) if nouns else ''
			v = random.choice( verbs ) if verbs else ''

			if not v:
				noun, pos = n if n else p
				related = get_related_word( wnl.lemmatize( noun, 'n' ) if 'S' in pos else noun )
				if related:
					v = ( random.choice( related ), 'VB' )
				else:
					search = '*'
					if noun in comps['verbs']:
						search = noun
					elif noun.split('-')[0] in comps['verbs']:
						search = noun.split('-')[0]
					v = ( random.choice( comps['verbs'][search] ), 'VB' )

			event_string = v[0].lower()
			
			if n and re.match( 'NN$', n[1] ) and n[0][-3:] != 'ing':
				dt = 'an' if n[0][0] in 'aeiou' else 'a'
				event_string += f' { dt }'
			if n:
				event_string += f' { n[0].lower() }'
			
			if p:
				prep = 'for'
				if '-' in p[0]: # substituted
					t = p[0].split('-')[0] # anon sub type
					if t == 'Place':
						prep = 'to'
					if t == 'Person':
						prep = 'width'
				event_string += f' { prep }'
				event_string += f' { p[0] }'

			events.append( event_string )

		else: # questions marks and such
			for word, pos in tagged:
				events.append( random.choice( comps['non-alpha'][word] ) )



	# add events to sentence, separated by comma or and
	for index, event in enumerate(events):
		sentence += event
		if index < len( events ) - 2:
			sentence += ', '
		elif index < len( events ) - 1:
			sentence += ' and '

	print( 'sent:', sentence )
	return sentence

def pos_in_frag( pos, frag ):
	# if any pos in array contains the pos string
	return True if [w for w in frag if re.match( pos, w ) ] else False

# substitute abbrevations like w/ and re:
def sub_text( text, sub_type ):
	for a in subs[sub_type]:
		if a in text:
			text = re.sub( re.escape(a), subs[sub_type][a], text )
	return text