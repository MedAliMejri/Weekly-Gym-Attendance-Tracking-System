import requests
import matplotlib.pyplot as plt
import datetime

# Dfine UID Tags and API URL
uid = "uid tag"
api_url = f"http://192.168.43.111:5000/api/data/{uid}"


try:
    response = requests.get(api_url)
    response.raise_for_status()
    all_data = response.json().get("data", [])
except requests.exceptions.RequestException as e:
    print("Erreur lors de la récupération des données :", e)
    exit()


end_date = datetime.datetime.now().date()
start_date = end_date - datetime.timedelta(days=7)


weekly_data = []
for entry in all_data:
    entry_time = datetime.datetime.strptime(entry["entry_time"], "%Y-%m-%d %H:%M:%S")
    if start_date <= entry_time.date() <= end_date:
        weekly_data.append(entry)


print("Données de la semaine dernière :", weekly_data)


daily_hours = {start_date + datetime.timedelta(days=i): 0 for i in range(8)}

for entry in weekly_data:
    entry_day = datetime.datetime.strptime(entry["entry_time"], "%Y-%m-%d %H:%M:%S").date()
    duration_parts = entry["duration"].split(':')
    hours = int(duration_parts[0])
    minutes = int(duration_parts[1])
    seconds = int(duration_parts[2])
    
    
    duration_hours = hours + minutes / 60 + seconds / 3600

   
    if entry_day in daily_hours:
        daily_hours[entry_day] += duration_hours  # Ajouter la durée plutôt que de la remplacer


dates = list(daily_hours.keys())
hours_spent = [daily_hours[date] for date in dates]


formatted_hours = [f"{int(h)}h {int((h % 1) * 60)}m" for h in hours_spent]

colors = ['#1f77b4'] * 7 + ['#ff7f0e']  # Couleurs personnalisées

plt.figure(figsize=(12, 7))
bars = plt.bar(dates, hours_spent, color=colors, width=0.6)


for i, v in enumerate(hours_spent):
    plt.text(bars[i].get_x() + bars[i].get_width() / 2 - 0.1, v + 0.1, formatted_hours[i],
             ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')


plt.title(f"Temps passé par jour à la salle de sport pour {uid} (dernière semaine)", fontsize=14, fontweight='bold')
plt.xlabel("Jour de la semaine", fontsize=12)
plt.ylabel("Heures passées", fontsize=12)

plt.xticks(rotation=45)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)


plt.ylim(0, max(hours_spent) + 1 if hours_spent else 1)

plt.tight_layout()
plt.show()


if not hours_spent:
    print("Aucune donnée à afficher pour les heures passées.")
