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
				'work on'
			],
			'Place': [
				'travel'
			],
			'nothing': [
				'do'
			]
		},
		'end': [
			"do nothing",
			"don't know what I do"
		],
		'eod': {
			'0': 'Not a bad day.',
			'1': 'Not a bad day.',
			'2': 'Not a bad day.',
			'3': 'Not a bad day.',
			'4': 'Not a bad day.',
			'5': 'Not a bad day.',
			'6': 'Not a bad day.',
			'7': 'Not a bad day.',
			'8': 'Not a bad day.',
			'9': 'Not a bad day.',
			'10': 'Not a bad day.',
			'11': 'Not a bad day.',
			'12': 'Not a bad day.',
			'13': 'Not a bad day.',
			'14': 'Not a bad day.',
			'15': 'Not a bad day.',
			'16': 'I\'m watching the clock.',
			'17': 'I\'m ready to get out of here.',
			'18': 'What a day.',
			'19': 'What a long day.',
			'20': 'What a long day.',
			'21': 'I\'m never going to get out of here.',
			'22': 'I\'m never going to get out of here.',
			'23': 'It\' getting late.',
			'24': 'It\' getting late.',
		},
		'busy': {
			'0': 'Didn\'t do too much today. ',
			'1': 'Pretty normal load today. ',
			'2': 'I have way too much to do. '
		}
	}