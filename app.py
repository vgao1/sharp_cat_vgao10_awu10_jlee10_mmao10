#Team SharpCat (Alvin Wu, Madelyn Mao, Jonathan Lee, Victoria Gao)
#SoftDev 
#P0 -- Da Art of Story Tellin' (Pt 2)
#2020-12-28

from flask import Flask,session            #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
import os

#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(24)

# delete after creating username/password in /auth
username = "dullcat" #USERNAME
password = "sharpiecats" #PASSWORD

@app.route("/") #, methods=['GET', 'POST'])
def disp_loginpage():
    if 'username' in session:
        return render_template('response.html', user = username, method = request.method)
    return render_template('login.html')

# (a/j) needs to be done 
# login mechanism, needs to be edited
@app.route("/auth") # , methods=['GET', 'POST'])
def authenticate():
    problem = 'none'
    if request.args['username'] == '' or request.args['password'] == '': #Check if fields are filled
        problem = 'Some fields are empty, try again'
        return render_template('error.html', error = problem)     
    print("\n\n\n")
    print("***DIAG: this Flask obj ***")
    print(app)
    print("***DIAG: request obj ***")
    print(request)
    print("***DIAG: request.args ***")
    print(request.args)
    print("***DIAG: request.args['username']  ***")
    print(request.args['username'])
    print("***DIAG: request.headers ***")
    print(request.headers)
    if username == request.args['username'] and password == request.args['password']: #Verify username and password
        session['username'] = username
        return render_template ('response.html', user = username, method = request.method)
    else:
        if username == request.args['username']: #Incorrect password
            problem = 'Incorrect Password'
        else:
            if password == request.args['password']: #Incorrect username
                problem = 'Incorrect Username'
            else:
                problem = 'None of your information is correct' #Both incorrect
        return render_template ('error.html', error = problem)

# (a/j) needs to be done 
# sign up for an account, signup.html takes username, password, bio 
# check if username is unique, add password specifications if desired
@app.route("/newuser") 
def newuser():
    return render_template('signup.html')

# (a/j) needs to be done 
# adds a blog, addblog.html(not completed) will take take in a title and a body of text.
@app.route("/addblog") 
def add():
    return render_template('addblog.html')

# (a/j) needs to be done 
# adds text to a previous page, 
@app.route("/updateblog") 
def update():
    return render_template('updateblog.html')

# (a/j) needs to be done 
# returns a list of the users
@app.route("/viewall") 
def viewall():
    return render_template('viewall.html')

# (a/j) needs to be done 
# returns a list of the blogs from a certain user
@app.route("/viewuser") 
def viewuser():
    return render_template('viewuser.html')

# (a/j) needs to be done 
# displays one blog
@app.route("/viewblog") 
def viewblog():
    return render_template('viewblog.html')


@app.route("/logout") #logout
def logout():
    session.pop('username', None)
    return render_template('login.html')

    
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()