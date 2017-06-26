from re import escape

from django.utils.text import slugify

def check_repo_name(name):
	name = slugify(name)

	return name