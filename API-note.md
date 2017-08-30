### RepoListAPIView:

- [x] Search filter
- [x] ordering filter

```python
	# USAGE of search filter and ordering filter
	# api/?search=repo&ordering=name
	# api/?search=repo&ordering=-owner   # reverse ordering
```

### RepoCreateAPIView:

- [x] Save with requested user
- [x] Work with model post_save, auto slugifying
- [ ] Other save validation (i.e name check and etc...)

### RepoUpdateAPIView:

- [x] Custom permission class to check permission to update the repo
- [ ] Name validation according to ```clean_name()``` of ```repos.forms.RepositoryModelForm```
- [ ] Tag parsing

```python
	queryset = Repository.objects.all()
	serializer_class = RepositoryCreateUpdateSerializer
	lookup_fields = ('owner', 'slug')
	permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
```

### RepoDetailAPIView:

- [x] Multi-slug field mixin
- [ ] Override "context-passing" method in order to pass Pygit2 tree objects 

```python
    # specify lookup_fields for multi-slug mixin
	lookup_fields = ('owner', 'slug')
```

### RepoDeleteAPIView

---

### Demo

http://127.0.0.1:8000/api/admin/create/

http://127.0.0.1:8000/api/admin/repo1/

http://127.0.0.1:8000/api/?search=repo

http://127.0.0.1:8000/api/?search=repo&ordering=-owner

http://127.0.0.1:8000/api/admin/repo3/delete

---

### TODO API Views
- File creation
    - file name check
    - create_commit
- Blob edit
    - file content
    - commit message
- Blob raw data (relatively easy)
