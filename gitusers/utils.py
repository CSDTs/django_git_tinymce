from repos.models import Repository

from pygit2 import Signature
from os import path


def owner_editor_check(repo, request_user):
    if not isinstance(repo, Repository):
        return False

    permission = False
    if request_user == repo.owner:
        permission = True
    if request_user in repo.editors.all():
        permission = True
    if request_user.is_superuser:
        permission = True

    if not permission:
        return False
    return True


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
    delete_item(repo, path.join(filename))
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
    delete_item(repo, path.join(directory, filename))
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


def delete_item(repo, file):
    index_tree = repo.index
    index_tree.read()
    files = []
    for e in index_tree:
        files.append(e.path)
    for f in files:
        # if the target file is found, or it exists in a subdirectory called file
        if f == file or f.startswith(file + '/'):
            try:
                index_tree.remove(f)
            except:
                pass
    index_tree.write()


def get_files_changed(git_repo, commit):
    files = []
    if commit.parents:
        for e in commit.tree.diff_to_tree(commit.parents[0].tree):
            files.append(e.delta.new_file.path)
    else:
        for e in commit.tree:
            files.append(e.name)

    return files
