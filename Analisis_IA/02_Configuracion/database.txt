# ============================================================================
# MAMBO ERP SOLUTIONS
# Archivo: database.py
# Propósito: Conexión única a SQL Server con control explícito de transacciones.
# ============================================================================

import pyodbc
from config import Config

def get_connection():
    """
    Retorna una conexión a FerreteriaDB.
    IMPORTANTE: autocommit=False obliga a llamar a conn.commit() explícitamente.
    Esto es vital para Facturación: si algo falla, el rollback devuelve el correlativo.
    """
    conn_str = (
        f"Driver={Config.DB_DRIVER};"
        f"Server={Config.DB_SERVER};"
        f"Database={Config.DB_DATABASE};"
        f"Trusted_Connection={Config.DB_TRUSTED_CONNECTION};"
        f"TrustServerCertificate={Config.DB_TRUST_SERVER_CERTIFICATE};"
    )
    # El único cambio real: forzar autocommit=False
    return pyodbc.connect(conn_str, autocommit=False)