from flask import Flask, flash, render_template, send_file, request, session, url_for, flash, send_file, redirect
from flask_login import LoginManager, login_required
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from documentConversion import convertDoc, removeWatermark
from tempfile import mkdtemp
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt

application = app = Flask(__name__)
application.config['SECRET_KEY'] = 'supersecretkey'
application.config['UPLOAD_FOLDER'] = 'Static/Files'

application.config['SESSION_FILE_DIR'] = mkdtemp()
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)


#application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
#engine = create_engine("mysql+pymysql://" + open("userpass.txt", "r").readlines()[0] + "@18.212.177.201:8080//register")
engine = create_engine("".join(["sqlite+pysqlite:///", os.getcwd(), "/register"]), echo=True)
db = scoped_session(sessionmaker(bind=engine))
#db = SQLAlchemy(app)


#Create users table in database.
if not engine.has_table("users"):
    print("Doesn't have users table!")
    #TODO replace this with a SQL statement that creates the users table.
    db.execute("""CREATE TABLE register.users(
        username STRING PRIMARY KEY NOT NULL,
        password STRING NOT NULL
    );""")
    #TODO then check that this actually creates a db file in the proper location in the filesystem.


#Login Manager
login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@application.route('/', methods=['GET',"POST"])
@application.route('/home', methods=['GET',"POST"])
@login_required
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        print(file.filename) #just to demonstrate
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),application.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        #Process file.
        path = "Static/Files/"+file.filename
        print(path)
        convertDoc(path.replace(" ", "_"), ".docx")
        outpath = path.replace(".pdf", ".docx").replace(".PDF", ".docx") #by default, we are only converting PDF to DocX #the second replace() function is for case insensitivity.
        print(outpath)
        return send_file(outpath.replace(" ","_"))
        #return "File has been uploaded. <a href='/'>Return to Index </a>"
    return render_template('index.html', form=form)
    
@application.route("/login", methods=["GET", "POST"])
def login():
    #Forget any user_id
    
    session.clear()
    
    #User reached route by posting (submitting the login form):
    if request.method == "POST":
    
        username = request.form.get("username")
        password = request.form.get("password")
        
        usernamedata=db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata=db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()
        
        if usernamedata is None:
            flash("No username", "danger")
            return render_template("login.html")
        else:
            for passwor_data in passworddata:
                if hsa256_crypt.verify(password, passwor_data):
                    session["log"]=True
                    
                    flash("You are now logged in!")
                else:
                    flash("Incorrect password", "danger")
                    return render_template("login.html")
    return render_template("login.html")
 

#create register method which creates an account and stores its User object in db. 
@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=="POST":
        name=request.form.get("name")
        username=request.form.get("username")
        password=request.form.get("password")
        confirm=request.form.get("confirm")
        secure_password=sha256_crypt.encrypt(str(password))
        
        usernamedata=db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        #usernamedata=str(usernamedata)
        if usernamedata==None:
            if password==confirm:
                db.execute("INSERT INTO users(name,username,password) VALUES(:name,:username,:password)",
        {"name":name,"username":username,"password":secure_password})
                db.commit()
                flash("You are registered and can now login","success")
                return redirect(url_for('login'))
            else:
                flash("password does not match","danger")
                return render_template('register.html')
        else:
            flash("user already existed, please login or contact admin","danger")
            return redirect(url_for('login'))
        
    return render_template('register.html')

            
def apology(message):
    flash(message)
    return redirect("/")

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)