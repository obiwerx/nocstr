##############################################################################
##        NOCSTR: NetOps Automation (Formerly Operation: MOTORHEAD)         ##
##  Written in Python, Flask, HTML, CSS, JavaScript, Jinja, and BootStrap   ##
##                                                                          ##
## module: nostr.py     Version: 0.91 ALPHA     Purpose: NetOps Automation  ##
## Author: Tim O'Brien  Team: Network Team A    Date: 06/30/2017            ##
##############################################################################

###########################################################################
######                     ALL OF THE IMPORTS!                        #####
###########################################################################
#We will be using REST calls and JSON, so requests is needed
import requests
#OS is needed to walk directory structures for finding config data
import os
#Audit log is stored in a flat sqlite3 database
import sqlite3
#Flask microframework used extensively for rendering front end and for
#processing back end commands, dispatching RESTful requests, etc...
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json
#Import network_hosts to have name resolution within nocstr functions
#import network_hosts

###########################################################################
#####                        GLOBAL VARIABLES                         #####
###########################################################################
resp_json = ""          #Global for JSON response storage
resp_health = ""        #Global for Health check data
resp_sync = ""          #Global for Sync check data
resp_pool = ""          #Global for pool check data

###########################################################################
#####                       APP CONFIGURATION                         #####
###########################################################################

app = Flask(__name__) #create application instance
app.config.from_object(__name__) #load config file from this file, nocstr.py

#Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'nocstr.db'),
    SECRET_KEY = 'n0cR0ck$+h3$0ck$',
    USERNAME = 'nocster',
    PASSWORD = 'nocnoc4411'
))
app.config.from_envvar('NOCSTR_SETTINGS', silent=True)

###########################################################################
#####            FRONT END ROUTING/BACKEND PROCESSING                 #####
###########################################################################

@app.route('/show_audit', methods=['GET', 'POST'])
def show_audit():
    """This function displays the audit log"""
    db = get_db()
    cur = db.execute('select incident, userName, realServer, timeStamp from logFile order by id desc LIMIT 10')
    logFile = cur.fetchall()
    return render_template('show_audit.html', logFile = logFile)

@app.route('/change', methods=['POST'])
def get_records():
    """Pulls a different number of files on user request"""
    db = get_db()
    cur = db.execute('select incident, userName, realServer, timeStamp from logFile order by id desc LIMIT (?)',
                     [request.form['limit']])
    logFile = cur.fetchall()
    flash('Pulled report as requested!')
    return render_template('show_audit.html', logFile = logFile)

@app.route('/')
def show_entries():
    """This function shows the audit entry screen"""
    return render_template('show_entries.html')

##########################################################################

@app.route('/process', methods=['GET', 'POST'])
def process_requests():
    """This function performs preflight checks"""
    error = None
    resp_json = member_check()
    resp_health = cpu_check()
    resp_sync = sync_check()
    resp_pool = pool_check()
    return render_template('process_request.html', resp_json = resp_json,
                           resp_health = resp_health, resp_sync = resp_sync,
                           resp_pool = resp_pool)

##########################################################################

@app.route('/add', methods=['POST'])
def add_entry():
    """This function adds a new audit entry to the database"""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into logFile (incident, userName, realServer) values(?, ?, ?)',
               [request.form['incident'], request.form['userName'], request.form['realServer']])
    db.commit() #Write to database
    flash('Request Log Updated! Please make a selection below:') #notification
    return redirect(url_for('process_requests'))

##########################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    """This function supports logging into the site"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Authentication Successful') #Notification
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

##########################################################################

@app.route('/logout')
def logout():
    """This function supports logging out of the site"""
    session.pop('logged_in', None)
    flash('You have been logged out') #Notification
    return redirect(url_for('show_entries'))

###########################################################################

@app.route('/out_of_service', methods=['GET', 'POST'])
def out_of_service():
    """Takes target server out of service"""
    #headers are required by iControl REST
    headers = {'Content-Type': 'application/json',}
    #the data fields to be manipulated via iControl REST
    data = '{"session": "user-disabled", "state": "user-down"}'
    #This is the actual REST call to iControl using the Requests Module
    requests.put('https://192.168.1.6/mgmt/tm/ltm/node/jclabweb01/',
    headers=headers, data=data, verify=False, auth=('admin', 'nocnoc4411'))
    #flash notifies users via a bar across the webpage
    flash('jclabweb01 has been successfully taken out of service!')
    #Redirect users back to the show_entries page
    return redirect(url_for('show_entries'))

###########################################################################

@app.route('/back_in_service', methods=['GET', 'POST'])
def back_in_service():
    """Put target server back in service"""
    headers = {'Content-Type': 'application/json',} #Required by iControl REST
    #headers are required by iControl REST
    data = '{"session": "user-enabled", "state": "user-up"}' #Bits to Set
    #the data fields to be manipulated via iControl REST
    requests.put('https://192.168.1.6/mgmt/tm/ltm/node/jclabweb01/', #REST call
    #This is the actual REST call to iControl using the Requests Module
    headers=headers, data=data, verify=False, auth=('admin', 'nocnoc4411'))
    #flash notifies users via a bar across the webpage
    flash('jclabweb01 has been successfully put back in service!') #Notification
    #Redirect users back to the show_entries page
    return redirect(url_for('show_entries')) #go back to show_entries page

###########################################################################
##### Health check classes for nocstr.  Put all validation here please#####
###########################################################################

def member_check():
    """Performs check on requested CI to see it's current state"""
    #This is the actual REST call to iControl using the Requests Module
    resp_json = requests.get('https://192.168.1.6/mgmt/tm/ltm/node/~Common~jclabweb01',
                             verify=False, auth=('admin', 'nocnoc4411'))
    #return data converted to JSON format
    return resp_json.json()

###########################################################################

def cpu_check():
    """Performs CPU utilization check and compares to threshold"""
    #This is the actual REST call to iControl using the Requests Module
    resp_health = requests.get('https://192.168.1.6/mgmt/tm/sys/cpu',
                               verify=False, auth=('admin', 'nocnoc4411'))
    #return data converted to JSON format
    return resp_health.json()

###########################################################################

def sync_check():
    """Performs check to make sure the f5 pair is in sync"""
    #This is the actual REST call to iControl using the Requests Module
    resp_sync = requests.get('https://192.168.1.6/mgmt/tm/cm/sync-status',
                             verify=False, auth=('admin', 'nocnoc4411'))
    #return data converted to JSON format
    return resp_sync.json()

###########################################################################

def pool_check():
    """Performs check to make sure target is last member in any pool"""
    #This is the actual REST call to iControl using the Requests Module
    resp_vs= requests.get('https://192.168.1.6/mgmt/tm/ltm/virtual/VS-noclab-http?options=pool',
                          verify = False, auth=('admin', 'nocnoc4411'))
    #convert to JSON
    resp_vs = resp_vs.json()
    #tranverse JSON dictionary, pull pool value, slice off /Common
    pool = resp_vs['pool'][8:]
    #This is the actual REST call to iControl using the Requests Module
    resp_pool = resp_vs= requests.get('https://192.168.1.6/mgmt/tm/ltm/pool/' + pool + '/members',
                                      verify = False, auth=('admin', 'nocnoc4411'))
    #return data converted to JSON format
    return resp_pool.json()

###########################################################################
#####    Helper classes for nocstr.  Put all utilities here Please    #####
###########################################################################

def find(path, target):
    """Utility function to walk directory, pull config, search for target"""
    lb_library = os.listdir(path)   #build directory list for python
    lb_list = set()

    #try to open file and search for target
    try:
        for filename in lb_library:
            if filename != 'archive':
                with open(path + filename, "r") as current_file:
                    text = current_file.read()
                    host_name = filename.split("_")
                    if host_name[0] not in lb_list:
                        lb_list.add(host_name[0])
                        if target in text:
                            return host_name
    except IOError as error:
        print("I/O Error ({0}): {1}".format(error.errno, error.strerror))

###########################################################################

###########################################################################
#####                   Database utility classes                      #####
###########################################################################

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

###########################################################################

def init_db():
    """Initializes database and schema"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

##########################################################################

def get_db():
    """Opens a new database connection if there is none yet for the current
    application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

##########################################################################

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

##########################################################################

@app.cli.command('initdb')
def initdb_command():
    """"Initalizes the database on the server via cli."""
    init_db()   #Initalizes database
    print('Initalized the database.  You\'re Welcome.')

##########################################################################
