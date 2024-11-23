import time
from machine import Pin, SPI
import urequests
import network
from mfrc522 import MFRC522
from user_data import get_user_data  # Import  function from user_data.py

# RFID configuration 
sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
sda = Pin(5, Pin.OUT)  
rst = Pin(22, Pin.OUT)  

# Initialisation for SPI communication
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

#Wi-Fi configuration
SSID = "" #write your ssid 
PASSWORD = "" #write your password

#Wi-Fi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connexion en cours...")
        time.sleep(1)

    print("Connecté au Wi-Fi:", wlan.ifconfig())

connect_wifi()
print("Lecteur RFID actif. Placez un tag à proximité pour lire l'UID.")

#RFID reader initialisation
rdr = MFRC522(spi, sda, rst)


entry_times = {}

while True:
    # Scan your RFID Tags
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:
        # read UID  tags
        (stat, raw_uid) = rdr.anticoll()

        if stat == rdr.OK:
            
            uid = int.from_bytes(bytes(raw_uid), "little")

            # uid reception
            name, last_name = get_user_data(uid)
            if name and last_name:
                
                masked_uid = f"{'*' * (len(str(uid)) - 3)}{str(uid)[-3:]}"
                print(f"UID du tag : {masked_uid} - Utilisateur : {name} {last_name}")

                # get local time 
                current_time = time.localtime()
                time_string = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(current_time[0], current_time[1],
                                                                           current_time[2], current_time[3],
                                                                           current_time[4], current_time[5])

                if uid not in entry_times:
                    
                    entry_times[uid] = current_time
                    print(f"Temps d'entrée enregistré pour {name} {last_name} à {time_string}")
                else:
                    
                    entry_time = entry_times.pop(uid)
                    duration = time.mktime(current_time) - time.mktime(entry_time)
                    hours, remainder = divmod(duration, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    duration_string = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
                    print(
                        f"Temps de sortie pour {name} {last_name} à {time_string}, Durée d'entraînement : {duration_string}")

                    
                    
                    data = {
                    "uid": str(uid),  # Utiliser l'UID masqué ici
                    "nom": name,
                    "prenom": last_name,
                    "entry_time": "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(entry_time[0], entry_time[1],
                                                                                   entry_time[2], entry_time[3],
                                                                                   entry_time[4], entry_time[5]),
                        "exit_time": time_string,
                        "duration": duration_string
                }


                    # URL de votre API pour envoyer les données
                    url = "http://192.168.1.4:5000/api/data" #change your local flask adress ip 
                    try:
                        response = urequests.post(url, json=data)
                        if response.status_code == 200:
                            print("Données envoyées avec succès :", response.text)
                        
                        response.close()  
                    except Exception as e:
                        print("Erreur lors de la connexion à l'API :", str(e))

            
            

    
    time.sleep(0.1)
