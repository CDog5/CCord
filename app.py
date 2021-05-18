from flask import Flask,redirect,url_for,render_template,request,session,send_file
import json,random,uuid
import waitress
from flask_restful import Api, reqparse,Resource
import models, hashlib, pickle
users = []
servers = []

def get_u_by_id(uid):
    for user in users:
        if user.id == uid:
            return user
def get_s_by_id(uid):
    for user in servers:
        if user.id == uid:
            usr = user
    return usr
def hashy(text):
    h = hashlib.sha256(bytes(text,"utf-8"))
    return h.hexdigest()
def save_db():
    with open('db.pickle','wb') as f:
        pickle.dump({'users':users,'servers':servers},f)

with open('db.pickle','rb') as f:
    data = pickle.load(f)
    users = data['users']
    servers = data['servers']



app = Flask(__name__)
app.secret_key = "BANANADOG"


@app.route('/')
def home():
    #if the user is logged in, redirect to dashboard, else leave here to login
    if session.get('user',None) is not None:
        return redirect(url_for('dash'))
    return render_template("index.html")



@app.route('/server/<sid>/channel/<cid>/',methods=["POST","GET"])
def channel(sid,cid):
    for server in servers:
        if server.id == sid:
            s = server
    
    return render_template('server.html',server=s,user=get_u_by_id(session['user']),channel=str(cid),getuid=get_u_by_id)
@app.route('/signup/',methods=["POST","GET"])
def sign_up():
    if request.method == "GET" or not request.form:
        return redirect(url_for('home'))
    form = request.form
    if not form['suusr'] or not form['suusr']:
        return redirect(url_for('home'))
    users.append(models.User(form['suusr'],hashy(form['supwd']))) 
    save_db()   
    return redirect(url_for('home'))
@app.route('/auth/',methods=["POST","GET"])
def lg_auth():
    if request.method == "GET" or not request.form:
        return redirect(url_for('home'))
    form = request.form
    if not form['lgusr']or not form['lgpwd']:
        return redirect(url_for('home'))
    for user in users:
        if user.hash == hashy(form['lgpwd']) and user.name.lower() == form['lgusr'].lower():
            user.online = True
            session['user'] = user.id
            return redirect(url_for('dash'))
   
    return redirect(url_for('home'))
@app.route('/send/',methods=["POST","GET"])
def send():
    info = request.form['info']
    s,c = info.split('$')
    msg = request.form['msg']
    if msg == '':
        return redirect(request.referrer)
    s = get_s_by_id(s.replace('$',''))
    for ch in s.channels:
        if ch.id == c:
 
            ch.msgs.append(models.Message(msg,get_u_by_id(session['user'])))

    save_db()
    
    return redirect(request.referrer)
@app.route('/logout/')
def logout():
    get_u_by_id(session['user']).online = False
    del session['user']
    return redirect(url_for('home'))

@app.route('/dashboard/')
def dash():

    if session.get("user",None) is None:
        return redirect(url_for("home"))
    
    return render_template("dashboard.html",user=get_u_by_id(session['user']),getuid=get_u_by_id)
@app.route('/newserver/',methods=["GET","POST"])
def new_server():
    #if not request.referrer:
     #   return redirect(url_for('home'))
    #server = {"name":name,"id":str(uuid.uuid4()),"initials":make_initials(name)}
    s = models.Server(request.form['sname'])
    u = get_u_by_id(session['user'])
    servers.append(s)
    u.invite(s)
    save_db()
    return redirect(request.referrer)
@app.route('/newchannel/',methods=["POST","GET"])
def new_channel():
    if not request.form:
        return redirect(request.referrer)
    s = get_s_by_id(request.form['sid'])
    u = get_u_by_id(session['user'])
    s.channels.append(models.Channel(request.form['cname']))
    save_db()
    return redirect(request.referrer)
@app.route('/server/<sid>/')
def server(sid):
    if not session['user']:
        return redirect(url_for('home'))
    u = get_u_by_id(session['user'])

    for se in servers:
        if se.id == sid:
            sv = se
    
    return render_template('server.html',server=sv,user=u,channel=None,getuid=get_u_by_id)

@app.route('/account/')
def account():
    return render_template("account.html")
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
waitress.serve(app,host='0.0.0.0')
