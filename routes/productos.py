from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import db, Producto, Proveedor, CargasInventario, MovimientosInventario
import pandas as pd
import io
import traceback
from datetime import datetime
import re

bp_productos = Blueprint('productos', __name__, url_prefix='/productos')

# --- FUNCIÓN PARA LIMPIAR EL PRECIO ---
def limpiar_precio(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None 
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    texto_limpio = re.sub(r'[^\d.,-]', '', str(valor))
    texto_limpio = texto_limpio.replace(',', '.')
    
    try:
        return float(texto_limpio)
    except ValueError:
        return None 
# --------------------------------------

@bp_productos.route('/')
def lista():
    try:
        busqueda = request.args.get('busqueda', '')
        if busqueda:
            productos = Producto.query.filter(Producto.Nombre.contains(busqueda)).all()
        else:
            productos = Producto.query.all()
        return render_template('productos/list.html', productos=productos, busqueda=busqueda)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos: {str(e)}"

@bp_productos.route('/crear', methods=['GET', 'POST'])
def crear():
    try:
        proveedores = Proveedor.query.all()
    except Exception:
        traceback.print_exc()
        proveedores = []
        
    if request.method == 'POST':
        try:
            nuevo = Producto(
                Nombre=request.form['nombre'],
                PrecioUnitario=request.form['precio'],
                SKU=request.form['sku'],
                UnidadMedida=request.form.get('unidad_medida', ''),
                ProveedorID=request.form.get('proveedor_id') or None,
                CodigoProveedor=request.form.get('codigo_proveedor', ''),
                FechaCreacion=datetime.now()
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Producto creado exitosamente.', 'success')
            return redirect(url_for('productos.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al crear producto: {str(e)}", "danger")
            
    return render_template('productos/form.html', proveedores=proveedores, producto=None)

@bp_productos.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = Producto.query.get_or_404(id)
    try:
        proveedores = Proveedor.query.all()
    except Exception:
        traceback.print_exc()
        proveedores = []

    if request.method == 'POST':
        try:
            producto.Nombre = request.form['nombre']
            producto.PrecioUnitario = request.form['precio']
            producto.SKU = request.form['sku']
            producto.UnidadMedida = request.form.get('unidad_medida', '')
            producto.ProveedorID = request.form.get('proveedor_id') or None
            producto.CodigoProveedor = request.form.get('codigo_proveedor', '')
            producto.FechaModificacion = datetime.now()
            
            db.session.commit()
            flash('Producto actualizado exitosamente.', 'success')
            return redirect(url_for('productos.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al editar producto: {str(e)}", "danger")

    return render_template('productos/form.html', proveedores=proveedores, producto=producto)

@bp_productos.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error al eliminar producto: {str(e)}", "danger")
    return redirect(url_for('productos.lista'))

@bp_productos.route('/exportar_excel')
def exportar_excel():
    try:
        productos = Producto.query.all()
        data = []
        for p in productos:
            data.append({
                'ID': p.ProductoID,
                'Nombre': p.Nombre,
                'Precio': p.PrecioUnitario,
                'SKU': p.SKU,
                'CodigoProveedor': p.CodigoProveedor
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Productos')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_productos.xlsx'
        )
    except Exception as e:
        traceback.print_exc()
        flash(f"Error al exportar a Excel: {str(e)}", "danger")
        return redirect(url_for('productos.lista'))

@bp_productos.route('/descargar_plantilla')
def descargar_plantilla():
    try:
        productos = Producto.query.all()
        data = []
        for p in productos:
            data.append({
                'SKU': p.SKU,
                'Nombre': p.Nombre,
                'Precio': '', # Vacío para que el proveedor lo llene
                'StockEnvio': '',           
                'UnidadMedida': p.UnidadMedida or '' 
            })
        
        if not data:
            data = [{
                'SKU': 'EJEMPLO-001',
                'Nombre': 'Producto de Ejemplo',
                'Precio': '',
                'StockEnvio': '',
                'UnidadMedida': 'Unidad'
            }]

        df = pd.DataFrame(data)
        
        # --- HOJA DE INSTRUCCIONES ---
        instrucciones = [
            ['INSTRUCCIONES PARA EL LLENADO DEL CATÁLOGO'],
            [''],
            ['1. NO modifique las columnas SKU, Nombre ni UnidadMedida.'],
            ['2. Llene la columna "StockEnvio" únicamente con la cantidad que nos proveerá.'],
            ['3. En la columna "Precio", ingrese el costo unitario del producto.'],
            ['4. IMPORTANTE: Todos los precios deben ser ingresados en CÓRDOBAS (NIO).'],
            ['5. Si sus precios están en Dólares (USD), realice la conversión a Córdobas antes de llenar la columna.'],
            ['6. NO utilice símbolos de moneda ($, C$, USD). Utilice solo números y punto decimal (Ejemplo correcto: 150.50 / Ejemplo incorrecto: $150.50)'],
            [''],
            ['Si tiene dudas, comuníquese con el departamento de compras.']
        ]
        df_instrucciones = pd.DataFrame(instrucciones)
        # -----------------------------

        output = io.BytesIO()
        # Escribimos ambas hojas en el mismo archivo Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Catalogo')
            df_instrucciones.to_excel(writer, index=False, sheet_name='INSTRUCCIONES', header=False)
            
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='catalogo_para_proveedor.xlsx'
        )
    except Exception as e:
        traceback.print_exc()
        flash(f"Error al generar plantilla: {str(e)}", "danger")
        return redirect(url_for('productos.carga_masiva'))

@bp_productos.route('/carga_masiva', methods=['GET', 'POST'])
def carga_masiva():
    try:
        proveedores = Proveedor.query.all() 
    except Exception as e:
        traceback.print_exc()
        proveedores = []

    if request.method == 'POST':
        try:
            if 'archivo_excel' not in request.files:
                flash('No se seleccionó ningún archivo', "danger")
                return redirect(request.url)
            
            file = request.files['archivo_excel']
            proveedor_id = request.form.get('proveedor_id')
            
            if file.filename == '' or not proveedor_id:
                flash('Debes seleccionar un archivo y un proveedor', "danger")
                return redirect(request.url)

            # Leemos la primera hoja (Catalogo)
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()
            
            columnas_requeridas = ['SKU', 'Nombre', 'Precio', 'StockEnvio', 'UnidadMedida']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                flash(f"El Excel no tiene las columnas: {', '.join(columnas_faltantes)}. Descarga la nueva plantilla.", "danger")
                return redirect(request.url)

            nueva_carga = CargasInventario(
                Fecha=datetime.now(),
                ProveedorID=proveedor_id,
                Usuario='Admin', 
                Referencia=file.filename
            )
            db.session.add(nueva_carga)
            db.session.flush() 

            for index, row in df.iterrows():
                sku_excel = str(row['SKU']).strip()
                
                if pd.isna(row['StockEnvio']) or str(row['StockEnvio']).strip() == '':
                    continue
                    
                nombre = row['Nombre']
                
                precio_limpio = limpiar_precio(row['Precio'])
                
                stock_envio = float(row['StockEnvio'])
                unidad_medida = str(row['UnidadMedida']).strip()

                producto = Producto.query.filter_by(SKU=sku_excel).first()

                if producto:
                    if precio_limpio is not None:
                        producto.PrecioUnitario = precio_limpio
                    
                    producto.UnidadMedida = unidad_medida
                    producto_id = producto.ProductoID
                else:
                    precio_final = precio_limpio if precio_limpio is not None else 0.00
                    
                    nuevo_producto = Producto(
                        Nombre=nombre,
                        PrecioUnitario=precio_final,
                        SKU=sku_excel,
                        ProveedorID=proveedor_id,
                        UnidadMedida=unidad_medida,
                        FechaCreacion=datetime.now()
                    )
                    db.session.add(nuevo_producto)
                    db.session.flush()
                    producto_id = nuevo_producto.ProductoID

                movimiento = MovimientosInventario(
                    Fecha=datetime.now(), 
                    ProductoID=producto_id,
                    Cantidad=stock_envio,
                    TipoMovimiento='Entrada', 
                    ProveedorID=proveedor_id,
                    CargaID=nueva_carga.CargaID,
                    Referencia=f"Carga: {file.filename}",
                    Usuario='Admin'
                )
                db.session.add(movimiento)

            db.session.commit()
            flash('Carga masiva procesada exitosamente.', 'success')
            return redirect(url_for('productos.lista'))

        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al procesar el Excel: {str(e)}", "danger")
            return redirect(request.url)

    return render_template('productos/carga_masiva.html', proveedores=proveedores)