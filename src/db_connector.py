from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json
import os

load_dotenv()
#postgresql://myuser:mypassword@localhost:5432/mydatabase Azure Key Vault
with open('credentials.json', 'r') as f:
    data = json.load(f)

user = data[0]['data']['user']
password = data[0]['data']['password']
database = data[0]['data']['database']
host = data[0]['data']['host']

# Construye la URL de la base de datos
DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{database}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#with engine.connect() as connection:
#    stmt = text("SELECT 1")
#    result = connection.execute(stmt)
#    print(result.fetchone())
inspector = inspect(engine)
tables = inspector.get_table_names(schema="variamos")
print(tables)
table_name = "project"

    # Obtiene las claves foráneas de la tabla
foreign_keys = inspector.get_foreign_keys(table_name,schema="variamos")

    # Imprime las claves foráneas
for fk in foreign_keys:
        print(f"Constrained column: {fk['constrained_columns']} -> Referenced table: {fk['referred_table']} (Column: {fk['referred_columns']})")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
