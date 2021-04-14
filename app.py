from flask import Flask, render_template, url_for, request, redirect, session, flash, send_file
from flask import make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os

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
    artist = db.Column(db.String(15))
    cover_photo = db.Column(db.String(100))
    duration = db.Column(db.Time)
    likes = db.Column(db.Integer, default=0)
    liked = db.relationship('Likes', backref='Songs')


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(15), nullable=False)
    mail_id = db.Column(db.String(15), nullable=False)
    likes = db.relationship('Likes', backref='Users')


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    song_id = db.Column(db.Integer, db.ForeignKey(Songs.id))
    like = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


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
            # message = "You have been succesfully registered in the Music Player!\nThank You For Registering."
            # server = smtplib.SMTP("smtp.gmail.com", 587)
            # server.starttls()
            # server.login("studentrepository20@gmail.com", "studentrepo")
            # server.sendmail("studentrepository20@gmail.com", email, message)
            db.session.commit()
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
                return currentuser.username
            else:
                flash("Incorrect password", "danger")
                return redirect("login")

    return render_template("log-in.html")


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
