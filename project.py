from flask import Flask, redirect, url_for, render_template, request, session, abort
from flask_mysqldb import MySQL
import tweepy
import textblob
import datetime
import joblib
import data_preprocess
import pandas as pd
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import pickle
import keys

app = Flask(__name__)
app.secret_key = "CodeSpecialist.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'student'
app.config['MYSQL_DB'] = 'be'
app.config['MYSQL_CHARSET'] = 'utf8'
mysql = MySQL(app)
GOOGLE_CLIENT_ID = "900008972111-vatj4trk6i2upu4lrk3h7aqa46t36gno.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/clogin")


@app.route("/protected_area")
@login_is_required
def protected_area():
    name = session["name"]
    email = session["email"]
    try:
        cur = mysql.connect.cursor()
        cur.execute("SELECT name FROM `glogin` WHERE `Email id`='" + email + "'")
        data = cur.fetchall()
        if data == ():
            cur.execute("INSERT INTO glogin(`name`,`Email id`)VALUES('" + name + "','" + email + "')")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " sentiments`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL, `Analysis` TEXT NOT NULL,`Positive` FLOAT NOT NULL,`Neutral` FLOAT NOT NULL,`Negative` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " emotions`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL,`anger` FLOAT NOT NULL,`disgust` FLOAT NOT NULL,`fear` FLOAT NOT NULL,`joy` FLOAT NOT NULL,`neutral` FLOAT NOT NULL,`sadness` FLOAT NOT NULL,`shame` FLOAT NOT NULL,`surprise` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " sentiments machine lerning`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL, `Analysis` TEXT NOT NULL,`Positive` FLOAT NOT NULL,`Negative` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.close()
        return redirect(url_for("tweeter", email=email, name=name))
    except Exception as e:
        return f"<h1>{e}</h1>"


@app.route("/")
def home():
    return render_template("Index.html")


@app.route("/aboutus")
def about_us():
    return render_template("about us.html")


@app.route("/own text", methods=["POST", "GET"])
def own_text():
    if request.method == "POST":
        text1 = request.form['text']
        text = data_preprocess.clean_own_text(text1)
        s = textblob.TextBlob(text)
        return render_template("own text.html", mess=True, n=s.polarity, text=text1)
    else:
        return render_template("own text.html")


@app.route("/new acc", methods=["POST", "GET"])
def new_acc():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["Phone"]
        email = request.form["Email"]
        password = request.form["Password"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO login(`name`,`phone number`,`Email id`,`pass`)VALUES('" + name + "'," + phone + ",'" + email + "','" + password + "')")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " sentiments`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL, `Analysis` TEXT NOT NULL,`Positive` FLOAT NOT NULL,`Neutral` FLOAT NOT NULL,`Negative` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " emotions`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL,`anger` FLOAT NOT NULL,`disgust` FLOAT NOT NULL,`fear` FLOAT NOT NULL,`joy` FLOAT NOT NULL,`neutral` FLOAT NOT NULL,`sadness` FLOAT NOT NULL,`shame` FLOAT NOT NULL,`surprise` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `" + email + " sentiments machine lerning`(`Date & Time` VARCHAR(45) NOT NULL, `Movie Name` TEXT NOT NULL,`Category` TEXT NOT NULL, `Analysis` TEXT NOT NULL,`Positive` FLOAT NOT NULL,`Negative` FLOAT NOT NULL)")
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("clogin"))
        except Exception as e:
            return f"<h1>{e}</h1>"
    else:
        return render_template("new acc.html")


@app.route("/clogin", methods=["POST", "GET"])
def clogin():
    if request.method == "POST":
        email = request.form["Email"]
        password = request.form["Password"]
        try:
            cur = mysql.connect.cursor()
            cur.execute("SELECT name FROM `login` WHERE `Email id`='" + email + "' AND `pass`='" + password + "'")
            data = cur.fetchall()
            name = data[0][0]
            cur.close()
            if data == ():
                return render_template("login.html", error="No record found")
            else:
                return redirect(url_for("tweeter", email=email, name=name))
        except Exception as e:
            return f"{e}"
    else:
        return render_template("login.html")


@app.route("/tweeter<email>,<name>", methods=["POST", "GET"])
def tweeter(email, name):
    if request.method == "POST":
        tweets = []
        likes = []
        time = []
        Movie_Name = request.form["Movie Name"]
        Number_of_tweets = int(request.form["Number of tweets"])
        Category = request.form["options-outlined"]
        sel = request.form["sel"]
        auth = tweepy.OAuthHandler(keys.API_key(), keys.API_key_secret())
        auth.set_access_token(keys.Access_token(), keys.Access_token_secret())
        api = tweepy.API(auth)
        for i in tweepy.Cursor(api.search, q=Movie_Name + " " + Category, tweet_mode="extended").items(
                Number_of_tweets):
            tweets.append(i.full_text)
            likes.append(str(i.favorite_count))
            time.append(str(i.created_at))
        if (len(tweets) == 0):
            return render_template("tweeter.html",
                                   error="Cannot find tweets on required move search for different movie")
        else:
            count = 0
            remove = []
            for i in range(len(tweets)):
                for j in range(i + 1, len(tweets)):
                    if tweets[i] == tweets[j]:
                        remove.append(j)
            remove = list(dict.fromkeys(remove))
            remove.sort()
            for i in remove:
                i -= count
                tweets.pop(i)
                likes.pop(i)
                time.pop(i)
                count += 1
            tweets = data_preprocess.translato(tweets)
            if sel == "1":
                tweets = data_preprocess.clean(tweets)
                print(tweets, "\n", len(tweets))
                print(likes, "\n", len(likes))
                print(time, "\n", len(time))
                print(email)
                print(Movie_Name)
                print(Category)
                positive_tweets = []
                positive_likes = []
                positive_time = []
                negative_tweets = []
                negative_likes = []
                negative_time = []
                neutral_tweets = []
                neutral_likes = []
                neutral_time = []
                mess = ""
                for i in range(len(tweets)):
                    s = textblob.TextBlob(tweets[i])
                    if s.polarity > 0:
                        positive_tweets.append(tweets[i])
                        positive_likes.append(likes[i])
                        positive_time.append(time[i])
                    if s.polarity == 0:
                        neutral_tweets.append(tweets[i])
                        neutral_likes.append(likes[i])
                        neutral_time.append(time[i])
                    if s.polarity < 0:
                        negative_tweets.append(tweets[i])
                        negative_likes.append(likes[i])
                        negative_time.append(time[i])
                positive = len(positive_tweets)
                negative = len(negative_tweets)
                neutral = len(neutral_tweets)
                positive = round(100 * positive / len(tweets), 2)
                negative = round(100 * negative / len(tweets), 2)
                neutral = round(100 * neutral / len(tweets), 2)
                if positive > negative and positive > neutral:
                    mess = "Blockbuster movie"
                if (neutral > negative and neutral > positive) or (positive == negative == neutral) or (
                        neutral == 0 and positive == negative) or ():
                    mess = "Average movie"
                if negative > positive and negative > neutral:
                    mess = "Flop movies"
                now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(
                        "INSERT INTO `" + email + " sentiments`(`Date & Time`,`Movie Name`,`Category`,`Analysis`,`Positive`,`Neutral`,`Negative`)VALUES('" + now + "','" + Movie_Name + "','" + Category + "','" + mess + "'," + str(
                            positive) + "," + str(neutral) + "," + str(negative) + ")")
                    mysql.connection.commit()
                    cur.close()
                    posn = len(positive_tweets)
                    neun = len(neutral_tweets)
                    negn = len(negative_tweets)
                    return render_template("show sentiment.html", mess=mess, positive=positive, negative=negative,
                                           neutral=neutral, posn=posn, neun=neun, negn=negn,
                                           positive_tweets=positive_tweets, positive_likes=positive_likes,
                                           positive_time=positive_time, negative_tweets=negative_tweets,
                                           negative_likes=negative_likes, negative_time=negative_time,
                                           neutral_tweets=neutral_tweets, neutral_likes=neutral_likes,
                                           neutral_time=neutral_time)
                except Exception as e:
                    return f"<h1>{e}</h1>"

            if sel == "2":
                anger = 0
                disgust = 0
                fear = 0
                joy = 0
                neutral = 0
                sadness = 0
                shame = 0
                surprise = 0
                filename = 'emotion_classifier_pipeline'
                saved_clf = joblib.load(open(filename, 'rb'))
                df = pd.DataFrame(tweets, columns=['Tweets'])
                test = df['Tweets']
                lis = saved_clf.predict(test)
                lis = list(lis)
                n = len(lis)
                for i in range(len(lis)):
                    print(lis[i])
                    if lis[i] == 'anger':
                        anger += 1
                    if lis[i] == 'disgust':
                        disgust += 1
                    if lis[i] == 'fear':
                        fear += 1
                    if lis[i] == 'joy':
                        joy += 1
                    if lis[i] == 'neutral':
                        neutral += 1
                    if lis[i] == 'sadness':
                        sadness += 1
                    if lis[i] == 'shame':
                        shame += 1
                    if lis[i] == 'surprise':
                        surprise += 1
                anger = round(100 * anger / len(tweets), 2)
                disgust = round(100 * disgust / len(tweets), 2)
                fear = round(100 * fear / len(tweets), 2)
                joy = round(100 * joy / len(tweets), 2)
                neutral = round(100 * neutral / len(tweets), 2)
                sadness = round(100 * sadness / len(tweets), 2)
                shame = round(100 * shame / len(tweets), 2)
                surprise = round(100 * surprise / len(tweets), 2)
                now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(
                        "INSERT INTO `" + email + " emotions`(`Date & Time`,`Movie Name`,`Category`,`anger`,`disgust`,`fear`,`joy`,`neutral`,`sadness`,`shame`,`surprise`)VALUES('" + now + "','" + Movie_Name + "','" + Category + "'," + str(
                            anger) + "," + str(disgust) + "," + str(fear) + "," + str(joy) + "," + str(
                            neutral) + "," + str(
                            sadness) + "," + str(
                            shame) + "," + str(surprise) + ")")
                    mysql.connection.commit()
                    cur.close()
                    return render_template("show emotions.html", anger=anger, disgust=disgust, fear=fear, joy=joy,
                                           neutral=neutral, sadness=sadness, shame=shame, surprise=surprise,
                                           tweets=tweets, likes=likes, time=time, n=n, lis=lis)
                except Exception as e:
                    return f"<h1>{e}</h1>"

            if sel == "3":
                positive_tweets = []
                positive_likes = []
                positive_time = []
                negative_tweets = []
                negative_likes = []
                negative_time = []
                mess = ""
                df = pd.DataFrame(tweets, columns=['Tweets'])
                test2 = df['Tweets']
                file = "tfidf.pickle"
                trans = pickle.load(open(file, 'rb'))
                text1 = trans.transform(test2)
                filename = 'saved_model.sav'
                saved_clf = pickle.load(open(filename, 'rb'))
                tweets1 = saved_clf.predict(text1)
                tweets1 = list(tweets1)
                for i in range(len(tweets1)):
                    if tweets1[i] == "positive":
                        positive_tweets.append(tweets[i])
                        positive_likes.append(likes[i])
                        positive_time.append(time[i])
                    if tweets1[i] == "negative":
                        negative_tweets.append(tweets[i])
                        negative_likes.append(likes[i])
                        negative_time.append(time[i])
                positive = len(positive_tweets)
                negative = len(negative_tweets)
                positive = round(100 * positive / len(tweets), 2)
                negative = round(100 * negative / len(tweets), 2)
                if positive > negative:
                    mess = "Blockbuster movie"
                if negative == positive:
                    mess = "Average movie"
                if negative > positive:
                    mess = "Flop movies"
                now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(
                        "INSERT INTO `" + email + " sentiments machine lerning`(`Date & Time`,`Movie Name`,`Category`,`Analysis`,`Positive`,`Negative`)VALUES('" + now + "','" + Movie_Name + "','" + Category + "','" + mess + "'," + str(
                            positive) + "," + str(negative) + ")")
                    mysql.connection.commit()
                    cur.close()
                    posn = len(positive_tweets)
                    negn = len(negative_tweets)
                    return render_template("show m sentiment.html", mess=mess, positive=positive, negative=negative,
                                           posn=posn, negn=negn, positive_tweets=positive_tweets,
                                           positive_likes=positive_likes, positive_time=positive_time,
                                           negative_tweets=negative_tweets, negative_likes=negative_likes,
                                           negative_time=negative_time)
                except Exception as e:
                    return f"<h1>{e}</h1>"
    else:
        return render_template("tweeter.html", name=name, email=email)


@app.route("/history<email>")
def history(email):
    try:
        cur = mysql.connect.cursor()
        cur.execute("SELECT * FROM `" + email + " sentiments`")
        sentiments = cur.fetchall()
        cur.execute("SELECT * FROM `" + email + " emotions`")
        emotions = cur.fetchall()
        cur.execute("SELECT * FROM `" + email + " sentiments machine lerning`")
        machine_lerning = cur.fetchall()
        cur.close()
        sn = len(sentiments)
        em = len(emotions)
        sml = len(machine_lerning)
        return render_template("history.html", sn=sn, sentiments=sentiments, em=em, emotions=emotions, sml=sml,
                               machine_lerning=machine_lerning)
    except Exception as e:
        return f"<h1>{e}</h1>"


if __name__ == "__main__":
    app.run(debug=False)
