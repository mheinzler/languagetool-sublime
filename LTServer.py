import sublime
import threading
import json

def _is_ST2():
	return (int(sublime.version()) < 3000)

if _is_ST2():
	from urllib import urlencode
	from urllib import urlopen
else:
	try:
		from urlparse import urlencode
		from urllib2 import urlopen
	except ImportError:
		from urllib.parse import urlencode
		from urllib.request import urlopen

def getResponse(server, text, language, disabledRules, callback):
	payload = {
		'language': language,
		'text': text.encode('utf8'),
		'User-Agent': 'sublime',
		'disabledRules' : ','.join(disabledRules)
	}

	# add the mother tongue if specified in the settings
	settings = sublime.load_settings('LanguageTool.sublime-settings')
	mother_tongue = settings.get('languagetool_mother_tongue', None)
	if mother_tongue:
		payload['motherTongue'] = mother_tongue

	# start a separate thread to contact the server
	post_thread = threading.Thread(target=_get_matches,
								   args=(server, payload, callback))
	post_thread.start()

# internal functions:

def _get_matches(server, payload, callback):
	content = _post(server, payload)
	if content:
		j = json.loads(content.decode('utf-8'))
		callback(j['matches'])
	else:
		callback(None)

def _post(server, payload):
	data = urlencode(payload).encode('utf8')
	try:
		content = urlopen(server, data).read()
		return content
	except IOError:
		return None
