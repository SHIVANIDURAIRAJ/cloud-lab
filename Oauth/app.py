import os
from urllib.parse import urlencode

from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-local-secret")

AUTH0_DOMAIN = "dev-zk27rtioyejxe6ni.us.auth0.com"
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")

CALLBACK_URL = "http://localhost:5000/callback"
HOME_URL = "http://localhost:5000"

oauth = OAuth(app)

oauth.register(
    name="auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"}
)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Login</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #101827, #243b55);
            font-family: Arial, sans-serif;
            color: white;
        }
        .card {
            width: 350px;
            padding: 35px;
            text-align: center;
            background: rgba(255,255,255,0.09);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 18px;
        }
        h1 { margin-bottom: 10px; }
        p { color: #cbd5e1; margin-bottom: 28px; }
        a {
            display: block;
            padding: 13px;
            margin-top: 12px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            background: #6366f1;
            color: white;
        }
        .signup { background: #334155; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Welcome Back!</h1>
        <p>Sign in securely with Auth0</p>
        <a href="/login">Login with Auth0</a>
        <a class="signup" href="/signup">Create Account</a>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/login")
def login():
    if not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
        return "Please configure AUTH0_CLIENT_ID and AUTH0_CLIENT_SECRET in .env", 500

    return oauth.auth0.authorize_redirect(
        redirect_uri=CALLBACK_URL
    )

@app.route("/signup")
def signup():
    if not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
        return "Please configure your Auth0 credentials in .env", 500

    return oauth.auth0.authorize_redirect(
        redirect_uri=CALLBACK_URL,
        screen_hint="signup"
    )

@app.route("/callback")
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        user = token.get("userinfo")

        if not user:
            user = oauth.auth0.userinfo(token=token)

        session["user"] = dict(user)
        return redirect(url_for("dashboard"))

    except Exception:
        app.logger.exception("Auth0 callback failed")
        return "Login failed. Check your Auth0 settings and Flask terminal.", 400


@app.route("/dashboard")
def dashboard():
    user = session.get("user")

    if not user:
        return redirect("/")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Application</title>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                min-height: 100vh;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #101827, #243b55);
                color: white;
            }
            nav {
                padding: 22px 8%;
                background: rgba(255,255,255,0.08);
                font-size: 22px;
                font-weight: bold;
            }
            main {
                min-height: 80vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 25px;
            }
            h1 { font-size: 46px; margin-bottom: 15px; }
            p { color: #cbd5e1; font-size: 18px; }
            .button {
                display: inline-block;
                margin-top: 25px;
                padding: 14px 28px;
                background: #6366f1;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }
            footer {
                text-align: center;
                padding: 20px;
                color: #cbd5e1;
            }
        </style>
    </head>
    <body>
        <nav>My Application</nav>
        <main>
            <h1>Welcome, {{ name }}!</h1>
            <p>You have successfully logged in.</p>
            <p>Welcome to your application. We're happy to have you here!</p>
            <a class="button" href="/logout">Logout</a>
        </main>
        <footer>Powered by Flask and Auth0</footer>
    </body>
    </html>
    """, name=user.get("name") or "User")

@app.route("/logout")
def logout():
    session.clear()

    params = urlencode({
        "client_id": AUTH0_CLIENT_ID,
        "returnTo": HOME_URL
    })

    return redirect(f"https://{AUTH0_DOMAIN}/v2/logout?{params}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
