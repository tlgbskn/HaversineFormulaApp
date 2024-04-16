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

@app.route('/')
def index():
    return render_template('index4.html')


@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        markers = request.get_json()
        if not markers:
            return jsonify({'error': 'No markers provided'}), 400

        marker_ids = [m['name'] for m in markers]
        data = {
            "ID": marker_ids,
            "Latitude": [m['lat'] for m in markers],
            "Longitude": [m['lng'] for m in markers],
            "Direction": [[] for _ in markers],
            "Distance": [[] for _ in markers]
        }

        for i in range(len(marker_ids)):
            for j in range(len(marker_ids)):
                if i != j:
                    coord1 = (markers[i]['lat'], markers[i]['lng'])
                    coord2 = (markers[j]['lat'], markers[j]['lng'])
                    distance = haversine(coord1, coord2)
                    direction = calculate_direction(coord1, coord2)
                    data["Direction"][i].append(direction)
                    data["Distance"][i].append(f"{distance:.2f} km")
                else:
                    data["Direction"][i].append("Self")
                    data["Distance"][i].append("0 km")

        df = pd.DataFrame(data)

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
