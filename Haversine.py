from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import math
import os
from os import path
 
app = Flask(__name__)
data_folder = path.join(path.dirname(__file__), 'data')

def haversine(coord1, coord2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    markers = request.get_json()
    marker_ids = [m['name'] for m in markers]  # Assuming 'name' is used as identifier
    data = {
        "ID": marker_ids,
        "Latitude": [m['lat'] for m in markers],
        "Longitude": [m['lng'] for m in markers]
    }

    # Create DataFrame from data
    df = pd.DataFrame(data)

    # Adding distances to the DataFrame
    for i, marker_id in enumerate(marker_ids):
        distances = []
        for j in range(len(markers)):
            if i != j:
                dist = haversine((markers[i]['lat'], markers[i]['lng']), (markers[j]['lat'], markers[j]['lng']))
                distances.append(dist)
            else:
                distances.append(0)  # Self-distance is zero
        df[f'Distance_to_{marker_id}'] = distances

    # Save the DataFrame to an Excel file
    if not path.exists(data_folder):
        os.makedirs(data_folder)
    df.to_excel(path.join(data_folder, 'noktalar.xlsx'), index=False)
    
    return jsonify({'message': 'Data saved successfully!'})

@app.route('/download_excel')
def download_excel():
    return send_from_directory(directory=data_folder, path='noktalar.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
