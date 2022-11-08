from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

# PAGES: endpoints that return webpages

@app.route('/')
def index():
    """
    The homepage. Overview and vague details
    """
    return render_template('index.html')


@app.route('/nodes')
def index():
    """
    Details on known nodes, ability to add new node
    """
    return render_template('index.html')


@app.route('/connections')
def index():
    """
    Current connections, allows user to start new connection
    """
    return render_template('index.html')



# API CALLS: not meant to be called by a browser

@app.route('/api/startlistener', methods=['POST'])
def startListener():
    """
    Takes parameters, validates them, and starts a listener process
    User can then monitor the listener from the main page
    """
    pass


@app.route('/api/startsender', methods=['POST'])
def startSender():
    """
    Takes parameters, validates them, and starts a sender process
    User can then monitor the sender from the main page
    """
    pass


@app.route('/api/nodes', methods=['GET'])
def getNodes():
    """
    Returns list of known nodes
    """
    pass


@app.route('/api/node/<node_id>', methods=['GET'])
def getNodeDetails(node_id):
    """
    Returns details for a single node
    """
    pass


@app.route('/api/addnode', methods=['POST'])
def addNode():
    """
    Called from a submission box. user has uploaded a key
    Save this file as a new server or client or whatever
    update config to keep track of it?
    """
    pass




if __name__ == '__main__':
    # Load config

    # start web server
    # app.run(debug=True, port=80)
    serve(app, port=80)