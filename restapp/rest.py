from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]
configfile = "creds.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(configfile, scope)
client = gspread.authorize(creds)

pesok = client.open("pesok")
kopya = pesok.sheet1
readytable = kopya.get_all_values()
column_names = readytable[0]
all_column_names = column_names
df = pd.DataFrame(readytable[1:], columns=readytable[0])

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'OK'}), 200

class Goroda(Resource):
    def get(self):
        return {'completetable': readytable}

class Materialy(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        return {'all_column_names': all_column_names, 'column_name': column_name}

class GorodaMaterialy(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        material = request.args.get('material')
        gorodmaterialtable = df.loc[df.iloc[:, 0] == column_name, df.columns.str.startswith(material)]
        return {'column_name': column_name, 'material': material, 'gorodmaterialtable': gorodmaterialtable.to_dict(orient='split')}

class GorodMaterialTable(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        material = request.args.get('material')
        gorodmaterialtable = df.loc[df.iloc[:, 0] == column_name, df.columns.str.startswith(material)]
        return {'gmdata': gorodmaterialtable.to_dict(orient='records')}

class ColumnNames(Resource):
    def get(self):
        return {'column_names': all_column_names}

class GorodaList(Resource):
    def get(self):
        cities = [row[0] for row in readytable]
        return {'cities': cities}

class GorodMaterialTableAPIView(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        material = request.args.get('material')
        gorodmaterialtable = df.loc[df.iloc[:, 0] == column_name, df.columns.str.startswith(material)]
        gorodematerialy = gorodmaterialtable.to_dict(orient='records')
        return jsonify({'gmdata': gorodematerialy})

api.add_resource(Goroda, '/goroda')
api.add_resource(Materialy, '/materialy')
api.add_resource(GorodaMaterialy, '/gorodamaterialy')
api.add_resource(GorodMaterialTable, '/gorodmaterialtable')
api.add_resource(ColumnNames, '/columnnames')
api.add_resource(GorodaList, '/gorodalist')
api.add_resource(GorodMaterialTableAPIView, '/gorod-material')

if __name__ == '__main__':
    app.run(debug=True)
