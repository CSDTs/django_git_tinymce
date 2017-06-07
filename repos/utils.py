from re import escape

def check_repo_name(name):
	if name == '':
		return 'new-unamed-repo'

	name = escape(name)
	name = name.replace('\\', '')
	name = name.replace('\ ', '-')
	name = name.replace('/', '')
	name = name.replace(' ', '')

	return name