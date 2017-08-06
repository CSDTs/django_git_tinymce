def find_file_oid_in_tree(filename, tree):
	for entry in tree:
		if entry.name == filename:
			return entry.id
		else:
			return 404


def create_commit(user, repo, message, filename):
	from pygit2 import Signature
	# example:
	'''
	author = Signature('Alice Author', 'alice@authors.tld')
	committer = Signature('Cecil Committer', 'cecil@committers.tld')
	tree = repo.TreeBuilder().write()
	repo.create_commit(
		'refs/heads/master', # the name of the reference to update
		author, committer, 'one line commit message\n\ndetailed commit message',
		tree, # binary string representing the tree object ID
		[] # list of binary strings representing parents of the new commit
	)
	'''
	ref = 'refs/heads/master'
	author = Signature(user.username, user.email)
	committer = Signature(user.username, user.email)
	repo.index.add(filename)
	repo.index.write()
	tree = repo.index.write_tree()
	parent = None
	try:
		parent = repo.revparse_single('HEAD')
	except KeyError:
		pass

	parents = []
	if parent:
		parents.append(parent.oid.hex)

	sha = repo.create_commit(ref, author, committer, message, tree, parents)
	return sha
