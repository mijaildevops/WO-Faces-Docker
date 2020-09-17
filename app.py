# Flask
from flask import Flask, jsonify, request
# DB
import pymysql
# Guid aletoreo
import uuid

#requests
import requests

# Cognitive Services
import cognitive_face as CF

# Time
import time

from Settings import server, connection
Conexion = connection

# Request
import http.client, urllib.request, urllib.parse, urllib.error, base64

# Cors
from flask_cors import CORS

# 
from Settings import SUBSCRIPTION_KEY, BASE_URL
CF.BaseUrl.set(BASE_URL)
CF.Key.set(SUBSCRIPTION_KEY)



#MAIN 
app = Flask(__name__)
cors = CORS(app)

#////////////////////////////////////////////////////////////////////////////////   
# Web Services For create "Users"  
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users', methods=['POST'])
def crear_Users():

    # Datos request
    try:
        UserName = request.json['username']
        Password = request.json['password']
        Name = request.json['name']
        LastName = request.json['lastname']
        Country = request.json['country']
        
    except:
        return {'Error': 'Incorrect Parameters'}
    
    # Datos from Body
    # Generar GroupId aleatoreo
    GroupId = str(uuid.uuid4())
    GroupName = 'Main'
    Level = 1
    Access = 'Primary'

    try:

        with connection.cursor() as cursor:

            # Si el Usuario no existe en la DB, procede a Crear el registro 
            sql = "INSERT INTO `Users` (UserName, Password, Name, LastName, Country) Values (%s, %s, %s,%s,%s)"
            cursor.execute(sql, (UserName, Password, Name, LastName, Country))
            connection.commit()

            # obtener Id del usuario Creado
            sql = "SELECT * FROM Users where UserName = %s"
            cursor.execute(sql, UserName)
            resultados = cursor.fetchone()
            connection.commit()
            UserId = resultados["Id"]

            # Crear registro con relacion User y group
            sql = "INSERT INTO `PersonGroups` (UserId, GroupId, Name, Level, Access) Values (%s, %s, %s,%s,%s)"
            cursor.execute(sql, (UserId, GroupId, GroupName, Level, Access))
            connection.commit()

            # Create Grupo FR-Data Base en Cognitivve-services
            CF.person_group.create(GroupId, UserName)

            #Objetos con la data a enviar
            Data = {'message': 'Usuario creado con exito', 'UserName': UserName, 'Name': Name, 'LastName': LastName, 'Country': Country}
            GroupData = {'GroupName': GroupName,'GroupId': GroupId, 'Level': Level, 'Access': Access}
          
        # Response 
        return jsonify (
            {'Message': 'Usuario Creado', 
            'UserData': Data,
            'PersonGroup': GroupData
            })

    except:
        return not_found()  

#////////////////////////////////////////////////////////////////////////////////   
# Web Services for add person to "FR DB"  
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/FRPerson', methods=['POST'])
def Add_person():

    # Datos request
    try:
        PersonName = request.json['personname']
        user_data = request.json['userdata']
        GroupId = request.json['GroupId']
        Frame = request.json['Frame']
    except:
        return {'Error': 'Incorrect Parameters'}
    
    try:

        # Create person
        response = CF.person.create(GroupId, PersonName, user_data)

        # cambiar por una await
        time.sleep(5)

        # Get person_id from response
        person_id = response['personId']

        #Now we can start adding face images to the person for training our system:
        CF.person.add_face(Frame, GroupId, person_id)

        # Train Group this accion debe realizarse cada vez que se agregue modifique una persona
        try:
            headers = {
                    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
                }

            params = urllib.parse.urlencode({
            })

            # Send request
            conn = http.client.HTTPSConnection('eastus.api.cognitive.microsoft.com')
            conn.request("POST", "/face/v1.0/persongroups/" + GroupId + "/train?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()

        except Exception as e:
            print("[Errno ] {0}".format(e))

        return {'message': 'Persona Entrenada con exito', 'person_id': person_id, 'PersonName': PersonName, 'GroupId': GroupId}
    
    except:
        return not_found()    
    
#////////////////////////////////////////////////////////////////////////////////   
# Web Services for add person to "FR DB"  
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/FRPerson/<GroupId>', methods=['GET'])
def List_person(GroupId):

    try:
        ListPerson = CF.person.lists(GroupId)
        return {'List': ListPerson}
    
    except:
        return not_found() 

#////////////////////////////////////////////////////////////////////////////////   
# Web Services for Identify person"FR DB"  
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/Identificacion', methods=['POST'])
def Identificacion():
    
    # Datos request
    try:
        GroupId = request.json['GroupId']
        Frame = request.json['Frame']
    except:
        return {'Error': 'Incorrect Parameters'}

    try:

        # Detectar Rostros
        response = CF.face.detect(Frame)
        face_ids = [d['faceId'] for d in response]

        # identificacion de personas
        identified_faces = CF.face.identify(face_ids, GroupId)

       

        return {'GroupId': GroupId, 'response': identified_faces}
    
    except:
        return not_found()     

#//////////////////////////////////////////////////////////////////////////////// 
# MANEJO DE ERRORES
#//////////////////////////////////////////////////////////////////////////////// 
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Pagina no encontrada ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(port = 3950, debug = True, host=server) # PC Main