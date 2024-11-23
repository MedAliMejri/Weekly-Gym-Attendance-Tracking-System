import time
from machine import Pin, SPI
import urequests
import network
from mfrc522 import MFRC522
from user_data import get_user_data  # Importer la fonction depuis user_data.py

# Configuration des broches pour le lecteur RFID
sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
sda = Pin(5, Pin.OUT)  # Pin CS (SDA) pour le lecteur RFID
rst = Pin(22, Pin.OUT)  # Pin RST pour le lecteur RFID

# Initialisation de la communication SPI
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

# Configuration Wi-Fi
SSID = "GLOBALNET"
PASSWORD = "73b91HgnV"

# Connexion au Wi-Fi
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

# Initialiser le lecteur RFID
rdr = MFRC522(spi, sda, rst)

# Dictionnaire pour stocker les temps d'entrée
entry_times = {}

while True:
    # Scanner un tag RFID
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:
        # Lecture de l'UID du tag
        (stat, raw_uid) = rdr.anticoll()

        if stat == rdr.OK:
            # Convertir l'UID en un nombre entier
            uid = int.from_bytes(bytes(raw_uid), "little")

            # Récupérer les données utilisateur
            name, last_name = get_user_data(uid)
            if name and last_name:
                # Masquer l'UID en gardant les trois derniers chiffres
                masked_uid = f"{'*' * (len(str(uid)) - 3)}{str(uid)[-3:]}"
                print(f"UID du tag : {masked_uid} - Utilisateur : {name} {last_name}")

                # Obtenir l'heure actuelle
                current_time = time.localtime()
                time_string = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(current_time[0], current_time[1],
                                                                           current_time[2], current_time[3],
                                                                           current_time[4], current_time[5])

                if uid not in entry_times:
                    # Si c'est la première fois qu'on voit cet UID, enregistrer l'heure d'entrée
                    entry_times[uid] = current_time
                    print(f"Temps d'entrée enregistré pour {name} {last_name} à {time_string}")
                else:
                    # Calculer la durée d'entraînement
                    entry_time = entry_times.pop(uid)
                    duration = time.mktime(current_time) - time.mktime(entry_time)
                    hours, remainder = divmod(duration, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    duration_string = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
                    print(
                        f"Temps de sortie pour {name} {last_name} à {time_string}, Durée d'entraînement : {duration_string}")

                    # Préparation des données à envoyer
                    
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
                    url = "http://192.168.1.4:5000/api/data"
                    try:
                        response = urequests.post(url, json=data)
                        if response.status_code == 200:
                            print("Données envoyées avec succès :", response.text)
                        
                        response.close()  # Fermer la réponse pour libérer des ressources
                    except Exception as e:
                        print("Erreur lors de la connexion à l'API :", str(e))

            # Attendre un moment pour éviter de lire le même tag plusieurs fois
            

    # Pause de courte durée pour réduire la charge de vérification
    time.sleep(0.1)