from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from repos.models import Repository


def create_repo(name, username):
	"""
	Creates a question with the given `question_text` and published the
	given number of `days` offset to now (negative for questions published
	in the past, positive for questions that have yet to be published).
	"""
	user, created = User.objects.get_or_create(
		username=username,
		email=username + '@email.com',
		password='top_secret'
	)

	return Repository.objects.create(name=name, owner=user)


class RepositoryListViewTests(TestCase):
	def test_view_with_no_questions(self):
		'''
		If no repositories exist, an appropriate message should be displayed
		'''
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)
		# self.assertContains(response, 'No repositories')
		self.assertQuerysetEqual(response.context['repository_list'], [])

	def test_index_view_with_one_repo(self):
		"""
		Test output with one repo.
		"""
		create_repo(name="testrepo1", username="bob")
		response = self.client.get(reverse('index'))

		self.assertQuerysetEqual(
			response.context['repository_list'],
			['<Repository: testrepo1 - bob>']
		)
