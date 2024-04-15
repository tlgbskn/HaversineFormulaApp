from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
import math
import os
from os import path

app = Flask(__name__)
data_folder = path.join(path.dirname(__file__), 'data')

# Haversine fonksiyonu
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

# Yön hesaplama fonksiyonu
def calculate_direction(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    angle = math.degrees(math.atan2(math.sin(lon2 - lon1) * math.cos(lat2),
                                    math.cos(lat1) * math.sin(lat2) -
                                    math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)))
    if angle < 0:
        angle += 360

    directions = ["Kuzey", "Kuzeydoğu", "Doğu", "Güneydoğu", "Güney", "Güneybatı", "Batı", "Kuzeybatı", "Kuzey"]
    return directions[int((angle + 22.5) / 45)]

# Excel'e veri yazma fonksiyonu
def organize_data_for_excel(markers):
    rows = []
    for i, marker1 in enumerate(markers):
        row = {'ID': marker1['name'], 'Latitude': marker1['lat'], 'Longitude': marker1['lng']}
        for j, marker2 in enumerate(markers):
            if i != j:
                distance = haversine((marker1['lat'], marker1['lng']), (marker2['lat'], marker2['lng']))
                direction = calculate_direction((marker1['lat'], marker1['lng']), (marker2['lat'], marker2['lng']))
                row[f'Distance to {marker2["name"]}'] = f"{distance:.2f} km"
                row[f'Direction to {marker2["name"]}'] = direction
            else:
                row[f'Distance to {marker2["name"]}'] = "0 km"
                row[f'Direction to {marker2["name"]}'] = "Self"
        rows.append(row)
    return pd.DataFrame(rows)

@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        markers = request.get_json()
        if not markers:
            return jsonify({'error': 'No markers provided'}), 400

        df = organize_data_for_excel(markers)
        if not path.exists(data_folder):
            os.makedirs(data_folder)
        df.to_excel(path.join(data_folder, 'noktalar.xlsx'), index=False)

        return jsonify({'message': 'Data saved successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_excel')
def download_excel():
    return send_from_directory(directory=data_folder, path='noktalar.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
