# ============================================================================
# MAMBO ERP SOLUTIONS
# Archivo: routes/facturacion.py
# ============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
from models.configuracion import Configuracion
from models.correlativo import Correlativo
from decimal import Decimal
import traceback

bp_facturacion = Blueprint('facturacion', __name__, url_prefix='/facturacion')

@bp_facturacion.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, c.Nombre AS Cliente, f.Total, f.Estado
            FROM Facturas f
            INNER JOIN Clientes c ON f.ClienteID = c.ClienteID
            ORDER BY f.FacturaID DESC
        """)
        facturas = cursor.fetchall()
        conn.close()
        return render_template('facturacion/list.html', facturas=facturas)
    except Exception as e:
        traceback.print_exc()
        flash(f'Error: {e}', 'error')
        return redirect(url_for('main.index'))

@bp_facturacion.route('/nueva', methods=['GET', 'POST'])
def nueva():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            empleado_id = request.form.get('empleado_id')
            
            producto_ids = request.form.getlist('producto_id[]')
            cantidades = request.form.getlist('cantidad[]')

            if not producto_ids or len(producto_ids) == 0:
                raise ValueError("Debe agregar al menos un producto a la factura.")

            cfg = Configuracion.get()
            iva_porcentaje = cfg['IVA']
            comision_porcentaje = cfg['Comision']
            tipo_cambio = cfg['TipoCambio']

            subtotal_global = Decimal('0.00')
            lineas_a_insertar = []

            for prod_id, cant_str in zip(producto_ids, cantidades):
                cantidad = Decimal(cant_str)
                if cantidad <= 0: continue

                cursor.execute("SELECT PrecioUnitario FROM Productos WHERE ProductoID = ?", (prod_id,))
                prod_row = cursor.fetchone()
                if not prod_row: raise ValueError(f"Producto ID {prod_id} no encontrado.")
                
                precio_unitario = Decimal(str(prod_row[0]))
                subtotal_linea = cantidad * precio_unitario
                subtotal_global += subtotal_linea

                cursor.execute("""
                    UPDATE Inventario SET CantidadDisponible = CantidadDisponible - ? 
                    WHERE ProductoID = ?
                """, (cantidad, prod_id))

                lineas_a_insertar.append((prod_id, cantidad, precio_unitario, subtotal_linea))

            monto_iva = subtotal_global * iva_porcentaje
            monto_comision = subtotal_global * comision_porcentaje 
            total = subtotal_global + monto_iva

            corr = Correlativo.siguiente(cursor, 'FAC')
            num_factura = corr['formateado']

            cursor.execute("""
                INSERT INTO Facturas (
                    NumeroFactura, ClienteID, EmpleadoID, Subtotal, IVA_Aplicado, MontoIVA, 
                    Comision_Aplicada, MontoComision, Total, TipoCambio
                ) OUTPUT INSERTED.FacturaID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                num_factura, cliente_id, empleado_id, subtotal_global, 
                iva_porcentaje, monto_iva, comision_porcentaje, monto_comision, total, tipo_cambio
            ))
            factura_id = cursor.fetchone()[0]

            for linea in lineas_a_insertar:
                cursor.execute("""
                    INSERT INTO FacturaDetalle (FacturaID, ProductoID, Cantidad, PrecioUnitario, SubtotalLinea)
                    VALUES (?, ?, ?, ?, ?)
                """, (factura_id, linea[0], linea[1], linea[2], linea[3]))

            conn.commit()
            conn.close()
            flash(f'¡Factura {num_factura} generada con éxito!', 'success')
            return redirect(url_for('facturacion.detalle', factura_id=factura_id))

        # --- FLUJO GET ---
        cursor.execute("SELECT ClienteID, Nombre FROM Clientes ORDER BY Nombre")
        clientes = cursor.fetchall()
        cursor.execute("SELECT EmpleadoID, Nombre FROM Empleados WHERE Activo = 1 ORDER BY Nombre")
        empleados = cursor.fetchall()
        cursor.execute("SELECT ProductoID, Nombre, PrecioUnitario, UnidadMedida FROM Productos ORDER BY Nombre")
        productos = cursor.fetchall()
        proxima_factura = Correlativo.peek('FAC')
        cfg = Configuracion.get()

        conn.close()
        return render_template('facturacion/form.html', clientes=clientes, empleados=empleados, 
                               productos=productos, proxima_factura=proxima_factura, cfg=cfg)

    except Exception as e:
        if 'conn' in locals():
            conn.rollback() 
            conn.close()
        traceback.print_exc()
        flash(f'Error al facturar: {e}', 'error')
        return redirect(url_for('facturacion.nueva'))

@bp_facturacion.route('/ver/<int:factura_id>')
def detalle(factura_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # CORREGIDO: Agregado f.FacturaID al inicio del SELECT
        cursor.execute("""
            SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, c.Nombre, e.Nombre, 
                   f.Subtotal, f.IVA_Aplicado, f.MontoIVA, f.Total, f.Estado, 
                   f.TipoCambio, f.MotivoAnulacion
            FROM Facturas f
            INNER JOIN Clientes c ON f.ClienteID = c.ClienteID
            INNER JOIN Empleados e ON f.EmpleadoID = e.EmpleadoID
            WHERE f.FacturaID = ?
        """, (factura_id,))
        factura = cursor.fetchone()

        cursor.execute("""
            SELECT p.Nombre, p.UnidadMedida, d.Cantidad, d.PrecioUnitario, d.SubtotalLinea
            FROM FacturaDetalle d
            INNER JOIN Productos p ON d.ProductoID = p.ProductoID
            WHERE d.FacturaID = ?
        """, (factura_id,))
        detalles = cursor.fetchall()
        conn.close()
        return render_template('facturacion/detalle.html', factura=factura, detalles=detalles)
    except Exception as e:
        traceback.print_exc()
        flash(f'Error: {e}', 'error')
        return redirect(url_for('facturacion.lista'))

@bp_facturacion.route('/anular/<int:factura_id>', methods=['POST'])
def anular(factura_id):
    try:
        motivo = request.form.get('motivo_anulacion')
        if not motivo or len(motivo.strip()) < 5:
            flash('Debe proporcionar un motivo válido (mín. 5 letras).', 'error')
            return redirect(url_for('facturacion.detalle', factura_id=factura_id))

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Estado FROM Facturas WHERE FacturaID = ?", (factura_id,))
        row = cursor.fetchone()
        if not row or row[0] == 'Anulada':
            raise ValueError("Factura no encontrada o ya está anulada.")

        cursor.execute("SELECT ProductoID, Cantidad FROM FacturaDetalle WHERE FacturaID = ?", (factura_id,))
        detalles = cursor.fetchall()
        for d in detalles:
            cursor.execute("""
                UPDATE Inventario SET CantidadDisponible = CantidadDisponible + ? 
                WHERE ProductoID = ?
            """, (d[1], d[0]))

        cursor.execute("""
            UPDATE Facturas SET Estado = 'Anulada', MotivoAnulacion = ? WHERE FacturaID = ?
        """, (motivo.strip(), factura_id))

        conn.commit()
        conn.close()
        flash('Factura anulada correctamente. El stock ha sido devuelto.', 'success')
        return redirect(url_for('facturacion.detalle', factura_id=factura_id))

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        traceback.print_exc()
        flash(f'Error al anular: {e}', 'error')
        return redirect(url_for('facturacion.detalle', factura_id=factura_id))