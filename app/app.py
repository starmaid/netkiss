# app.py
# This file runs the flask webserver

import json
import os
import subprocess

from flask import Flask, render_template, request, redirect, url_for, send_file
from waitress import serve

from net import zWorker

app = Flask(__name__)
listener = None
sender = None

# PAGES: endpoints that return webpages =======================================

@app.route('/')
def index():
    """
    The homepage. Network graph and data preview.
    """
    global listener
    text = None
    image = None
    if listener is not None:
        # we have some data to preview
        d = listener.getData()
        print(d)
        if d['type'] == 'txt':
            text = d['data'] 
        # TODO handle and implement more types of data
    
    return render_template('index.html',zport=config['zmqservport'], isdebug=config['debug'],text=text,image=image)


@app.route('/connections', methods=['GET','POST'])
def connections():
    """
    Current connections, allows user to start new connection
    or close an existing one.
    GET:
        (returns webpage)
    
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
        msg = None

        if 'type' in request.form.keys() and 'action' in request.form.keys():
            if request.form['action'] == 'connect':
                if request.form['type'] == 'listener':
                    if listener is not None:
                        msg = "Error: already connected to server"
                    else:
                        if request.form['hostname'] in friends.keys():
                            f = friends[request.form['hostname']]
                            listener = zWorker(zWorker.LISTENER,datadir=os.path.dirname(__file__))
                            success = listener.start(port=f['port'],host=f['hostname'])
                            print('after listener start')
                            if not success:
                                msg = "Unable to connect to server. Check configuration."
                                listener = None
                            else:
                                print('successfully started listener')
                        else:
                            msg = 'Hostname not found'
                elif request.form['type'] == 'sender':
                    if sender is not None:
                        msg = "Error: server already active"
                    else:
                        sender = zWorker(zWorker.SENDER,datadir=os.path.dirname(__file__))
                        success = sender.start(port=config['zmqservport'])
                        if not success:
                            msg = "Unable to start server. Check configuration."
                            listener = None
                else:
                    msg = 'Not a valid type'
            elif request.form['action'] == 'disconnect':
                if request.form['type'] == 'listener':
                    if listener is None:
                        msg = "Error: no active server connection"
                    else:
                        listener.stop()
                        listener = None
                elif request.form['type'] == 'sender':
                    if sender is None:
                        msg = "Error: no active server"
                    else:
                        sender.stop()
                        sender = None
                else:
                    msg = 'Not a valid type'
            else:
                msg = 'Not a valid action'
        
        if msg is None:
            # Successful request
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
        # this is just a GET for the page
        return render_template('connections.html',
            zsender=sender,
            zlistener=listener,
            friends=friends)
        

@app.route('/nodes', methods=['GET'])
def nodes():
    """
    Address book. Add new node. Edit node. Delete node?
    
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
    global version

    return render_template('info.html',
        version=version,
        hostname=config['hostname'],
        port=config['zmqservport']
        )


@app.route('/pubkey')
def pubkey():
    path = os.path.join(app.root_path,'./data/server/server.key')
    return send_file(path, as_attachment=True)


@app.route('/api/nodes', methods=['GET','POST'])
def getNodes():
    """
    GET:
    Returns list of known nodes
        {
            "starmaid.us.to": {
                "hostname": "starmaid.us.to",
                "port": 6000
            },
            ...
        }

    POST:
    Called from a submission box. user has uploaded a key
    Save this file as a new server or client or whatever
    update config and save file.
        form = {
            "hostname": "mimi.com",
            "port": "9000"
        }
        files = {
            "key": [public key]
        }
    

    """
    global friends

    if request.method == 'POST':
        if 'hostname' in request.form.keys() and 'port' in request.form.keys():
            # TODO handle changing the hostname and updating records,
            # instead of just creating a new user if hostname isnt in friends
            
            nHostname = request.form['hostname']
            nPortStr = request.form['port']

            try:
                nPort = int(nPortStr)
            except:
                return render_template('nodes.html',
                            friends=friends, 
                            error='bad port',
                            hostname=nHostname,
                            port=nPortStr)

            if nHostname in friends.keys():
                friends[nHostname]['port'] = nPort
            else:
                friends[nHostname] = {
                    'hostname': nHostname,
                    'port': nPort
                }

            didsave = saveFriends(friends)
            if not didsave:
                return render_template('nodes.html',
                            friends=friends, 
                            error='error saving friends json',
                            hostname=nHostname,
                            port=nPortStr)

            if 'key' in request.files.keys() and request.files['key'].filename != '':
                newfile = request.files['key']

                # now lets do a bunch of checks on the file...
                if newfile.filename.split('.')[-1] != 'key':
                    return render_template('nodes.html',
                                friends=friends, 
                                error='bad file extension',
                                hostname=nHostname,
                                port=nPortStr)

                # TODO There has got to be a better way to find filesize without reading it
                # newfile.content_length ?
                fcontent = newfile.read()
                try:
                    fcontd = fcontent.decode('ascii')
                except:
                    print('decode error')
                
                print(len(fcontd))
                if len(fcontd) > 400:
                    return render_template('nodes.html',
                                friends=friends, 
                                error='file too large to be a pubkey',
                                hostname=nHostname,
                                port=nPortStr)
                
                if 'public-key' not in fcontd:
                    return render_template('nodes.html',
                                friends=friends, 
                                error='file does not contain key',
                                hostname=nHostname,
                                port=nPortStr)
                
                newpath = os.path.join(app.root_path,
                    os.path.normpath(f'./data/friends/{nHostname}.key'))
                
                with open(newpath,'w') as f:
                    # Sanitize CR out
                    f.write(fcontd.replace('\r',''))

            # return a view of the page with the name they just edited
            return redirect(url_for('nodes',view=nHostname))
        else:
            return
    else:
        # just send the JSON over
        return friends


# USER API: For the user's program to interact with ===========================

@app.route('/getdata', methods=['GET'])
def getdata():
    global listener
    if listener is None:
        # Theres no listener, so whatever.
        d = {'connected': False}
    else:
        d = listener.getData()
    return d


@app.route('/setdata', methods=['POST'])
def setdata():
    if request.method == 'POST':
        #print(request.form)
        try:
            r = request.form.to_dict()
        except:
            data = request.form
            r = str(request.values)

        print(r)
        if r is not None:
            if 'data' not in r.keys():
                # this means just accept the whole thing. who cares
                data = str(r)
                pass
            else:
                data = r['data']
                if 'b64encoded' in r.keys():
                    try:
                        encoded = bool(r['b64encoded'])
                    except:
                        encoded = False
                else:
                    encoded = False
                if 'type' in r.keys():
                    dtype = str(r['type'])
                else:
                    dtype = 'txt'
        else:
            encoded = False
            dtype = 'txt'
            pass
        
        global sender
        global listener
        if sender is None:
            d = {'connected': False}
        else:
            if listener is not None:
                chain = listener.header['chain']
                if chain[0] == config['hostname']:
                    chain.pop(0)
                chain.append(config['hostname'])
            else:
                chain = [config['hostname']]

            print(' '.join([str(v) for v in [data, dtype, chain, encoded]]))
            success = sender.setData(data, dtype, chain, encoded)
            d = {'connected': success}
        
        return d
    else:
        return 'Endpoint only accepts POST'


# NON-PAGE HELPERS: do other tasks in the program =============================

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
    version = subprocess.check_output("git describe --tags", shell=True).decode().strip().split('-')[0]

    # start web server
    if config is not None and friends is not None:
        if config['debug']:
            app.run(debug=True, port=config['flaskport'])
        else:
            # This is the 'production' WSGI server
            serve(app, port=config['flaskport'])
