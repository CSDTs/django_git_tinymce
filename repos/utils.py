from django.conf import settings

from . import preset_html

import pygit2

import os
import time


def repo_setup(git_repo, repo_instance):
    if not isinstance(git_repo, pygit2.Repository):
        raise TypeError("git_object is not a pygit2 Repository object")

    if git_repo.head_is_unborn:
        s = pygit2.Signature('Repo_Init', 'csdtrpi@gmail.com', int(time.time()), 0)
        data = '<p><h1>{}</h1></p>'.format(repo_instance)
        fn = 'README.html'
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # data = preset_html.left_navbar
        # # fn = "nav_" + repo_instance.slug + ".html"
        # fn = "left_navbar"
        # f = open(os.path.join(git_repo.workdir, fn), 'w')
        # f.write(data)
        # f.close()
        # # b = git_repo.create_blob_fromworkdir(fn)
        # git_repo.index.read()
        # git_repo.index.add(fn)
        # git_repo.index.write()

        # index.html
        data = preset_html.index_html
        fn = "index.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # background.html
        data = preset_html.background
        fn = "background.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # origin.html
        # data = """
        # <h1>Origins</h1>
        # <p><img src="./img/{0}.png"></p>
        # <p>Origins.html</p>
        # """.format(repo_instance.slug)
        # fn = "origins.html"
        # f = open(os.path.join(git_repo.workdir, fn), 'w')
        # f.write(data)
        # f.close()
        # # b = git_repo.create_blob_fromworkdir(fn)
        # git_repo.index.read()
        # git_repo.index.add(fn)
        # git_repo.index.write()

        # tutorial.html
        # data = """
        # <h1>Tutorial</h1>
        # <p><img src="./img/{0}.png"></p>
        # <p>Tutorial.html</p>
        # """.format(repo_instance.slug)
        # fn = "tutorial.html"
        # f = open(os.path.join(git_repo.workdir, fn), 'w')
        # f.write(data)
        # f.close()
        # git_repo.index.read()
        # git_repo.index.add(fn)
        # git_repo.index.write()

        # software.html
        # data = """
        # <h1>Software</h1>
        # <p><img src="./img/{0}.png"></p>
        # <p>Software.html</p>
        # """.format(repo_instance.slug)
        # fn = "software.html"
        # f = open(os.path.join(git_repo.workdir, fn), 'w')
        # f.write(data)
        # f.close()
        # git_repo.index.read()
        # git_repo.index.add(fn)
        # git_repo.index.write()

        # teaching.html
        # data = """
        # <h1>Teaching Materials</h1>
        # <p><img src="./img/{0}.png"></p>
        # <p>Teaching.html</p>
        # """.format(repo_instance.slug)
        # fn = "teaching.html"
        # f = open(os.path.join(git_repo.workdir, fn), 'w')
        # f.write(data)
        # f.close()
        # git_repo.index.read()
        # git_repo.index.add(fn)
        # git_repo.index.write()

        # img/git_repo.png
        with open(os.path.join(settings.STATIC_ROOT, '../img/default_image.png'), 'rb') as f:
            data = f.read()

        fn = "{}.png".format(repo_instance.slug)
        # f = open(os.path.join(git_repo.workdir, 'img', fn), 'w')
        # f.write(data)
        # f.close()

        if not os.path.exists(os.path.join(repo_instance.get_repo_path(), 'img')):
            try:
                os.makedirs(os.path.dirname(os.path.join(repo_instance.get_repo_path(), 'img', fn)))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:  # noqa: F821
                    raise
        try:
            file = open(os.path.join(repo_instance.get_repo_path(), 'img', fn), 'wb')
        except OSError:
            pass
        # with open(fn, 'wb') as f:
        #     f.write(data)
        file.write(data)
        file.close()

        git_repo.index.read()
        git_repo.index.add(os.path.join('img', fn))
        git_repo.index.write()
        tree2 = git_repo.index.write_tree()

        git_repo.create_commit('HEAD', s, s, 'Initialized repo\
            with a nav_{}.html, README.html, and pages'.format(repo_instance.slug), tree2, [])
