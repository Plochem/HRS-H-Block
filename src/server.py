import flask
from flask import Flask, render_template, request

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return "<img src='https://ih1.redbubble.net/image.394584645.5749/ap,550x550,12x12,1,transparent,t.u4.png'><b>page&nbsp;,doesn't exist</b>"

@app.errorhandler(405)
def method_not_allowed(e):
    return "you&nbsp;thought"
 
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')  # access the data inside 
        password = request.form.get('password')

        if email == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"
    return render_template('login.html', message=message)
 
if __name__ == '__main__':
  app.run(debug=True)
