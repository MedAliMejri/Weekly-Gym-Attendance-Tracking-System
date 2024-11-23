from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
MONGODB_URI = "mongodb+srv://mohamedalimejri108:LAn1P1JtlS4LjVja@rfid.xv6bo.mongodb.net/"
#MONGODB_URI = "mongodb+srv://bechir256haboubiS:EgtCABkFnDjRdJO6@gymmanagement.gqk3a.mongodb.net/"
client = MongoClient(MONGODB_URI)
db = client["GymManagement"]
user_data_collection1 = db["UserData"]
user_data_collection2 = db["data"]

@app.route('/api/user/<uid>', methods=['GET'])
def get_user_data(uid):
    print(f"Reçu une requête GET pour l'UID : {uid}")
    try:
        user = user_data_collection1.find_one({"uid": uid})
        if user:
            user_data = {
                "name": user.get("name", "Nom inconnu"),
                "last_name": user.get("last_name", "Prénom inconnu")
            }
            response = {"status": "success", "user": user_data}
            print(f"Utilisateur trouvé : {response}")
            return jsonify(response), 200
        else:
            response = {"status": "error", "message": "Utilisateur non trouvé"}
            print(f"Utilisateur non trouvé pour l'UID : {uid}")
            return jsonify(response), 404
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        print(f"Erreur lors de la récupération de l'utilisateur : {response}")
        return jsonify(response), 500
@app.route('/api/data/<uid>', methods=['GET'])
def get_all_data_for_user(uid):
   print(f"Reçu une requête GET pour récupérer les données de l'UID : {uid}")
   try:
       # Récupérer toutes les entrées pour cet utilisateur
       data_entries = list(user_data_collection2.find({"uid": uid}))


       # Convertir chaque document MongoDB en un format JSON sérialisable
       data_list = []
       for entry in data_entries:
           entry["_id"] = str(entry["_id"])  # Convertir ObjectId en chaîne
           data_list.append(entry)


       return jsonify({"status": "success", "data": data_list}), 200
   except Exception as e:
       response = {"status": "error", "message": str(e)}
       print(f"Erreur lors de la récupération des données utilisateur : {response}")
       return jsonify(response), 500

@app.route('/api/data', methods=['POST'])
def add_user_data():
    print("Reçu une requête POST pour ajouter des données utilisateur")
    try:
        data = request.json
        # Validation des données reçues
        if not data or 'uid' not in data or 'nom' not in data or 'prenom' not in data:
            return jsonify({"status": "error", "message": "Données manquantes"}), 400
        
        # Insérer les données dans la collection
        user_data_collection2.insert_one(data)
        response = {"status": "success", "message": "Données ajoutées avec succès"}
        print(response)
        return jsonify(response), 201
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        print(f"Erreur lors de l'ajout des données utilisateur : {response}")
        return jsonify(response), 500

if __name__ == '__main__':
    print("Démarrage du serveur Flask sur le port 5000...")
    app.run(host='0.0.0.0', port=5000)
