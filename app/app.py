from flask import Flask, render_template, request, send_file
from waitress import serve
import json
import os

from net import zWorker


app = Flask(__name__)
listener = None
sender = None

# PAGES: endpoints that return webpages

@app.route('/')
def index():
    """
    The homepage. Overview and vague details
    """
    return render_template('index.html',zport=config['zmqservport'], isdebug=config['debug'])


@app.route('/connections', methods=['GET','POST'])
def connections():
    """
    Current connections, allows user to start new connection
    
    POST:
        type: listener/sender
        action: start/stop
        friend: id (for listener only)
    """
    global sender
    global listener

    if request.method == 'POST':
        if 'type' in request.form.keys() and 'action' in request.form.keys():
            if request.form['type'] == 'listener':
                if 'friend' in request.form.keys():
                    pass
        else:
            # bad post request - show error
            return render_template('connections.html',zsender=sender,zlistener=listener, error=True)

    else:
        if sender is None:
            sender = zWorker(zWorker.SENDER)
        
        return render_template('connections.html',zsender=sender,zlistener=listener)
    

@app.route('/nodes')
def nodes():
    """
    Details on known nodes, ability to add new node
    """
    return render_template('nodes.html')


@app.route('/info')
def info():
    """
    Version, your own pubkey, and other info
    """
    return render_template('info.html',
        version='0.0.0',
        hostname=config['hostname'],
        port=config['zmqservport']
        )


@app.route('/pubkey')
def pubkey():
    path = os.path.join(app.root_path,'./data/server/pubkey.key')
    return send_file(path, as_attachment=True)


# API CALLS: not meant to be called by a browser

@app.route('/api/listener', methods=['POST'])
def startListener():
    """
    Takes parameters, validates them, and starts a listener process
    User can then monitor the listener from the main page
    
    messagetype:
        start
        stop
    """
    
    pass


@app.route('/api/sender', methods=['POST'])
def startSender():
    """
    Takes parameters, validates them, and starts a sender process
    User can then monitor the sender from the main page

    messagetype:
        start
        stop
    """
    pass


@app.route('/api/nodes', methods=['GET','POST'])
def getNodes():
    """
    GET:
    Returns list of known nodes

    POST:
    Called from a submission box. user has uploaded a key
    Save this file as a new server or client or whatever
    update config to keep track of it?
    """
    pass


@app.route('/api/node/<node_id>', methods=['GET'])
def getNodeDetails(node_id):
    """
    Returns details for a single node
    """
    pass



if __name__ == '__main__':
    # Load config

    with open('./app/data/config.json') as c:
        try:
            config = json.load(c)
        except:
            print('unable to load config. Exiting')
            config = None
    

    # start web server
    if config is not None:
        if config['debug']:
            app.run(debug=True, port=config['flaskport'])
        else:
            serve(app, port=config['flaskport'])
