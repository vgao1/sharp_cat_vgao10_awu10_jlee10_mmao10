#Team SharpCat (Alvin Wu, Madelyn Mao, Jonathan Lee, Victoria Gao)
#SoftDev 
#P0 -- Da Art of Story Tellin' (Pt 2)
#2020-12-28

from flask import Flask,session            #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request, redirect           #facilitate form submission
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
        return render_template('response.html', user = session['username'], status = True)
    else:
        return render_template('login.html',status=False)

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
        return render_template('response.html', user = request.args['username'],status=True)
    else:
        return render_template ('error.html',status=False)

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
        return render_template('login.html',status=False)

# middle method, going straight to signup doesn't work. renders the actual signup page    
@app.route("/newuser", methods = ['GET','POST'])
def newuser():
        return render_template('signup.html',status=False)

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
    return render_template('response.html',status=True,user = session['username'])

# (a/j) needs to be done 
# adds a blog, addpost.html(not completed) will take take in a title and a body of text.
@app.route("/post/new") 
def newpost():
    return render_template('addpost.html',status=True,user = session['username'])

# (j) set up
# redirects logged in user to their own blog
@app.route("/blog") 
def loggedinblog():
    return redirect('/blog/'+ session['username'])

# (a/j) needs a lot of work
# edit menu for a previously posted post, must have been the current user's (needs verification) 
@app.route("/post/<posturl>/edit") 
def updaterender(posturl):
    c = db.cursor()
    c.execute('SELECT Title, Text FROM posts WHERE ID=?', (posturl,))
    data = c.fetchall()
    data = data[0]
    oldtitle = data[0]
    oldtext = data[1]
    print(posturl)
    return render_template('updatepost.html',status=True, oldtitle = oldtitle, oldtext = oldtext, posturl = posturl)

@app.route("/update/<posturl>")
def update(posturl):
    c = db.cursor()
    c.execute('UPDATE posts SET Title =' + request.args['Title'] + ', Text =' + request.args['Text'] + ', Date =' + datetime.today().strftime('%Y-%m-%d-%H:%M') + 'WHERE ID=?',(posturl,))
    db.commit()
    return redirect('/post/' + posturl)
    

# (j) bugfix time!!
# lists all blog entries from a user (replaced viewuser)
@app.route("/blog/<usrname>") 
def viewuserblog(usrname):
    c = db.cursor()
    c.execute('SELECT ID FROM users WHERE username = \'' + str(usrname) + '\'')
    userid = c.fetchall()[0]
    c.execute('SELECT ID, Title, Text, Date FROM posts WHERE UserID = \'' + str(userid[0]) + '\''
        'ORDER BY ID DESC') #descending
    posts = c.fetchall()
    c.close()
    return render_template('viewuserblog.html', user=usrname, posts=posts, status = True)

# (j) bugfix time!!
# returns all posts by everyone, recent ones first
@app.route("/all") 
def viewall():
    c.execute('SELECT * FROM posts ORDER BY ID DESC') #descending
    posts1 = c.fetchall()
    # add user fetch with id and replacing in posts var :pensive:
    return render_template('viewallposts.html', posts=posts1, status = True, user=session['username'])

# (j) bugfix time!! also needs optimization
# displays one post
# reminder on db: ID Integer, UserID text, Title text, Text text, Date text
@app.route("/post/<posturl>") # changed from viewblog
def viewblogpost(posturl):
    if posturl.isnumeric(): # to avoid errors
        c = db.cursor()
        c.execute('SELECT UserID,Title, Text, Date FROM posts WHERE ID = \'' + str(posturl) + '\'') # gets the post info by ID
        postinfo = c.fetchall()[0]
        c.execute('SELECT Username FROM users WHERE ID = \'' + str(postinfo[0]) + '\'') # gets user by user ID from post
        userinfo = c.fetchall()
        userinfo = userinfo[0]
        c.close()
        print(postinfo[0])
        print(postinfo[1])
        print(postinfo[2])
        print(userinfo[0])
        if userinfo[0] == session['username']:
            return render_template('viewblogpost.html', title=postinfo[1], author=userinfo[0], body=postinfo[2], date=postinfo[3], status = True, allowEdit = True, user = session['username'], posturl = posturl)
        else:
            return render_template('viewblogpost.html', title=postinfo[1], author=userinfo[0], body=postinfo[2], date=postinfo[3], status = True, allowEdit = False, user = session['username'], posturl = posturl)        
    else:
        return render_template('error.html', error='Not a valid blog post URL!')


# mm i feel like this needs something but idk what
# profile displays the current user's biography
@app.route("/profile")
def viewprofile():
    c = db.cursor()
    c.execute('SELECT Bio FROM users WHERE Username=?',(session['username'],))
    data = c.fetchone()
    data = str(data[0])
    return render_template('profile.html',status=True, bio = data, user = session['username'])

@app.route("/logout") #logout
def logout():
    session.pop('username', None)
    return render_template('login.html',status=False)

    
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()
