from flask import Flask,request, render_template,redirect,url_for,abort
import requests
import os

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

list1 = []
app = Flask(__name__)

    
@app.route('/', methods =['POST', 'GET'])
def index():
    helpbtn = ""
    hisbtn = ""
    chabtn =""
    
    list2 = []
    citycloud =""
    citytime = ""
    citytem = ""
    Tcitytem = ""
    if "helpbtn" in request.form:
        
         return redirect(url_for('h_elp')) 
    elif "chabtn" in request.form:
        
         city = request.form['text']
         chabtn = city
         url = "https://api.seniverse.com/v3/weather/now.json?key=kelsy6uu0gufudjz&" + "location=%s&language=zh-Hans&unit=c" % city
         try:
             r = requests.get(url)
        
   
    
    
    

        
             dict2 = r.json()['results']
    
    
    
             citycloud = dict2[0]['now']['text']
             citytem = dict2[0]['now']['temperature'] 
             cityming = dict2[0]['location']['name']
             citytime = dict2[0]['last_update'].replace('T',' ')[:10]
    
             Tcitytem = citytem +"℃"
             list1.append('%s,%s,%s,%s' % (cityming, citycloud, Tcitytem, citytime))
        
        
         except KeyError:
             chabtn = "没有你查询的城市，请重新输入"
             
    elif "hisbtn" in request.form:
         return redirect(url_for('his'))
         
    return render_template('index.html', hisbtn=hisbtn, helpbtn=helpbtn, chabtn=chabtn,citycloud=citycloud, Tcitytem=Tcitytem ,citytime=citytime)
    
@app.route('/his', methods =['POST', 'GET'])
def his():
    return render_template('history.html', list1=list1)
@app.route('/h_elp', methods =['POST', 'GET'])
def h_elp():
    

    return render_template('help.html')

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
        if msg.content in ['历史']:
            strlist = ''.join(list1)
            
            reply = create_reply(strlist, msg)
            
        elif msg.content in ['帮助']:
            reply = create_reply(_help, msg)
            
        else:
            
            url = "https://api.seniverse.com/v3/weather/now.json?key=kelsy6uu0gufudjz&" + "location=%s&language=zh-Hans&unit=c" % msg.content
            
            try:
                r = requests.get(url)
        
   
    
    
    

        
                dict2 = r.json()['results']
    
    
    
                citycloud = dict2[0]['now']['text']
                citytem = dict2[0]['now']['temperature'] 
                cityming = dict2[0]['location']['name']
                citytime = dict2[0]['last_update'].replace('T',' ')[:10]
    
                Tcitytem = citytem +"℃"
                _msg = "你查询的城市:%s 天气状况: %s 温度%s摄氏度" % (cityming, citycloud, Tcitytem)
                list1.append('%s,%s,%s,%s' % (cityming, citycloud, Tcitytem, citytime))
                reply = create_reply(_msg, msg)
            except KeyError:
                 return "没有你查询的城市，请重新输入"
        
    else:
        
        
        reply = create_reply('对不起无法识别', msg)
    return reply.render()
    
if __name__ == '__main__':
    app.run()