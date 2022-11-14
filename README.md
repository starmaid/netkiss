# NetKiss Project

Its fun to connect computers. Lets see what we can do with that

## Inspiration

[timebomb](http://electronicartist.net/virocene/timebomb/index.html) and [the lovers](http://electronicartist.net/virocene/the-lovers/index.html)

## Screenshots

### Minimum Viable Product

I'm currently trying to get the most basic functionality working. This includes basic contact management, connecting/disconnecting, and basic data transfer.

My backend code is being made with an eye for the future, but the frontend is very "just enough to prove it works"

![](/docs/v1_index.png)

![](/docs/v1_connections.png)

![](/docs/v1_nodes.png)

![](/docs/v1_info.png)


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


## Install


1. Install git.

    ```
    sudo apt install git
    ```

2. Download the files from this repository.

    ```
    git clone https://github.com/starmaid/pulseofexploration.git
    ```

3. Navigate to, make executable, and run the install script. Get a cup of tea, it will take some time.

    ```
    cd ./pulseofexploration
    chmod +x ./install.sh
    ./install.sh
    ```
