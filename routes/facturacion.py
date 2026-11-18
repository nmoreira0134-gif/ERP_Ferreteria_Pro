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
            SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, 
                   ISNULL(c.Nombre, 'Cliente Borrado') AS Cliente, 
                   f.Total, f.Estado
            FROM Facturas f
            LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
            ORDER BY f.FacturaID DESC
        """)
        facturas = cursor.fetchall()
        conn.close()
        return render_template('facturacion/list.html', facturas=facturas)
    except Exception as e:
        traceback.print_exc()
        flash(f'Error al cargar lista: {e}', 'error')
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

                # 1. VALIDACIÓN DE STOCK (Usando el Kardex real)
                cursor.execute("""
                    SELECT ISNULL(SUM(Cantidad), 0) 
                    FROM MovimientosInventario 
                    WHERE ProductoID = ?
                """, (prod_id,))
                stock_row = cursor.fetchone()
                stock_actual = Decimal(str(stock_row[0])) if stock_row else Decimal('0.00')
                
                if stock_actual < cantidad:
                    raise ValueError(f"Stock insuficiente. Solo hay {stock_actual} unidades disponibles para este producto.")

                cursor.execute("SELECT PrecioUnitario FROM Productos WHERE ProductoID = ?", (prod_id,))
                prod_row = cursor.fetchone()
                if not prod_row: raise ValueError(f"Producto ID {prod_id} no encontrado.")
                
                precio_unitario = Decimal(str(prod_row[0]))
                subtotal_linea = cantidad * precio_unitario
                subtotal_global += subtotal_linea

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
                # 3. INSERTAR DETALLE DE LA FACTURA
                cursor.execute("""
                    INSERT INTO FacturaDetalle (FacturaID, ProductoID, Cantidad, PrecioUnitario, SubtotalLinea)
                    VALUES (?, ?, ?, ?, ?)
                """, (factura_id, linea[0], linea[1], linea[2], linea[3]))
                
                # 4. REGISTRAR EN EL KARDEX (Cantidad negativa para que reste en la suma)
                cursor.execute("""
                    INSERT INTO MovimientosInventario (ProductoID, TipoMovimiento, Cantidad, Referencia, Usuario, Fecha)
                    VALUES (?, 'Salida', ?, ?, ?, GETDATE())
                """, (linea[0], -linea[1], num_factura, 'Admin'))

            conn.commit()
            conn.close()
            flash(f'¡Factura {num_factura} generada y registrada en Kardex!', 'success')
            return redirect(url_for('facturacion.detalle', factura_id=factura_id))

        # --- FLUJO GET ---
        cursor.execute("SELECT ClienteID, Nombre FROM Clientes ORDER BY Nombre")
        clientes = cursor.fetchall()
        cursor.execute("SELECT EmpleadoID, Nombre FROM Empleados WHERE Activo = 1 ORDER BY Nombre")
        empleados = cursor.fetchall()
        
        # CONSULTA CORREGIDA: Calcula el stock desde el Kardex (Suma de Cantidades)
        cursor.execute("""
            SELECT 
                p.ProductoID, 
                p.Nombre, 
                p.PrecioUnitario, 
                p.UnidadMedida, 
                ISNULL(SUM(m.Cantidad), 0) AS Stock
            FROM Productos p
            LEFT JOIN MovimientosInventario m ON p.ProductoID = m.ProductoID
            GROUP BY p.ProductoID, p.Nombre, p.PrecioUnitario, p.UnidadMedida
            ORDER BY p.Nombre
        """)
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
        cursor.execute("""
            SELECT f.FacturaID, f.NumeroFactura, f.FechaEmision, c.Nombre, e.Nombre, 
                   f.Subtotal, f.IVA_Aplicado, f.MontoIVA, f.Total, f.Estado, 
                   f.TipoCambio, f.MotivoAnulacion
            FROM Facturas f
            LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID
            INNER JOIN Empleados e ON f.EmpleadoID = e.EmpleadoID
            WHERE f.FacturaID = ?
        """, (factura_id,))
        factura = cursor.fetchone()
        if not factura:
            flash('Factura no encontrada.', 'error')
            return redirect(url_for('facturacion.lista'))

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

        cursor.execute("SELECT NumeroFactura, Estado FROM Facturas WHERE FacturaID = ?", (factura_id,))
        row = cursor.fetchone()
        if not row or row[1] == 'Anulada':
            raise ValueError("Factura no encontrada o ya está anulada.")
        
        num_factura = row[0]

        cursor.execute("SELECT ProductoID, Cantidad FROM FacturaDetalle WHERE FacturaID = ?", (factura_id,))
        detalles = cursor.fetchall()
        
        for d in detalles:
            # Registrar Devolucion en Kardex (Cantidad positiva para que SUME)
            cursor.execute("""
                INSERT INTO MovimientosInventario (ProductoID, TipoMovimiento, Cantidad, Referencia, Usuario, Fecha)
                VALUES (?, 'Devolucion', ?, ?, ?, GETDATE())
            """, (d[0], d[1], f"Anulación de {num_factura}", "SYSTEM"))

        cursor.execute("""
            UPDATE Facturas SET Estado = 'Anulada', MotivoAnulacion = ? WHERE FacturaID = ?
        """, (motivo.strip(), factura_id))

        conn.commit()
        conn.close()
        flash(f'Factura {num_factura} anulada. Stock devuelto y Kardex actualizado.', 'success')
        return redirect(url_for('facturacion.detalle', factura_id=factura_id))

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        traceback.print_exc()
        flash(f'Error al anular: {e}', 'error')
        return redirect(url_for('facturacion.detalle', factura_id=factura_id))