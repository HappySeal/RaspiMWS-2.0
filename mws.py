##Oncelikle ihtiyacimiz olan kutuphanelerimizi ekliyoruz
from flask import Flask
from flask import render_template
##Flask kutuphanesini ekletince projemize ek olarak iki dosya ekleniyor(Static , Templates)
##Templates de web de gorunecek olan html kodumuz , Static dosyamiz da web sayfamizda kullanacagimiz fotograflar ve grafik olusturmak icin kullanacagimiz javascript kutuphanelerimiz
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP
##DTH11 ve BMP180 sensorlerimizin kutuphanelerini ekliyoruz
import time,sqlite3
## Zamani bulmak icin kullanacagimiz time , veri tabani icin kullandigimiz sqlite3 modullerini ekledik
app = Flask(__name__)
app.debug = True
#Flaskdan uygulamamizi kuruyoruz
grafikTarih = []
grafikNem = []
grafikSicaklik = []
grafikBasinc=[]
#Grafige dokecegimiz Tarih , Nem , Sicaklik ve Basinc listelerini tanimladik
def export(dayBefore = 0):
	return str(int(time.strftime("%d"))-dayBefore)+"/"+time.strftime("%m")+"/"+time.strftime("%Y")
def hourStr():
	return str(time.strftime("%H")+":"+time.strftime("%M"))
def dakika():
    return int(time.strftime("%H"))*60+(int(time.strftime("%M")))
## Anlik dakika degerini tanimlayacak fonksiyonu tanimliyoruz
Sondk=dakika()
##Ve 1 kere kayit aliyoruz
Nem,Sicaklik = Adafruit_DHT.read_retry(11,4)
##DHT 11 Nem ve sicaklik sensorunden gelen verileri cekiyoruz
con = sqlite3.connect("havaVT.db",check_same_thread=False)
##Veritabanimiz ile baglanti kuruyoruz
cursor = con.cursor()
##Degisiklik yapmamizi saglayacak imlec(cursor) degiskenimizi tanimliyoruz
def table():
    cursor.execute("CREATE TABLE IF NOT EXiSTS hava (saatTXT TEXT,tarihTXT TEXT,basinc INT,nem INT,sicaklik INT)")
##Tablomuzu ve bunun bolumlerini tanimliyoruz.
table()
## Ve tablomuzu olusturuyoruz
def cikisListesi():
    global grafikTarih,grafikSicaklik,grafikNem,grafikBasinc,con,cursor,Sondk,Nem,Sicaklik,Basinc
    if(dakika()-Sondk >=10):
        ##Eger son kayitdan 10 dk gecmis ise
        cursor.execute("INSERT INTO hava (saatTXT,tarihTXT,basinc,nem,sicaklik) VALUES (?,?,?,?,?)",((hourStr()),(export()),Basinc,Nem,Sicaklik))
        con.commit()
        ##Verileri Veri tabanina kaydetiyoruz
        Sondk=dakika()
        ##Kaydedildigi dakikayi Son kayit olarak kaydediyoruz
    grafikTarih = []
    grafikNem = []
    grafikSicaklik = []
    grafikBasinc=[]
    cursor.execute("SELECT * FROM hava")
    entryAll = cursor.fetchall()
    con.commit()
    for i in range(0,15):
        grafikTarih.append((entryAll[len(entryAll)-(1+i)])[0])
        grafikNem.append((entryAll[len(entryAll)-(1+i)])[3])
        grafikSicaklik.append((entryAll[len(entryAll)-(1+i)])[4])
        grafikBasinc.append((entryAll[len(entryAll)-(1+i)])[2])
##Grafigimizde yer alacak degerleri veri tabanindan cekerek degiskenlerimize ekliyoruz
cikisListesi()
#print(grafikTarih,"\n",grafikNem,"\n",grafikSicaklik,"\n",grafikBasinc,"\n")
@app.route("/")
##Bu noktadan sonraki fonksiyonlarimiz templates icinde bulunan ayni adli html dosyamiza etki edeceldir
def mws():
    global Nem,Sicaklik,grafikNem,grafikTarih,grafikSicaklik,grafikBasinc,con,cursor,Sondk
    tahmin=""
    sensor = BMP.BMP085()
    ##BMP180 basinc sensoru kuruyoruz
    Nem,Sicaklik = Adafruit_DHT.read_retry(11,4)
    ##DHT11 sensorunden gelen verileri okuyoruz
    Basinc = int(sensor.read_pressure()/100)
    ##BMP 180 sensorunden gelen verileri okuyoruz
    cikisListesi()
    ##Grafigimizdeki degerlerimizi guncelliyoruz
    if(Nem>=75 and Sicaklik<=20 and Basinc<=1000):
        tahmin =("Bugunku degerlere bakilir ise, nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" derece, yagmur yagma ihtimali var. ")
    elif(Nem<=30 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bugunku degerlere bakilir ise, nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" derece, kuru sicaklar etkili dikkatli olun.")
    elif(Nem >=70 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bugunku degerlere bakilir ise, nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" derece, bunaltici sicaklar etkili dikkatli olun.")
    elif(Nem>=50 and Sicaklik <=0 and Basinc<=1013):
        tahmin = "Bugunku degerlere bakilir ise, nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" derece, kar ihtimali var dikkatli olun."
    else:
        tahmin = ("Bugunku degerlere bakilir ise, nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" derece, hava sicakliklari normal seviyelerde seyrediyor.")
    return render_template('mws.html', temp=(Adafruit_DHT.read_retry(11,4))[1],hum=(Adafruit_DHT.read_retry(11,4))[0],press=Basinc,sicaklik=grafikSicaklik,nem=grafikNem,basinc=grafikBasinc,gunTemp=grafikTarih,gunNem=grafikTarih,gunPress=grafikTarih,tahmin=tahmin)
    ##HTML dosyamizda bulunan eksik yerleri yukarida belirtildigi gibi dolduruyoruz
if __name__ == "__main__":
    cikisListesi()
    app.run(host='0.0.0.0', port=7777)
    ##Uygulamamizi yerel ag uzerinden 7777 port ile yayimliyoruz
