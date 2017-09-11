from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.text import slugify
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
	CreateView,
	UpdateView,
	DeleteView,
	FormView,
)
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy

from .utils import find_file_oid_in_tree, create_commit, create_commit_folders, delete_commit, delete_commit_folders, find_file_oid_in_tree_using_index
from django_git.mixins import OwnerRequiredMixin
from repos.forms import (
	RepositoryModelForm,
	RepositoryUpdateModelForm,
	TinyMCEFileEditForm,
	FileCreateForm,
	FileRenameForm,
	RepoForkRenameForm
)
from repos.models import Repository, ForkedRepository
from tags.models import Tag

from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE

import pygit2
from os import path
from shutil import copytree
import os
import time
from pathlib import Path
import shutil
import datetime


User = get_user_model()

class IndexView(LoginRequiredMixin, ListView):
	model = Repository
	template_name = 'gituser/index.html'

	def get_queryset(self):

		queryset = Repository.objects.filter(owner=self.request.user)

		search_query = self.request.GET.get('search')
		if search_query:
			queryset = queryset.filter(
				Q(name__icontains=search_query) |
				Q(description__icontains=search_query)
			).order_by('name')
		return queryset


class IndividualIndexView(LoginRequiredMixin, ListView):
	model = Repository
	template_name = 'gituser/index.html'

	def get_queryset(self):
		user = self.kwargs['username']
		user_specific = User.objects.get(username=user)
		queryset = Repository.objects.filter(owner=user_specific.id)

		search_query = self.request.GET.get('search')
		if search_query:
			queryset = queryset.filter(
				Q(name__icontains=search_query) |
				Q(description__icontains=search_query)
			).order_by('name')
		return queryset


# User's repo list view - profile/dashboard
class RepositoryListView(LoginRequiredMixin, ListView):
	model = Repository
	template_name = 'gituser/index.html'

	def get_queryset(self):
		queryset = Repository.objects.filter(owner=self.request.user)
		return queryset


class RepositoryCreateView(LoginRequiredMixin, CreateView):
	model = Repository
	template_name = 'repo/create.html'
	form_class = RepositoryModelForm
	# success_url is default to model's get_absolute_url.

	def get_form_kwargs(self):
		kwargs = super(RepositoryCreateView, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_valid(self, form):
		user = self.request.user
		form.instance.owner = user

		valid_data = super(RepositoryCreateView, self).form_valid(form)

		tags = form.cleaned_data.get("tags")
		if tags:
			tags_list = tags.split(',')

			for tag in tags_list:
				tag = str(tag).strip()
				if tag == '' or tag is None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(form.instance)

		return valid_data


class RepositoryDetailView(DetailView):
	model = Repository
	template_name = 'repo/repo_detail.html'

	def get_queryset(self):
		queryset = super(RepositoryDetailView, self).get_queryset()

		return queryset.filter(owner__username=self.kwargs.get('username'))

	def get_context_data(self, **kwargs):
		context = super(RepositoryDetailView, self).get_context_data(**kwargs)

		repo_obj = self.get_object()
		user = self.request.user

		# open repo dir and display repo files
		try:
			git_repo = pygit2.Repository(repo_obj.get_repo_path())

			context['is_owner'] = True if repo_obj.owner == user else False

			if git_repo.is_empty:
				context['empty'] = True

				return context
			else:
				# get last commit
				commit = git_repo.revparse_single('HEAD')
				tree = commit.tree
				tree = sorted(tree, key=lambda entry: entry.filemode)

				context['tree'] = tree
				context['branches'] = list(git_repo.branches)
				context['last_commit'] = commit
				context['branch_name'] = "master"
				context['tab'] = "files"

		except IOError:
			raise Http404("Repository does not exist")

		return context

class ReduxRepositoryDetailView(View):
	template_name = 'repo/redux_repo.html'
	component = 'repo/src/client.min.js'


	def get(self, request, slug, username):
    	# gets passed to react via window.props
		owner_name = self.kwargs['username']
		repo_name = self.kwargs['slug']
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs['directories']
		user = User.objects.get(username=owner_name)
		repo = Repository.objects.get(owner=user.id,name__iexact=repo_name)
		forked_repos = ForkedRepository.objects.filter(original=repo)
		fork_count = len(forked_repos)
		print('repo.id', repo.id)
		try:
			orig_fork = ForkedRepository.objects.get(fork__id=repo.id)
			if orig_fork:
				is_fork = True
			orig = orig_fork.original
			print('orig_fork', orig_fork)
			fork_name = orig.name
			fork_owner = orig.owner.username
		except:
			orig_fork = None
			is_fork = False
			orig = None
			fork_name = None
			fork_owner = None

		props = {
					'repo_name': repo_name,
					'repo_owner': owner_name,
					'repo_owner_id' : user.id,
					'repo_id': repo.id,
					'directory': directory,
					'fork_count': fork_count,
					'is_fork': is_fork,
					'fork_name': fork_name,
					'fork_owner': fork_owner,



		}

		context = {

        	'component': self.component,
        	'props': props,
		}

		return render(request, self.template_name, context)

class ReduxRepositoryFolderDetailView(View):

	template_name = 'repo/redux_repo.html'
	component = 'repo/src/client.min.js'


	def get(self, request, slug, username, directories, directories_ext=None):
    	# gets passed to react via window.props
		owner_name = self.kwargs['username']
		repo_name = self.kwargs['slug']
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs['directories']
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs['directories_ext']
		user = User.objects.get(username=owner_name)
		repo = Repository.objects.get(owner=user.id,name__iexact=repo_name)
		forked_repos = ForkedRepository.objects.filter(original=repo)
		fork_count = len(forked_repos)
		try:
			orig_fork = ForkedRepository.objects.get(fork__id=repo.id)
			if orig_fork:
				is_fork = True
			orig = orig_fork.original
			print('orig_fork', orig_fork)
			fork_name = orig.name
			fork_owner = orig.owner.username
		except:
			orig_fork = None
			is_fork = False
			orig = None
			fork_name = None
			fork_owner = None

		props = {
					'repo_name': repo_name,
					'repo_owner': owner_name,
					'repo_owner_id' : user.id,
					'repo_id': repo.id,
					'directory': directory,
					'fork_count': fork_count,
					'is_fork': is_fork,
					'fork_name': fork_name,
					'fork_owner': fork_owner,


		}

		context = {

        	'component': self.component,
        	'props': props,
		}

		return render(request, self.template_name, context)




class RepositoryForkView(LoginRequiredMixin, FormView):
	template_name = 'repo/rename_forked_repo.html'
	form_class = RepoForkRenameForm


	def get_success_url(self):
		return reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.request.user.username,
				'slug': self.kwargs.get('slug')

			}
		)


	def get(self, request, *args, **kwargs):

		User = get_user_model()
		username_in_url = self.kwargs.get("username")
		# prevents forking your own repo:
		if username_in_url == request.user.username:
			raise Http404("You cannot fork your own repo")
		origin_user = User.objects.get(username=username_in_url)
		origin_repo = self.kwargs.get("slug")
		origin_repo = Repository.objects.get(slug=origin_repo, owner=origin_user)

		context = {}
		context['form'] = RepoForkRenameForm()

		try:
			obj = Repository.objects.get(
				slug=origin_repo.name,
				owner=request.user
			)

			context['message'] = "You already have a repo with the same name. Please rename your fork:"

		except Repository.DoesNotExist:

			obj = Repository.objects.create(
				name=origin_repo.name,
				description=origin_repo.description,
				owner=request.user
			)
			src = origin_repo.get_repo_path()
			dst = obj.get_repo_path()
			try:
			    #if path already exists, remove it before copying with copytree()
			    if os.path.exists(dst):
			        shutil.rmtree(dst)
			        shutil.copytree(src, dst)
			except OSError as e:
			    # If the error was caused because the source wasn't a directory
			    if e.errno == errno.ENOTDIR:
			       shutil.copy(source_dir_prompt, destination_dir_prompt)
			    else:
			        print('Directory not copied. Error: %s' % e)

			new_entry = ForkedRepository(original=origin_repo, fork=obj)
			# not sure why this isn't needed:
			# new_entry.save()


			return HttpResponseRedirect(reverse(
				'gitusers:repo_detail',
				args=(request.user.username, obj.slug))
			)


		return render(request, self.template_name, context)

	def form_valid(self, form):
		valid_data = super(RepositoryForkView, self).form_valid(form)
		User = get_user_model()
		username_in_url = self.kwargs.get("username")
		origin_user = User.objects.get(username=username_in_url)
		new_reponame = form.cleaned_data.get("new_reponame")
		origin_repo = self.kwargs.get("slug")
		origin_repo = Repository.objects.get(slug=origin_repo, owner=origin_user)
		obj = Repository.objects.create(
			name=new_reponame,
			description=origin_repo.description,
			owner=self.request.user
		)
		src = origin_repo.get_repo_path()
		dst = obj.get_repo_path()
		try:
			#if path already exists, remove it before copying with copytree()
			if os.path.exists(dst):
				shutil.rmtree(dst)
				shutil.copytree(src, dst)
		except OSError as e:
			# If the error was caused because the source wasn't a directory
			if e.errno == errno.ENOTDIR:
			   shutil.copy(source_dir_prompt, destination_dir_prompt)
			else:
				print('Directory not copied. Error: %s' % e)

		new_entry = ForkedRepository(original=origin_repo, fork=obj)
		new_entry.save()

		return HttpResponseRedirect(reverse(
			'gitusers:repo_detail',
			args=(self.request.user.username, obj.slug))
		)



class RepositoryUpdateView(OwnerRequiredMixin, UpdateView):
	model = Repository
	template_name = 'repo/setting.html'
	form_class = RepositoryUpdateModelForm
	id = None

	def get_object(self):
		queryset = super(RepositoryUpdateView, self).get_queryset()
		queryset = queryset.get(owner__username=self.kwargs.get('username'),slug=self.kwargs.get('slug'))
		return queryset

	def get_form_kwargs(self):
		kwargs = super(RepositoryUpdateView, self).get_form_kwargs()
		kwargs.update({'request': self.request})
		kwargs.update({'old_name': self.object.name})
		return kwargs

	def get_initial(self):
		initial = super(RepositoryUpdateView, self).get_initial()
		tags = self.get_object().tag_set.all()
		initial['tags'] = ", ".join([tag.title for tag in tags])
		return initial

	def form_valid(self, form):
		valid_data = super(RepositoryUpdateView, self).form_valid(form)
		tags = form.cleaned_data.get("tags")
		# de-associate all associated tags and re-create them
		# so that we don't have to go through and compare with get_initial()
		# all again.
		obj = self.get_object()

		slug = slugify(form.cleaned_data.get("name"))
		obj.slug = slug


		obj.tag_set.clear()

		if tags:
			tags_list = tags.split(',')

			for tag in tags_list:
				tag = str(tag).strip()
				if tag == '' or tag is None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(self.get_object())
		obj.save()

		# return HttpResponseRedirect(reverse(
		# 	"gitusers:repo_detail",
		# 	kwargs={
		# 		'username': self.kwargs.get('username'),
		# 		'slug': slug
		#
		# 	}
		# )
		# )


		# return valid_data

		return HttpResponseRedirect(reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.kwargs.get('username'),
				'slug': slug

			}
		)
		)

	# def get_success_url(self):
	#
	# 	return reverse(
	# 		"gitusers:index",
	# 		kwargs={
	# 			'username': self.object.owner,
	# 			# 'slug': self.object.slug
	#
	# 		}
	# 	)





class RepositoryDeleteView(OwnerRequiredMixin, DeleteView):
	model = Repository
	template_name = 'repo/delete.html'
	success_url = reverse_lazy('index')

	def get_queryset(self):
		queryset = super(RepositoryDeleteView, self).get_queryset()

		return queryset.filter(owner__username=self.kwargs.get('username'))


class RepositoryCreateFileView(OwnerRequiredMixin, FormView):
	template_name = 'repo/create_file.html'
	form_class = FileCreateForm

	def get_initial(self, **kwargs):
		initial = super(RepositoryCreateFileView, self).get_initial()
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs['directories']
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs['directories_ext']
		if directory != "":
			initial['filename'] = directory + '/.html'
		else:
			initial['filename'] = '.html'
		return initial

	def form_valid(self, form):
		filename = form.cleaned_data['filename']
		filecontent = form.cleaned_data['content']
		commit_message = form.cleaned_data['commit_message']

		repo = Repository.objects.get(
			owner=self.request.user,
			slug=self.kwargs['slug']
		)
		git_repo = pygit2.Repository(repo.get_repo_path())

		if not git_repo.is_empty:
			commit = git_repo.revparse_single('HEAD')
			tree = commit.tree

			if find_file_oid_in_tree(filename, tree) != 404:
				form.add_error(None, "File named {} already exists".format(filename))
				return self.form_invalid(form)
		dirname = ""
		filename2 = filename
		if ".." in filename:
			form.add_error(None, "Can't have '..' anywhere in directories structure")
			return self.form_invalid(form)
		if "/" in filename:
			# import re
			# pattern = re.compile(r"^(.+)/([^/]+)$")
			# matches = pattern.search(filename)
			# print('matches', matches)
			dirname, filename2 = os.path.split(filename)

		if not os.path.exists(path.join(repo.get_repo_path(), dirname)):
		    try:
		        os.makedirs(os.path.dirname(path.join(repo.get_repo_path(), dirname, filename2)))
		    except OSError as exc: # Guard against race condition
		        if exc.errno != errno.EEXIST:
		            raise
		print('dirname', dirname)
		print('filename2', filename2)
		file = open(path.join(repo.get_repo_path(), dirname, filename2), 'w')
		file.write(filecontent)
		file.close()


		b = git_repo.create_blob_fromworkdir(path.join(dirname, filename2))
		bld = git_repo.TreeBuilder()
		bld.insert(filename2, b, os.stat(os.path.join(repo.get_repo_path(), dirname, filename2)).st_mode )
		t = bld.write()
		# git_repo.index.read()
		# git_repo.index.add(path.join( dirname, filename2))
		# git_repo.index.write()
		email = "nonegiven@nonegiven.com"
		if self.request.user.email:
			email = self.request.user.email
		# s = pygit2.Signature(self.request.user.username, email, int(time()), 0)
		#s = pygit2.Signature('Alice Author', 'alice@authors.tld', int(time()), 0)
		#c = git_repo.create_commit('HEAD', s,s, commit_message, t, [git_repo.head.target])


		create_commit_folders(self.request.user, git_repo, commit_message, filename2, dirname)

		return super(RepositoryCreateFileView, self).form_valid(form)

	def get_success_url(self):
		if 'directories_ext' in self.kwargs:
			return reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories'),
					'directories_ext': self.kwargs.get('directories_ext')
				}
			)
		if 'directories' in self.kwargs:
			return reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories')
				}
			)
		return reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.request.user.username,
				'slug': self.kwargs.get('slug')

			}
		)


class BlobEditView(OwnerRequiredMixin, FormView):
	template_name = 'repo/file_edit.html'
	form_class = TinyMCEFileEditForm
	blob = None
	repo = None
	repo_obj = None

	def get_initial(self, **kwargs):
		self.success_url = '/{}/{}'.format(self.request.user, self.kwargs['slug'])

		initial = super(BlobEditView, self).get_initial()

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs.get('directories')
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs.get('directories_ext')
		try:
			self.repo_obj = Repository.objects.get(
				owner=self.request.user,
				slug=self.kwargs['slug']
			)

			self.repo = pygit2.Repository(self.repo_obj.get_repo_path())

			if self.repo.is_empty:
				raise Http404

			index_tree = self.repo.index
			commit = self.repo.revparse_single('HEAD')
			tree = commit.tree
			# blob = self.repo[find_file_oid_in_tree(filename, tree)]
			#
			# print('directory', directory)
			# if directory != "":
			# 	item = tree.__getitem__(str(directory))
			# 	print('item', item)
			# 	index_tree.read_tree(item.id)

			if directory != "":
				folders = directory.split("/")
				dir = ""
				for folder in folders:
					dir += folder + "/"
					item = tree.__getitem__(str(dir))
					index_tree.read_tree(item.id)
					print('index_tree_int', index_tree)

			print('find_file_oid_in_tree_using_index(filename, index_tree)', find_file_oid_in_tree_using_index(filename, index_tree))
			blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
			blob = self.repo[blob_id]


			if not blob.is_binary and isinstance(blob, pygit2.Blob):
				initial['content'] = blob.data

		except IOError:
			raise Http404("Repository does not exist")
		return initial

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.

		# Base object is immutable and Blob doesn't have a constructor
		# Have to directly change the actually file in file system
		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		directory = ""
		if self.kwargs.get('directories'):
			directory = self.kwargs.get('directories')
		if self.kwargs.get('directories_ext'):
			directory += "/" + self.kwargs.get('directories_ext')

		user = self.request.user
		print('user', user.email)

		try:
			repo_path = self.repo_obj.get_repo_path()
			file = open(path.join(repo_path, directory, filename), 'w')

			file.truncate()
			file.write(form.cleaned_data['content'])

			file.close()

			commit_message = form.cleaned_data['commit_message']
			commit_message = str(filename) + ' ' + commit_message
			# sha = create_commit(user, self.repo, commit_message, filename)
			print ('filename', filename)
			print('directory', directory)
			create_commit_folders(user, self.repo, commit_message, filename, directory)

		except OSError:
			raise form.ValidationError("Save error, please check the file.")

		return super(BlobEditView, self).form_valid(form)


class BlobRawView(View):
	def get(self, request, **kwargs):

		filename = self.kwargs.get('filename')
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs.get('directories')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs.get('directories_ext')
		repo_obj = None

		try:
			repo_obj = Repository.objects.get(
				owner__username=self.kwargs.get('username'),
				slug=self.kwargs['slug']
			)
			repo = pygit2.Repository(repo_obj.get_repo_path())

			if repo.is_empty:
				print('asdfasdfasdfasfd')
				raise Http404("The repository is empty")

		except:
			raise Http404("Failed to open repository")

		try:
			index_tree = repo.index
			commit = repo.revparse_single('HEAD')
			tree = commit.tree
			if directory != "":
				folders = directory.split("/")
				dir = ""
				for folder in folders:
					dir += folder + "/"
					item = tree.__getitem__(str(dir))
					index_tree.read_tree(item.id)
					print('index_tree_int', index_tree)
			# if directory != "":
			# 	item = tree.__getitem__(path.join(directory, filename))
			# 	index_tree.read_tree(item.id)
			# 	print('index_tree_int', index_tree)
			blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
			if blob_id != 404:
				return HttpResponse(repo[blob_id].data)
			else:
				raise Http404("Read raw data error")

		except OSError:
			raise Http404("Failed to open or read file")

# Not Working:
class BlobDeleteView(DeleteView):

	template_name = 'repo/delete.html'
	# success_url = reverse_lazy('index')

	def get(self, request, **kwargs):

		filename = self.kwargs.get('filename')

		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		repo_obj = None

		try:
			repo_obj = Repository.objects.get(
				owner__username=self.kwargs.get('username'),
				slug=self.kwargs['slug']
			)
			repo = pygit2.Repository(repo_obj.get_repo_path())

			if repo.is_empty:
				print('asdfasdfasdfasfd')
				raise Http404("The repository is empty")

		except:
			raise Http404("Failed to open repository")

		commit = repo.revparse_single('HEAD')
		tree = commit.tree
		blob_id = find_file_oid_in_tree(filename, tree)
		file_name = str(filename)
		commit_message = str(filename) + ' deleted'
		delete_commit(self.request.user, repo, commit_message, filename)
		try:
			os.remove(os.path.join(repo.workdir) +  file_name)
		except OSError:
			pass
		return HttpResponseRedirect(reverse(
			'gitusers:repo_detail',
			args=(request.user.username, repo_obj.slug))
		)


class BlobDeleteFolderView(DeleteView):

	template_name = 'repo/delete.html'
	success_url = reverse_lazy('index')

	def get(self, request, **kwargs):

		filename = self.kwargs.get('filename')
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs['directories']
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs['directories_ext']

		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		repo_obj = None

		try:
			repo_obj = Repository.objects.get(
				owner__username=self.kwargs.get('username'),
				slug=self.kwargs['slug']
			)
			repo = pygit2.Repository(repo_obj.get_repo_path())

			if repo.is_empty:
				print('asdfasdfasdfasfd')
				raise Http404("The repository is empty")

		except:
			raise Http404("Failed to open repository")

		index_tree = repo.index
		commit = repo.revparse_single('HEAD')
		tree = commit.tree
		print('str(directory)', str(directory))
		print('directory.split("/")', directory.split("/"))
		folders = directory.split("/")
		for folder in folders:
			try:
				item = tree.__getitem__(str(folder))
				index_tree.read_tree(item.id)
			except:
				pass
		blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
		print('index_tree.__contains__(filename)', index_tree.__contains__(filename))
		# index_tree.remove(str(filename))
		# index_tree.write()
		# for entry in index_tree:
			# print('entry.path', entry.path)


		file_name = str(filename)
		print('file_name', file_name)
		commit_message = str(filename) + ' deleted'
		delete_commit_folders(self.request.user, repo, commit_message, file_name, directory)
		try:
			os.remove(os.path.join(repo.workdir, directory, file_name))
		except OSError:
			pass
		if 'directories_ext' in self.kwargs:
			return HttpResponseRedirect(reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories'),
					'directories_ext': self.kwargs.get('directories_ext')
				}
			)
		)
		if 'directories' in self.kwargs:
			return HttpResponseRedirect(reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories')
				}
			)
		)
		return HttpResponseRedirect(reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.request.user.username,
				'slug': self.kwargs.get('slug')

			}
		)
		)


class RenameFileView(FormView):
	template_name = 'repo/rename_file.html'
	form_class = FileRenameForm
	def get_initial(self, **kwargs):
		self.success_url = '/{}/{}'.format(self.request.user, self.kwargs['slug'])

		initial = super(RenameFileView, self).get_initial()

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		directory = ""
		if 'directories' in self.kwargs:
			directory = self.kwargs.get('directories')
		if 'directories_ext' in self.kwargs:
			directory += "/" + self.kwargs.get('directories_ext')
		try:
			self.repo_obj = Repository.objects.get(
				owner=self.request.user,
				slug=self.kwargs['slug']
			)

			self.repo = pygit2.Repository(self.repo_obj.get_repo_path())

			if self.repo.is_empty:
				raise Http404

			index_tree = self.repo.index
			commit = self.repo.revparse_single('HEAD')
			tree = commit.tree
			# blob = self.repo[find_file_oid_in_tree(filename, tree)]
			#
			# print('directory', directory)
			# if directory != "":
			# 	item = tree.__getitem__(str(directory))
			# 	print('item', item)
			# 	index_tree.read_tree(item.id)

			if directory != "":
				folders = directory.split("/")
				dir = ""
				for folder in folders:
					dir += folder + "/"
					item = tree.__getitem__(str(dir))
					index_tree.read_tree(item.id)
					print('index_tree_int', index_tree)

			print('find_file_oid_in_tree_using_index(filename, index_tree)', find_file_oid_in_tree_using_index(filename, index_tree))
			blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
			blob = self.repo[blob_id]


			if not blob.is_binary and isinstance(blob, pygit2.Blob):
				initial['content'] = blob.data

		except IOError:
			raise Http404("Repository does not exist")
		return initial

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.

		# Base object is immutable and Blob doesn't have a constructor
		# Have to directly change the actually file in file system
		new_filename = form.cleaned_data['new_filename']
		print('new_filename', new_filename)
		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		directory = ""
		if self.kwargs.get('directories'):
			directory = self.kwargs.get('directories')
		if self.kwargs.get('directories_ext'):
			directory += "/" + self.kwargs.get('directories_ext')



		user = self.request.user
		print('user', user.email)


		repo_path = self.repo_obj.get_repo_path()
		# file = open(path.join(repo_path, directory, filename), 'w')
		# os.rename('a.txt', 'b.kml')
		old_file = os.path.join(repo_path, directory, filename)
		new_file = os.path.join(repo_path, directory, new_filename)
		my_file = Path(new_file)

		index_tree = self.repo.index
		if find_file_oid_in_tree_using_index(new_filename, index_tree) != 404:
			form.add_error(None, "File named {} already exists".format(new_filename))
			return self.form_invalid(form)
		os.rename(old_file, new_file)



		#file.truncate()
		#file.write(form.cleaned_data['content'])

		#file.close()

		commit_message = form.cleaned_data['commit_message']
		commit_message = 'Renamed ' + str(filename) + ' to ' + str(new_filename) + ' - ' + commit_message
		# sha = create_commit(user, self.repo, commit_message, filename)
		print ('filename', filename)
		print('directory', directory)
		delete_commit_folders(user, self.repo, commit_message, filename, directory)
		create_commit_folders(user, self.repo, commit_message, new_filename, directory)

		# except OSError:
		# 	raise form.ValidationError("Save error, please check the file.")

		# return super(RenameFileView, self).form_valid(form)
		if 'directories_ext' in self.kwargs:
			return HttpResponseRedirect(reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories'),
					'directories_ext': self.kwargs.get('directories_ext')
				}
			)
		)
		if 'directories' in self.kwargs:
			return HttpResponseRedirect(reverse(
				"gitusers:repo_detail_folder",
				kwargs={
					'username': self.request.user.username,
					'slug': self.kwargs.get('slug'),
					'directories': self.kwargs.get('directories')
				}
			)
		)
		return HttpResponseRedirect(reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.request.user.username,
				'slug': self.kwargs.get('slug')

			}
		)
		)

	def get(self, request, *args, **kwargs):
		context = super(RenameFileView, self).get_context_data(**kwargs)
		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		context['object'] = filename
		directory = ""
		if self.kwargs.get('directories'):
			directory = self.kwargs.get('directories')
		if self.kwargs.get('directories_ext'):
			directory += "/" + self.kwargs.get('directories_ext')
		context['directory'] = directory
		return render(request, self.template_name, context)


class ForkedReposView(ListView):
	model = Repository
	template_name = 'repo/forked_repos.html'

	def get_queryset(self):
		# queryset = super(ForkedReposView, self).get_queryset()

		self.owner_name = self.kwargs['username']
		self.repo_name = self.kwargs['slug']
		user = User.objects.get(username=self.owner_name)
		repo = Repository.objects.get(owner=user.id,name=self.repo_name)
		forked_repos = ForkedRepository.objects.filter(original=repo)
		return forked_repos

	def get_context_data(self, **kwargs):
		context = super(ForkedReposView, self).get_context_data(**kwargs)
		forked_repos = self.get_queryset()
		repos = []
		for repo in forked_repos:
			repo = Repository.objects.get(owner=repo.fork.owner,name=repo.fork.name)
			repos.append(repo)
		print('repos', repos)
		context['orig_repo'] = self.repo_name
		context['orig_author'] = self.owner_name
		context['repos'] = repos
		return context

class CommitLogView(ListView):
	model = Repository
	template_name = 'repo/commits.html'
	paginate_by = 200


	def get_queryset(self):
		# queryset = super(ForkedReposView, self).get_queryset()

		self.owner_name = self.kwargs['username']
		self.repo_name = self.kwargs['slug']
		user = User.objects.get(username=self.owner_name)
		repo = Repository.objects.get(owner=user.id,name=self.repo_name)
		try:
			git_repo = pygit2.Repository(repo.get_repo_path())
		except IOError:
			raise Http404("Repository does not exist")
		commits = []
		class Commit(object):
			message = ""
			hex = ""
			committer = ""
			commit_time = ""
			def __init__(self, hex, message, committer, commit_time):
				self.message = message
				self.hex = hex
				self.committer = committer
				self.commit_time = commit_time
		for commit in git_repo.walk(git_repo.head.target, GIT_SORT_TOPOLOGICAL):
			time = datetime.datetime.fromtimestamp(int(commit.commit_time)).strftime('%m-%d-%Y %H:%M:%S')

			commit_obj = Commit(commit.hex, commit.message, commit.committer.name, time)
			commits.append(commit_obj)

		return commits


	def get_context_data(self, **kwargs):
		context = super(CommitLogView, self).get_context_data(**kwargs)
		commits = self.get_queryset()
		context['orig_repo'] = self.repo_name
		context['orig_author'] = self.owner_name
		page = self.request.GET.get('page', 1)
		paginator = Paginator(commits, 200)
		try:
			commits = paginator.page(page)
		except PageNotAnInteger:
			commits = paginator.page(1)
		except EmptyPage:
			commits = paginator.page(paginator.num_pages)

		context['commits'] = commits
		return context


class CommitView(ListView):
	model = Repository
	template_name = 'repo/commit.html'
	# paginate_by = 200

	def get_queryset(self):
		queryset = super(CommitView, self).get_queryset()
		return queryset

	def get_context_data(self, **kwargs):
		context = super(CommitView, self).get_context_data(**kwargs)
		self.owner_name = self.kwargs['username']
		self.repo_name = self.kwargs['slug']
		self.commit_hex = self.kwargs['commit']
		context['orig_repo'] = self.repo_name
		context['orig_author'] = self.owner_name
		user = User.objects.get(username=self.owner_name)
		repo = Repository.objects.get(owner=user.id,name=self.repo_name)
		try:
			git_repo = pygit2.Repository(repo.get_repo_path())
		except IOError:
			raise Http404("Repository does not exist")
		try:
			commit = git_repo.revparse_single(self.commit_hex)
			context['message'] = commit.message
			context['hash'] = commit.hex
			diff  = git_repo.diff(commit.parents[0], commit).patch
			# patches = [p for p in diff]
			# old_files = []
			# hunks_files = []
			# for patch in patches:
			# 	old_files.append(patch.delta)
			# 	hunks_files.append(patch.hunks)
			context['diff'] = diff
			files = []
			for e in commit.tree:
				files.append(e.name)
			context['files'] = files
		except:
			context['message'] = None
			context['hash'] = self.commit_hex
			context['diff'] = None
			context['files'] = None
		# context['hunks'] = hunks_files

		return context