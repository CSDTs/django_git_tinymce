#!/bin/bash

# Setup the NodeJS PPA
curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
rm nodesource_setup.sh

sudo apt-get update
sudo apt-get upgrade

# Install python
sudo apt-get install -y python3-pip python3-dev

# Install the database
sudo apt-get install -y postgresql postgresql-contrib
# Set password
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
# Create the database
sudo -u postgres createdb django_git_tinymce

# Install libraries for the community site
pip3 install --upgrade pip
pip3 install --upgrade -r /vagrant/requirements.txt
