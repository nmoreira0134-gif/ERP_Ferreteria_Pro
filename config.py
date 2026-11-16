class Config:
    SECRET_KEY = 'clave-secreta-para-desarrollo-local'
    DB_DRIVER = "{ODBC Driver 18 for SQL Server}"
    DB_SERVER = "localhost" 
    DB_DATABASE = "FerreteriaDB"
    DB_TRUSTED_CONNECTION = "yes"
    DB_TRUST_SERVER_CERTIFICATE = "yes"