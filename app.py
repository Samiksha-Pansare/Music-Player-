from flask import Flask, render_template, url_for, request, redirect, session, flash, send_file
from flask import make_response, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)

db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message = "You need to Login first"

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MusicPlayer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    artist = db.Column(db.String(15))
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


# @login_manager.user_loader
# def load_user(user_id):
#     return Users.query.get(int(user_id))


# @app.route('/signUp', methods=['GET', 'POST'])
# def signUp():
#     if request.method == "POST":
#         username = request.form['username']
#         password = request.form['password']
#         hashed_password = generate_password_hash(password, method="sha256")
#         cpassword = request.form['cpassword']
#         email = request.form['email']

#         mentor = Mentor.query.filter_by(username=mentorname).first()
#         user = Student.query.filter_by(rollno=rollno).first()
#         if user:
#             flash("User with the Roll No. Already Exists", "warning")
#             return redirect("/signUp")
#         if(password == cpassword):
#             new_user = Student(fname=fname, rollno=rollno, password=hashed_password,
#                                email=email, mobno=mobno, mentor=mentor)
#             db.session.add(new_user)
#             message = "You have been succesfully registered in the Student Repository!\nThank You For Registering."
#             server = smtplib.SMTP("smtp.gmail.com", 587)
#             server.starttls()
#             server.login("studentrepository20@gmail.com", "studentrepo")
#             server.sendmail("studentrepository20@gmail.com", email, message)
#             db.session.commit()
#             flash("Sucessfully Registered!", "success")
#             return redirect('/login')
#         else:
#             flash("Passwords don't match", "danger")
#             return redirect("/signUp")

#     return render_template("signUp.html")

# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == "POST":
#         username = request.form['username']
#         password = request.form['password']

#         user = Student.query.filter_by(username=username).first()

#         if not user:
#             flash("No such Student found, Try Signing Up First", "warning")
#             return redirect("/signUp")

#         if user:
#             if check_password_hash(user.password, password):
#                 login_user(user)
#                 return redirect(url_for("home", currentuser=current_user))
#             else:
#                 flash("Incorrect password", "danger")
#                 return redirect("login")

#     return render_template("login.html")


@app.route('/')
def index():
    return "Hello"


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
