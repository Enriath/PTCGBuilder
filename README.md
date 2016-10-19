PTCGBuilder
===

A Pokemon TCG Deck Builder, built in Python!

###What it does (right now):

* Allows you to search for cards, including EX, Mega, and BREAK.
* Displays these pokemon with official English card art from pokemon.com.
* Rudimentary deck building.

###What it will do:

* Allow building of decks, with useful breakdowns, such as rarity, set, and card type.

###Current issues:

* Missing Promo Cards from #157 onwards [(see this issue for more information)](https://github.com/Hydrox6/PTCGBuilder/issues/4#issuecomment-254939018).
* Missing Saving

###Feel free to suggest features in the [Issues](https://github.com/Hydrox6/PTCGBuilder/issues) tab.

###How to Run

If there are Releases, use them. They'll likely be Windows only for a while.

If you want to run the *cutting edge*, hot off the presses code, follow these instructions:

####1. Download and Install Python 3

Windows and Mac can get a binary from [here](https://www.python.org/downloads/)
Linux will want to install with their chosen Package Management System, such as APT.

**Make sure you install Tkinter. It's bundled with Python, you just have to say you want it.**

####2. Install [Pillow](https://pillow.readthedocs.io/en/3.3.x/)

With a fresh Python 3 installation, simply open the Command Line/Terminal and type:
`pip3 install Pillow`

If you have multiple Python installations, instead run:
`py -3.x -m pip install Pillow`, where x is your desired Python 3 version (eg: x would be 4 if you wanted to install Pillow on Python 3.4)

####3. Download/Clone the Repo

If you're cloning, I'll assume you know what to do.

If you don't have a Git Client, GitHub provides a .zip download. You can find it in the big green "Clone or download" button. Download and extract this .zip file.

####4. Run it!

Start by opening the Command Line/Terminal, navigate to the directory where the files are.

On a fresh install, run:
`python3 main.py`

On a multi-installation system, run:
`py -3.x main.py`, where x is the version you installed Pillow on earlier.

