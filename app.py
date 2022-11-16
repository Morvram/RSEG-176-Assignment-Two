from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from documentConversion import convertDoc, removeWatermark

application = app = Flask(__name__)
application.config['SECRET_KEY'] = 'supersecretkey'
application.config['UPLOAD_FOLDER'] = 'Static/Files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@application.route('/', methods=['GET',"POST"])
@application.route('/home', methods=['GET',"POST"])
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

if __name__ == '__main__':
    application.run(debug=True)