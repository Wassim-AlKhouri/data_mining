import folium
import pandas as pd

# Charger les données
data = pd.read_csv('sncb_prepared.csv', sep=';')

# Créer une carte centrée sur la Belgique
belgium_map = folium.Map(location=[50.8503, 4.3517], zoom_start=8)

# Palette de couleurs pour différencier les types d'incidents
colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'darkred', 'darkblue', 'darkgreen']

# Groupes de points par type d'incident
incident_groups = data.groupby('incident_type')

# Ajouter des lignes pour chaque type d'incident
for i, (incident_type, group) in enumerate(incident_groups):
    # Obtenir les coordonnées des incidents
    points = list(zip(group['approx_lat'], group['approx_lon']))
    
    # Ajouter une polyligne reliant les points
    folium.PolyLine(
        locations=points,
        color=colors[i % len(colors)],
        weight=2.5,
        popup=f"Type d'incident : {incident_type}"
    ).add_to(belgium_map)

    # Ajouter des marqueurs pour les points
    for lat, lon in points:
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=colors[i % len(colors)],
            fill=True,
            fill_opacity=0.6
        ).add_to(belgium_map)

# Enregistrer la carte dans un fichier HTML
belgium_map.save('carte_incidents.html')
print("Carte enregistrée : ouvrez 'carte_incidents.html' dans votre navigateur.")
