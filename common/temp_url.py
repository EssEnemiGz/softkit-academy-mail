from itsdangerous import URLSafeTimedSerializer
from flask import url_for

def generate_serializer(app):
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_temp_url(endpoint, user_email, app, expires_in=3600):
    serializer = generate_serializer(app)
    token = serializer.dumps(user_email, salt='email-confirm')
    return url_for(endpoint, token=token, _external=True)