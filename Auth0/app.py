import os
from flask import Flask, jsonify, redirect, session, url_for, request, render_template
from authlib.integrations.flask_client import OAuth
from auth import requires_auth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = False

# Auth0 config
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    api_base_url=f"https://{os.getenv('AUTH0_DOMAIN')}",
    access_token_url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"), audience=os.getenv("API_IDENTIFIER"))

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = token.get('userinfo')
    roles = []
    # Try to get roles from userinfo custom claim
    if userinfo:
        roles = userinfo.get('https://myapp.example.com/roles', [])
    # If userinfo is not present, try to get it from id_token
    if not userinfo and 'id_token' in token:
        from authlib.jose import jwt
        claims = jwt.decode(token['id_token'], None, claims_options={})
        userinfo = claims
        roles = claims.get('https://myapp.example.com/roles', [])
    session['user'] = userinfo
    session['roles'] = roles
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    roles = session.get('roles', [])
    return render_template('dashboard.html', user=user, roles=roles)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo=http://localhost:7000&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )

if __name__ == '__main__':
    app.run(port=7000)
