from flask import Flask
from flask import render_template
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP
import time,sqlite3
app = Flask(__name__)
app.debug = True

timeNow = time.time()
Hum,Temp = Adafruit_DHT.read_retry(11,4)
oldHum,oldTemp = Hum,Temp
con = sqlite3.connect("airDB.db")
cursor = con.cursor()
def table():
    cursor.execute("CREATE TABLE IF NOT EXISTS air (year TEXT,mon TEXT,day TEXT,pre INT,hum INT,tem INT)")
table()
HumId,TempId = "stable","stable"
@app.route("/")
def mws():
    global timeNow,oldHum,oldTemp,Hum,Temp,HumId,TempId
    if((time.time()-timeNow)>=600):
        oldHum,oldTemp = Hum,Temp
        sensor = BMP180.BMP085()
        Press = sensor.read_pressure()
        Hum,Temp = Adafruit_DHT.read_retry(11,4)
        day = time.strftime("%d")
        month = time.strftime("%m")
        year = time.strftime("%y%")
        cursor.execute("INSERT INTO air (year,mon,day,pre,hum,tem) VALUES (?,?,?,?,?,?)",(year,month,day,Press,Hum,Temp))
        con.commit()
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
    return render_template('mws.html', temp=(Adafruit_DHT.read_retry(11,4))[1],hum=(Adafruit_DHT.read_retry(11,4))[0],idHum=HumId,idTemp=TempId)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
