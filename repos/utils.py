from django.conf import settings

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
        # head = git_repo.lookup_reference('HEAD').resolve()

        # Nav bar:
        data = """
        <nav class="navbar navbar-inverse navbar-local visible-xs">\
    <div class="container-fluid">\
    <div class="navbar-header">\
        <a class="navbar-brand" href="/{1}/{2}/render/index.html">{0}</a>
        <button aria-expanded="false" class="navbar-toggle collapsed"
        data-target="#nav-menu" data-toggle="collapse" type="button">
        <span class="sr-only">Toggle navigation</span> <span class="icon-bar">
        </span> <span class="icon-bar"></span> <span class="icon-bar">
        </span></button>\
    </div>\
    <div class="collapse navbar-collapse navbar-right" id="nav-menu">\
        <ul class="nav navbar-nav">\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/index.html">Background</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/origins.html">Origins</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/teaching.html">Teaching Materials</a>\
            </li>\
        </ul>\
\
    </div>\
    </div>\
</nav>\
\
\
<!-- sidebar -->\
        <div class="stuck">\
            <div class="col-xs-6 col-sm-3 sidebar-offcanvas" id="sidebar" role="navigation">\
                <ul class="nav">\
                    <li class="active"><a href="/{1}/{2}/render/index.html">Background</a></li>\
                    <li class="indented"><a href="/{1}/{2}/render/origins.html">Origins</a></li>\
                    <li><a href="/{1}/{2}/render/tutorial.html">Tutorial</a></li>\
                    <li><a href="/{1}/{2}/render/software.html">Software</a></li>\
                    <li><a href="/{1}/{2}/render/teaching.html">Teaching Materials</a></li>\
                </ul>\
            </div>\
        </div>""".format(repo_instance.name, repo_instance.owner, repo_instance.slug)
        fn = "nav_" + repo_instance.slug + ".html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # index.html
        data = """
        <h1>{0}</h1>
        <p><img src="./img/{1}.png"></p>
        <p>Index.html</p>
        """.format(repo_instance.name, repo_instance.slug)
        fn = "index.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # origin.html
        data = """
        <h1>Origins</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Origins.html</p>
        """.format(repo_instance.slug)
        fn = "origins.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # tutorial.html
        data = """
        <h1>Tutorial</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Tutorial.html</p>
        """.format(repo_instance.slug)
        fn = "tutorial.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # software.html
        data = """
        <h1>Software</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Software.html</p>
        """.format(repo_instance.slug)
        fn = "software.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # teaching.html
        data = """
        <h1>Teaching Materials</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Teaching.html</p>
        """.format(repo_instance.slug)
        fn = "teaching.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

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


def repo_setup1(git_repo, repo_instance):
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
        # head = git_repo.lookup_reference('HEAD').resolve()

        # Nav bar:
        data = """
        <nav class="navbar navbar-inverse navbar-local visible-xs">\
    <div class="container-fluid">\
    <div class="navbar-header">\
        <a class="navbar-brand" href="/{1}/{2}/render/index.html">{0}</a>
        <button aria-expanded="false" class="navbar-toggle collapsed"
        data-target="#nav-menu" data-toggle="collapse" type="button">
        <span class="sr-only">Toggle navigation</span> <span class="icon-bar">
        </span> <span class="icon-bar"></span> <span class="icon-bar">
        </span></button>\
    </div>\
    <div class="collapse navbar-collapse navbar-right" id="nav-menu">\
        <ul class="nav navbar-nav">\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/index.html">Background</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/origins.html">Origins</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/teaching.html">Teaching Materials</a>\
            </li>\
        </ul>\
\
    </div>\
    </div>\
</nav>\
\
\
<!-- sidebar -->\
        <div class="stuck">\
            <div class="col-xs-6 col-sm-3 sidebar-offcanvas" id="sidebar" role="navigation">\
                <ul class="nav">\
                    <li class="active"><a href="/{1}/{2}/render/index.html">Background</a></li>\
                    <li class="indented"><a href="/{1}/{2}/render/origins.html">Origins</a></li>\
                    <li><a href="/{1}/{2}/render/tutorial.html">Tutorial</a></li>\
                    <li><a href="/{1}/{2}/render/software.html">Software</a></li>\
                    <li><a href="/{1}/{2}/render/teaching.html">Teaching Materials</a></li>\
                </ul>\
            </div>\
        </div>""".format(repo_instance.name, repo_instance.owner, repo_instance.slug)
        fn = "nav_" + repo_instance.slug + ".html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # index.html
        data = """
        <h1>{0}</h1>
        <p><img src="./img/{1}.png"></p>
        <p>Index.html</p>
        """.format(repo_instance.name, repo_instance.slug)
        fn = "index.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # origin.html
        data = """
        <h1>Origins</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Origins.html</p>
        """.format(repo_instance.slug)
        fn = "origins.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        # b = git_repo.create_blob_fromworkdir(fn)
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # tutorial.html
        data = """
        <h1>Tutorial</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Tutorial.html</p>
        """.format(repo_instance.slug)
        fn = "tutorial.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # software.html
        data = """
        <h1>Software</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Software.html</p>
        """.format(repo_instance.slug)
        fn = "software.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

        # teaching.html
        data = """
        <h1>Teaching Materials</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Teaching.html</p>
        """.format(repo_instance.slug)
        fn = "teaching.html"
        f = open(os.path.join(git_repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        git_repo.index.read()
        git_repo.index.add(fn)
        git_repo.index.write()

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
