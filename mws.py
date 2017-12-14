##Öncelikle ihtiyacımız olan kütüphanelerimizi ekliyoruz
from flask import Flask
from flask import render_template
##Flask kütüphanesini ekletince projemize ek olarak iki dosya ekleniyor(Static , Templates)
##Templates de web de görünecek olan html kodumuz , Static dosyamız da web sayfamızda kullanacağımız fotoğraflar ve grafik oluşturmak için kullanacağımız javascript kütüphanelerimiz
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP
##DTH11 ve BMP180 sensörlerimizin kütüphanelerini ekliyoruz
import time,sqlite3,dateStr
## Zamanı bulmal için kullanacağımız time , veri tabanı için kullandığımız sqlite3 , bulunduğumuz tarihi bir yazıya dönüştürecek kendi yaptığım dateStr modüllerini ekledik
app = Flask(__name__)
app.debug = True
#Flaskdan uygulamamızı kuruyoruz
grafikTarih = []
grafikNem = []
grafikSicaklik = []
grafikBasinc=[]
#Grafiğe dökeceğimiz Tarih , Nem , Sıcaklık ve Basinc listelerini tanımladık
def dakika():
    return int(time.strftime("%H"))+60*(int(time.strftime("%M")))
## Anlık dakika değerini tanımlayacak fonksiyonu tanımlıyoruz
Sondk=dakika()
##Ve 1 kere kayıt alıyoruz
Nem,Sicaklik = Adafruit_DHT.read_retry(11,4)
##DHT 11 Nem ve sıcaklık sensöründen gelen verileri çekiyoruz
con = sqlite3.connect("havaVT.db",check_same_thread=False)
##Veritabanımız ile bağlantı kuruyoruz
cursor = con.cursor()
##Değişiklik yapmamızı sağlayacak imleç(cursor) değişkenimizi tanımlıyoruz
def table():
    cursor.execute("CREATE TABLE IF NOT EXISTS hava (saatTXT TEXT,tarihTXT TEXT,basinc INT,nem INT,sicaklik INT)")
##Tablomuzu ve bunun bölümlerini tanımlıyoruz.
table()
## Ve tablomuzu oluşturuyoruz
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
##Grafiğimizde yer alacak değerleri veri tabanından çekerek değişkenlerimize ekliyoruz
cikisListesi()
#print(grafikTarih,"\n",grafikNem,"\n",grafikSicaklik,"\n",grafikBasinc,"\n")
@app.route("/")
##Bu noktadan sonraki fonksiyonlarımız templates içinde bulunan aynı adlı html dosyamıza etki edeceldir
def mws():
    global Nem,Sicaklik,grafikNem,grafikTarih,grafikSicaklik,grafikBasinc,con,cursor,Sondk
    tahmin=""
    sensor = BMP.BMP085()
    ##BMP180 basınç sensörü kuruyoruz
    Nem,Sicaklik = Adafruit_DHT.read_retry(11,4)
    ##DHT11 sensöründen gelen verileri okuyoruz
    Basinc = int(sensor.read_pressure()/100)
    ##BMP 180 sensöründen gelen verileri okuyoruz
    if(dakika()-Sondk >=1):
        ##Eğer son kayıtdan 10 dk geçmiş ise
        cursor.execute("INSERT INTO hava (saatTXT TEXT,tarihTXT TEXT,basinc INT,nem INT,sicaklik INT) VALUES (?,?,?,?,?)".format(dateStr.hourStr(),dateStr.export(),Basinc,Nem,Sicaklik))
        con.commit()
        ##Verileri Veri tabanına kaydetiyoruz
        Sondk = dakika()
        ##Kaydedildiği dakikayı Son kayıt olarak kaydediyoruz
        cikisListesi()
        ##Grafiğimizdeki değerlerimizi güncelliyoruz
    if(Nem>=75 and Sicaklik<=20 and Basinc<=1000):
        tahmin =("Bu günkü değerlere bakılır ise, Nem %"+Nem+" seviyelerinde seyrediyor ve sıcaklık "+Sicaklik+" yağmur yağma ihtimali var. ")
    elif(Nem<=30 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bu günkü değerlere bakılır ise,Nem %"+Nem+" seviyelerinde seyrediyor ve sıcaklık "+Sicaklik+" kuru sıcaklar etkili dikkatli olun.")
    elif(Nem >=70 and Sicaklik>=25 and Basinc>=1013):
        tahmin = ("Bu günkü değerlere bakılır ise,Nem %"+Nem+" seviyelerinde seyrediyor ve sıcaklık "+Sicaklik+" bunaltıcı sıcaklar etkili dikkatli olun.")
    else:
        tahmin = ("Bu günkü değerlere bakılır ise,Nem %"+Nem+" seviyelerinde seyrediyor ve sıcaklık "+Sicaklik+" hava sıcaklıkları normal seviyelerde seyrediyor.")
    return render_template('mws.html', temp=(Adafruit_DHT.read_retry(11,4))[1],hum=(Adafruit_DHT.read_retry(11,4))[0],press=Basinc,sicaklik=grafikSicaklik,nem=grafikNem,basinc=grafikBasinc,gunTemp=grafikTarih,gunNem=grafikTarih,gunPress=grafikTarih,tahmin=tahmin)
    ##HTML dosyamızda bulunan eksik yerleri yukarıda belirtildiği gibi dolduruyoruz
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777)
    ##Uygulamamızı yerel ağ üzerinden 7777 port ile yayımlıyoruz