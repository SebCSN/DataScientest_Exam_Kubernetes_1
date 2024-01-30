from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.engine import create_engine
from sqlalchemy import text
import os
from typing import Optional

#############################################################################################################################
# Création d'une instance de FastAPI avec le titre "User API" :

# creating a FastAPI server
server = FastAPI(title='User API') 


#############################################################################################################################
# Configuration de la connexion à la base de données MySQL en utilisant SQLAlchemy pour créer un moteur de base de données :

# creating a connection to the database
mysql_url = os.getenv('MYSQL_URL')
mysql_user = 'root'
mysql_password = os.getenv('MYSQL_PASSWORD')
database_name = 'Main' # BDD créée à l'intérieur du conteneur

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
        results = connection.execute(text('SELECT * FROM Users;'))

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
        results = connection.execute(text(
            'SELECT * FROM Users WHERE Users.id = {};'.format(user_id)))

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

# Route pour créer un nouvel utilisateur
@server.post('/users', response_model=User)
async def create_user(user: User):
    with mysql_engine.connect() as connection:
        query = text('INSERT INTO Users (username, email) VALUES (:username, :email);') # Insére un nouvel utilisateur dans la base de données
        result = connection.execute(query, {"username": user.username, "email": user.email})

        connection.commit() # Enregistrement des modifs en BDD

    # Retourne le nouvel utilisateur créé :
    return User(user_id=result.lastrowid, username=user.username, email=user.email)

# Route pour supprimer un utilisateur en fonction de user_id
@server.delete('/users/{user_id:int}')
async def delete_user(user_id: int):
    with mysql_engine.connect() as connection:
        # Vérification si l'utilisateur existe
        existing_user = connection.execute(
            text('SELECT * FROM Users WHERE Users.id = {};'.format(user_id))
        ).fetchall()

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail='Unknown User ID'
            )

        # Suppression de l'utilisateur de la base de données
        query = text('DELETE FROM Users WHERE Users.id = :user_id;')
        connection.execute(query, {"user_id": user_id})

        connection.commit() # Enregistrement des modifs en BDD

    # Retourne un message indiquant que l'utilisateur a été supprimé avec succès
    return {"message": f"User with ID {user_id} has been deleted"}