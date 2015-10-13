from flask import Flask, request, render_template
# Configurations
USERNAME = "admin" # (temporary check until database is working)
PASSWORD = "password"

# Create app object
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods=['POST', 'GET'])
def home(name=None):
    if request.method == 'POST':
        return "This is a test! It works! %s username" % request.form['username']
    else:
        return "It failed"

@app.route('/test/')
def test():
    return 'The web site you are trying to reach is undergoing construction by a team of highly trained monkies. Please visit another time!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
