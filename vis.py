import requests
import matplotlib.pyplot as plt
import datetime

# Définir l'UID cible et l'URL de l'API
uid = "905153780138"
api_url = f"http://192.168.43.111:5000/api/data/{uid}"

# Requête pour récupérer toutes les données de présence de cet utilisateur
try:
    response = requests.get(api_url)
    response.raise_for_status()
    all_data = response.json().get("data", [])
except requests.exceptions.RequestException as e:
    print("Erreur lors de la récupération des données :", e)
    exit()

# Définir les dates de début et de fin pour la plage exacte
end_date = datetime.datetime.now().date()
start_date = end_date - datetime.timedelta(days=7)

# Filtrer les données pour les enregistrements des 7 derniers jours
weekly_data = []
for entry in all_data:
    entry_time = datetime.datetime.strptime(entry["entry_time"], "%Y-%m-%d %H:%M:%S")
    if start_date <= entry_time.date() <= end_date:
        weekly_data.append(entry)

# Debug : Vérifier les données filtrées
print("Données de la semaine dernière :", weekly_data)

# Agréger le temps passé par jour, avec des dates allant de start_date à end_date inclus
daily_hours = {start_date + datetime.timedelta(days=i): 0 for i in range(8)}

for entry in weekly_data:
    entry_day = datetime.datetime.strptime(entry["entry_time"], "%Y-%m-%d %H:%M:%S").date()
    duration_parts = entry["duration"].split(':')
    hours = int(duration_parts[0])
    minutes = int(duration_parts[1])
    seconds = int(duration_parts[2])
    
    # Calculer la durée en heures décimales
    duration_hours = hours + minutes / 60 + seconds / 3600

    # Ajouter la durée au jour correspondant
    if entry_day in daily_hours:
        daily_hours[entry_day] += duration_hours  # Ajouter la durée plutôt que de la remplacer

# Préparer les données pour le graphique
dates = list(daily_hours.keys())
hours_spent = [daily_hours[date] for date in dates]

# Convertir les heures en format heures:minutes pour affichage
formatted_hours = [f"{int(h)}h {int((h % 1) * 60)}m" for h in hours_spent]

# Créer le graphique avec une barre rouge pour aujourd'hui
colors = ['#1f77b4'] * 7 + ['#ff7f0e']  # Couleurs personnalisées

plt.figure(figsize=(12, 7))
bars = plt.bar(dates, hours_spent, color=colors, width=0.6)

# Ajouter les valeurs formatées sur le graphique
for i, v in enumerate(hours_spent):
    plt.text(bars[i].get_x() + bars[i].get_width() / 2 - 0.1, v + 0.1, formatted_hours[i],
             ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

# Titrage et étiquetage
plt.title(f"Temps passé par jour à la salle de sport pour {uid} (dernière semaine)", fontsize=14, fontweight='bold')
plt.xlabel("Jour de la semaine", fontsize=12)
plt.ylabel("Heures passées", fontsize=12)

# Formatage des axes
plt.xticks(rotation=45)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Ajuster l'axe des Y pour qu'il affiche entre 0 et le maximum des heures passées
plt.ylim(0, max(hours_spent) + 1 if hours_spent else 1)

plt.tight_layout()
plt.show()

# Si aucune courbe n'est affichée, indiquez que cela pourrait être dû à des données insuffisantes
if not hours_spent:
    print("Aucune donnée à afficher pour les heures passées.")
