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


app = Flask(__name__)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to Login first"

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MusicPlayer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(15))
    cover_photo = db.Column(db.String(100))
    duration = db.Column(db.Time)
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
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']
        mail_id = request.form['mail_id']

        user = Users.query.filter_by(username=username).first()
        if user:
            flash("User Name Already Exists, Choose Different", "warning")
            return redirect("/signUp")
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
            return redirect("/signUp")

    return render_template("sign-up.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        print("username - ", username)
        print("password - ", password)

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
    return render_template('home.html')

@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/allsonglist', methods=['POST', 'GET'])
@login_required
def allsonglist():
    return render_template('allsonglist.html')

@app.route('/likedsonglist', methods=['POST', 'GET'])
@login_required
def likedsonglist():
    return render_template('likedsonglist.html')

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    return render_template('search.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    print(f_ext)
    picture_path = os.path.join(
        app.root_path, 'static\Song\SongCover', picture_fn)
    print(picture_path)
    form_picture.save(picture_path)
    print("form_picture Saved")
    return picture_fn

def save_song(form_song):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_song.filename)
    song_fn = random_hex + f_ext
    print(f_ext)
    song_path = os.path.join(
        app.root_path, 'static\Song\song',song_fn)
    print(song_path)
    form_song.save(song_path)
    print("form_song Saved")
    return song_fn


@app.route('/addsongs', methods=['POST', 'GET'])
def addsongs():
    if request.method=='POST':
        songpath = request.files['songpath']
        songname = request.form.ge('songname')
        artist = request.form.get('artist')
        cover_photo = request.files['cover_photo']
        song_file = save_song(songname)
        cover_file = save_picture(cover_photo)
        print("songfile variable assigned")
        print(song_file)
        audio = MP3(f"static\Song\song\{}".format(song_file))
        audio_info = audio.info    
        length_in_secs = int(audio_info.length)
        hours, mins, seconds = convert(length_in_secs)
        duration = f"{}:{}".format(mins,seconds)
        print(duration)
        new_song = Songs(path=song_file, name=songname, cover_photo = cover_file, artist=artist,duration=duration)
        student.image_file = picture_file
        db.session.commit()
        print("Session commited")
        return "songadded"
    return render_template('add_songs.html')
    


@app.route('/profilepic/<int:student_id>', methods=['POST'])
def profilepic(student_id):
    print("inside profile pic function")
    student = Student.query.filter_by(id=student_id).first()
    print("Query for one student")
    picture_file = save_picture(request.files['profile_pic'])
    print("picture_file variable assigned")
    print(picture_file)
    student.image_file = picture_file
    db.session.commit()
    print("Session commited")
    return redirect(url_for("feed", currentuser=current_user))
        




    return render_template('add_songs.html')





if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
