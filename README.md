[![Build Status](https://travis-ci.org/antismap/micpyplayer.svg?branch=master)](https://travis-ci.org/antismap/micpyplayer)

# micpyplayer
Simple music player in python with ncurses and libvlc. This project is still in early stages.

## Installation 

You need to install ncurses and libvlc. 

### Fedora 

Under Fedora, do

    sudo dnf install vlc python3-vlc vlc-devel ncurses-libs ncurses-devel

### Ubuntu

Under Ubuntu:

    sudo apt-get install libvlc-dev vlc

and the bindings with pip 

    pip3 install python-vlc


## Usage
    ./micpyplayer.py <directory_path>
use the arrows to move up and down, right-arrow is for enter.

## Screenshots

![alt text](https://github.com/antismap/micpyplayer/blob/master/screenshots/screen1.jpg?raw=true)
