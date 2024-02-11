# DataScientest_Exam_Kubernetes_1

## Consignes :

On cherche à créer un ensemble de fichiers de déploiement destinés à déployer une API de données. 

L'API est constituée de deux conteneurs :

- Le 1er conteneur contient une base de données MySQL : `datascientest/mysql-k8s:1.0.0`

- Le 2ème conteneur contient une API FastAPI.
  
  Ce 2ème conteneur de l'API FastAPI n'est pas encore construit mais les différents fichiers sont déjà créés :

  - Le `Dockerfile`
    
    ```
    FROM ubuntu:20.04
    
    ADD files/requirements.txt files/main.py ./
    
    RUN apt update && apt install python3-pip libmysqlclient-dev -y && pip install -r requirements.txt
    
    EXPOSE 8000
    
    CMD uvicorn main:server --host 0.0.0.0
    ```
    
  - Le fichier `main.py` qui contient l'API
    
    ```python
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from sqlalchemy.engine import create_engine
    
    # creating a FastAPI server
    server = FastAPI(title='User API')
    
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
    
    # creating a User class
    class User(BaseModel):
        user_id: int = 0
        username: str = 'daniel'
        email: str = 'daniel@datascientest.com'
    
    @server.get('/status')
    async def get_status():
        """Returns 1
        """
        return 1
    
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
    ```
    
  - Le fichier `requirements.txt` qui contient les librairies Python à installer
    
    ```
    fastapi
    sqlalchemy
    mysqlclient==2.1.1
    uvicorn
    ```

Il faudra créer un `Deployment` avec 3 `Pods`, chacun de ces Pods contenant à la fois un conteneur MySQL et un conteneur FastAPI. Il faudra ensuite créer un `Service` et un `Ingress` pour permettre l'accès à l'API.


Remarque :

Il faudra donc compléter le code fourni pour l'API de manière à permettre la communication entre l'API et la base de données, reconstruire l'image Docker correspondante et la téléverser dans DockerHub. 
De plus, il faudra changer le code de l'API pour récupérer le mot de passe de la base de données : `datascientest1234`. Toutefois, ce mot de passe ne peut pas être codé en dur et doit donc être mis dans un `Secret`.

## Etape n°1 : Test de déploiment avec un docker compose

- Correction du code Python pour pouvoir exécuter coorectement les requêtes :

    ```python
    from sqlalchemy import text

    ...
    results = connection.execute(text('SELECT * FROM Users;'))
    ...
    results = connection.execute(text(
        'SELECT * FROM Users WHERE Users.id = {};'.format(user_id)))
    ```

- Récupération des variables d'environnement MYSQL_URL et MYSQL_PASSWORD dans le code de l'application :

    ```python
    import os
    ...
    mysql_url = os.getenv('MYSQL_URL')
    ...
    mysql_password = os.getenv('MYSQL_PASSWORD')
    ```

- Ajout de la fonctionnalité d'ajout et de suppression d'utilisateur pour tester la persistance des données.

- Remarque : Si on rentre dans le conteneur lancé à partir de l'image datascientest/mysql-k8s:1.0.0, on a :

    ```bash
    docker-compose up -d
    Building with native build. Learn about native build in Compose here: https://docs.docker.com/go/compose-native-build/
    Creating network "datascientest_exam_kubernetes_1_default" with the default driver
    Creating datascientest_exam_kubernetes_1_ma_bdd_1 ... done
    Creating datascientest_exam_kubernetes_1_mon_api_1 ... done

    ubuntu@ip-172-31-45-18:~/DataScientest_Exam_Kubernetes_1$ docker ps 
    CONTAINER ID   IMAGE                                     COMMAND                  CREATED          STATUS          PORTS                    NAMES
    7091bebc4a26   datascientest_exam_kubernetes_1_mon_api   "/bin/sh -c 'uvicorn…"   11 seconds ago   Up 10 seconds   0.0.0.0:8001->8000/tcp   datascientest_exam_kubernetes_1_mon_api_1
    957043b24471   datascientest/mysql-k8s:1.0.0             "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   3306/tcp, 33060/tcp      datascientest_exam_kubernetes_1_ma_bdd_1

    ubuntu@ip-172-31-45-18:~/DataScientest_Exam_Kubernetes_1$ docker exec -it datascientest_exam_kubernetes_1_ma_bdd_1 bash
    root@957043b24471:/# mysql -u root -p
    Enter password: 
    ...

    mysql> show databases;
    +--------------------+
    | Database           |
    +--------------------+
    | Main               |
    | information_schema |
    | mysql              |
    | performance_schema |
    | sys                |
    +--------------------+
    5 rows in set (0.00 sec)

    mysql> use Main
    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A

    Database changed
    mysql> show tables;
    +----------------+
    | Tables_in_Main |
    +----------------+
    | Users          |
    +----------------+
    1 row in set (0.00 sec)

    mysql> select * from Users;
    +-----+-----------+-------------------------------------------------+
    | id  | username  | email                                           |
    +-----+-----------+-------------------------------------------------+
    |   1 | August    | eu.neque.pellentesque@eumetus.edu               |
    |   2 | Linda     | eleifend.Cras.sed@cursusnonegestas.com          |
    ...
    |  99 | Keefe     | mattis.Integer@lectussit.edu                    |
    | 100 | Abbot     | Cum.sociis@risusvariusorci.ca                   |
    +-----+-----------+-------------------------------------------------+
    100 rows in set (0.01 sec)
    ```

- Après avoir enregistré l'adresse ip du serveur sur ClouDNS au nom de domaine seb-coasne.cloudns.biz, le service est accessible à l'adresse : http://kube.seb-coasne.cloudns.biz:8001/docs

## Etape n°2 : Push de mon image sur Docker hub

- Dans le terminal, j’ai effectué les commandes suivantes : 

    ```bash
    docker build -t dockersebc/datascientest-exam-kubernetes-1:latest .
    docker run -p 8000:8000 dockersebc/datascientest-exam-kubernetes-1
    ```

- En se rendant sur son navigateur web à l’adresse `adresse_ip_vm:8000/docs`, on accéde bien aux infos de la documentation de mon api.

- On se loggue à son compte DockerHub sur la VM et on pousse l'image : : 

    ```bash
    docker login
    docker push dockersebc/datascientest-exam-kubernetes-1:latest
    ```

## Etape n°3 : Déploiement de l'app avec fichiers yaml standards

- Il suffit d'exécuter la commande `chmod +x ./deploiement.sh && ./deploiement.sh` pour lancer le déploiement.
- Le service est accessible ici : 
    - http://kubernetes.seb-coasne.cloudns.biz/docs
    - http://kubernetes.seb-coasne.cloudns.biz/users
    - ...

## Etape n°4 : Déploiement de l'app avec Kustomize

- Mise en place de la structure de répertoire : Création du répertoire mon_kustomize contenant un sous-répertoire base pour stocker mes ressources de base et éventuellement des répertoires supplémentaires pour d'autres environnements ou configurations.
- Création des fichiers Kustomize : Dans le sous-répertoire base, création d'un fichier kustomization.yaml qui référence les ressources qu'on souhaite déployer.
- Définition des ressources :
Dans le dossier base, on crée les fichiers YAML pour nos ressources. 
- Personnalisez avec Kustomize :
Dans le fichier kustomization.yaml dans mon_kustomize/base, on peut spécifier les ressources qu'on souhaite inclure, les modifications qu'on souhaite apporter et les secrets qu'on souhaite utiliser.
- Exécution de `kustomize build mon_kustomize/base` pour générer notre configuration Kubernetes consolidée. Et on peut utiliser cette configuration pour déployer nos ressources Kubernetes avec `kubectl apply -k mon_kustomize/base/`.