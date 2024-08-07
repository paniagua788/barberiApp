from flask import Flask, render_template, request, jsonify, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import pytz

app = Flask(__name__)

# Configuración de Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './secure/barberiapp-431201-ae772328f5b5.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

SPREADSHEET_ID = '1B0NAArfCPsx08F_Qas3g3-PGuKpwyuQm63P66dN9C1s'

weekday_times = ["10:00", "11:00", "13:30", "14:30", "15:30", "16:30", "17:30", "18:30", "19:30"]
saturday_times = ["09:00", "10:00", "11:00", "13:30", "14:30", "15:30", "16:30", "17:30"]

TIMEZONE = pytz.timezone("America/Asuncion")

def get_reserved_times(date):
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Hoja 1!A:D'
    ).execute()
    values = result.get('values', [])

    reserved_times = [row[3] for row in values if row[2] == date]
    return reserved_times

def get_available_times(date):
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    current_time = datetime.datetime.now(TIMEZONE).time()
    if date_obj.weekday() == 6:  # Domingo
        return []
    
    if date_obj.weekday() == 5: #Sabaduki
        available_times = saturday_times
    else:
        available_times = weekday_times

    if date_obj.date() == datetime.datetime.now(TIMEZONE).date():
        current_time_str = current_time.strftime("%H:%M")
        available_times = [time for time in available_times if time > current_time_str]
    
    reserved_times = get_reserved_times(date)
    return [time for time in available_times if time not in reserved_times]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/available_times')
def available_times_route():
    date = request.args.get('date')
    times = get_available_times(date)
    return jsonify(times)

@app.route('/confirmacion')
def confirmacion():
    nombre = request.args.get('nombre')
    servicio = request.args.get('servicio')
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')
    return render_template('confirmacion.html', nombre=nombre, servicio=servicio, fecha=fecha, hora=hora)

@app.route('/agendar', methods=['POST'])
def agendar():
    nombre = request.form['nombre']
    servicio = request.form['servicio']
    fecha = request.form['fecha']
    hora = request.form['hora']
    contacto = request.form['contacto']

    reserved_times = get_reserved_times(fecha)
    if hora in reserved_times:
        return  render_template('error_reservado.html'), 400

    values = [[nombre, servicio, fecha, hora, contacto]]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f'Hoja 1!A1',
        valueInputOption='RAW',
        body=body
    ).execute()

    return redirect(url_for('confirmacion', nombre=nombre, servicio=servicio, fecha=fecha, hora=hora, contacto=contacto))




if __name__ == "__main__":
    app.run(debug=True)