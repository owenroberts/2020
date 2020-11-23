# build sentence fragments
import random
import re
import nltk
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

sometimes_verbs = ['call']
# call is verb sometimes (maybe if no other verb ... )

# abbreviations
abrv_check = [('w/', 'with'), ('.25', 'some')]

# acronyms that are mis categorized as prop nouns 
acronyms = ['LOA', 'WFH']

# weird nouns
weird_nouns = ['nothing']

# break down a sentence ... i need a verb and noun, subject and object

# check types
anon_types = ['Org', 'Person', 'Place', 'Publication', 'List']

def build_sentence( text, beginning ):
	print( 'text:', text )

	sentence = beginning
	events = [] # each things that happens during time period

	# get fragments of each time entry, usually one fragment is one "event"
	fragments = [f for f in text.split(',')]
	for frag in fragments:
		frag = frag.strip()

		# print( 'frag:', frag )

		# check for some common abbreviations
		for abrv, sub in abrv_check:
			if abrv in frag:
				r = re.compile( re.escape(abrv) )
				frag = re.sub( r, sub, frag )

		tagged = tag_and_anon( frag ) # get tagged, anonymize 
		types = {}

		# some fixes for tags before breaking down by pos
		for index, tag in enumerate( tagged ):
			word, pos = tag

			if word in acronyms:
				pos = pos.replace( 'P', '' )
				tagged[index] = ( word, pos )

			# check for words in db, some orgs are tagged incorrectly as JJ etc
			# does this work for two word orgs etc? 
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
				word = word.lower()
				pos = 'VB'
				tagged[index] = ( word, pos )

			# lower case non-prop nouns
			if re.match( r'NNS*$', pos ) and re.match( r'[A-Z]', word) and word not in acronyms:
				word = word.lower()
				tagged[index] = ( word, pos )

		# print( 'tagged', tagged )
		if any( t[1].isalpha() for t in tagged ):

			grammar = """
				NP: {<NNP.*>+<DT>?<JJ>*<NN.*>+} # proper noun phrases 
				INNN: {<IN><NNS?>} # needs article
				"""
			cp = nltk.RegexpParser( grammar )
			chunks = cp.parse( tagged )
			# print( 'chunks:', chunks )
			chunked = []		

			# modify noun phrases
			for child in chunks:
				if type( child ) == nltk.tree.Tree:
					if child.label() == 'NP':
						if 'NNP' in child.leaves()[0][1]:
							noun = child.leaves()[0][0]
							chunked.extend( child.leaves()[1:] )

							prep = ('for', 'IN' )
							is_sub = pns.search( q.sub == noun )
							if is_sub and is_sub[0]['sub'] != is_sub[0]['word']:
								sub_type = noun.split(' ')[0]
								if sub_type == 'Person':
									prep = ('with', 'IN')

							chunked.append( prep )
							chunked.append( child.leaves()[0] )
						else: 
							print( '** uh oh ** ' )
					if child.label() == 'INNN':
						children = child.leaves()
						children.insert(1, ('a', 'DT'))
						chunked.extend( children )
				else:
					chunked.append( child )

			# add a verb if it needs one
			verbs = [t for t in chunked if 'VB' in t[1]]
			if not verbs:
				noun, pos = [t for t in chunked if re.match( r'NNS*', t[1] )][0] # first noun (?)
				sing = noun.lower() 

				# get type
				sub_type = ''
				is_sub = pns.search( q.sub == noun )
				if is_sub and is_sub[0]['sub'] != is_sub[0]['word']:
					sub_type = noun.split(' ')[0]


				
				if 'S' in pos:  # noun is plural
					sing = wnl.lemmatize( sing, 'n' )
				elif noun not in weird_nouns and noun[-3:] != 'ing' and sub_type != 'Place': # noun is singular and not "nothing" or gerund
					print( word, pos, sub_type, sub_type != 'Place' )
					if 'P' in pos or noun == 'LOA':  # prop noun gets the
						chunked.insert(0, ('the', 'DT') ) 
					else:
						chunked.insert(0, ('a', 'DT') ) # add an article
				
				related = get_related_word( sing )
				if related:
					verb = random.choice( list(related) )
					chunked.insert(0, (verb, 'VB') )
				else:
					search = '*'
					if noun in comps['verbs']:
						search = noun
					elif sub_type in comps['verbs']:
						search = sub_type
					
					verb = random.choice( comps['verbs'][search])
					chunked.insert(0, (verb, 'VB') )

			events.append( ' '.join([t[0] for t in chunked if any( c.isalpha() for c in t[1])]) )

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
