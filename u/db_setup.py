# for cl testing, set up db 
	# import db_setup
	# db, q, pns, pos = db_setup.setup()

def setup():
	from tinydb import TinyDB, Query
	import re
	db = TinyDB( 'db.json' )
	q = Query()
	pns = db.table( 'prop_noun_subs' )
	pos = db.table( 'pos_stats' )
	return db, q, pns, pos
