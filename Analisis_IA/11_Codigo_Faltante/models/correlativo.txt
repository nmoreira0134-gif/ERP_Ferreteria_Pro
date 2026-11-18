# ============================================================================
# MAMBO ERP SOLUTIONS
# Archivo: models/correlativo.py
# Propósito: Emisión atómica de números de documento.
# ============================================================================

from database import get_connection

class Correlativo:
    @staticmethod
    def siguiente(cursor, tipo_documento: str) -> dict:
        """
        Consume el número DENTRO de una transacción existente.
        Si el caller hace rollback, el número regresa a su estado anterior.
        """
        cursor.execute("""
            UPDATE dbo.Correlativos
               SET UltimoNumero = UltimoNumero + 1
             OUTPUT INSERTED.UltimoNumero, INSERTED.Serie, INSERTED.Longitud
              WHERE TipoDocumento = ? AND Activo = 1
        """, tipo_documento)

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Correlativo inactivo o inexistente: '{tipo_documento}'")

        numero, serie, longitud = int(row[0]), row[1], int(row[2])
        return {
            "numero": numero,
            "serie": serie,
            "formateado": f"{serie}-{numero:0{longitud}d}",
        }

    @staticmethod
    def peek(tipo_documento: str) -> dict:
        """Muestra el próximo número SIN consumirlo (para la UI)."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT Serie, UltimoNumero, Longitud FROM dbo.Correlativos WHERE TipoDocumento = ? AND Activo = 1", tipo_documento)
            row = cur.fetchone()
            if not row: return None
            
            serie, ultimo, longitud = row[0], int(row[1]), int(row[2])
            proximo = ultimo + 1
            return {
                "serie": serie,
                "ultimo": ultimo,
                "proximo": proximo,
                "formateado": f"{serie}-{proximo:0{longitud}d}",
            }
        finally:
            conn.close()