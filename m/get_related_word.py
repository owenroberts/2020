# use concept net to get a verb related to a noun
# if concept net doesn't get anything, try wordnet
# or just get everything from both?

import requests
from nltk.corpus import wordnet as wn

cn_url = 'http://api.conceptnet.io/c/en/'

exceptions = ['e_mail']

# add pos if necessary - now its only getting verbs

def get_related_word( word ):
	# print( '** word:', word, '**' ) 

	data = requests.get( f'{cn_url}/{word}' ).json()
	# print( data )
	related = set()

	for edge in data['edges']:
		if 'language' in edge['end'].keys():
			if edge['end']['language'] == 'en':
				if 'sense_label' in edge['end'].keys():
					if 'v,' in edge['end']['sense_label']:
						w = edge['end']['term'].split('/')[3]
						w = w.replace( '_', '' if w in exceptions else ' ' )
						related.add( w )

	# print( 'concept net:', related )

	# if len( related ) == 0:
	syns = wn.synsets( word )
	verbs = [s for s in syns if 'v' in s.name().split('.')[1]]
	lemmas = [lemma.name().replace( '_', ' ' ) for verb in verbs for lemma in verb.lemmas()]
	entailments = [ent for verb in verbs for ent in verb.entailments()]
	ent_lemmas = [lemma.name().replace( '_', ' ' ) for entailment in entailments for lemma in entailment.lemmas()]
	related.update( lemmas )
	related.update( ent_lemmas )

	# print( 'entailments:', ent_words )

	return list( related )

if __name__ == "__main__":
    import sys
    print( get_related_word( sys.argv[1] ) )
