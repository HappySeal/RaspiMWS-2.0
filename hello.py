from flask import Flask
from flask import render_template
import Adafruit_DHT
app = Flask(__name__)
app.debug = True

@app.route("/")
def temp():
    Hum,Temp = Adafruit_DHT.read_retry(11,4)
    return render_template('mws.html', temp="Temp")
def hum():
    Hum,Temp = Adafruit_DHT.read_retry(11,4)
    return render_template('mws.html', hum="Hum")
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
