# NISMOD International

NISMOD International is a general framework for the analysis and modelling of
national infrastructure systems.

## Vagrant

The Vagrantfile defines the automated setup for a virtual machine, which will
provide a reproducible development environment.

To use it, first install:

1. [Virtualbox](www.virtualbox.org)
1. [Vagrant](vagrantup.com)

Then on the command line, from this directory, run:

    vagrant up

This will download a virtual machine image and install all the packages and
software which are required to test and run NISMOD onto that virtual machine.

To run the web app, log into the virtual machine with:

    vagrant ssh

Then run the script:

    python /vagrant/app/__init__.py

And visit `localhost:8080` in a browser on the host machine.

## Database

Database migrations are stored as plain `sql` files, numbered sequentially.

While the schema is likely to change in early development, consider these at
risk and subject to change.

The vagrant development environment sets up a Postgres database with PostGIS
installed.
