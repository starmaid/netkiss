# NetKiss Project

Its fun to connect computers. Lets see what we can do with that, what if we played telephone?

## Inspiration

[timebomb](http://electronicartist.net/virocene/timebomb/index.html) and [the lovers](http://electronicartist.net/virocene/the-lovers/index.html)

Computers that pass around a file, and change it as they do.

## Install

### Install to try on your computer

You'll need Python 3 installed.

1. Download this repository (with git or just the zip file)

2. Use pip to install the dependencies

    ```
    pip3 install pyzmq flask waitress
    ```

3. Run the install python script

    ```
    python3 installer.py
    ```

4. Set parameters in the `/app/data/config.json` for your site. 

5. Run the Program by double clicking the `run.bat` file.

6. Hit `Ctrl+C` to stop the server.


### Install on a Raspberry Pi

This will allow the server to run on startup.

1. Install git.

    ```
    sudo apt install git
    ```

2. Download the files from this repository.

    ```
    git clone https://github.com/starmaid/netkiss.git
    ```

3. Navigate to, make executable, and run the install script. Get a cup of tea, it will take some time.

    ```
    cd ./netkiss
    chmod +x ./install.sh
    ./install.sh
    ```

4. Set parameters in the `/app/data/config.json` for your site. 

5. Reboot the pi. The server should start as the pi powers on.

### Config info

*hostname*: the public endpoint for your server. If you do not have a hostname, you can use your IP address.

*debug*: tells how much to print and if the server is availible externally. You will need to set this to `false` if you want to connect to the server from another computer.

*zmqservport*: this is the port number you will open in your router to allow traffic in.

*flaskport*: this is the port number you navigate to in your browser to access the console. 

## Screenshots

### Minimum Viable Product

I'm currently trying to get the most basic functionality working. This includes basic contact management, connecting/disconnecting, and basic data transfer.

My backend code is being made with an eye for the future, but the frontend is very "just enough to prove it works"

![](/docs/index.png)

![](/docs/connections.png)

![](/docs/nodes.png)

![](/docs/info.png)


## Program Layout

![Alt text](/docs/netkiss-App.drawio.png)

![Alt text](/docs/netkiss-Packet.drawio.png)

![Alt text](/docs/netkiss-Wide_Network.drawio.png)


```
app/
    templates/
    data/
        config.json     # what port to use
        server/
            pubkey.key
            secret.key
        friends/
            friends.json
            friend1.key
            friend2.key
            friend3.key
    app.py
    networking.py

```


