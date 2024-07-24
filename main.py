from flask import Flask, render_template, request, send_file, jsonify
import requests
import os
import pandas as pd
import json

app = Flask(__name__)

# Replace with your actual API key
API_KEY = '81d72b007d8e962be816ae8047d3d246'
API_URL = 'https://api.openweathermap.org/data/2.5/weather'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form['city_name']
        params = {
            'q': city_name,
            'appid': API_KEY
        }
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            weather_data = {
                'Weather Description': data['weather'][0]['description'],
                'Temperature (°C)': data['main']['temp'] - 273.15,  # Convert from Kelvin to Celsius
                'Feels Like (°C)': data['main']['feels_like'] - 273.15,  # Convert from Kelvin to Celsius
                'Humidity (%)': data['main']['humidity'],
                'Wind Speed (km/h)': data['wind']['speed'] * 3.6,  # Convert from m/s to km/h
                'Sunrise (UTC)': pd.to_datetime(data['sys']['sunrise'], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
                'Sunset (UTC)': pd.to_datetime(data['sys']['sunset'], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
                'Pressure (hPa)': data['main']['pressure'],
                'Visibility (m)': data['visibility'],
                'Country': data['sys']['country'],
                'City': data['name'],
                'Latitude': data['coord']['lat'],
                'Longitude': data['coord']['lon'],
                'Timezone (hours)': data['timezone'] / 3600,  # Convert seconds to hours
                'Wind Degree': data['wind']['deg'],
                'Wind Gust (km/h)': data['wind'].get('gust', 'N/A') * 3.6 if 'gust' in data['wind'] else 'N/A'
            }

            # Ensure the reports directory exists
            if not os.path.exists('reports'):
                os.makedirs('reports')

            # Convert to DataFrame
            df = pd.DataFrame([weather_data])

            # Save DataFrame to CSV
            csv_path = os.path.join('reports', 'weather_report.csv')
            df.to_csv(csv_path, index=False)

            # Save DataFrame to Excel
            excel_path = os.path.join('reports', 'weather_report.xlsx')
            df.to_excel(excel_path, index=False)

            # Save DataFrame to HTML
            html_path = os.path.join('reports', 'weather_report.html')
            df.to_html(html_path, index=False)

            # Save DataFrame to JSON
            json_path = os.path.join('reports', 'weather_report.json')
            df.to_json(json_path, orient='records')

            return render_template('index.html', data=weather_data)

        else:
            return render_template('index.html', error=f'Error: {response.status_code}')

    return render_template('index.html')


@app.route('/download/<file_format>')
def download(file_format):
    file_map = {
        'csv': 'weather_report.csv',
        'xlsx': 'weather_report.xlsx',
        'html': 'weather_report.html',
        'json': 'weather_report.json'
    }
    file_name = file_map.get(file_format)
    if file_name:
        file_path = os.path.join('reports', file_name)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    return 'File not found', 404


if __name__ == '__main__':
    app.run(debug=True)
