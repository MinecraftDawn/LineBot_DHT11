from flask import Flask, request, abort , send_file

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import os
        
app = Flask(__name__)

#濕度及溫度全域變數
humidity=50
temperature=25


# Channel Access Token
line_bot_api = LineBotApi('Channel Access Token')
# Channel Secret
handler = WebhookHandler('Channel Secret')

# 監聽目標為 /download 的 Post Request
@app.route("/download", methods=['POST','GET'])
def download():
    #設定檔案位置
    urlPath = app.root_path + "/test.png"
    #如果檔案存在才繼續
    if os.path.isfile(urlPath):
        print("檔案存在")
        return send_file(urlPath,as_attachment=True)    
    
# 監聽目標為 / 的 Post Get Request
@app.route("/<hum>/<temp>", methods=['POST','GET'])
def getDHT(hum,temp):
    #修改hum及temp
    print(hum)
    print(temp)
    humidity = hum
    temperature = temp
    #呼叫產生圖片的函式
    createImg(humidity,temperature)
    return "Test"

# 監聽目標為 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 的標頭值
    signature = request.headers['X-Line-Signature']
    # 以文字方式取得request body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # 處理webhook主體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	# 取得使用者的user_id
    userID = event.source.user_id
    # 取得使用者發出的訊息
    message = TextSendMessage(text=event.message.text)
    # 回復與使用者傳送相同的訊息
    line_bot_api.reply_message(event.reply_token, message) 

    #發送圖片給Line使用者
    image_message = ImageSendMessage(
        original_content_url='https://00ae8503.ngrok.io/download',
        preview_image_url='https://00ae8503.ngrok.io/download'
    )
    line_bot_api.push_message(userID,image_message)

from PIL import Image, ImageDraw, ImageFont
def createImg(humidity,temperature):
    #需要先有一張"晴天.jpg"存放於和本檔案相同的路徑
    imageA = Image.open("晴天.jpg")
    #建立Draw物件，準備修改圖片
    Drawimg = ImageDraw.Draw(imageA)
    #建立font物件
    font = ImageFont.truetype("arial.ttf", 50)
    #將文字畫在圖片上
    Drawimg.text((0, 0), str("humidity: " + str(humidity)), fill=(0,0,0), font=font)
    Drawimg.text((0, 70), str("temperature: " + str(temperature)), fill=(0,0,0), font=font)
    #儲存圖片
    imageA.save('test.png')
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)