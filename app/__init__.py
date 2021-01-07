#Team SharpCat (Alvin Wu, Madelyn Mao, Jonathan Lee, Victoria Gao)
#SoftDev 
#P0 -- Da Art of Story Tellin' (Pt 2)
#2020-12-28

from flask import Flask,session            #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from datetime import datetime
import os
import sqlite3   #enable control of an sqlite database

DB_FILE="discobandit.db"
db = sqlite3.connect(DB_FILE, check_same_thread = False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
c.execute('CREATE TABLE IF NOT EXISTS users(ID Integer, Username text, Password text, Bio text);')
c.execute('CREATE TABLE IF NOT EXISTS posts(ID Integer, UserID text, Title text, Text text, Date text);')
db.commit()
username = ''
password = ''
app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(24)
postcount = -1
usercount = -1


@app.route("/") #, methods=['GET', 'POST'])
def disp_loginpage():
    if 'username' in session:
        return render_template('response.html', user = username)
    return render_template('login.html')

# (A) working at the moment 
# login mechanism, needs to be edited
@app.route("/auth") # , methods=['GET', 'POST'])
def authenticate():
    problem = 'none'
    if request.args['username'] == '' or request.args['password'] == '': #Check if fields are filled
        return render_template('error.html', error = 'Some fields are empty, try again')     
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
    username = request.args['username']
    password = request.args['password']
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password = ?', (username,password))
    data = c.fetchall()
    if len(data) == 1:
        session['username'] = username
        session['password'] = password
        c.execute('SELECT ID FROM users WHERE username=? AND password = ?', (username,password))
        userid = c.fetchone()
        session['UserID'] = int(userid[0])
        print(userid)
        return render_template('response.html', user = request.args['username'])
    else:
        return render_template ('error.html')

# (A) done
# sign up for an account, signup.html takes username, password, bio 
# check if username is unique, add password specifications if desired

@app.route("/signup") #methods = ['GET','POST'])
def signup():
        global usercount
        c = db.cursor()
        username = request.args['newusername']
        password = request.args['newpassword']
        bio = request.args['bio']
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        data = c.fetchall()
        if len(data) > 0:
            return render_template('error.html', error = 'A user with that username already exists')
        usercount+= 1
        params = (usercount,username,password,bio)
        c.execute('INSERT INTO users(ID,Username,Password,Bio) VALUES(?,?,?,?)', params)
        db.commit()
        return render_template('login.html')

# middle method, going straight to signup doesn't work. renders the actual signup page    
@app.route("/newuser", methods = ['GET','POST'])
def newuser():
        return render_template('signup.html')


# (a/j) needs to be done 
# adds a blog, addblog.html(not completed) will take take in a title and a body of text.
@app.route("/addblog") 
def addblog():
    return render_template('addblog.html')

@app.route("/add") 
def add():
    global postcount
    c = db.cursor()
    text = request.args['Text']
    title = request.args['Title']
    postcount += 1
    params = (postcount,session['UserID'],title,text,datetime.today().strftime('%Y-%m-%d-%H:%M'))
    c.execute('INSERT INTO posts(ID,UserID,Title,Text,Date) VALUES(?,?,?,?,?)', params)
    db.commit()
    return render_template('response.html',user = session['username'])


# (a/j) needs to be done 
# lists all blog entries from a user
@app.route("/viewallblogs") 
def viewallblogs():
    return render_template('viewallblogs.html')

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

# profile displays a user's biography
@app.route("/profile")
def viewprofile():
    return render_template('profile.html',status=True)

@app.route("/logout") #logout
def logout():
    session.pop('username', None)
    return render_template('login.html')

    
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()
