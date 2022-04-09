# garef-rpi-gopro-interface

## Installation

Clone the dev branch of this project (DON'T USE PIP!)
```sh
git clone http://github.com/konradit/gopro-py-api
cd gopro-py-api
python setup.py install
```
Create an `images` folder in root to store images that have been taken<br/>
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
(server.c is simply a wrapper for server.py for now :trollface:)
