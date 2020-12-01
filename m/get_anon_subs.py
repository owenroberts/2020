# tag the text and anonymize proper nouns and such

import re
from m import db
from m import subs # substitions
subs = subs.subs()

def strip_slashes( text ):
	return " ".join([w.replace('/', ' and ') for w in text.split(' ')])

def get_subs( text ):

	text = sub_text( text, 'abbreviations', True ) # sub common abbr for full words
	text = sub_text( text, 'special_abbreviations', False )
	text = sub_text( text, 'acronyms', True ) # sub common acronyms for full words
	text = strip_slashes( text )

	# search for things to remove
	records = db.re.all()
	for r in records:
		phrase, sub = r['phrase'], r['sub']
		r = r'\b' + re.escape( phrase ) + r'\b'
		if re.search( r, text ):
			text = re.sub( r, sub, text )

	# check for proper noun subs already added in the database
	pns = db.pns.all()
	for r in pns:
		word_list, sub = r['word'], r['sub']
		if sub not in word_list: # ignore words that sub themselves
			for word in word_list:
				if word in text:
					text = re.sub( r'\b' + word + r'\b', sub, text )

	return text

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