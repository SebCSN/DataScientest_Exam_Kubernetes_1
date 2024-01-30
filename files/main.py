from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.engine import create_engine


#############################################################################################################################
# Création d'une instance de FastAPI avec le titre "User API" :

# creating a FastAPI server
server = FastAPI(title='User API') 


#############################################################################################################################
# Configuration de la connexion à la base de données MySQL en utilisant SQLAlchemy pour créer un moteur de base de données :

# creating a connection to the database
mysql_url = ''  # to complete
mysql_user = 'root'
mysql_password = ''  # to complete
database_name = 'Main'

# recreating the URL connection
connection_url = 'mysql://{user}:{password}@{url}/{database}'.format(
    user=mysql_user,
    password=mysql_password,
    url=mysql_url,
    database=database_name
)

# creating the connection
mysql_engine = create_engine(connection_url)


#############################################################################################################################
# Définition d'une classe User héritant de BaseModel de Pydantic pour représenter la structure des données utilisateur.
# Attributs de la classe User :
#   - user_id : attribut de type entier avec une valeur par défaut de 0.
#   - username : attribut de type chaîne de caractères avec une valeur par défaut de 'daniel'.
#   - email : attribut de type chaîne de caractères avec une valeur par défaut de 'daniel@datascientest.com'.

# creating a User class
class User(BaseModel):
    user_id: int = 0 
    username: str = 'daniel'
    email: str = 'daniel@datascientest.com'


#############################################################################################################################
# Définition des routes de l'API :

# Route simple qui renvoie le nombre 1 :
@server.get('/status') 
async def get_status():
    """Returns 1
    """
    return 1

# Route qui interroge la base de données pour récupérer tous les utilisateurs :
@server.get('/users') 
async def get_users():
    with mysql_engine.connect() as connection:
        results = connection.execute('SELECT * FROM Users;')

    results = [
        User(
            user_id=i[0],
            username=i[1],
            email=i[2]
            ) for i in results.fetchall()]
    return results

# Route qui prend en paramètre user_id de type entier dans l'URL et renvoie les informations de l'utilisateur correspondant :
@server.get('/users/{user_id:int}', response_model=User)
async def get_user(user_id):
    with mysql_engine.connect() as connection:
        results = connection.execute(
            'SELECT * FROM Users WHERE Users.id = {};'.format(user_id))

    results = [
        User(
            user_id=i[0],
            username=i[1],
            email=i[2]
            ) for i in results.fetchall()]

    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail='Unknown User ID')
    else:
        return results[0]