# NISMOD International

NISMOD International is a general framework for the analysis and modelling of
national infrastructure systems.

## Vagrant notes

The Vagrantfile defines the automated setup for a virtual machine, which will
provide a reproducible development environment.

To use it, first install:

1. [Virtualbox](www.virtualbox.org)
1. [Vagrant](vagrantup.com)

Then on the command line, from this directory, run:

    vagrant up

This will download a virtual machine image and install all the packages and
software which are required to test and run NISMOD onto that virtual machine.
