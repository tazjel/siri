# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


###############################
## custom general functions
###############################

@auth.requires_login()
def displayusers():
    """
    Shows the list of users
    """
    response.flash = 'This page shows a list of users'
    query = (db.auth_user)
    users = db(query).select()
    return dict(users = users)


###############################
## custom time clock functions
###############################

@auth.requires_login()
def mainpage():
    """
    this will become the index page
    """
    fields = ['project','work_date','time_in','time_out','description']
    form = SQLFORM(db.timeclock, submit_button = 'Submit Hours', fields = fields)
    if form.process(onvalidation=calcHours).accepted:
        response.flash = 'Thank you for submitting your time ' + str(form.vars.hours)
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Welcome ' + session.auth.user.first_name + ' your id is: ' + str(session.auth.user.id)
    response.title = 'Welcome ' + session.auth.user.first_name
    response.subtitle = 'please review your time or fill out the form below to add time'

    query = (db.timeclock.usr_id == session.auth.user.id)
    clockEntries = db(query).select()
    return dict(form=form, clockEntries=clockEntries)

def calcHours(form):
    hourDiff = int(form.vars.time_out[0:2]) - int(form.vars.time_in[0:2])
    minDiff = (int(form.vars.time_out[3:5]) - int(form.vars.time_in[3:5]))/60.0
    form.vars.hours = hourDiff + minDiff

def clockadmin():
    adminMenu = MENU([['Manage Projects', False, URL(manageprojects)],['Manage Users', False, URL(manageusers)],['Manage Groups', False, URL(managegroups)]])
    
    users = db(db.auth_user).select()
    projects = db(db.siri_projects).select()
    groups = db(db.auth_group).select()

    return dict(adminMenu=adminMenu, users=users, projects=projects, groups=groups)

def manageprojects():
    form = SQLFORM(db.siri_projects)
    if form.process().accepted:
        response.flash = 'Thank you for submitting a new project'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Welcome ' + session.auth.user.first_name + ' your id is: ' + str(session.auth.user.id)
    projects = db(db.siri_projects).select()

    return dict(form=form, projects=projects)
    
def editproject():
    record = db.siri_projects(request.args(0)) or redirect(URL('clockadmin'))
    form = SQLFORM(db.siri_projects, record)
    if form.process(next='manageprojects').accepted:
        response.flash = 'Thank you, the project has been updated'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Please update the project info'
    return dict(form=form)
    
def managegroups():
    groups = db(db.auth_group).select()
    
    return dict(groupList=groups)

def manageusers():
    userFilter = MENU([[],[]])
    users = db(db.auth_user).select()

    return dict(userList=users)

@auth.requires_login()
def addtime():
    """
    Allows a loggedin user to add an entry for time worked
    """
    form = SQLFORM(db.timeclock)
    if form.process().accepted:
        response.flash = 'Thank you for submitting your time'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Welcome ' + session.auth.user.first_name + ' your id is: ' + str(session.auth.user.id)
    response.title = 'New Entry'
    response.subtitle = 'please fill out the form below'
    hoursTest = type(db.timeclock.time_in)
    return dict(form=form, hoursTest=hoursTest)

@auth.requires_login()
def displaytime():
    """
    Shows the entries for the user that is logged in
    """
    response.flash = 'This page shows your entries'
    query = (db.timeclock.usr_id == session.auth.user.id)
    # query = (db.timeclock)
    # set = db(query)
    # rows = set.select()
    # row = rows[0]
    # print str(rows)
    clockEntries = db(query).select()
    return dict(clockEntries = clockEntries)

#################################
## custom FamilySearch functions
#################################

def fsapply():
    """
    Allows interested students to apply for the opportunity
    """
    form = SQLFORM(db.fs_prospects,fields = ['interested_location','interested_dates','language_level','referred_by','resume'])
    if form.process().accepted:
        response.flash = 'Thank you, we will keep you updated about this and future opportunities'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Welcome, please fill out the information below'
    return dict(form=form)

def fsregister():
    """
    Allows approved prospects to register for their project
    """
    form = SQLFORM(db.fs_students, fields = ['opp_location','internship','training_hotel','birthday','emergency_name','emergency_phone'])
    if form.process().accepted: #**** next=fsoverview - directs user to an overview page
        response.flash = 'Thank you, we will be making arrangements for your trip'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Welcome, please fill out the information below'
    return dict(form=form)

def fsstudentupdate():
    """
    Allows administration to fill out or update additional information about the student
    """
    record = db.fs_students(request.args(0)) or redirect(URL('index'))
    form = SQLFORM(db.fs_students, record)
    if form.process(next='fsshowstudents').accepted:
        response.flash = 'Thank you, the student has been updated'
    elif form.errors:
        response.flash = 'There was an error on the form'
    else:
        response.flash = 'Please update the students info'
    return dict(form=form)

def fsshowstudents():
    """
    Shows a list of all students
    **** need to figure out how to filter it
    """
    response.flash = 'Please choose a student to edit'
    query = (db.fs_students)
    students = db(query).select()
    return dict(students = students)
