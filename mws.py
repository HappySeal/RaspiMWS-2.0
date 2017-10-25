from flask import Flask
from flask import render_template
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP
import time,sqlite3,dateStr
app = Flask(__name__)
app.debug = True

graphDate = []
graphHum = []
graphTemp = []
graphPress=[]
hourNow = int(time.strftime("%H"))
Hum,Temp = Adafruit_DHT.read_retry(11,4)
con = sqlite3.connect("airDB.db")
cursor = con.cursor()
def table():
    cursor.execute("CREATE TABLE IF NOT EXISTS air (clockTXT TEXT,dateTXT TEXT,pre INT,hum INT,tem INT)")
table()
def exportListing():
    global graphDate,graphTemp,graphHum,graphPress
    graphDate = []
    graphHum = []
    graphTemp = []
    graphPress=[]
    for i in range(0,5):
        cursor.execute("SELECT * FROM air")
        entryAll = cursor.fetchall()
        if entryAll < 5:
            print("Lutfen gecmis 5 saate ait bilgileri manuel olarak giriniz..")
            break
        con.commit()
        graphDate.append((entryAll[i])[0])
        graphHum.append((entryAll[i])[3])
        graphTemp.append((entryAll[i])[4])
        graphPress.append((entryAll[i])[2])
exportListing()
@app.route("/")
def mws():
    global Hum,Temp,graphHum,graphDate,graphTemp,graphPress,hourNow
    sensor = BMP.BMP085()
    Hum,Temp = Adafruit_DHT.read_retry(11,4)
    Press = sensor.read_pressure()
    if(int(time.strftime("%H"))-hourNow >=1):
        cursor.execute("INSERT INTO air * VALUES (?,?,?,?,?)".format(dateStr.hourStr(),dateStr.export(),Press,Hum,Temp))
		con.commit()
        hourNow = int(time.strftime("%H"))
        exportListing()

    return render_template('mws.html', temp=(Adafruit_DHT.read_retry(11,4))[1],hum=(Adafruit_DHT.read_retry(11,4))[0],press=Press,sicaklik=graphTemp,nem=graphHum,basinc=graphPress,gunTemp=graphDate,gunNem=graphDate,gunPress=graphDate)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777)
