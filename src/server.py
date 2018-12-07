import flask
from flask import Flask, render_template, request, session, redirect, escape
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'idk_what_this_is'
app.config['MYSQL_DATABASE_USER'] = 'server_2290'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Gf134!oijfdF45Dm34l!'
app.config['MYSQL_DATABASE_DB'] = 'server_2290'
app.config['MYSQL_DATABASE_HOST'] = '172.106.202.143'
mysql.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><br><b>page&nbsp;doesn't exist</b>"

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect('/')
 
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
    
        session['email'] = email
        if email == 'root' and password == 'pass': # make it check with DB
            return redirect('/classes') 
        if email == 'admin' and password == 'admin':
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
        cursor.execute("SELECT * FROM server_2290.classes")
        data = cursor.fetchall()
        return render_template('classes.html', email = session['email'], data = data)
    else:
        return redirect('/')

@app.route('/manage')
def add_class():
    if 'admin' in session:
        if session['admin'] is True:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM server_2290.classes")
            data = cursor.fetchall()
            return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><br><b>page&nbsp;EXISTS FE*IRFPHJFIPHENSJ/b>"
            #return render_template('manageClasses.html',data = data)
            #admins should be able to view classes and add/remove classes from this page
        else:
            return redirect('/')
    else:
        return redirect('/') # todo: redirect to page person came from

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        classID = request.form.get('class_id')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT numSignedUp FROM server_2290.classes WHERE id = " + str(classID))
        print(classID) # if someone inspects element, they can change the val of button which will affect the classID
        numSignedUp = cursor.fetchone()[0] # prints out the class id you sign up for
        studentCol = "student" + str(numSignedUp+1)
        cursor.execute("SHOW COLUMNS FROM server_2290.classes LIKE '" + studentCol + "'") # check if there is a col for student
        result = cursor.fetchone()
        if result is not None: # column exists
            print(result[0])
        else:
            print("oof")
            #alter table create
    return redirect('/classes')

@app.route('/logout')
def logout():
    session.pop('email', None) # deletes current session
    session.pop('admin', None)
    return redirect('/')
 
if __name__ == '__main__':
  app.run(debug=True)
