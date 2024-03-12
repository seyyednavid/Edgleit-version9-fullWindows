"""
This module defines routes for the web application, including sign-in, main page, server settings,
video management (uploading, removing), and call-forwarding functionality.
"""

from appContents import app
from flask import render_template, request, flash, redirect, url_for
from appContents.models import Settings
from flask import redirect, url_for, request
from appContents.websocket import called_position
from werkzeug.utils import secure_filename
from appContents.forms import SignInForm
from appContents import db;
from flask import session
from datetime import timedelta
import os;
import re;

            

# Set the session permanent and specify session timeout for 60 minutes
app.permanent_session_lifetime = timedelta(minutes=30)




@app.errorhandler(404)
def page_not_found(error):
    # Render a custom 404 page
    return render_template('404.html'), 404

@app.route("/")
@app.route("/signin",  methods=['GET', 'POST'])
def signin():
    """
    Route for sign-in page.

    Renders the sign-in form. If the form is submitted with valid credentials, the user is
    redirected to the main page; otherwise, an error message is displayed.
    """
    form = SignInForm()
    if form.validate_on_submit():
        if(form.username.data == os.getenv("SIGNIN_USERNAME") and form.password.data ==os.getenv("SIGNIN_PASSWORD")) :
          session['authenticated'] = True
          return redirect(url_for('main'))
        else :
          flash("Invalid username or password", "error")
    return render_template("signin.html" , form=form)





@app.route("/main")
def main():
    """
    Route for the main page.

    Renders the main page if the user is authenticated; otherwise, redirects to the sign-in page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    return render_template("main.html")





@app.route("/settings", methods=["POST", "GET"])
def edgelit_save():
    """
    Route for managing server settings (Edgeled's settings).

    GET method:
        Renders the server settings page, displaying existing settings.

    POST method:
        Processes form submission for updating server settings and redirects to the main page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    if request.method == "GET":
        edgeled_settings = {
            'flashspeededgelit': [],
            'numofflashes': [],
            'on_color': [],
            'off_color': [],
            'free_color': [],
            'busy_color': []
        }
        for i in range(1, 24):
            data_in_db = Settings.query.filter_by(id=i).first()
            if data_in_db:
                edgeled_settings['flashspeededgelit'].append(data_in_db.flashspeededgelit)
                edgeled_settings['numofflashes'].append(data_in_db.numofflashes)
                edgeled_settings['on_color'].append(data_in_db.on_color)
                edgeled_settings['off_color'].append(data_in_db.off_color)
                edgeled_settings['free_color'].append(data_in_db.free_color)
                edgeled_settings['busy_color'].append(data_in_db.busy_color)
        # Get the whole info from db and show them into Server setting page
        return render_template("serverSetting.html", edgeled_settings=edgeled_settings)
    elif request.method == "POST":
        form_data = request.form
        for i in range(1, 24):
            existing_setting = Settings.query.filter_by(id=i).first()
            if existing_setting:
                existing_setting.flashspeededgelit = form_data[f'flashspeededgelit{i}']
                existing_setting.numofflashes = form_data[f'numofflashes{i}']
                existing_setting.on_color = form_data[f'on_color{i}']
                existing_setting.off_color = form_data[f'off_color{i}']
                existing_setting.free_color = form_data[f'free_color{i}']
                existing_setting.busy_color = form_data[f'busy_color{i}']
            else:
                new_setting = Settings(
                    flashspeededgelit=form_data[f'flashspeededgelit{i}'],
                    numofflashes=form_data[f'numofflashes{i}'],
                    on_color=form_data[f'on_color{i}'],
                    off_color=form_data[f'off_color{i}'],
                    free_color=form_data[f'free_color{i}'],
                    busy_color=form_data[f'busy_color{i}']
                )
                db.session.add(new_setting)
        db.session.commit()
        return redirect(url_for('main'))





videos_folder = "appContents/static/videos"
# List all files in the videos folder
video_files = os.listdir(videos_folder)
# Create a dictionary to store video files
video_files_dict = {}
# Iterate through the list of filenames
for filename in video_files:
    # Check if the filename is for the background video
    if filename.lower() == "background.mp4":
        background_filename = filename
        # Add the background filename to the dictionary
        video_files_dict["background"] = background_filename
    else:
        # Extract the numeric part of the filename using regular expression
        match = re.match(r'(\d+)\.mp4', filename)
        if match:
            key = match.group(1)
            video_files_dict[key] = filename

@app.route('/callforward')
def call_forward():
    """
    Route for callforward page to display desired videos.

    Renders the callforward page, passing the dictionary of video filenames.
    """
    return render_template('callforward.html', video_files=video_files_dict, position=called_position, flask_ip_address=os.getenv("FLASK_IP_ADDRESS"), websocket_port=os.getenv("WEBSOCKET_PORT"))





# Validation for accepting only .mp4 file for uploading videos
ALLOWED_EXTENSIONS = ['mp4']

def allowed_file(filename):
    """Check if the filename has a valid .mp4 extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_filename(filename):
    """Normalize the filename by converting it to lowercase and removing spaces."""
    parts = filename.strip().split(".")
    return parts[0].lower().replace(' ', '').replace('_', '') + "." + parts[1]

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Route for uploading videos.

    GET method:
        Renders the upload videos page.

    POST method:
        Processes video upload, saves the files, and redirects back to the upload page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    
    if request.method == 'GET':
        return render_template("uploadVideos.html") 
    
    elif request.method == 'POST':
        uploaded_files = request.files.getlist('video')
        upload_folder = os.path.join(app.root_path, 'static', 'videos')
        
        # Check if no files were selected
        if not uploaded_files or all(video.filename == '' for video in uploaded_files):
            flash('No files selected for upload', 'error')
            return redirect(url_for('upload'))
        
         # Process uploaded files
        for video in uploaded_files:
            if video.filename != '':
                if allowed_file(video.filename):
                    # Normalize the filename
                    filename = normalize_filename(secure_filename(video.filename))
                    # Condition for accepting video file names:
                    # The filename must be 'background.mp4' or a numeric value between 1.mp4 and 100.mp4    
                    if filename == 'background.mp4' or (filename.endswith('.mp4') and filename[:-4].isdigit() and 1 <= int(filename[:-4]) <= 100):
                        video.save(os.path.join(upload_folder, filename))
                    else:
                        flash('Invalid filename. Video names must be between 1.mp4 and 100.mp4, including background.mp4', 'error')
                        return redirect(url_for('upload'))
                else:
                    flash('Invalid file format. Only .mp4 files are allowed.', 'error')
                    return redirect(url_for('upload'))
        
        # Check if all files were successfully uploaded
        if len(uploaded_files) == 1:
            flash('Video uploaded successfully', 'success')
        else:
            flash(f'All {len(uploaded_files)} videos uploaded successfully', 'success')
        return redirect(url_for('upload'))
    
    return redirect(url_for('upload'))






def get_video_files():
    """
    Retrieve a list of video files from the static/videos directory.

    Returns:
        list: List of video file names.
    """
    upload_folder = os.path.join(app.root_path, 'static', 'videos')
    video_files = os.listdir(upload_folder)
    sorted_video_files = sorted(video_files, key=custom_sort_key)
    return sorted_video_files

def custom_sort_key(filename):
    """
    Custom ing key function for ing filenames.

    This function separates filenames into numeric and non-numeric parts,
    converting the numeric part into an integer and keeping the non-numeric
    part as a string. The resulting tuple is used as the ing key.
    """
    parts = [], []
    for c in filename:
        parts[0 if c.isdigit() else 1].append(c)
    return (int(''.join(parts[0])), ''.join(parts[1]))


@app.route('/remove')
def show_remove_page():
    """
    Route for displaying videos on the remove page.

    Renders the removeVideos page, passing the list of current video files.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    current_video_files = get_video_files()
    return render_template('removeVideos.html', video_files=current_video_files)


@app.route('/remove_video/<filename>')
def remove_video(filename):
    """
    Route for removing a video file.

    Removes the specified video file and redirects to the remove page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    upload_folder = os.path.join(app.root_path, 'static', 'videos')
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"The video '{filename}' has been successfully removed.", "success")
    else:
        flash(f"The video '{filename}' does not exist.", "error")
    return redirect(url_for('show_remove_page'))

@app.route("/logout")
def logout():
    """
    Route for logging out the user.

    Clears the session and redirects to the sign-in page.
    """
    session.clear()
    return redirect(url_for('signin'))


