import flask
from flask import Flask, render_template, request, session, redirect, escape
from flaskext.mysql import MySQL
from datetime import timedelta
import string

app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'idk_what_this_is'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass'
app.config['MYSQL_DATABASE_DB'] = 'sys'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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
        return render_template('error.html')

@app.route('/manage')#todo: allow admin to add classes to the database
def Admin_Page():
    if 'admin' in session and 'email' in session:
        if session['admin'] is True:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys.classes")
            data = cursor.fetchall()
            return render_template('manage.html', email = session['email'], classes = data)
            #admins should be able to view classes and add/remove classes from this page
        else:
            return redirect('/classes')
    else:
        return render_template('error.html')
@app.route('/manage', methods = ['POST'])
def manage():
    if session['admin'] is True:
        if request.method == 'POST':
            ClassName = request.form.get('className')
            Description = request.form.get('desc')
            ClassSize = request.form.get('classSize')
            Location = request.form.get('location')
            Teacher = request.form.get('teacher')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sys.classes (name, description, numSignedUp, maxCapacity, location, teacher1) VALUES ('" + ClassName + "','" +  Description + "', '0', '" +  ClassSize + "', '" + Location + "','" + Teacher + "')")
            conn.commit()
    return redirect('/manage')
@app.route('/classes', methods=['POST'])
def signup():
    if request.method == 'POST' and 'email' in session:
        classID = request.form.get('class_id') # if someone inspects element, they can change the val of button which will affect the classID, but does that really matter b/c they will just sign up for another class
        classIDCancel = request.form.get('class_id_cancel')
        if classID is None and classIDCancel is not None: # person is canceling a class
            classIDCancel = int(classIDCancel)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sys.classes WHERE id = " + str(classIDCancel))
            currClass = cursor.fetchone()
            cursor.execute("SELECT * FROM sys.classes") # fetch class table so i can print out the list of the classes
            data = cursor.fetchall()

            if currClass is None: # checks if selected class is not valid
                return render_template('classes.html', message="A class with an id of " + str(classIDCancel) + " does not exist.", email = session['email'], classes=data)
            if session['email'] not in currClass: # checks if the person is in the class
                return render_template('classes.html', message="You cannot cancel a class that you are not signed up for.", email = session['email'], classes=data)
            
            cursor.execute("SHOW COLUMNS FROM sys.classes LIKE 'student%'") # gets all the columns that start with "student"
            columns = cursor.fetchall()
            
            shiftLeft = False
            for column in columns:
                cursor.execute("SELECT " + column[0] + " FROM sys.classes WHERE id=" + str(classIDCancel)) # column[0] gets the name of the current column
                selectedEmail = cursor.fetchone()[0] # without the [0], it returns a tuple and not just one string
                currStudentNum = int(column[0].replace("student", ""))
                if shiftLeft is False:
                    if session['email'] == selectedEmail:
                        shiftLeft = True

                if shiftLeft is True:
                    if currStudentNum == currClass[3]: #  check if at last column
                        cursor.execute("UPDATE sys.classes SET " + column[0] +"= NULL WHERE id = " + str(classIDCancel))
                        conn.commit()
                        break
                    else:
                        cursor.execute("SELECT student" + str(currStudentNum+1) + " FROM sys.classes WHERE id=" + str(classIDCancel))
                        nextEmail = cursor.fetchone()[0] # without the [0], it returns a tuple and not just one string
                        cursor.execute("UPDATE sys.classes SET " + column[0] +"='" + nextEmail + "' WHERE id = " + str(classIDCancel))
                        print("setting " + column[0] + " to " + nextEmail)
                        conn.commit()

            cursor.execute("UPDATE sys.classes SET numSignedUp =" + str(currClass[3]-1) + " WHERE id = " + str(classIDCancel)) # currClass[3] hold the current number of students signed up
            conn.commit()
            shiftLeft = False
            cursor.execute("SELECT * FROM sys.classes") # fetch class table with updated values
            data = cursor.fetchall()
            return render_template('classes.html', message="You successfully canceled that class.", email = session['email'], classes=data)
        else: # person is signing up for a class
            classID = int(classID)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT numSignedUp,maxCapacity FROM sys.classes WHERE id = " + str(classID))
            currClass = cursor.fetchone()
            cursor.execute("SELECT * FROM sys.classes") # fetch class table so i can print out the list of the classes
            data = cursor.fetchall()
            if currClass is None:
                return render_template('classes.html', message="A class with an id of " + str(classID) + " does not exist.", email = session['email'], classes=data)
            numSignedUp = currClass[0] # get current number signed up
            maxCapacity = currClass[1] # get max amount of students

            if numSignedUp >= maxCapacity: # checks if the class is full
                return render_template('classes.html', message="That class is currently full.", email = session['email'], classes=data)
            
            cursor.execute("SELECT COUNT(*) FROM sys.classes") # gets number of classes
            numOfClasses = int(cursor.fetchone()[0]) # without the [0], it returns a tuple and not just one string
            for i in range(numOfClasses):
                if session['email'] in data[i]: # checks if the student is already signed up for that class
                    return render_template('classes.html', message="You already signed up for another class.", email = session['email'], classes=data)

            studentCol = "student" + str(numSignedUp+1)
            cursor.execute("SHOW COLUMNS FROM sys.classes LIKE '" + studentCol + "'") # Attempts to get studentCol
            result = cursor.fetchone()

            if result is None: # if column doesn't exist, then add new column for student
                prevStudentCol = "student" + str(numSignedUp)
                cursor.execute("ALTER TABLE sys.classes ADD COLUMN " + studentCol + " VARCHAR(50) NULL AFTER " + prevStudentCol)

            cursor.execute("UPDATE sys.classes SET " + studentCol +"='" + session['email'] + "' WHERE id = " + str(classID))
            cursor.execute("UPDATE sys.classes SET numSignedUp =" + str(numSignedUp+1) + " WHERE id = " + str(classID))
            conn.commit()
            cursor.execute("SELECT * FROM sys.classes") # fetch class table with updated values
            data = cursor.fetchall()
            return render_template('classes.html', message="You have successfully signed up.", email = session['email'], classes=data)
    else:
        return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('email', None) # deletes current session
    session.pop('admin', None)
    return redirect('/')
 
if __name__ == '__main__':
    app.run(debug=True)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `sys`.`classes` (`id` INT NOT NULL AUTO_INCREMENT,`name` VARCHAR(45) NULL,`description` VARCHAR(100) NULL,`numSignedUp` INT NULL,`maxCapacity` INT NULL, `location` VARCHAR(50) NULL, `teacher1` VARCHAR(50) NULL,`student1` VARCHAR(50) NULL, PRIMARY KEY (`id`))")
    cursor.execute("CREATE TABLE IF NOT EXISTS `sys`.`users` (`id` INT NOT NULL,`email` VARCHAR(45) NULL,`password` VARCHAR(100) NULL, `classSignedUp` VARCHAR(45) NULL, PRIMARY KEY (`id`))")
    conn.commit()