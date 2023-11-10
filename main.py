##pip install geopandas
##pip install Flask
from flask import Flask, jsonify, request
import geopandas as gpd
from shapely.geometry import mapping
import pandas as pd

app = Flask(__name__)
##Cargando el archivo GeoJson
geojson_path = './National_Obesity_By_State.geojson'
gdf = gpd.read_file(geojson_path)

@app.route('/')##Ruta de inicio
def root():
    return "Home"

@app.route('/estados', methods=['GET']) ## a)Extrae todos los nombres e identificaciones de los estados
def get_estados():    
    estados_data = []
    for index, row in gdf.iterrows():
        estado = {"nombre": row['NAME'], "id": row['FID']}
        estados_data.append(estado)
    return jsonify(estados_data), 200


@app.route('/estado/id_nombre', methods=['GET'])
def obtener_filtro():
    parametro1 = request.args.get('NAME')
    parametro2 = request.args.get('FID')
    if parametro1 is None or parametro2 is None:
        return jsonify({"error": "Se requieren ambos parámetros"}), 400
    # Aquí puedes realizar cualquier lógica con los parámetros
    resultado = {"NAME": parametro1, "FID": parametro2}
    return jsonify(resultado), 200
# ejemplo para filtrar
# http://127.0.0.1:5000/estado/id_nombre?FID=1&NAME=Texas


@app.route('/estado', methods=['GET']) ## b)Recuperar el índice de Obesidad y el área de un estado específico 
def obtener_datos():
    parametro_name = request.args.get('NAME')
    parametro_fid = request.args.get('FID')
    if parametro_name is not None:
        # Buscar por NAME
        estado = gdf[gdf['NAME'] == parametro_name]
    elif parametro_fid is not None:
        # Buscar por FID
        try:
            parametro_fid = int(parametro_fid)
            estado = gdf[gdf['FID'] == parametro_fid]
        except ValueError:
            return jsonify({"error": "El valor de FID debe ser un número"}), 400
    else:
        # Si no ingresan parametros devolverá todos los ID y Nombres
        estados_data = [{"nombre": row['NAME'], "id": row['FID']} for index, row in gdf.iterrows()]
        return jsonify(estados_data), 200
    if estado.empty:
        return jsonify({"error": "Estado no encontrado"}), 404

    # Manejar MultiPolygon
    coordinates = []
    multipolygon = estado.iloc[0]['geometry']
    for polygon in multipolygon.geoms:
        exterior_coords = list(polygon.exterior.coords)
        coordinates.append(exterior_coords)
        
    estado_dict = estado[['NAME', 'FID', 'Obesity']].to_dict(orient='records')[0]
    estado_dict['coordinates'] = coordinates
    return jsonify(estado_dict), 200
## Ejemplo de filtrado
## http://127.0.0.1:5000/estado?FID=1&NAME=Texas
## http://127.0.0.1:5000/estado?FID=1
## http://127.0.0.1:5000/estado?NAME=California


@app.route('/estado/max_obesidad', methods=['GET']) ## c) 1-Encontrar el índice del máximo valor de obesidad
def obtener_estado_max_obesidad():    
    indice_max_obesidad = gdf['Obesity'].idxmax()
    estado_max_obesidad = gdf.loc[indice_max_obesidad, ['NAME', 'Obesity']]
    if estado_max_obesidad.empty:
        return jsonify({"error": "No se encontró el estado con el mayor índice de obesidad"}), 404

    estado_dict = estado_max_obesidad.to_dict()
    return jsonify(estado_dict), 200
## http://127.0.0.1:5000/estado/max_obesidad


@app.route('/estado/min_obesidad', methods=['GET']) ## c) 2-Encontrar el índice del minimo valor de obesidad
def obtener_estado_min_obesidad():    
    indice_min_obesidad = gdf['Obesity'].idxmin()
    estado_min_obesidad = gdf.loc[indice_min_obesidad, ['NAME', 'Obesity']]
    if estado_min_obesidad.empty:
        return jsonify({"error": "No se encontró el estado con el menor índice de obesidad"}), 404

    estado_dict = estado_min_obesidad.to_dict()
    return jsonify(estado_dict), 200
## http://127.0.0.1:5000/estado/min_obesidad


@app.route('/estado/obesidad_promedio', methods=['GET']) ## c) 3-Obesidad promedio
def obtener_obesidad_promedio():
    obesidad_promedio = gdf['Obesity'].mean()
    return jsonify({"obesidad_promedio": obesidad_promedio}), 200
## http://127.0.0.1:5000/estado/obesidad_promedio


@app.route('/todo', methods=['GET'])
def obtener_todo():
    # Iterar sobre todas las filas del GeoDataFrame
    estados_data = []
    for index, row in gdf.iterrows():
        # Verificar si la geometría no es nula antes de aplicar mapping
        if not pd.isnull(row['geometry']):
            estado = {
                'NAME': row['NAME'],
                'FID': row['FID'],
                'Obesity': row['Obesity'],
                'geometry': mapping(row['geometry'])
            }

            estados_data.append(estado)

    return jsonify(estados_data), 200
## http://127.0.0.1:5000/todo


if __name__ == "__main__":
    app.run(debug=True) 