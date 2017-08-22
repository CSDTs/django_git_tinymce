from rest_framework.generics import ListAPIView

from repos.models import Repository
from .serializers import RepositorySerializer

class RepoListAPIView(ListAPIView):
	queryset = Repository.objects.all()
	serializers_class = RepositorySerializer