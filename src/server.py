import flask
from flask import Flask, render_template

app = Flask(__name__)      
 
@app.route('/')
def home():
    return "hi!"
  #return render_template('home.html')

@app.route("/dankmemes")
def lol():
    return "DANK MEMESSS"
 
if __name__ == '__main__':
  app.run(debug=True)
