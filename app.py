from flask import Flask, flash, render_template, send_file, request, session, url_for, flash, send_file, redirect
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from documentConversion import convertDoc, removeWatermark
from helpers import login_required #TODO this package won't import. Resolve that.

application = app = Flask(__name__)
application.config['SECRET_KEY'] = 'supersecretkey'
application.config['UPLOAD_FOLDER'] = 'Static/Files'

application.config['SESSION_FILE_DIR'] = mkdtemp()
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@application.route('/', methods=['GET',"POST"])
@application.route('/home', methods=['GET',"POST"])
#TODO require login.
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
    
@app.route("/login", methods=["GET", "POST"])
def login():
    #Forget any user_id
    
    session.clear()
    
    #User reached route by posting (submitting the login form):
    if request.method == "POST":
        #Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.")
        #Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password.")
        
        #Protects the app from SQL injection attacks.
        if "'" in request.form.get("username") or ";" in request.form.get("username") or "'" in request.form.get("password") or ";" in request.form.get("password"):
            return apology("No SQL injection, please!")
        
        #Query database for username.
        #TODO actually create the database lol
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
                          
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)    

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")
        
            
def apology(message):
    flash(message)
    return redirect("/")

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)