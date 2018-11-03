import flask
from flask import Flask, render_template

app = Flask(__name__)      
 
@app.route('/')
def home():
    return render_template('login.html')

@app.route("/dashboard", methods=['POST'])
def lol():
    return "DANK MEMESSS"
 
if __name__ == '__main__':
  app.run(debug=True)
