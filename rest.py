from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app)
######################################################################################
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]
configfile = "creds.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(configfile, scope)
client = gspread.authorize(creds)

######################################################################################
pesok = client.open("pesok")
kopya = pesok.sheet2
readytable = kopya.get_all_values()
column_names = readytable[0]
unique_first_words = set()
for col_name in column_names:
    if col_name.strip():
        first_word = col_name.split()[0]
        unique_first_words.add(first_word)
df = pd.DataFrame(readytable[1:], columns=readytable[0])
gorodematerialy = dict()
print(df)

######################################################################################
class Goroda(Resource):
    def get(self):
        return {'completetable': readytable}

class Materialy(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        return {'unique_first_words': list(unique_first_words), 'column_name': column_name}

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
        return {'column_names': list(unique_first_words)}

class GorodaList(Resource):
    def get(self):
        cities = [row[0] for row in readytable]
        return {'cities': cities}
class GorodMaterialTableAPIView(Resource):
    def get(self):
        column_name = request.args.get('column_name')
        material = request.args.get('material')

        # Assuming df is a global DataFrame you've defined earlier
        gorodmaterialtable = df.loc[df.iloc[:, 0] == column_name, df.columns.str.startswith(material)]
        gorodematerialy = gorodmaterialtable.to_dict(orient='records')

        html_table = gorodmaterialtable.to_html(classes='table table-striped table-hover', index=False)

        # Assuming you have a GorodMaterialTableSerializer similar to Django
        # If not, you can create a simple dictionary like this
        serializer_data = {'gmdata': gorodematerialy}

        # Return the serialized data
        return jsonify(serializer_data)
api.add_resource(Goroda, '/goroda')
api.add_resource(Materialy, '/materialy')
api.add_resource(GorodaMaterialy, '/gorodamaterialy')
api.add_resource(GorodMaterialTable, '/gorodmaterialtable')
api.add_resource(ColumnNames, '/columnnames')
api.add_resource(GorodaList, '/gorodalist')
api.add_resource(GorodMaterialTableAPIView, '/gorod-material')
if __name__ == '__main__':
    app.run(debug=False)
