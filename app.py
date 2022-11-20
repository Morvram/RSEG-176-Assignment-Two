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

application = app = Flask(__name__)
application.config['SECRET_KEY'] = 'supersecretkey'
application.config['UPLOAD_FOLDER'] = 'Static/Files'

application.config['SESSION_FILE_DIR'] = mkdtemp()
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)


#TODO create User class (https://realpython.com/using-flask-login-for-user-management-with-flask/)



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
        
        #Using request form input to generate user
        
        #Ensure username and password were submitted, and protect from SQL injection attacks.
        if not request.form.get("username"):
            return apology("Must provide username.")
        if not request.form.get("password"):
            return apology("Must provide password.")
        if "'" in request.form.get("username") or ";" in request.form.get("username") or "'" in request.form.get("password") or ";" in request.form.get("password"):
            return apology("No SQL injection, please!")
            
        user = User.objects(name=username, password=password).first()
        
        if user:
            login_user(user)
            return redirect("/")
        else:
            return apology("Login not successful.")
        

    else:
        return render_template("login.html")
 

#TODO create register method which creates an account and stores its User object in db. 
            
def apology(message):
    flash(message)
    return redirect("/")

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)