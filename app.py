from flask import Flask, render_template, url_for, request, redirect, session, flash, send_file
from flask import make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
from mutagen.mp3 import MP3
from pygame import *


app = Flask(__name__)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to Login first"

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MusicPlayer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(15))
    cover_photo = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    liked = db.relationship('Likes', backref='Songs')


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    mail_id = db.Column(db.String(15), nullable=False, unique=True)
    likes = db.relationship('Likes', backref='Users')


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    song_id = db.Column(db.Integer, db.ForeignKey(Songs.id))
    like = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if mixer.get_init:
        stop()
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']
        mail_id = request.form['mail_id']

        user = Users.query.filter_by(username=username).first()
        if user:
            flash("User Name Already Exists, Choose Different", "warning")
            return redirect("/signup")
        if(password == cpassword):
            new_user = Users(username=username,
                             password=hashed_password, mail_id=mail_id)
            db.session.add(new_user)
            db.session.commit()

            # message = "You have been succesfully registered in the Music Player!\nThank You For Registering."
            # server = smtplib.SMTP("smtp.gmail.com", 587)
            # server.starttls()
            # server.login("studentrepository20@gmail.com", "studentrepo")
            # server.sendmail("studentrepository20@gmail.com", email, message)

            flash("Sucessfully Registered!", "success")
            return redirect('/login')
        else:
            flash("Passwords don't match", "danger")
            return redirect("/signup")

    return render_template("sign-up.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if mixer.get_init():
        stop()
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        print(user)

        if not user:
            flash("No such User found, Try Signing Up First", "warning")
            return redirect("/signup")

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                print("Login Done!")
                return redirect("allsonglist")
            else:
                flash("Incorrect password", "danger")
                return redirect("login")

    return render_template("log-in.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "<h1>User Logged out</h1>"


@app.route('/')
def index():
    if mixer.get_init():
        stop()
    return render_template('home.html')


@app.route('/dashboard/<id>', methods=['POST', 'GET'])
@login_required
def dashboard(id):
    song = Songs.query.filter_by(id=id).first()
    return render_template('dashboard.html', song=song)


@app.route('/allsonglist', methods=['POST', 'GET'])
def allsonglist():
    songs = Songs.query.all()
    return render_template('allsonglist.html', songs=songs)


@app.route('/likedsonglist', methods=['POST', 'GET'])
@login_required
def likedsonglist():
    return render_template('likedsonglist.html')


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == "POST":
        print("Inside if")
        search_string = request.form['search_string']
        search = "{0}".format(search_string)
        search = search+'%'
        print(search)
        print("Initiated")

        results = Songs.query.filter(
            or_(Songs.name.like(search), Songs.artist.like(search))).all()
        print(results)
        if len(results) == 0:
            flash("No such song availabe!")
            print("mnoo")
        return render_template('search.html', results=results)
    return render_template('search.html')


def save_picture(form_picture):
    picture_fn = form_picture.filename
    print(picture_fn)
    picture_path = os.path.join(
        app.root_path, 'static\Song\SongCover', picture_fn)
    print(picture_path)
    form_picture.save(picture_path)
    print("Form_picture Saved")
    return picture_fn


def save_song(form_song):
    song_fn = form_song.filename
    song_path = os.path.join(
        app.root_path, 'static\Song\song', song_fn)
    print(song_path)
    form_song.save(song_path)
    print("Form_song Saved")
    return song_fn


@app.route('/addsongs', methods=['POST', 'GET'])
def addsongs():
    if request.method == 'POST':
        print("Inside if loop")
        songname = request.form.get('song')
        song = request.files['songpath']
        artist = request.form.get('artist')
        cover_photo = request.files['cover_photo']
        print("Got all the Form Info")
        song_file = save_song(song)
        cover_file = save_picture(cover_photo)
        print("Saved Song And Cover Photo")
        print(song_file)
        print(cover_file)

        audio = MP3(f"static\Song\song\{song_file}")
        audio_info = audio.info
        length_in_secs = int(audio_info.length)
        hours, mins, seconds = convert(length_in_secs)

        duration = f"{mins}:{seconds}"
        print(duration)

        path = f"static\Song\song\{song_file}"

        new_song = Songs(path=path, name=songname,
                         cover_photo=cover_file, artist=artist, duration=duration)
        db.session.add(new_song)
        db.session.commit()
        print("Session commited")
        return "Song Added"
    return render_template('add_songs.html')


@app.route('/play/<id>', methods=['POST'])
def play(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.load(song.path)
    mixer.music.play()
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/pause/<id>', methods=['POST'])
def pause(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.pause()
    url = f"/dashboard/{id}"
    return redirect(url)


@app.route('/unpause/<id>', methods=['POST'])
def unpause(id):
    mixer.init()
    song = Songs.query.filter_by(id=id).first()
    mixer.music.unpause()
    url = f"/dashboard/{id}"
    return redirect(url)


def stop():
    mixer.music.stop()
    return 0


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
