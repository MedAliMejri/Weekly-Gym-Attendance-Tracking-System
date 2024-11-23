# user_data.py
import urequests as requests

def get_user_data(uid):
    try:
        url = f'http://192.168.1.4:5000/api/user/{uid}'  # Modify cthis url every time you connect to mongodb
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["user"]["name"], data["user"]["last_name"]
            else:
                print("Utilisateur non trouvé.")
                return None, None
        else:
            print("Erreur dans la réponse de l'API :", response.text)
            return None, None
    except Exception as e:
        print("Impossible de se connecter à l'API :", e)
        return None, None

