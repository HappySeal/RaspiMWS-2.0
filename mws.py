from flask import Flask
from flask import render_template
import Adafruit_DHT
import time
app = Flask(__name__)
app.debug = True

timeNow = time.time()
Hum,Temp = Adafruit_DHT.read_retry(11,4)
oldHum,oldTemp = Hum,Temp

HumId,TempId = "stable","stable"
@app.route("/")
def mws():
    global timeNow,oldHum,oldTemp,Hum,Temp,HumId,TempId
    if((time.time()-timeNow)>=600):
        oldHum,oldTemp = Hum,Temp
        Hum,Temp = Adafruit_DHT.read_retry(11,4)
        timeNow=time.time()
    if(oldTemp < Temp):
        TempId = "up"
    if(oldTemp > Temp):
        TempId ="down"
    if(oldHum < Hum):
        HumId = "up"
    if(oldHum > Hum):
        HumId = "down"
    if(oldTemp == Temp):
        TempId = "stable"
    if(oldHum == Hum):
        HumId = "stable"
    return render_template('mws.html', temp=Temp,hum=Hum,idHum=HumId,idTemp=TempId)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
