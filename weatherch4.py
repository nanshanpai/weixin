from flask import Flask,request, render_template,redirect,url_for,abort
import requests
import os
import sqlite3 as sql

from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)

# set token or get from environments
TOKEN = os.getenv('WECHAT_TOKEN', 'weatherch4')
AES_KEY = os.getenv('WECHAT_AES_KEY', '')
APPID = os.getenv('WECHAT_APPID', '')

app = Flask(__name__)



list1 = [] 
@app.route('/')
def home():
    

    return render_template('home.html')

@app.route('/', methods =['POST', 'GET'])
def index():

    if request.form.get('chabtn', None) == "查询":
         trow = ""
         cityming =""
         citycloud = ""
         Tcitytem = ""
         citytime =""
         
         
         chabtn = ""
         con = sql.connect("weather.db")
         cur = con.cursor()
          
         city = request.form['text']
         
         cur.execute("select city from chaxun where ctime=date('now')")
         citylist =  cur.fetchall()
         print(citylist)
         i = (city,)
         
         
         try:
              if i in citylist:
                   a = ""
                   b = ""
                   x = ""
                   y = ""


                   t = (city,)
                   con = sql.connect("weather.db")
                   cur = con.cursor()
                   cur.execute("select * from chaxun where city=? and ctime=date('now')",t)
                   trow = cur.fetchone()
                   
                   con.commit()
                   x = trow[0]
                   y = trow[1]
                   a = trow[2]
                   b = trow[3]
                   list1.append('%s,%s,%s,%s' % (trow[0], trow[1], trow[2], trow[3]))
                   
                   return render_template('home.html',x=x,y=y,a=a,b=b)
              else: 
                                  
                   url = "https://api.seniverse.com/v3/weather/now.json?key=kelsy6uu0gufudjz&" + "location=%s&language=zh-Hans&unit=c" % city
                   r = requests.get(url)
                   dict2 = r.json()['results']
                   citycloud = dict2[0]['now']['text']
                   citytem = dict2[0]['now']['temperature'] 
                   cityming = dict2[0]['location']['name']
                   citytime = dict2[0]['last_update'].replace('T',' ')[:10]
    
                   Tcitytem = citytem +"℃"
                   
                   list1.append('%s,%s,%s,%s' % (cityming, citycloud, Tcitytem, citytime))
         
                   con = sql.connect("weather.db")
                   cur = con.cursor()
            
                   cur.execute("INSERT INTO chaxun (city,cloud,ctemp,ctime)\
                VALUES (?,?,?,?)",(cityming,citycloud,Tcitytem,citytime) )
              
                   con.commit()
                   return render_template('home.html',cityming=cityming,citycloud=citycloud, Tcitytem=Tcitytem ,citytime=citytime) 
         except KeyError:
            return render_template('newagain.html')
              
             
    elif  request.form.get('hisbtn', None) == "历史":
        return redirect(url_for('his'))
         
    elif  request.form.get('helpbtn', None) == "帮助":
        
         return redirect(url_for('h_elp'))   
         
    elif  request.form.get('gzbtn', None) == "更正":
         try:
         
              city = request.form['text']
              citygz,cloudgz = city.split(' ')
         
              with sql.connect("weather.db") as con: 
              
                   cur = con.cursor()
                 
                   cur.execute("UPDATE chaxun set cloud =?  where city =? ",(cloudgz,citygz))
                   con.commit()
                   rowl = "你更正了"+citygz + "的天气为" +cloudgz
                   return render_template("gz.html",rowl = rowl)
         except ValueError:
             
              return render_template("gesh.html")
   
     

  
      
    

@app.route('/h_elp', methods =['POST', 'GET'])
def h_elp():
    

    return render_template('help.html')

@app.route('/his', methods =['POST', 'GET'])
def his():

   return render_template("history.html",list1=list1)
   
@app.route('/weixin',methods = ['POST', 'GET'])
def weixinchat():
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    encrypt_type = request.args.get('encrypt_type', 'raw')
    msg_signature = request.args.get('msg_signature', '')
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    if request.method == 'GET':
        echo_str = request.args.get('echostr', '')
        return echo_str

    # POST request
    _help = "1.输入城市名称查询天气。\n 2.输入帮助查询帮助信息. \n 3.输入历史查询历史记录。"
    
    msg = parse_message(request.data)
    if msg.type == 'text':
        openid = msg.source
        if msg.content in ['历史']:
             con = sql.connect("weather.db")
             cur = con.cursor()
             cur.execute("select city from chaxun where ctime=date('now')")
             citylist =  cur.fetchall()
             strlist = "".join(['{} 查询 {}: {}\n'.format(item[0], item[1],item[2])
                      for item in citylist])
            
             reply = create_reply(strlist, msg)
            
        elif msg.content in ['帮助']:
             reply = create_reply(_help, msg)
            
        else:
            
            

          try:                        
            url = "https://api.seniverse.com/v3/weather/now.json?key=kelsy6uu0gufudjz&" + "location=%s&language=zh-Hans&unit=c" % msg.content
            r = requests.get(url)
            dict2 = r.json()['results']
            citycloud = dict2[0]['now']['text']
            citytem = dict2[0]['now']['temperature'] 
            cityming = dict2[0]['location']['name']
            citytime = dict2[0]['last_update'].replace('T',' ')[:10]

            Tcitytem = citytem +"℃"
                 
                 
            starlist = '%s,%s,%s,%s' % (cityming, citycloud, Tcitytem, citytime)

            con = sql.connect("weather.db")
            cur = con.cursor()

            cur.execute("INSERT INTO chaxun (city,cloud,ctemp,ctime)\
              VALUES (?,?,?,?)",(cityming,citycloud,Tcitytem,citytime) )

            con.commit()
            reply = create_reply(starlist, msg)
          except KeyError:
                 return "没有你查询的城市，请重新输入"           
         
        
    else:
        
        
        reply = create_reply('对不起无法识别', msg)
    return reply.render()

if __name__ == '__main__':
    app.run()