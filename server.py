from flask import Flask, render_template
# Configurations
USERNAME = "admin"
PASSWORD = "password"

# Create app object
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def home(name=None):
    return render_template('simpleLink.html', name=name)

@app.route('/test/')
def test():
    return 'The web site you are trying to reach is undergoing construction by a team of highly trained monkies. Please visit another time!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
