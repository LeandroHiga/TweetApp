from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from datetime import datetime
import tweepy
import os

#Init app
app = Flask(__name__)
CORS(app)

#Twitter Keys
auth = tweepy.OAuthHandler("L34y0Ez744ifincFlkzqLus57", "c99M7ymvB5B74p16aAu70YZPbJaRx0VP48hW2UJoN8KNOs7hr8")
auth.set_access_token("1104063783234879490-kY0DJFnHf29bT11WdvMspTqbGvHqST", "DrHQf9AztSRwJPmDRXjURkFiLx8YmVM23A96C2Ac0xUwd")

api = tweepy.API(auth)

#Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/twitter"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False


db = SQLAlchemy(app) #Init Database
ma = Marshmallow(app) #Init Marshmallow

#Word Class/Model
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(20))
    date_created = db.Column(db.DateTime , default=datetime.now)

    #Constructor
    def __init__(self, word, date_created):
        self.word = word
        self.date_created = date_created

#Word Schema
class WordSchema(ma.Schema):
    class Meta:
        fields = ("id", "word", "date_created")

#Init Schema
word_schema = WordSchema()
words_schema = WordSchema(many=True)

#Create Database 
db.create_all()

#Create/Insert a new word
@app.route('/word', methods=['POST'])
def addWord():
    word = request.json['word']
    date_created = request.json['date_created']

    new_word = Word(word, date_created)

    db.session.add(new_word)
    db.session.commit()

    return word_schema.jsonify(new_word)

#Get All words
@app.route('/word', methods=['GET'])
def getWords():
    all_words = Word.query.all()

    result = words_schema.dump(all_words)

    return jsonify(result)

#Delete a word
@app.route('/word/<id>', methods=['DELETE'])
def deleteWord(id):
    word = Word.query.get(id)
    db.session.delete(word)
    db.session.commit()

    return word_schema.jsonify(word)

#Buscador
@app.route('/buscador', methods=["GET", "POST"])
def buscador():
    if request.method == "POST":
        word = request.form["word"]
        return redirect(url_for("word", wrd=word)) #Call word function and pass parameter wrd
    else:
        return render_template("buscador.html")

@app.route('/')
def inicio():
        return render_template("buscador.html")

#Function to fetch tweets and render in template
@app.route('/buscador/<wrd>')
def word(wrd):
    tweets = []
    public_tweets = api.search(q=wrd, count=5)

    for tweet in public_tweets:
        print("TWEET", tweet.text)
        tweets.append(tweet.text)
        print(public_tweets)
    return render_template("tweets.html", tweets=tweets)

#Historial
@app.route('/historial')
def historial():
    return render_template("historial.html")

#Run Server
if __name__ == "__main__":
    app.run(debug=True)
