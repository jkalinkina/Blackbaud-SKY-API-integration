#Source script: https://github.com/reddit-archive/reddit/wiki/oauth2-python-example

#!/usr/bin/env python
from flask import Flask, abort, request
from uuid import uuid4
import requests
import requests.auth
import urllib
CLIENT_ID = 'Application ID'
CLIENT_SECRET = 'Application Secret'
REDIRECT_URI = "http://localhost:65010/sky_callback"

def base_headers():
    return {"Authorisation": "Basic " + CLIENT_SECRET,
            "Content-Type": "application/x-www-form-urlencoded"}


app = Flask(__name__)
@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with SKY API</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI}
    url = "https://oauth2.sky.blackbaud.com/authorization?" + urllib.parse.urlencode(params)
    return url

# To implement at later stage: we may want to store valid states in a database or memcache.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True

@app.route('/sky_callback')
def sky_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    access_token = get_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    return "Your token is: %s" % access_token

def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.post("https://oauth2.sky.blackbaud.com/token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]
    
if __name__ == '__main__':
    app.run(debug=True, port=65010)