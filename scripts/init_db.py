import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(user='postgres', password='yayin119', host='127.0.0.1', port='5432')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE skypredict;')
    print('Database skypredict created successfully.')
    cursor.close()
    conn.close()
except psycopg2.errors.DuplicateDatabase:
    print('Database skypredict already exists.')
except Exception as e:
    print(f'Error: {e}')
