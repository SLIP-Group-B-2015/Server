# Server
Contains files to run the server.

We use python's Flask for the web pages (http://flask.pocoo.org/) and run the server off a university machine.

To get to the server use a DICE terminal and these commands:

\> ssh jamiemcc@ssh.comp-soc.com

Password: "SlipGroupBee"

\> ssh elara.comp-soc.com 

Password: "SlipGroupBee"

Server code is in  /home/jamiemcc/SLIPServer/Server.

Flask should be installed on the UoE linux machines (else install it on your own machine), all you need to do is activate the server environment by switching to home/jamiemcc/SLIPServer (make sure it containins venv) and type "source venv/bin/activate" then you can move into the Server directory and type "python server.py" to run the server.
