import json
import os

from flask import Flask, render_template, request, redirect, url_for, send_file
from net import zWorker
from waitress import serve

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
    global friends
    global config

    if request.method == 'POST':
        print(request.form)

        msg = None

        if 'type' in request.form.keys() and 'action' in request.form.keys():
            if request.form['action'] == 'connect':
                if request.form['type'] == 'listener':
                    if request.form['hostname'] in friends.keys():
                        f = friends[request.form['hostname']]
                        listener = zWorker(zWorker.LISTENER,datadir=os.path.dirname(__file__))
                        success = listener.start(port=f['port'],host=f['hostname'])
                        if not success:
                            msg = "Unable to connect to server. Check configuration."
                            listener = None
                        else:
                            print('successfully started listener')
                    else:
                        msg = 'Hostname not found'
                elif request.form['type'] == 'sender':
                    sender = zWorker(zWorker.SENDER,datadir=os.path.dirname(__file__))
                    success = sender.start(port=config['zmqservport'])
                    if not success:
                        msg = "Unable to start server. Check configuration."
                        listener = None
                else:
                    msg = 'Not a valid type'
            elif request.form['action'] == 'disconnect':
                if request.form['type'] == 'listener':
                    listener.stop()
                    listener = None
                elif request.form['type'] == 'sender':
                    sender.stop()
                    sender = None
                else:
                    msg = 'Not a valid type'
            else:
                msg = 'Not a valid action'
        
        if msg is None:
            return render_template('connections.html',
                zsender=sender,
                zlistener=listener,
                friends=friends)
        else:
            # bad post request - show error
            return render_template('connections.html',
                zsender=sender,
                zlistener=listener,
                friends=friends,
                error=True,
                errormsg=msg)

    else:
        #if sender is None:
        #    sender = zWorker(zWorker.SENDER)
        
        return render_template('connections.html',
            zsender=sender,
            zlistener=listener,
            friends=friends)
        

@app.route('/nodes', methods=['GET'])
def nodes():
    """
    Details on known nodes, ability to add new node
    view node if 
    
    """
    global friends

    if 'refresh' in request.args.keys():
            if request.args['refresh'] == 'true':
                friends = loadFriends()

    if 'view' in request.args.keys():
        f = request.args['view']
        if f in friends.keys():
            path = os.path.join(app.root_path,os.path.normpath(f'./data/friends/{f}.key'))
            #print(path)
            #print(os.path.exists(path))
            if os.path.exists(path):
                haskey = "Key saved for this user"
            else:
                haskey = "Key not uploaded for this user"
            return render_template('nodes.html',
                friends=friends,
                hostname=friends[f]['hostname'],
                port=friends[f]['port'],
                haskey=haskey
                )
    
    if 'new' in request.args.keys():
        if request.args['new'] == 'true':
            return render_template('nodes.html',friends=friends,hostname='new')

    return render_template('nodes.html',friends=friends)


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
    path = os.path.join(app.root_path,'./data/server/server.key')
    return send_file(path, as_attachment=True)


# this ones for fun teehee

@app.route('/nitw')
def nitw():
    path = os.path.normpath("C:\\Users\\star-tower\\Pictures\\new nitw.png")
    return send_file(path, as_attachment=False)


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
    global friends
    if request.method == 'POST':
        if 'hostname' in request.form.keys() and 'port' in request.form.keys():
            nHostname = request.form['hostname']
            nPortStr = request.form['port']

            try:
                nPort = int(nPortStr)
            except:
                print('not a port')
                return render_template('nodes.html',friends=friends, error='bad hostname',hostname=nHostname,port=nPortStr)

            if nHostname in friends.keys():
                friends[nHostname]['port'] = nPort
            else:
                friends[nHostname] = {
                    'hostname': nHostname,
                    'port': nPort
                }

            didsave = saveFriends(friends)
            if not didsave:
                print('error saving friends json')

            if 'key' in request.files.keys() and request.files['key'].filename != '':
                newfile = request.files['key']
                print(newfile.filename)

                if newfile.filename.split('.')[-1] != 'key':
                    print('wrong extension IDIOT!!!!')
                    return render_template('nodes.html',friends=friends, error='bad file extension',hostname=nHostname,port=nPortStr)

                fcontent = newfile.read()
                try:
                    fcontd = fcontent.decode('ascii')
                except:
                    print('decode error')
                
                print(len(fcontd))
                if len(fcontd) > 400:
                    print('file too dang long')
                
                if 'public-key' not in fcontd:
                    print('not a public-key')
                
                print(fcontd)

                newpath = os.path.join(app.root_path,
                    os.path.normpath(f'./data/friends/{nHostname}.key'))
                
                with open(newpath,'w') as f:
                    f.write(fcontd.replace('\r',''))

            return redirect(url_for('nodes',view=nHostname))
        else:
            return
    else:
        return friends
        



# ============ NON PAGE HELPERS ===========

def loadConfig():
    with open('./app/data/config.json', 'r') as c:
        try:
            config = json.load(c)
        except:
            print('unable to load config. Exiting')
            config = None
    return config


def loadFriends():
    with open('./app/data/friends/friends.json', 'r') as f:
        try:
            friends = json.load(f)
        except:
            print('unable to load friends. Exiting')
            friends = None
    return friends

def saveFriends(friends):
    path = os.path.join(app.root_path,os.path.normpath('./data/friends/friends.json'))
    print(path)
    with open(path, 'w') as f:
        try:
            json.dump(friends, f, indent=4)
        except Exception as e:
            print(e)
            return None
    return friends

if __name__ == '__main__':
    # Load config

    config = loadConfig()
    friends = loadFriends()

    # start web server
    if config is not None and friends is not None:
        if config['debug']:
            app.run(debug=True, port=config['flaskport'])
        else:
            serve(app, port=config['flaskport'])
