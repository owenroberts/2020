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
	# print( text )

	sentence = beginning
	events = [] # each things that happens during time period

	# get fragments of each time entry, usually one fragment is one "event"
	fragments = [f for f in text.split(',')]
	for frag in fragments:
		frag = frag.strip()
		frag = sub_text( frag, 'abbreviations', True ) # sub common abbr for full words
		frag = sub_text( frag, 'special_abbreviations', False )
		frag = sub_text( frag, 'acronyms', True ) # sub common acronyms for full words
		# print( 'frag:', frag )

		tagged = tag_and_anon( frag ) # get tagged, anonymize 
		tagged = sub_check_verbs( tagged )
		# print( 'tagged', tagged )

		# lower case non-prop nouns
		if any( t[1].isalpha() for t in tagged ):

			grammar = '''
				NP: { <NN>?<IN>?<DT>?<NN.*> } # include JJ
				VP: { <VB.*><RP>? }
			'''
			cp = nltk.RegexpParser( grammar )
			chunks = cp.parse( tagged )

			nouns = [] # noun phrases
			props = [] # prop noun phrases
			verbs = [] # verb phrases

			for chunk in chunks:
				if type( chunk ) == nltk.tree.Tree:
					if chunk.label() == 'NP':
						# NNPS ?
						if 'NNP' in [t[1] for t in chunk.leaves()]:
							props.append( chunk.leaves() )
						else:
							nouns.append( chunk.leaves() )
					if chunk.label() == 'VP':
						verbs.append( chunk.leaves() )

			# props = [t for t in tagged if 'NNP' in t[1]] # prop nouns
			# nouns = [t for t in tagged if re.match( r'NNS?$', t[1])] # regular noun
			# verbs = [t for t in tagged if 'VB' in t[1]] # verbs

			# these list with tuples word, pos
			pp = random.choice( props ) if props else ''
			np = random.choice( nouns ) if nouns else ''
			vp = random.choice( verbs ) if verbs else ''

			if not vp:
				if np:
					noun, pos = [t for t in np if 'NN' in t[1]][0]
				elif pp:
					noun, pos = [t for t in pp if 'NNP' in t[1]][0]
				else:
					print( ' ** fuck no noun ** ' )
				related = get_related_word( wnl.lemmatize( noun, 'n' ) if 'S' in pos else noun )
				if related:
					vp = [( random.choice( related ), 'VB' )]
				else:
					search = '*'
					if noun in comps['verbs']:
						search = noun
					elif noun.split('-')[0] in comps['verbs']:
						search = noun.split('-')[0]
					vp = [( random.choice( comps['verbs'][search] ), 'VB' )]

			event_string = " ".join([v[0].lower() for v in vp])
			
			if np and needs_article( np ):
				n = [t for t in np if 'NN' in t[1]][0]
				dt = 'an' if n[0][0] in 'aeiou' else 'a'
				np.insert( np.index( n ), ( dt, 'DT' ) )

			if np:
				event_string += f' { " ".join([n[0].lower() for n in np]) }'
			
			if pp:
				p = [t for t in pp if 'NNP' in t[1]][0] # prop noun
				t = p[0].split('-')[0] # anon sub type
				if np:
					prep = 'for'
					if t == 'Place':
						prep = 'to'
					if t == 'Person':
						prep = 'with'
					event_string += f' { prep }'
				elif t == 'Place':
					event_string += f' to'

				if p:
					event_string += f' { " ".join([n[0] for n in pp]) }'

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

	# print( '*:', sentence )
	return sentence

def needs_article( noun_phrase ):
	if 'DT' in [t[1] for t in noun_phrase]:
		return False
	noun, pos = [n for n in noun_phrase if 'NN' in n[1]][0]
	if not re.match( 'NN$', pos ):
		return False
	if noun[-3:] == 'ing':
		return False
	if noun in subs['uncountable']:
		return False
	return True

def pos_in_frag( pos, frag ):
	# if any pos in array contains the pos string
	return True if [w for w in frag if re.match( pos, w ) ] else False

# substitute abbrevations like w/ and re:
def sub_text( text, sub_type, use_boundary ):
	for a in subs[sub_type]:
		if a in text:
			if use_boundary:
				r = r'\b' + re.escape( a ) + r'\b' 
			else:
				r = a
			text = re.sub( r, subs[sub_type][a], text )
	return text

# substitute commonly mistagged nouns
def sub_check_verbs( tagged ):
	for index, tag in enumerate( tagged ):
		word, pos = tag
		if word.lower() in subs['check_verbs']:
			pos = 'VB'
			tagged[index] = ( word, pos )
	return tagged