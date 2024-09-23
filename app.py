from flask import *
from flask_cors import CORS
import common.mail_manager as mail_manager
import common.db_interpreter as db_interpreter
import common.temp_url as temp_url
from dotenv import load_dotenv
from datetime import timedelta
import supabase
import jwt
import os

# Server config
load_dotenv()
mail_passw = os.getenv("MAIL_PASSW")
mail_user = os.getenv("MAIL_USR")
mail_no_reply = os.getenv("MAIL_NOREPLY")

api = os.getenv("SUPABASE_KEY")
database = os.getenv("SUPABASE_URL")
secret_key = os.getenv("SECRET_KEY")
admin_email = os.getenv("EMAIL")
admin_passw = os.getenv("PASSW")
server_url = os.getenv("SERVER")
server_code = os.getenv('SERVER_CODE')

# Configuracion de la aplicacion web
app = Flask(__name__)
CORS(app, origins=["https://softkitacademy.com", "https://www.softkitacademy.com"])
if secret_key == None: secret_key = "ewkwer1231231kajeklew3213ropewp21oiewrop312309-490i3u2313jwlelk"
app.secret_key = secret_key
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_DOMAIN'] = f".{server_url.split('//')[1]}"
app.permanent_session_lifetime = timedelta(weeks=52) # Sesion con duracion de 52 semanas o 1 año

db = supabase.create_client(database, api)
auth_key = db.auth.sign_in_with_password( {'email':admin_email, 'password':admin_passw} )
if auth_key.session:
    token = auth_key.session.access_token
    pass
else:
    print(f"Error de auth. {auth_key.error}")

@app.route("/", methods=["GET"])
def index():
    response = make_response("OK")
    response.status_code = 200
    return response

@app.route("/email/subscription/pending", methods=["POST"])
def subscribe_to_mails():
    if "email" not in request.args:
        err = make_response( "You need to enter a email" )
        err.status_code = 400
        return err
        
    if request.args.get("email") == None:
        err = make_response( "You need to enter a email" )
        err.status_code = 400
        return err
    
    email = request.args.get("email")
    url = temp_url.generate_temp_url("confirmation_to_mails", f"{email}", app=app, expires_in=3600)
    msg = f'<a href="{url}&email={email}">Click aquí para confirmar su subscripción</a>'
    try:
        query = db.table("newsletter").insert({"email":email})
        result = db_interpreter.no_return(query=query)
    except:
        if result.output_data().code == "23505":
            pass
        else:
            err = make_response( "ERROR REGISTERING YOUR  E-MAIL" )
            err.status_code = 500
            return err
    
    try:
        server = mail_manager.connectToSMTP(smtp_usr=mail_user, smtp_passw=mail_passw)
        mail_manager.sendMail(from_email=mail_user, alias=mail_no_reply, to_email=email, body=msg, subject="SoftKit Academy - Newsletter Confirmation", server=server)
    except: 
        err = make_response( "ERROR SENDING YOUR CONFIRMATION E-MAIL" )
        err.status_code = 500
        return err

    response = make_response("DONE!")
    response.status_code = 200
    return response

@app.route("/email/subscription/confirm", methods=["GET"])
def confirmation_to_mails():
    if "email" not in request.args:
        err = make_response( "You need to enter a email" )
        err.status_code = 400
        return err
        
    if request.args.get("email") == None:
        err = make_response( "You need to enter a email" )
        err.status_code = 400
        return err
    
    email = request.args.get("email")
    query = db.table("newsletter").update({"confirmation":True}).eq("email", email)
    result = db_interpreter.no_return(query=query)
    
    if result.status_code() == 200:
        response = make_response( "DONE!" )
        response.status_code = 200
        return response
    else: 
        err = make_response( "ERROR, TRY AGAIN" )
        err.status_code = 500
        return err
    
@app.route('/security/logged', methods=["PUT"])
def recent_login():
    data = request.get_json()
    if not len(data):
        abort(400)
    
    email = data.get("email")
    if email == None:
        err = make_response( "You need to enter a email" )
        err.status_code = 400
        return err
        
    key = request.headers.get("Authorization")
    if key == None:
        abort(401)
        
    print(key)
    try:
        payload = jwt.decode(key.split(" ")[1], secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print(2)
        response = make_response( "Token expired ")
        response.status_code = 401
        return response
    except jwt.InvalidTokenError:
        print(3)
        response = make_response( "Token invalid ")
        response.status_code = 401
        return response
    
    if secret_key == payload.get("data"):
        msg = """
        <h1>Alguien accedió a su cuenta recientemente<h1><br>
        <br>
        <p>Este sistema está en beta, nuevas funciones llegarán pronto</p>
        """
        subject = "Security Alert - SoftKit Academy"
        try:
            server = mail_manager.connectToSMTP(smtp_usr=mail_user, smtp_passw=mail_passw)
            mail_manager.sendMail(from_email=mail_user, alias=mail_no_reply, to_email=email, body=msg, subject=subject, server=server)
        except: 
            err = make_response( "ERROR SENDING YOUR CONFIRMATION E-MAIL" )
            err.status_code = 500
            return err
    
    response = make_response( "DONE!" )
    response.status_code = 200
    return response
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static/icons", "favicon.ico")
    
if __name__=="__main__":
    app.run(debug=True, port=6666)