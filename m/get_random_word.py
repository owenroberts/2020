# get a random word (for adverbs and adjectives)

from random import choice
from nltk.corpus import wordnet as wn

words = {}
words['r'] = list( wn.all_synsets( 'r' ) )  # adverbs
words['s'] = list( wn.all_synsets( 's' ) )  # adjectives

def get_random_word( pos ):
	word = choice( words[pos] ).name().split( '.' )[0]
	return word.replace( '_', ' ' )
