# Server
Contains files to run the server.

We use python's Flask for the web pages (http://flask.pocoo.org/) and run the server off a university machine.

To get to the server use a DICE terminal and these commands:

\> ssh jamiemcc@ssh.comp-soc.com

Password: "SlipGroupBee"

\> ssh elara.comp-soc.com 

Password: "SlipGroupBee"

Server code is in  /home/jamiemcc/SLIPServer/Server in the file server.py.

Flask should be installed on the UoE linux machines (else install it on your own machine), all you need to is activate the server environment by changing to the repository directory containing venv and type "source venv/bin/activate" then you can use "python server.py" to execute code.
