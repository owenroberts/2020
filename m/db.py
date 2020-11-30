# db utils

from tinydb import TinyDB, Query
from tinydb.operations import set

db = TinyDB( 'db.json' )
q = Query()

# tables
pns = db.table( 'prop_noun_subs' )
pos = db.table( 'pos_stats' )
ps = db.table( 'pos_sequences' )
re = db.table( 'replace' )
rv = db.table( 'related_verbs' ) # save related verbs from concept net to speed up commons verbs

# db funcs
def has_word( word_list, word ):
	return word in word_list

def add_word( word ):
	def transform( doc ):
		doc['word'].append( word )
	return transform

def get_type_len( t ):
	return len([r for r in pns.all() if t in r['sub']])

def pns_has_word( word ):
	return pns.search( q.word.test( has_word, word ) )

def add_pns_word( word, sub ):
	return pns.update( add_word( word ), q.sub == sub )

def add_pns_record( word, t ): # type
	n = get_type_len( t )
	s = f'{t}-{ n + 1 }'
	has_word = pns_has_word( word )
	if has_word:
		if word not in has_word[0]['word']:
			return update_pns_word( word, s )
	else:
		return pns.insert({'word': [word], 'sub': s })

def update_pns_word( word, sub ):
	return pns.update( set('sub', sub), q.word.test( has_word, word ) )

def type_recount( t ):
	count = 1
	records = [r for r in pns.all() if t in r['sub']]
	for rec in records:
		update_pns_word( rec['word'][0], f'{t}-{count}' )
		count = count + 1

def remove( phrase, sub ):
	return re.insert( { 'phrase': phrase, 'sub': sub if sub else '' } )
