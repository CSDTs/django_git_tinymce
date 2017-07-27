#!/bin/bash

# Setup the NodeJS PPA
curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
rm nodesource_setup.sh

sudo apt-get update
# sudo apt-get upgrade -y

# Install python
sudo apt-get install -y python3-pip python3-dev

sudo apt-get install -y libffi-dev

# Install cmake
sudo apt install -y cmake

# Install libgit2 system wide
wget https://github.com/libgit2/libgit2/archive/v0.26.0.tar.gz
tar xzf v0.26.0.tar.gz
cd libgit2-0.26.0/
cmake .
make
sudo make install

# Install the database
sudo apt-get install -y postgresql postgresql-contrib
# Set password
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
# Create the database
sudo -u postgres createdb django_git_tinymce

# Install libraries for the community site
sudo pip3 install --upgrade pip
sudo pip3 install -r /vagrant/requirements.txt

# Link pygit2 with libgit2
sudo ldconfig