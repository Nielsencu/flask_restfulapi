import os

local = True

if local:
    #For local
    user = "postgres"
    password = "Tuv#24893"
    host = 'localhost'
    port = '5432'
    database = 'customerdb'
    #
else:
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOST']
    database = os.environ['POSTGRES_DB']
    port = os.environ['POSTGRES_PORT']

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'