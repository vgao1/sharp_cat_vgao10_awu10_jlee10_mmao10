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
c.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER NOT NULL PRIMARY KEY, Username text NOT NULL, Password text, Bio text);')
c.execute('CREATE TABLE IF NOT EXISTS posts(ID INTEGER NOT NULL PRIMARY KEY, UserID text NOT NULL, Title text NOT NULL, Text text, Date text);')
db.commit()
app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(24)



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
        params = (username,password,bio)
        c.execute('INSERT INTO users(Username,Password,Bio) VALUES(?,?,?)', params)
        db.commit()
        return render_template('login.html',status=False)

# middle method, going straight to signup doesn't work. renders the actual signup page    
@app.route("/newuser", methods = ['GET','POST'])
def newuser():
        return render_template('signup.html',status=False)

@app.route("/add") 
def add():
    c = db.cursor()
    text = request.args['Text']
    title = request.args['Title']
    params = (session['UserID'],title,text,datetime.today().strftime('%Y-%m-%d-%H:%M'))
    c.execute('INSERT INTO posts(UserID,Title,Text,Date) VALUES(?,?,?,?)', params)
    db.commit()
    return render_template('response.html',status=True,user = session['username'])

# (j) set up
# redirects logged in user to their own blog
@app.route("/blog") 
def loggedinblog():
    return redirect('/blog/'+ session['username'])

# (a+j) we did it finally
# edit menu for a previously posted post, must have been the current user's (needs verification) 
@app.route("/post/<posturl>/edit") 
def updaterender(posturl):
    c = db.cursor()
    c.execute('SELECT Title, Text FROM posts WHERE ID = ?', (posturl,))
    data = c.fetchall()
    data = data[0]
    oldtitle = data[0]
    oldtext = data[1]
    print(posturl)
    return render_template('updatepost.html',status=True, oldtitle = oldtitle, oldtext = oldtext, posturl = posturl)

@app.route("/update/<posturl>", methods=['GET'])
def update(posturl):
    c = db.cursor()
    c.execute('UPDATE posts SET Title = \'' + request.args.get('Title') + '\', Text =\'' + request.args.get('Text') + '\' WHERE ID = ?', (posturl,))
    db.commit()
    return redirect('/post/' + str(posturl))
    

# (j) bugfix time!!
# lists all blog entries from a user (replaced viewuser)
@app.route("/blog/<usrname>") 
def viewuserblog(usrname):
    c = db.cursor()
    c.execute('SELECT ID FROM users WHERE username = \'' + str(usrname) + '\'')
    userid = c.fetchall()[0]
    c.execute('SELECT ID, Title, Text, Date FROM posts WHERE UserID = \'' + str(userid[0]) + '\'')
    posts = c.fetchall()
    c.execute('SELECT Bio FROM users WHERE username = \'' + str(usrname) + '\'')
    bio = c.fetchall()[0]
    c.close()
    if ('username' not in session):
        return render_template('viewuserblog.html', blogger=usrname, userid = str(userid[0]), posts=posts, status = False, user = 'Guest')
    else:
        return render_template('viewuserblog.html', blogger=usrname, userid = str(userid[0]), posts=posts, status = True, user = session['username'])

@app.route("/viewusers")
def viewusers():
    c = db.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    return render_template('viewallusers.html', users = users, status = True, user = session['username'])
    

# (j) bugfix time!!
# returns all posts by everyone, recent ones first
@app.route("/all") 
def viewall():
    c = db.cursor()
    c.execute('SELECT * FROM posts')
    posts1 = c.fetchall()
    # add user fetch with id and replacing in posts var :pensive:
    c.execute('SELECT username FROM users')
    usernames = c.fetchall()
    c.close()
    print(usernames)
    print(posts1)
    authors = []
    for u in posts1:
        authors.append(usernames[int(u[1])-1])
    authors.reverse() #important to preserve order!!!
    if ('username' not in session):
        return render_template('viewallposts.html', posts=posts1, status = False, author = authors, user = 'Guest')
    else:
        return render_template('viewallposts.html', posts=posts1, status = True, author = authors, user = session['username'])

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
        if ('username' not in session):
            return render_template('viewblogpost.html', title=postinfo[1], author=userinfo[0], body=postinfo[2], date=postinfo[3], status = False, allowEdit = False, user = 'Guest', posturl = posturl)
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
    if ('username' not in session):
        return redirect('/')
    else:       
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
