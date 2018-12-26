import flask
from flask import Flask, render_template, request, session, redirect, escape
from flaskext.mysql import MySQL
from datetime import timedelta

app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'idk_what_this_is'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass'
app.config['MYSQL_DATABASE_DB'] = 'sys'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
mysql.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><br><b>page&nbsp;doesn't exist</b>"

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect('/')
 
@app.route('/')
def home(): # home page
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == 'root' and password == 'pass': # make it check with DB
            session.permanent = True
            session['email'] = email
            return redirect('/classes') 
        if email == 'admin' and password == 'admin':
            session.permanent = True
            session['email'] = email
            session['admin'] = True
            return redirect('/manage')
        else:
            message = "Wrong username or password"
    return render_template('login.html', message=message)

@app.route('/classes')
def classes():
    if 'email' in session: # checks if session exists (user is logged in)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sys.classes")
        data = cursor.fetchall()
        return render_template('classes.html', email = session['email'], classes = data)
    else:
        return redirect('/')

@app.route('/manage')
def add_class():
    if 'admin' in session and 'email' in session:
        if session['admin'] is True:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys.classes")
            data = cursor.fetchall()
            return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><br><b>page&nbsp;Welcome to the admin page!/b>"
            #return render_template('manageClasses.html',data = data)
            #admins should be able to view classes and add/remove classes from this page
        else:
            return redirect('/classes')
    else:
        return redirect('/classes') # todo: redirect saying the user does not have permission to view the page with a button to go back to classes

@app.route('/classes', methods=['POST'])
def signup():
    if request.method == 'POST' and 'email' in session:
        classID = request.form.get('class_id') # if someone inspects element, they can change the val of button which will affect the classID
        classIDCancel = request.form.get('class_id_cancel')
        if classID is None and classIDCancel is not None: # person is canceling a class
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys.classes WHERE id = " + str(classIDCancel))
            currClass = cursor.fetchone()
            if currClass is None:
                return render_template('classes.html', message="A class with an id of " + str(classIDCancel) + " does not exist", email = session['email'], classes=data)
            if session['email'] not in currClass:
                return render_template('classes.html', message="You cannot cancel a class that you are not signed up for", email = session['email'], classes=data)
            
            return
        else:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT numSignedUp,maxCapacity FROM sys.classes WHERE id = " + str(classID))
            data = cursor.fetchone()
            if data is None:
                return render_template('classes.html', message="A class with an id of " + str(classID) + " does not exist", email = session['email'], classes=data)
            numSignedUp = data[0] # get current number signed up
            maxCapacity = data[1] # get max amount of students 

            cursor.execute("SELECT * FROM sys.classes") # fetch class table so i can print out the list of the classes
            data = cursor.fetchall()

            if numSignedUp >= maxCapacity: # checks if the class is full
                return render_template('classes.html', message="That class is full", email = session['email'], classes=data)
            if session['email'] in data[classID]: # checks if the student is already signed up for that class
                return render_template('classes.html', message="You already signed up for that class", email = session['email'], classes=data)

            studentCol = "student" + str(numSignedUp+1)
            cursor.execute("SHOW COLUMNS FROM sys.classes LIKE '" + studentCol + "'") # Attempts to get studentCol
            result = cursor.fetchone()

            if result is None: # if column doesn't exist, then add new column for student
                prevStudentCol = "student" + str(numSignedUp)
                cursor.execute("ALTER TABLE sys.classes ADD COLUMN " + studentCol + " VARCHAR(50) NULL AFTER " + prevStudentCol)

            cursor.execute("UPDATE sys.classes SET " + studentCol +"='" + session['email'] + "' WHERE id = " + classID)
            cursor.execute("UPDATE sys.classes SET numSignedUp =" + str(numSignedUp+1) + " WHERE id = " + classID)
            conn.commit()
            return render_template('classes.html', message="Successfully signed up!", email = session['email'], classes=data)
    else:
        return redirect('/')

@app.route('/done')
def done():
    return '<b>good job</b><a href="/classes"> Back to classes </a>'


@app.route('/logout')
def logout():
    session.pop('email', None) # deletes current session
    session.pop('admin', None)
    return redirect('/')
 
if __name__ == '__main__':
    app.run(debug=True)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `sys`.`classes` (`id` INT NOT NULL,`name` VARCHAR(45) NULL,`description` VARCHAR(100) NULL,`numSignedUp` INT NULL,`maxCapacity` INT NULL,`teacher1` VARCHAR(50) NULL,`student1` VARCHAR(50) NULL, PRIMARY KEY (`id`))")
    cursor.execute("CREATE TABLE IF NOT EXISTS `sys`.`users` (`id` INT NOT NULL,`email` VARCHAR(45) NULL,`password` VARCHAR(100) NULL, `classSignedUp` VARCHAR(45) NULL, PRIMARY KEY (`id`))")
    conn.commit()
