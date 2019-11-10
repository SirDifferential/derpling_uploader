### Derpling Uploader

Uploads Starcraft 2 replays to sc2replaystats.com

### Motivation

sc2replaystats.com offers a tool that tracks your replay folder and automatically uploads any SC2 replay files to the service. However, the tool is offered as a closed source executable that cannot be easily audited. This project offers an alternative tool in a few hundred lines of auditable Python.

This tool performs essentially the same steps, except it only keeps track of replays that are created when this program is running. Any replays that were created when the derpling wasn't running will be ignored.

### Installation

* Install Python 3: [https://www.python.org](https://www.python.org). Make sure pip is installed as well.
* `pip install watchdog requests`
* Open `derpling_uploader.pyw` in a text editor
* Insert your hash into the `HASH_KEY` variable. The key can be found on SC2ReplayStats at "My Account" -> "Download Application" -> "Your HashKey"
* Insert your replay folder in the `FOLDER` variable. Use forward slashes please. That is: `C:/Users/youseruser`, not `C:\Users\youruser`. Otherwise Python may assume the string literal is an escaped unicode sequence.

### One time usage, launches the uploader in the background

`python derpling_uploader.pyw`

### Launch with a console window

* Copy `derpling_uploader.pyw` to `derpling_uploader.py`
* Double click `derpling_uploader.py`

### Start on system boot

* Create a shortcut to `derpling_uploader.pyw`
* run `shell:startup` or manually go to `C:/Users/youruser/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Start-up`
* Copy the shortcut there

### FAQ

* What's .pyw?

On Windows you can start the python interpreter without a console window popping up by having the filename as `.pyw` instead of `.py`

* It doesn't work

There's a `log.txt` in the same dir as your `derpling_uploader.pyw`. See what the derpling has to say.

* The log.txt has a permission denied error

There are two potential sources for permission errors:

1) A real permission problem. The script executes under your user and should have access to `C:/Users/youruser/Documents`, but Windows permissions have been strange on more than one occasion. In this case, investigate the permissions on your own. Good luck. I won't be able to help with that.
2) The file is busy. This happens if the file is being written to in another process and Windows reports the error as "permission denied" instead of EBUSY or something of that nature. If this happens, let me know over the issues. The watchdog waits a few seconds when a new file is created so that Starcraft has time to write the file in full and close the file handles.