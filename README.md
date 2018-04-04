[![Build Status](https://travis-ci.org/CSDTs/django_git_tinymce.svg?branch=master)](https://travis-ci.org/CSnap/django_git_tinymce)[![Coverage Status](https://coveralls.io/repos/github/CSDTs/django_git_tinymce/badge.svg?branch=master)](https://coveralls.io/github/CSDTs/django_git_tinymce?branch=master)[![Updates](https://pyup.io/repos/github/CSDTs/django_git_tinymce/shield.svg)](https://pyup.io/repos/github/CSDTs/django_git_tinymce/)

# django_git_tinymce
This is the main repo for controlling teacher contributions to the CSDT community website. It is still in development.

It is designed to act as a private git server, from which teachers can add new content or change old content using the tinymce wiziwig to fit their classroom and needs, while simultaneously sharing that content to help other teachers with their work.

# Requirements
```
sudo apt-get install libffi-dev
```

# Setup

Install:
* VirtualBox
  * Linux: sudo apt-get install virtualbox
  * Windows & Mac: https://www.virtualbox.org/wiki/Downloads
* Vagrant
  * Linux: sudo apt-get install vagrant
  * Windows & Mac: https://www.vagrantup.com/downloads.html
* libffi-dev (For Misaka)
  * Linux: sudo apt-get install libffi-dev
* Git
  * Linux: sudo apt-get install git
  * Windows & Mac: https://git-scm.com/downloads
    * For windows make sure C:\Program Files\Git\usr\bin [is in your path variable](http://www.computerhope.com/issues/ch000549.htm)


Then run:
```bash
git clone https://github.com/CSnap/django_git_tinymce
cd django_git_tinymce
vagrant up
vagrant ssh
cd /vagrant
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py runserver 0.0.0.0:8001
```

The site should now be accessible at via web browser at localhost:1234

To access site admin:

- To set up admin for site: ```python3 manage.py createsuperuser```
- Visit ```/admin```


# React/Redux

Frontend was created using React (Redux). To set up webpack for compiling the React JSX code into a client.min.js file, browse to ```/static/js/repo/``` (or /menu/ if you are working on the menu page) and type into the terminal ```npm install```. This will set up your NPM dependencies in a /node_modules folder (You will need Node installed). Remember not to upload /node_modules to github (it is .gitignore'd anyway). Use the command ```webpack``` to compile your React code into the client.min.js file, which you _do_ want to upload to github. You can of course use webpack-dev-server to autocompile on save, though you will still need to use the ```webpack``` command for the final compilation of client.min.js before uploading to github because of React warnings regarding production mode.
