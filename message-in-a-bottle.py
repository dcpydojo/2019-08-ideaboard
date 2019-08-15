import secrets
import time
import json

from bottle import get, post, run, template, request

_SECURE_STORAGE = {}


@get('/')
def new_message():
    return template('''
<form method="post">
    Message: <input name="message" type="text" /> <br/>
    Expires in: <input name="expiration" type="number" min="1" max="86400" /> seconds <br/>
    Maximum views: <input name="views" type="number" min="1" max="99999" /> <br/>
    <button>cork it!</button>
</form>
    ''')

@post('/')
def make_new_message():
    message = request.forms.get('message')
    if message:
        new_id = secrets.token_urlsafe()
        expires_in = request.forms.get('expiration')
        expires_at = time.time() + float(expires_in)
        max_views = int(request.forms.get('views'))
        _SECURE_STORAGE[new_id] = (message, expires_at, max_views)

    with open('super-secret-database.json', 'w') as f:
        json.dump(_SECURE_STORAGE, f, indent=2)

    return template('''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
    <html>
    <body>
    <strong>success!</strong>
    <p>your bottle is at
      <marquee><a href="/{{new_id}}">{{new_id}}</a></marquee>
    </p>
    <p>it will expire in {{expires_in}} second(s)</p>
    </body>
    </html>
    ''', new_id=new_id, expires_in=expires_in)

@get('/<identifier>')
def look_up_message(identifier):
    try:
        message, expires_at, max_views = _SECURE_STORAGE[identifier]
        if expires_at > time.time() and max_views:
            _SECURE_STORAGE[identifier] = (message, expires_at, max_views - 1)
        elif expires_at < time.time():
            missed = time.time() - expires_at
            return template('''
            <p>You missed it by {{missed}} seconds</p>
            ''', missed=missed)
        else:
            del _SECURE_STORAGE[identifier]
            message = "That ship has sailed"
    except KeyError:
         message = "What? Speak up!"

    return template('''
    <div style="background: url(https://lh3.googleusercontent.com/lb8Uma5B39E2R6A86Pu3zHiE825pvTlA8jzAyUMN0BAN8Dkx74VYtwPgadttpKQyWKNrcz-I6Tc3kosgSz1h3INO6qEOrcFZYuU01_CcKtxsMiKEDUI64gjYs151voVATTGIcxzn7Fk=w500-h333-no)">
        <marquee>{{message}}</marquee>
        </div>
        ''', message=message)


# Initialize from the super secret database
with open('super-secret-database.json') as f:
    _SECURE_STORAGE = json.load(f)

run(host='localhost', port=8080, debug=True)

