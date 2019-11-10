# Copyright 2019 Jesse Kaukonen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Watches the SC2 replay folder for new files and uploads each new replay file
# to Sc2ReplayStats.com.
#
# You must find your hash key in the Sc2ReplayStats.com
# account settings and insert it in this file below this comment block and then
# specify the replay folder in the variable directly below it.
#
# Does not upload replays that existed in the folder before this program started.

# Insert your hash key here. Don't share it with anyone else.
HASH_KEY=""

# Insert your Starcraft 2 replay folder here
FOLDER="C:/Users/youruser/Documents/Starcraft II/Accounts/accountnumber/somestring/Replays/Multiplayer"

dest="https://sc2replaystats.com"
endpoint_upload="/post_functions.php"
endpoint_validate="/account/validateHashKey/0/0/"
derpling_version="1.0"
user_agent="Derpling Uploader " + derpling_version

import time
import sys
import os
import base64
import logging
import datetime

# pip install requests
import requests

# pip install watchdog
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# Wrapper that prints to console and file
def derp_print(msg):
	dstr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logging.info(dstr + ": " + msg)
	print(msg)

# Goes through the replay file and makes sure its beginning looks like
# a valid sc2 replay file.
def validate_replay_data(fdata):
	if fdata[0] != 0x4D or fdata[1] != 0x50 or fdata[2] != 0x51 or fdata[3] != 0x1B:
		derp_print("File does not begin with a valid MPQ header")
		return False
	return True

# Validates the file at the given path is readable and returns its data as base64.
# On error an empty string is returned.
def load_file(fpath):

	derp_print("Reading file: " + fpath)

	f = None
	fdata = ""
	b64 = ""

	try:
		f = open(fpath, "rb")
	except Exception as e:
		derp_print("Failed opening file: " + fpath + ". Exception: " + str(e))
		return ""

	try:
		fdata = f.read()
	except Exception as e:
		derp_print("Exception reading file data: " + str(e))
		return ""

	if validate_replay_data(fdata) == False:
		derp_print("Failed validating replay file contents")
		return ""

	try:
		b64 = base64.b64encode(fdata)
	except Exception as e:
		derp_print("Exception base64 encoding file data: " + str(e))
		return ""

	derp_print("Successfully loaded file: " + fpath)
	return b64

# Verifies that the given hash key is accepted by the remote server
def validate_hash_key():

	# The validation request is simply a POST request without any data
	req_dest = dest + endpoint_validate + HASH_KEY
	r = requests.post(req_dest)

	if r.status_code != 200:
		derp_print("Failed validating hash key: non-200 response")
		return False

	if r.text != "true":
		derp_print("Failed validating hash key: Got invalid response from server: " + r.text)
		return False

	derp_print("Hash key is valid")

	return True

# Uploads a replay
# @param b64data: base64 encoded contents of a replay file
# returns True if the upload completed successfully, otherwise returns False
def upload(b64data):
	# Upload request contains the file in base64
	req_dest = dest + endpoint_upload

	r = requests.post(req_dest, data={
		"func": "uploadReplay",
		"fileBase64": b64data,
		"hash_key": HASH_KEY,
		"program": user_agent
	})

	if r.status_code != 200:
		derp_print("Failed uploading replay: status code: " + str(r.status_code))
		derp_print("Response: " + r.text)
		return False

	derp_print("Upload completed successfully")
	return True

# Called when a *.SC2Replay file is created
def on_created(ev):

	# Wait for a while. There's a problem where Windows gives a
	# "permission denied" error if the file is opened instantly opon
	# the creation event happening. Maybe it's because the file is open
	# in another process.
	time.sleep(5)

	fpath = ev.src_path
	b64data = load_file(fpath)
	if len(b64data) == 0:
		return

	if validate_hash_key() == False:
		return

	if upload(b64data) == False:
		return

if __name__ == "__main__":

	# Log into a file next to the main python script
	scriptdir=(os.path.dirname(os.path.realpath(__file__)))
	logpath = scriptdir + "/log.txt"
	logging.basicConfig(filename=logpath,level=logging.DEBUG)
	logging.info("Starting derpling uploader version: " + derpling_version)

	if os.path.isdir(FOLDER) == False:
		derp_print("Folder does not exist: " + FOLDER)
		sys.exit(1)

	derp_print("Watching for folder: " + FOLDER)

	# Create event handlers
	ev_handler = PatternMatchingEventHandler(patterns=["*.SC2Replay"], ignore_directories=True, case_sensitive=True)
	ev_handler.on_created = on_created

	obs = Observer()
	obs.schedule(ev_handler, FOLDER, recursive=False)
	obs.start()

	try:
		while True:
			time.sleep(5)
	except KeyboardInterrupt:
		derp_print("Joining file observer")
		obs.stop()
		obs.join()

	derp_print("Exiting")

