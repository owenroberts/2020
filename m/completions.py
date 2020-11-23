# all the data for sentence completions etc
def completions():
	return {
		'first_sent': {
			'Monday': [
				"I have a case of the Mondays."
			],
			'Tuesday': [
				"It's Tuesday."
			],
			'Wednesday': [
				"Hump day!"
			],
			'Thursday': [
				"It's Thursday."
			],
			'Friday': [
				"Thank god it's Friday."
			],
			'Saturday': [
				"Working on Saturday."
			],
			'Sunday': [
				"Working on the Lord's day."
			]
		},
		'non-alpha': {
			'?': [
				"don't know what I do"
			]
		},
		'verbs': {
			'*': [
				'work on',
				'do'
			],
			'Place': [
				'travel to'
			],
			'nothing': [
				'do'
			]
		}
	}