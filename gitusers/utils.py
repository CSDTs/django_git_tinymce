from pygit2 import Signature
from os import path


def find_file_oid_in_tree(filename, tree):
    for entry in tree:
        if entry.type == 'blob':
            if entry.name.lower() == filename.lower():
                return entry.id
    return 404


def find_file_oid_in_tree_using_index(filename, index_tree):
    for entry in index_tree:
        if entry.path.lower() == filename.lower():
            return entry.hex
    return 404


def find_folder_oid_in_tree(foldername, tree):
    for entry in tree:
        if entry.type == 'tree':
            if entry.name.lower() == foldername.lower():
                return entry.id
    return 404


def create_commit(user, repo, message, filename):
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
    # we don't require email addresses for accounts, so this throws an error
    # if that is the case for the user
    # ...making a default email, though I'm not sure how effective that is
    useremail = ""
    if user.email != "":
        useremail = user.email
    else:
        useremail = 'none@noemail.com'
    author = Signature(user.username, useremail)
    committer = Signature(user.username, useremail)
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


def create_commit_folders(user, repo, message, filename, directory):
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
    # we don't require email addresses for accounts, so this throws an error
    # if that is the case for the user
    # ...making a default email, though I'm not sure how effective that is
    useremail = ""
    if user.email != "":
        useremail = user.email
    else:
        useremail = 'none@noemail.com'
    author = Signature(user.username, useremail)
    committer = Signature(user.username, useremail)
    index_tree = repo.index
    index_tree.read()
    index_tree.add(path.join(directory, filename))
    index_tree.write()
    index_tree = repo.index
    tree2 = index_tree.write_tree()
    parent = None
    try:
        parent = repo.revparse_single('HEAD')
    except KeyError:
        pass
    parents = []
    if parent:
        parents.append(parent.oid.hex)
    sha = repo.create_commit(ref, author, committer, message, tree2, parents)
    return sha


def delete_commit(user, repo, message, filename):
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
    # we don't require email addresses for accounts, so this throws an error
    # if that is the case for the user
    # ...making a default email, though I'm not sure how effective that is
    useremail = ""
    if user.email != "":
        useremail = user.email
    else:
        useremail = 'none@noemail.com'
    author = Signature(user.username, useremail)
    committer = Signature(user.username, useremail)
    repo.index.remove(filename)
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


def delete_commit_folders(user, repo, message, filename, directory):
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
    # we don't require email addresses for accounts, so this throws an error
    # if that is the case for the user
    # ...making a default email, though I'm not sure how effective that is
    useremail = ""
    if user.email != "":
        useremail = user.email
    else:
        useremail = 'none@noemail.com'
    author = Signature(user.username, useremail)
    committer = Signature(user.username, useremail)
    index_tree = repo.index
    index_tree.read()
    index_tree.remove(path.join(directory, filename))
    index_tree.write()
    index_tree = repo.index

    tree2 = index_tree.write_tree()
    parent = None
    try:
        parent = repo.revparse_single('HEAD')
    except KeyError:
        pass

    parents = []
    if parent:
        parents.append(parent.oid.hex)

    sha = repo.create_commit(ref, author, committer, message, tree2, parents)
    return sha
