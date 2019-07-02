# Project: Wine App

This project creates and displays a database of wines categorized by country. The app uses Python to create a web server and query a database, displaying the results in a browser.

The project was to fulfill a Udacity Nanodegree in Full-Stack Web Development.

## Web Version

The project is accessible on the web at [54.191.61.128.xip.io](http://54.191.61.128.xip.io)

The host is an Amazon Lightsail instance running Ubuntu 18.04. Software installed on the instance:
* Apache 2.4.29
* PostgreSQL 10.9
* Python 3.6.8

Configurations:
* SSH through port 2200
* Other ports available: 80 (http), 123 (ntp)
* Authenciation is key-based only
* Local timezone is UTC
* Python is hosted via mod_wsgi

Third-party resources used:
* mod_wsgi
* flask
* sqlalchemy
* oauth2client

## Repository Contents

The project code is written in two main Python files along with a css file and html template files:
* views.py -- creates web server and views to display in browser
* models.py -- creates the database wines.db (not necessary to run if you use the existing db)
* static folder -- contains styles.css for formatting the application
* templates folder -- contains a number of html files used as templates by the application
* Vagrantfile -- used to configure the virtual environment (see below)

## Running locally

Code in the repository is configured to run locally as follows. Changes required by the web version, commented out, are annotated in a "FOR WSGI ON APACHE" comment.

### Set up the Virtual Machine

The project was executed on a Linux virtual machine using 
VirtualBox and Vagrant. Here's how to set them up.

1. Install VirtualBox v5.1 after downloading from [VirtualBox.org](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
2. Install Vagrant after downloading from [Vagrantup.com](https://www.vagrantup.com/downloads.html)
3. From your terminal run `vagrant --version` to confirm the installation was successful.
4. To configure the VM, make sure the Vagrantfile is the project folder.
5. In your terminal cd to the project folder.
6. To start the VM, run `vagrant up`. 
7. Log into the new machine with `vagrant ssh`
8. To find shared files, cd to `/vagrant`
9. To shut down the vm, run `vagrant halt`

### Set up the Database

A working database with content, wines.db, is included in the project package. If you want to create a fresh database, run the models.py file in Python 3:
`$ python3 models.py`

### Add private keys for logging in

To log into the application you will need to provide the server with private api keys in the top level of the project folder:
* Put Google api keys in a json file called "client_secrets.json". For formatting, see [developers.google.com](https://developers.google.com/api-client-library/python/guide/aaa_client_secrets).
* Put Facebook api keys in a json file called "fb_client_secrets.json". Use this formatting for the file:
```
{
    "web": {
      "app_id": "CODE",
      "app_secret": "CODE"
    }
  }
```

### Run the program

To run the program, cd to the project folder and run views.py with Python 3:
`$ python3 views.py`
Navigate your browser to `localhost:5000` to view the application.

Note that you will have to log in with either Google or Facebook in order to see links that will enable you to update the database, e.g. to create, edit, or delete a wine entry.

## JSON Endpoints

JSON versions are available as follows:
* Wine catalog: /catalog/json
* Country list: /countries/json
* Single wine by id: /wine/ID/json

## Known Issues

* Facebook login is not available on the web version
* Currently the logout process requires the user to click a second "Complete the sign out process" link after choosing to logout.

