__author__ = 'cmantas'

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys, json
from datetime import datetime

db_file = 'files/persitance.db'
CREDENTIALS_FILE = 'files/okeanos_credentials.json'
ROLES_FILE = 'files/roles.json'
ENV_VARS_FILE = 'files/env_vars.json'

#dictinory of credentials per user
credentials = dict()
init_scripts = dict()
env_vars = dict()


def executescript(script):
    try:
        con = lite.connect(db_file)
        cur = con.cursor()
        cur.executescript(script)
        con.commit()
    except lite.Error, e:
        if con: con.rollback()
        print "Error %s:" % e.args[0]
    finally:
        if con: con.close()

# INIT the tables
executescript("CREATE TABLE IF NOT EXISTS ROLES(VMID INTEGER PRIMARY KEY, Role TEXT)")


def execute_query(query):
    try:
        con = lite.connect(db_file)
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    except lite.Error, e:
        if con: con.rollback()
        print "Error %s:" % e.args[0]
        return None
    finally:
        if con: con.close()


def execute_lookup(query):
    for r in execute_query(query): return r


def add_role(VMID, Role):
    script_remove = "DELETE FROM ROLES WHERE VMID=%d" % VMID
    executescript(script_remove)
    script_add = "INSERT INTO ROLES VALUES (%d, '%s');" % (VMID, Role)
    executescript(script_add)

def remove_vm(VMID):
    script_remove = "DELETE FROM ROLES WHERE VMID=%d" % VMID
    executescript(script_remove)


def get_role(VMID):
    query = "SELECT Role FROM ROLES WHERE VMID='%d'" % VMID
    return execute_lookup(query)[0]


def get_vm_ids_by_role(role):
    """
    returns all VM ids of the role specified
    :param role:
    """
    query = "SELECT VMID FROM ROLES WHERE Role='%s'" % role
    return [r[0] for r in execute_query(query)]


def load_credentials():
    """
    loads the credentials from the CREDENTIALS_FILE in memory
    :return:
    """
    credentials_string = open(CREDENTIALS_FILE, 'r').read()
    credentials_in = json.loads(credentials_string)
    for c in credentials_in:
        user = c['user']; expiry_txt = c['expiry']
        expiry = date_object = datetime.strptime(expiry_txt, '%Y-%m-%d')
        c['expiry'] = expiry
        credentials[user] = c


def load_roles():
    """
    loads the roles and their particulars from the ROLES_FILE in memory
    :return:
    """
    roles_in = json.loads(open(ROLES_FILE, 'r').read())
    for role in roles_in:
        init_scripts[role] = roles_in[role]['init_scripts']


def get_credentials(user):
    """
    retreives the authentication url and authentication  token for the given user
    :param user: the user name of for whom the credentials will be loaded
    :return: url, token
    """
    c = credentials[user]
    url = c['auth_url']; token = c['token']; expiry = c['expiry']
    if expiry<datetime.now():
        print "ERROR: okeanos auth token has expired"
    return url, token


# load the credentials from the relevant file
load_credentials()
load_roles()
#load the images from the file
env_vars = json.loads(open(ENV_VARS_FILE, 'r').read())

