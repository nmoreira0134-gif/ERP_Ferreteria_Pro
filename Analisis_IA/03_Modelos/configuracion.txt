from decimal import Decimal, InvalidOperation
from database import get_connection

_cache = None

class Configuracion:
    @staticmethod
    def get(force_refresh: bool = False) -> dict:
        global _cache
        if _cache is not None and not force_refresh:
            return _cache

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT ConfiguracionId, RazonSocial, RUC, Direccion, Telefono,
                       Email, Moneda, IVA, Comision, ComisionSobreTotal,
                       FechaActualizacion, ActualizadoPor, TipoCambio
                  FROM dbo.Configuracion WHERE ConfiguracionId = 1
            """)
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Tabla Configuracion vacía.")

            _cache = {
                "ConfiguracionId": row[0], "RazonSocial": row[1], "RUC": row[2],
                "Direccion": row[3], "Telefono": row[4], "Email": row[5],
                "Moneda": row[6], "IVA": Decimal(str(row[7])),
                "Comision": Decimal(str(row[8])), "ComisionSobreTotal": bool(row[9]),
                "FechaActualizacion": row[10], "ActualizadoPor": row[11],
                "TipoCambio": Decimal(str(row[12])),
            }
            return _cache
        finally:
            conn.close()

    @staticmethod
    def update(iva=None, comision=None, comision_sobre_total=None, tipo_cambio=None, usuario: str = "SYSTEM") -> bool:
        global _cache
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT IVA, Comision, ComisionSobreTotal, TipoCambio FROM dbo.Configuracion WHERE ConfiguracionId = 1")
            row = cur.fetchone()
            if not row: raise RuntimeError("Configuración no inicializada.")

            try:
                nueva_iva = Decimal(str(iva)) if iva is not None else row[0]
                nueva_com = Decimal(str(comision)) if comision is not None else row[1]
                nuevo_tc = Decimal(str(tipo_cambio)) if tipo_cambio is not None else row[3]
            except InvalidOperation as exc:
                raise ValueError(f"Valores no numéricos: {exc}")

            nuevo_cst = bool(comision_sobre_total) if comision_sobre_total is not None else bool(row[2])

            if not (Decimal("0") <= nueva_iva <= Decimal("1")):
                raise ValueError(f"IVA fuera de rango [0,1]: {nueva_iva}")
            if not (Decimal("0") <= nueva_com <= Decimal("1")):
                raise ValueError(f"Comisión fuera de rango [0,1]: {nueva_com}")

            cur.execute("""
                UPDATE dbo.Configuracion
                   SET IVA = ?, Comision = ?, ComisionSobreTotal = ?, TipoCambio = ?,
                       FechaActualizacion = SYSDATETIME(), ActualizadoPor = ?
                 WHERE ConfiguracionId = 1
            """, nueva_iva, nueva_com, 1 if nuevo_cst else 0, nuevo_tc, usuario)

            cur.execute("""
                INSERT INTO dbo.Configuracion_Historial
                (ConfiguracionId, IVA, Comision, ComisionSobreTotal, Usuario)
                VALUES (1, ?, ?, ?, ?)
            """, nueva_iva, nueva_com, 1 if nuevo_cst else 0, usuario)

            conn.commit()
            _cache = None
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()