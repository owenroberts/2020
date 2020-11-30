# get a random word (for adverbs and adjectives)

from random import choice
from nltk.corpus import wordnet as wn

def get_random_word( pos ):

	word = choice( list( wn.all_synsets( pos ) ) ).name().split( '.' )[0]
	return word.replace( '_', ' ' )
