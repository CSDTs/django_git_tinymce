[![Build Status](https://travis-ci.org/CSnap/django_git_tinymce.svg?branch=master)](https://travis-ci.org/CSnap/django_git_tinymce)

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
sudo apt-get install libffi-dev
cd /vagrant
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The site should now be accessible at via web browser at localhost:8000
