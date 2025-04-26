 from flask import Flask, render_template, request, redirect, url_for, session
 from google.oauth2 import credentials
 from googleapiclient.discovery import build
 from google_auth_oauthlib.flow import Flow
 import os
 import json
 

 app = Flask(__name__)
 app.secret_key = "6272bob677274"  # Change this to a random string!
 

 # --- Google Sheets API Setup ---
 CLIENT_SECRET_FILE = 'client_secret.json'  # Path to your client_secret.json file
 API_SERVICE_NAME = 'sheets'
 API_VERSION = 'v4'
 SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
 

 def get_credentials():
  flow = Flow.from_client_secrets_file(
  CLIENT_SECRET_FILE,
  scopes=SCOPES,
  redirect_uri=url_for('callback', _external=True)
  )
  creds = flow.run_local_server(port=0)
  return creds
 

 @app.route('/callback')
 def callback():
  creds = get_credentials()
  session['token'] = creds.to_json()
  return redirect(url_for('index'))
 

 def get_sheets_service():
  if 'token' in session:
  creds = credentials.Credentials.from_authorized_user_info(
  json.loads(session['token']), SCOPES)
  else:
  return None
  return build(API_SERVICE_NAME, API_VERSION, credentials=creds)
 

 # --- Helper Functions ---
 def get_sheet_data():
  service = get_sheets_service()
  if not service:
  return []
  SHEET_ID = '1S2kqkC4Plllbwi3Mt5QQR0Wy5cGGb7oEupiXqcZU2Zg'  # Replace with your Google Sheet ID
  RANGE_NAME = 'Sheet1'  # Replace with the name of your sheet
  results = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
  values = results.get('values', [])
  if not values:
  return []
  headers = values[0]
  entries = []
  for i, row in enumerate(values[1:]):
  entry = {}
  entry['index'] = i + 2  # Google Sheets rows start at 1, headers are row 1
  for j, header in enumerate(headers):
  entry[header] = row[j] if j < len(row) else ''
  entries.append(entry)
  return entries
 

 def append_sheet_data(data):
  service = get_sheets_service()
  if not service:
  return
  SHEET_ID = '1S2kqkC4Plllbwi3Mt5QQR0Wy5cGGb7oEupiXqcZU2Zg'
  RANGE_NAME = 'Sheet1'
  values = [list(data.values())]
  body = {'values': values}
  service.spreadsheets().values().append(
  spreadsheetId=SHEET_ID, range=RANGE_NAME,
  valueInputOption='USER_ENTERED', body=body
  ).execute()
 

 def update_sheet_data(index, data):
  service = get_sheets_service()
  if not service:
  return
  SHEET_ID = '1S2kqkC4Plllbwi3Mt5QQR0Wy5cGGb7oEupiXqcZU2Zg'
  RANGE_NAME = f'Sheet1!A{index}:F{index}'  # Assuming 6 columns (A to F)
  values = [list(data.values())]
  body = {'values': values}
  service.spreadsheets().values().update(
  spreadsheetId=SHEET_ID, range=RANGE_NAME,
  valueInputOption='USER_ENTERED', body=body
  ).execute()
 

 # --- Routes ---
 @app.route('/')
 def index():
  entries = get_sheet_data()
  return render_template('index.html', entries=entries)
 

 @app.route('/add', methods=['GET', 'POST'])
 def add():
  if request.method == 'POST':
  new_entry = {
  'Day & Date': request.form['Day & Date'],
  'Time': request.form['Time'],
  'Activity or Record of Information': request.form['Activity or Record of Information'],
  'Include': request.form['Include'],
  'Any Problems/TRAINING': request.form['Any Problems/TRAINING'],
  'Any other notes for the day?': request.form['Any other notes for the day?']
  }
  append_sheet_data(new_entry)
  return redirect(url_for('index'))
  return render_template('add.html')
 

 @app.route('/edit/<int:index>', methods=['GET', 'POST'])
 def edit(index):
  entries = get_sheet_data()
  entry = next((e for e in entries if e['index'] == index), None)
  if request.method == 'POST':
  updated_entry = {
  'Day & Date': request.form['Day & Date'],
  'Time': request.form['Time'],
  'Activity or Record of Information': request.form['Activity or Record of Information'],
  'Include': request.form['Include'],
  'Any Problems/TRAINING': request.form['Any Problems/TRAINING'],
  'Any other notes for the day?': request.form['Any other notes for the day?']
  }
  update_sheet_data(index, updated_entry)
  return redirect(url_for('index'))
  return render_template('edit.html', entry=entry, index=index)
 

 @app.route('/search', methods=['GET', 'POST'])
 def search():
  entries = get_sheet_data()
  results = []
  if request.method == 'POST' or request.method == 'GET':
  search_type = request.form.get('search_type') or request.args.get('search_type')
  search_term = request.form.get('search_term') or request.args.get('search_term')
  if search_type and search_term:
  for entry in entries:
  if search_type == 'Include' and search_term.lower() in entry['Include'].lower():
  results.append(entry)
  elif search_type == 'keyword' and search_term.lower() in entry['Activity or Record of Information'].lower():
  results.append(entry)
  return render_template('search.html', results=results)
  return render_template('search.html')
 

 if __name__ == '__main__':
  app.run(debug=True)
