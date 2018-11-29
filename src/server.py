import flask
from flask import Flask, render_template, request, session, redirect, url_for, escape
app = Flask(__name__)
app.secret_key = 'idk_what_this_is'

@app.errorhandler(404)
def page_not_found(e):
    return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><br><b>page&nbsp;doesn't exist</b>"

@app.errorhandler(405)
def method_not_allowed(e):
    return "you&nbsp;thought"
 
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
            return redirect('/classes')
        else:
            message = "Wrong username or password"
    return render_template('login.html', message=message)

@app.route('/classes')
def classes():
    if 'email' in session: # checks if session exists (user is logged in)
        return render_template('classes.html', email = session['email'])
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('email', None) # deletes current session
    return redirect('/')
 
if __name__ == '__main__':
  app.run(debug=True)
