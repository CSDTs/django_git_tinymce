from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from repos.models import Repository

from os.path import join


User = get_user_model()


class RepoModelTest(TestCase):
    def setUp(self):
        jacob = User.objects.create_user(
            username='jacob',
            email='jacob@email.com',
            password='top_secret'
        )

        Repository.objects.create(name='testRepoUser', owner=jacob)
        Repository.objects.create(name='teEst 1 2 3', owner=jacob)

    def test_create_with_anonymousUser(self):
        anon = AnonymousUser()
        self.assertRaises(
            ValueError,
            Repository.objects.create,
            name='teEst 1 2 3 4',
            owner=anon
        )

    def test_creation(self):
        repo = Repository.objects.get(name='testRepoUser', owner__username='jacob')

        self.assertEqual(repo.name, 'testRepoUser')
        self.assertEqual(repo.owner.username, 'jacob')
        self.assertEqual(repo.slug, 'testrepouser')
        self.assertEqual(
            repo.get_repo_path(),
            join(
                settings.REPO_DIR,
                repo.owner.username,
                str(repo.pk)
            )
        )
        self.assertEqual(repo.__str__(), 'testRepoUser - jacob')

    def test_slugify(self):
        repo = Repository.objects.get(name='teEst 1 2 3', owner__username='jacob')

        self.assertEqual(repo.slug, 'teest-1-2-3')
