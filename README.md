# garef-rpi-gopro-interface

## Installation

Clone the dev branch of this project (DON'T USE THE PIP VERSION!)
```sh
git clone http://github.com/konradit/gopro-py-api
cd gopro-py-api
python setup.py install
```
Install the Python C header:
```sh
sudo apt install python3-dev
```
You may need to install `python3.9-dev` instead (or your specific version)

## Running
### Client
Run `main.py`

### Server
Compile and execute `server.c` with
```sh
sh compile.sh
./server
```
(server.c is simply a wrapper for server.py for now)

## How it works
### Client
#### The GoPro class
Provides an interface with the connected GoPro using the `gopro-py-api` library

If SMART_START is set to True, it will auto-send a turn-on signal to any connected GoPro if it is offline.

#### The ObcInterfaceClient class
Provides an interface with the server, allows for sending and receiving data to the server.

#### The Main class
Main program, has different tests like GoPro debug mode (.gpDebug()), ObcInterfaceClient test (.startOicTest())

## Options
`GOPRO_INTERFACE` Default: eth1, the hardware interface to connect to the GoPro from<br/>
`GOPRO_PIN` Default: 23, the pin to use to power on the GoPro<br/>
`IMAGE_QUALITY` Default: 70, JPEG compression quality<br/>
`PORT` Default: 65402, port for server and client to communicate on<br/>