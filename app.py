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
import sqlite3
from passlib.hash import sha256_crypt
import watermark

application = app = Flask(__name__)
application.config['SECRET_KEY'] = 'supersecretkey'
application.config['UPLOAD_FOLDER'] = 'Static/Files'

application.config['SESSION_FILE_DIR'] = mkdtemp()
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)

con = sqlite3.connect("register.db", check_same_thread=False)
cur = con.cursor()

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
    
@application.route('/', methods=['GET',"POST"])
def home():
    try:
        if session["log"] == False:
            return apology("Please log in.")
    except: #session['log'] doesn't exist.
        return apology("Please log in.")
    if request.method == "POST":
        print("Request method is POST.")
        form = UploadFileForm()
        print("form is UploadFileForm().")
        if form.validate_on_submit():
            print("Grabbing file...")
            file = form.file.data # First grab the file
            print("Grabbed file.")
            print(file.filename) #just to demonstrate
            print("Saving file...")
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),application.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
            print("Saved file.")
            #Process file.
            print("Path:")
            path = "Static/Files/"+file.filename
            print(path)
            #Add watermark
            print("Adding watermark...")
            path = watermark.put_watermark(path, "watermark_"+path,"watermark.pdf")
            print("Watermark added.")
            print("Converting document...")
            convertDoc(path.replace(" ", "_"), ".docx")
            print("Converted. Outpath:")
            outpath = path.replace(".pdf", ".docx").replace(".PDF", ".docx") #by default, we are only converting PDF to DocX #the second replace() function is for case insensitivity.
            print(outpath)
            print("Sending file...")
            return send_file(outpath.replace(" ","_"))
            #return "File has been uploaded. <a href='/'>Return to Index </a>"
    return render_template("index.html", form=UploadFileForm())
    
    
@application.route("/login", methods=["GET", "POST"])
def login():
    #Forget any user_id
    
    #session.clear()
    #print("Cleared session.")
    
    #User reached route by posting (submitting the login form):
    if request.method == "POST":
    
        username = request.form.get("username")
        password = request.form.get("password")
        
        #Protect from SQL injection attacks.
        if "'" in request.form.get("username") or ";" in request.form.get("username") or "'" in request.form.get("password") or ";" in request.form.get("password"):
            return apology("No SQL injection, please!")
        
        usernamedata=cur.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata=cur.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()
        
        if usernamedata is None:
            flash("No username", "danger")
            return render_template("login.html")
        else:
            for passwor_data in passworddata:
                if sha256_crypt.verify(password, passwor_data):
                    session["log"]=True
                    session["logged_in"]=True
                    session["user_name"] = username
                    print("Logged in.")
                    flash("You are now logged in!")
                    return render_template("index.html", form=UploadFileForm())
                else:
                    flash("Incorrect password", "danger")
                    print("Not logged in.")
                    return render_template("login.html")
    return render_template("login.html")
 

#create register method which creates an account and stores its User object in db. 
@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        confirm=request.form.get("confirmation")
        
        #Protect from SQL injection attacks.
        if "'" in request.form.get("username") or ";" in request.form.get("username") or "'" in request.form.get("password") or ";" in request.form.get("password"):
            return apology("No SQL injection, please!")
            
        print("Confirmed data received from form.")
        secure_password=sha256_crypt.hash(str(password))
        print("Created secure password.")
        usernamedata=cur.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        print("Retrieved usernamedata.")
        #usernamedata=str(usernamedata)
        if usernamedata is None:
            if password==confirm:
                cur.execute("INSERT INTO users(username,password) VALUES(:username,:password)",
        {"username":username,"password":secure_password})
                con.commit()
                print("Committed new user to database.")
                flash("You are registered and can now login","success")
                return redirect("/login")
            else:
                print("Password mismatch.")
                flash("password does not match","danger")
                return render_template('register.html')
        else:
            print("User already existed.")
            flash("user already existed, please login or contact admin","danger")
            return redirect("/login")
        
    return render_template('register.html')

            
def apology(message):
    flash(message)
    print(message)
    return render_template("login.html")

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)