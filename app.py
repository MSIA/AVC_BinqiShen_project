import traceback
import logging.config

from flask import Flask
from flask import render_template, request, redirect, url_for
from src.add_application import Application, ApplicationManager

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
application_manager = ApplicationManager(app)
GENDERS = ['Male', 'Female']


@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """

    try:
        tracks = application_manager.session.query(Application).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html', tracks=tracks, genders=GENDERS)
    except:
        traceback.print_exc()
        logger.warning("Not able to display tracks, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST', 'GET'])
def add_entry():
    """View that process a POST with new song input

    :return: redirect to index page
    """
    if request.method == 'GET':
        return "Visit the homepage to add songs"
    elif request.method == 'POST':
        try:
            application_manager.add_track(
                artist=request.form['artist'],
                album=request.form['album'],
                title=request.form['title']
            )
            logger.info(
                "New song added: %s by %s",
                request.form['title'],
                request.form['artist']
            )
            return redirect(url_for('index'))
        except:
            logger.warning("Not able to display tracks, error page returned")
            return render_template('error.html')


@app.route('/about', methods=['GET'])
def about():
    """Add an 'about' page

    :return: redirect to the 'about' page
    """
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
