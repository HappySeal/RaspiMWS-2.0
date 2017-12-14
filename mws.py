##Oncelikle ihtiyacimiz olan kutuphanelerimizi ekliyoruz
from flask import Flask
from flask import render_template
##Flask kutuphanesini ekletince projemize ek olarak iki dosya ekleniyor(Static , Templates)
##Templates de web de gorunecek olan html kodumuz , Static dosyamiz da web sayfamizda kullanacagimiz fotograflar ve grafik olusturmak icin kullanacagimiz javascript kutuphanelerimiz
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP
##DTH11 ve BMP180 sensorlerimizin kutuphanelerini ekliyoruz
import time,sqlite3,dateStr
## Zamani bulmak icin kullanacagimiz time , veri tabani icin kullandigimiz sqlite3 , bulundugumuz tarihi bir yaziya donusturecek kendi yaptigim dateStr modullerini ekledik
app = Flask(__name__)
app.debug = True
#Flaskdan uygulamamizi kuruyoruz
grafikTarih = []
grafikNem = []
grafikSicaklik = []
grafikBasinc=[]
#Grafige dokecegimiz Tarih , Nem , Sicaklik ve Basinc listelerini tanimladik
def dakika():
    return int(time.strftime("%H"))+60*(int(time.strftime("%M")))
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
    cursor.execute("CREATE TABLE iF NOT EXiSTS hava (saatTXT TEXT,tarihTXT TEXT,basinc iNT,nem iNT,sicaklik iNT)")
##Tablomuzu ve bunun bolumlerini tanimliyoruz.
table()
## Ve tablomuzu olusturuyoruz
def cikisListesi():
    global grafikTarih,grafikSicaklik,grafikNem,grafikBasinc,con,cursor
    grafikTarih = []
    grafikNem = []
    grafikSicaklik = []
    grafikBasinc=[]
    cursor.execute("SELECT * FROM hava")
    entryAll = cursor.fetchall()
    con.commit()
    for i in range(0,len(entryAll)):
        grafikTarih.append((entryAll[i])[0])
        grafikNem.append((entryAll[i])[3])
        grafikSicaklik.append((entryAll[i])[4])
        grafikBasinc.append((entryAll[i])[2])
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
    if(dakika()-Sondk >=1):
        ##Eger son kayitdan 10 dk gecmis ise
        cursor.execute("iNSERT iNTO hava (saatTXT TEXT,tarihTXT TEXT,basinc iNT,nem iNT,sicaklik iNT) VALUES (?,?,?,?,?)".format(dateStr.hourStr(),dateStr.export(),Basinc,Nem,Sicaklik))
        con.commit()
        ##Verileri Veri tabanina kaydetiyoruz
        Sondk = dakika()
        ##Kaydedildigi dakikayi Son kayit olarak kaydediyoruz
        cikisListesi()
        ##Grafigimizdeki degerlerimizi guncelliyoruz
    if(Nem>=75 and Sicaklik<=20 and Basinc<=1000):
        tahmin =("Bu gunku degerlere bakilir ise, Nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" yagmur yagma ihtimali var. ")
    elif(Nem<=30 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bu gunku degerlere bakilir ise,Nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" kuru sicaklar etkili dikkatli olun.")
    elif(Nem >=70 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bu gunku degerlere bakilir ise,Nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" bunaltici sicaklar etkili dikkatli olun.")
    else:
        tahmin = ("Bu gunku degerlere bakilir ise,Nem %"+str(Nem)+" seviyelerinde seyrediyor ve sicaklik "+str(Sicaklik)+" hava sicakliklari normal seviyelerde seyrediyor.")
    return render_template('mws.html', temp=(Adafruit_DHT.read_retry(11,4))[1],hum=(Adafruit_DHT.read_retry(11,4))[0],press=Basinc,sicaklik=grafikSicaklik,nem=grafikNem,basinc=grafikBasinc,gunTemp=grafikTarih,gunNem=grafikTarih,gunPress=grafikTarih,tahmin=tahmin)
    ##HTML dosyamizda bulunan eksik yerleri yukarida belirtildigi gibi dolduruyoruz
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777)
    ##Uygulamamizi yerel ag uzerinden 7777 port ile yayimliyoruz
