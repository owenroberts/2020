# build sentence fragments
import random
from random import choice
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 

from m.get_related_words import get_related_words
from m.get_random_word import get_random_word
from m.completions import completions
from m.get_anon_subs import get_subs

from m import db

from m import subs # substitions
subs = subs.subs()

comps = completions()
wnl = WordNetLemmatizer()

names = {} # dict to keep track of randomized names
rchars = 'ABCDEFHIJKLMNOPQRSTUVWXY' # random chars to use for names


def build_sentence( text ):
	# print( text )

	events = [] # each things that happens during time period

	# get fragments of each time entry, usually one fragment is one "event"
	fragments = [f for f in text.split(',')]
	for frag in fragments:
		frag = frag.strip()
		frag = get_subs( frag )
		# print( 'frag:', frag )

		tokens = word_tokenize( frag )
		tagged = nltk.pos_tag( tokens )
		tagged = sub_check_verbs( tagged )
		tagged = check_props( tagged )
		# print( 'tagged', tagged )

		# lower case non-prop nouns
		if any( t[1].isalpha() for t in tagged ):

			grammar = '''
				NP: { <NN>?<IN>?<DT>?<NN.*> } # include JJ?
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

			# these list with tuples word, pos
			pp = choice( props ) if props else ''
			np = choice( nouns ) if nouns else ''
			vp = choice( verbs ) if verbs else ''

			if not vp:
				noun = ''
				pos = ''
				if np:
					noun, pos = [t for t in np if 'NN' in t[1]][0]
				elif pp:
					noun, pos = [t for t in pp if 'NNP' in t[1]][0]
				else:
					print( ' ** fuck no noun ** ' )
					print( text )
					print( tagged )
				
				related = get_related_words( wnl.lemmatize( noun, 'n' ) if 'S' in pos else noun )
				
				if related:
					vp = [( choice( related ), 'VB' )]
				else:
					search = '*'
					if noun in comps['verbs']:
						search = noun
					elif noun.split('-')[0] in comps['verbs']:
						search = noun.split('-')[0]
					vp = [( choice( comps['verbs'][search] ), 'VB' )]

			event_string = '' # put it all together

			# get adverb
			adv = ''
			if random.choice([0, 1]):
				adv = get_random_word( 'r' )

			if adv[-2:] == 'ly':
				event_string += f'{adv} '

			event_string += " ".join([v[0].lower() for v in vp])

			if adv and adv[-2:] != 'ly':
				event_string += f' {adv}'
			
			if np and needs_article( np ):
				n = [t for t in np if 'NN' in t[1]][0]
				dt = 'an' if n[0][0] in 'aeiou' else 'a'
				np.insert( np.index( n ), ( dt, 'DT' ) )

			if np:
				if choice([0, 0, 1]):
					adj = get_random_word( 's' )
					event_string += f' { adj }'
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
					sub_pn = []
					for n, pos in pp:
						if n in names:
							sub_pn.append( names[n] )
						else:
							sub_pn.append( n )
					event_string += f' { " ".join( sub_pn ) }'

			events.append( event_string )

		else: # questions marks and such
			for word, pos in tagged:
				events.append( choice( comps['non-alpha'][word] ) )

	sentence = ''

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
	noun, pos = [n for n in noun_phrase if 'NN' in n[1]][-1] # last noun in noun phrase 
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

# substitute commonly mistagged nouns
def sub_check_verbs( tagged ):
	for index, tag in enumerate( tagged ):
		word, pos = tag
		if word.lower() in subs['check_verbs']:
			pos = 'VB'
			tagged[index] = ( word, pos )
	return tagged

# make sure anything that's subbed is NNP
def check_props( tagged ):
	for index, tag in enumerate( tagged ):
		word, pos = tag
		if '-' in word:
			t = word.split('-')[0]
			if t in subs['types']:
				if word not in names: # add names to dict for later substitution
					names[word] = get_random_name( t )
				tagged[index] = ( word, 'NNP' )
	return tagged

def get_random_name( t ): # type
	if t == 'Org':
		s = get_random_string( choice( [3, 6] ) )
		c = choice( ['Company', 'Organization'] )
		return f'{ c } { s }' if choice( [0, 1] ) else  f'The { s } { c }'
	if t == 'Person':
		l = get_random_string( 1 )
		m = choice( ['Mr.', 'Ms.', 'Mx.'] )
		return f'{ l }—' if choice([0, 1]) else f'{ m } { l }'
	if t == 'Place':
		e = choice( ['ville', ' City', 'town', 'ton', 'ford'] )	
		n = get_random_string( 1 )
		d = '—' * choice( [2, 3, 4, 5] )
		return f'{ n }{ d }{ e }'
	if t == 'Publication':
		e = choice( ['Times', 'Post', 'Gazette'] )
		n = get_random_string( 4 )
		return f'{ n } { e }'
	if t == 'List':
		e = choice( ['List', 'Mailing List', 'Listserv'] )
		n = get_random_string( 4 )
		return f'{ n } { e }'
	if t == 'App':
		n = get_random_string( choice( [3, 4] ) )
		return f'{ n }App'
	else:
		return f'{ get_random_string( choice( [3, 4, 5] ) ) }'

def get_random_string( n ):
	string = ''
	while len(string) < n:
		string += choice( rchars )
	return string