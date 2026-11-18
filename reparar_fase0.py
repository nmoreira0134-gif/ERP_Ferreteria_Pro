#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reparar_fase0.py — ERP_Ferreteria_Pro
Aplica reparaciones de FASE 0 (estabilización).
- Idempotente: re-ejecutable sin duplicar cambios.
- Backups: *.bak.YYYYMMDD_HHMMSS
- Uso: python reparar_fase0.py
"""
import os, re, shutil, secrets
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).parent.resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
STATS = {"aplicado":0,"saltado":0,"manual":0,"error":0}

def log(msg, tipo="INFO"):
    p = {"INFO":"·","OK":"✅","SKIP":"⏭️ ","WARN":"⚠️ ","ERR":"❌"}.get(tipo,"·")
    print(f"{p} {msg}")

def leer(p): return p.read_text(encoding="utf-8") if p.exists() else None
def escribir(p, contenido):
    if p.exists(): shutil.copy2(p, p.with_name(p.name + f".bak.{TS}"))
    p.write_text(contenido, encoding="utf-8")

# ---------- FIX-01 .gitignore ----------
def fix_gitignore():
    p = RAIZ/".gitignore"
    bloques = ["venv/","__pycache__/","*.pyc","*.pyo","*.bak","*.bak.*",
               "*.zip","*.rar",".env",".env.*","!.env.example","*.log",
               ".vscode/",".idea/"]
    contenido = leer(p) or ""
    faltan = [b for b in bloques if b not in contenido]
    if not faltan:
        log(".gitignore ya completo","SKIP"); STATS["saltado"]+=1; return
    escribir(p, contenido + "\n# Añadido por reparar_fase0.py\n" + "\n".join(faltan) + "\n")
    log(f".gitignore: {len(faltan)} patrones añadidos","OK"); STATS["aplicado"]+=1

# ---------- FIX-02 .env ----------
def fix_env():
    p = RAIZ/".env"
    if p.exists():
        log(".env ya existe","SKIP"); STATS["saltado"]+=1; return
    p.write_text(
        "# Generado por reparar_fase0.py — NO COMMITEAR\n"
        f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
        "FLASK_DEBUG=false\n"
        "DB_SERVER=localhost\n"
        "DB_DATABASE=FerreteriaDB\n", encoding="utf-8")
    log(".env creado con SECRET_KEY aleatoria","OK"); STATS["aplicado"]+=1

# ---------- FIX-03 app.py ----------
def fix_app():
    p = RAIZ/"app.py"; contenido = leer(p)
    if contenido is None:
        log("app.py no existe","ERR"); STATS["error"]+=1; return
    nuevo = contenido
    if "from dotenv import load_dotenv" not in nuevo:
        nuevo = nuevo.replace(
            "from flask import Flask",
            "import os\nimport traceback\nfrom flask import Flask\nfrom dotenv import load_dotenv\n\nload_dotenv()", 1)
        log("app.py: load_dotenv añadido","OK"); STATS["aplicado"]+=1
    else:
        log("app.py: load_dotenv ya presente","SKIP"); STATS["saltado"]+=1
    if "ODBC+Driver+17" in nuevo:
        nuevo = nuevo.replace("ODBC+Driver+17","ODBC+Driver+18")
        log("app.py: driver 17→18","OK"); STATS["aplicado"]+=1
    else:
        log("app.py: driver ya unificado","SKIP"); STATS["saltado"]+=1
    if "'mambo_erp_secret_key'" in nuevo:
        nuevo = nuevo.replace("'mambo_erp_secret_key'","os.getenv('SECRET_KEY','dev-insecure-key')")
        log("app.py: SECRET_KEY → env","OK"); STATS["aplicado"]+=1
    else:
        log("app.py: SECRET_KEY ya de env","SKIP"); STATS["saltado"]+=1
    if "traceback.print_exc()" not in contenido:
        viejo = "    except Exception as e:\n        print(f\"❌ ERROR al registrar"
        nuevo_exc = "    except Exception as e:\n        traceback.print_exc()\n        print(f\"❌ ERROR al registrar"
        if viejo in nuevo:
            nuevo = nuevo.replace(viejo, nuevo_exc, 1)
            log("app.py: traceback en registrar_modulo","OK"); STATS["aplicado"]+=1
        else:
            log("app.py: patrón except no encontrado","WARN"); STATS["manual"]+=1
    else:
        log("app.py: traceback ya presente","SKIP"); STATS["saltado"]+=1
    if "registrar_modulo('usuarios'" not in nuevo and "registrar_modulo('puestos', 'bp_puestos')" in nuevo:
        nuevo = nuevo.replace(
            "registrar_modulo('puestos', 'bp_puestos')",
            "registrar_modulo('puestos', 'bp_puestos')\nregistrar_modulo('usuarios', 'bp_usuarios')", 1)
        log("app.py: usuarios registrado","OK"); STATS["aplicado"]+=1
    elif "registrar_modulo('usuarios'" in nuevo:
        log("app.py: usuarios ya registrado","SKIP"); STATS["saltado"]+=1
    if "app.run(debug=True)" in nuevo:
        nuevo = nuevo.replace("app.run(debug=True)",
            "app.run(debug=os.getenv('FLASK_DEBUG','false').lower()=='true')")
        log("app.py: debug condicional","OK"); STATS["aplicado"]+=1
    else:
        log("app.py: debug ya condicional","SKIP"); STATS["saltado"]+=1
    if nuevo != contenido: escribir(p, nuevo)

# ---------- FIX-04 config.py ----------
def fix_config():
    p = RAIZ/"config.py"; contenido = leer(p)
    if contenido is None:
        log("config.py no existe","ERR"); STATS["error"]+=1; return
    if "os.getenv('SECRET_KEY'" in contenido:
        log("config.py: SECRET_KEY ya de env","SKIP"); STATS["saltado"]+=1; return
    if "SECRET_KEY = 'clave-secreta-para-desarrollo-local'" not in contenido:
        log("config.py: patrón no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, "import os\n\n" + contenido.replace(
        "SECRET_KEY = 'clave-secreta-para-desarrollo-local'",
        "SECRET_KEY = os.getenv('SECRET_KEY','dev-insecure-key')"))
    log("config.py: SECRET_KEY → env","OK"); STATS["aplicado"]+=1

# ---------- FIX-05 models/__init__.py ----------
def fix_models_init():
    p = RAIZ/"models"/"__init__.py"; contenido = leer(p)
    if contenido is None:
        log("models/__init__.py no existe","ERR"); STATS["error"]+=1; return
    if "from .correlativo import Correlativo" in contenido:
        log("models/__init__.py: Correlativo ya importado","SKIP"); STATS["saltado"]+=1; return
    if "# from .correlativo import Correlativo" not in contenido:
        log("models/__init__.py: patrón no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, contenido.replace(
        "# from .correlativo import Correlativo # Descomenta si lo tienes",
        "from .correlativo import Correlativo"))
    log("models/__init__.py: Correlativo importado","OK"); STATS["aplicado"]+=1

# ---------- FIX-06 configuracion.py traceback ----------
def fix_configuracion_traceback():
    p = RAIZ/"models"/"configuracion.py"; contenido = leer(p)
    if contenido is None:
        log("models/configuracion.py no existe","ERR"); STATS["error"]+=1; return
    if "traceback.print_exc()" in contenido:
        log("configuracion.py: traceback ya presente","SKIP"); STATS["saltado"]+=1; return
    if "import traceback" not in contenido:
        contenido = "import traceback\n" + contenido
    viejo = "        except Exception:\n            conn.rollback()\n            raise"
    nuevo_exc = "        except Exception:\n            traceback.print_exc()\n            conn.rollback()\n            raise"
    if viejo not in contenido:
        log("configuracion.py: patrón except no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, contenido.replace(viejo, nuevo_exc))
    log("configuracion.py: traceback añadido","OK"); STATS["aplicado"]+=1

# ---------- FIX-07 gastos.Fecha Date ----------
def fix_gastos_fecha():
    p = RAIZ/"models"/"gastos.py"; contenido = leer(p)
    if contenido is None:
        log("models/gastos.py no existe","ERR"); STATS["error"]+=1; return
    if "Fecha = db.Column(db.Date" in contenido:
        log("gastos.py: Fecha ya es Date","SKIP"); STATS["saltado"]+=1; return
    if "Fecha = db.Column(db.DateTime, default=datetime.now)" not in contenido:
        log("gastos.py: patrón no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, contenido.replace(
        "Fecha = db.Column(db.DateTime, default=datetime.now)",
        "Fecha = db.Column(db.Date, default=lambda: datetime.now().date())"))
    log("gastos.py: Fecha DateTime→Date","OK"); STATS["aplicado"]+=1

# ---------- FIX-08 productos except desnudos ----------
def fix_productos_except():
    p = RAIZ/"routes"/"productos.py"; contenido = leer(p)
    if contenido is None:
        log("routes/productos.py no existe","ERR"); STATS["error"]+=1; return
    nuevo, n = re.subn(r"except:\s*\n(\s*)",
        r"except Exception:\n\1    traceback.print_exc()\n\1", contenido)
    if n == 0:
        log("productos.py: sin except desnudos","SKIP"); STATS["saltado"]+=1; return
    escribir(p, nuevo)
    log(f"productos.py: {n} except desnudos corregidos","OK"); STATS["aplicado"]+=1

# ---------- FIX-09 usuarios url_prefix + traceback ----------
def fix_usuarios():
    p = RAIZ/"routes"/"usuarios.py"; contenido = leer(p)
    if contenido is None:
        log("routes/usuarios.py no existe","ERR"); STATS["error"]+=1; return
    nuevo = contenido
    if "url_prefix='/usuarios'" not in nuevo:
        if "Blueprint('usuarios', __name__)" in nuevo:
            nuevo = nuevo.replace(
                "Blueprint('usuarios', __name__)",
                "Blueprint('usuarios', __name__, url_prefix='/usuarios')", 1)
            log("usuarios.py: url_prefix añadido","OK"); STATS["aplicado"]+=1
    else:
        log("usuarios.py: url_prefix ya presente","SKIP"); STATS["saltado"]+=1
    if "traceback.print_exc()" not in contenido:
        if "import traceback" not in nuevo:
            nuevo = "import traceback\n" + nuevo
        viejo = "    except Exception as e:\n        return f\"Error en la base de datos: {e}\""
        nuevo_exc = "    except Exception as e:\n        traceback.print_exc()\n        return f\"Error en la base de datos: {e}\""
        if viejo in nuevo:
            nuevo = nuevo.replace(viejo, nuevo_exc, 1)
            log("usuarios.py: traceback añadido","OK"); STATS["aplicado"]+=1
    else:
        log("usuarios.py: traceback ya presente","SKIP"); STATS["saltado"]+=1
    if nuevo != contenido: escribir(p, nuevo)

# ---------- FIX-10 facturacion detalle ----------
def fix_facturacion_detalle():
    p = RAIZ/"routes"/"facturacion.py"; contenido = leer(p)
    if contenido is None:
        log("routes/facturacion.py no existe","ERR"); STATS["error"]+=1; return
    nuevo = contenido
    if "INNER JOIN Clientes c ON f.ClienteID = c.ClienteID" in nuevo:
        nuevo = nuevo.replace(
            "INNER JOIN Clientes c ON f.ClienteID = c.ClienteID",
            "LEFT JOIN Clientes c ON f.ClienteID = c.ClienteID", 1)
        log("facturacion.py: INNER→LEFT JOIN clientes","OK"); STATS["aplicado"]+=1
    else:
        log("facturacion.py: JOIN ya LEFT","SKIP"); STATS["saltado"]+=1
    marca = "        factura = cursor.fetchone()\n"
    if marca in nuevo and "if not factura:" not in nuevo and "if factura is None:" not in nuevo:
        nuevo = nuevo.replace(marca, marca +
            "        if not factura:\n            flash('Factura no encontrada.', 'error')\n            return redirect(url_for('facturacion.lista'))\n", 1)
        log("facturacion.py: factura None manejado","OK"); STATS["aplicado"]+=1
    else:
        log("facturacion.py: factura None ya manejado","SKIP"); STATS["saltado"]+=1
    if nuevo != contenido: escribir(p, nuevo)

# ---------- FIX-11 base.html flash ----------
def fix_base_flash():
    p = RAIZ/"templates"/"base.html"; contenido = leer(p)
    if contenido is None:
        log("base.html no existe","ERR"); STATS["error"]+=1; return
    if "get_flashed_messages" in contenido:
        log("base.html: flash ya presente","SKIP"); STATS["saltado"]+=1; return
    original = '''    <main class="container mx-auto p-6 mt-4">
        {% block content %}
        {% endblock %}
    </main>'''
    bloque = '''    <main class="container mx-auto p-6 mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-3 rounded {{ 'bg-green-100 text-green-800' if category == 'success' else 'bg-red-100 text-red-800' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}
        {% endblock %}
    </main>'''
    if original not in contenido:
        log("base.html: patrón <main> no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, contenido.replace(original, bloque, 1))
    log("base.html: flash block añadido","OK"); STATS["aplicado"]+=1

# ---------- FIX-12 productos/list $ → C$ ----------
def fix_productos_precio():
    p = RAIZ/"templates"/"productos"/"list.html"; contenido = leer(p)
    if contenido is None:
        log("productos/list.html no existe","ERR"); STATS["error"]+=1; return
    if 'C$ {{ "%.2f"|format(producto.PrecioUnitario) }}' in contenido:
        log("productos/list.html: ya es C$","SKIP"); STATS["saltado"]+=1; return
    viejo = '<td class="py-3 px-6 text-left">${{ producto.PrecioUnitario }}</td>'
    nuevo_html = '<td class="py-3 px-6 text-left">C$ {{ "%.2f"|format(producto.PrecioUnitario) }}</td>'
    if viejo not in contenido:
        log("productos/list.html: patrón $ no encontrado","WARN"); STATS["manual"]+=1; return
    escribir(p, contenido.replace(viejo, nuevo_html, 1))
    log("productos/list.html: $ → C$","OK"); STATS["aplicado"]+=1

# ---------- FIX-13 facturacion/form IDs duplicados ----------
def fix_facturacion_js():
    p = RAIZ/"templates"/"facturacion"/"form.html"; contenido = leer(p)
    if contenido is None:
        log("facturacion/form.html no existe","ERR"); STATS["error"]+=1; return
    if 'class="precio-visual"' in contenido:
        log("facturacion/form.html: ya usa clases","SKIP"); STATS["saltado"]+=1; return
    nuevo = contenido
    nuevo = nuevo.replace('id="precio-visual"','class="precio-visual"')
    nuevo = nuevo.replace('id="subtotal-visual"','class="subtotal-visual"')
    nuevo = nuevo.replace("fila.querySelector('#precio-visual')","fila.querySelector('.precio-visual')")
    nuevo = nuevo.replace("fila.querySelector('#subtotal-visual')","fila.querySelector('.subtotal-visual')")
    if nuevo == contenido:
        log("facturacion/form.html: patrones id no encontrados","WARN"); STATS["manual"]+=1; return
    escribir(p, nuevo)
    log("facturacion/form.html: IDs→clases en JS","OK"); STATS["aplicado"]+=1

# ---------- FIX-14 requirements.txt + python-dotenv ----------
def fix_requirements():
    p = RAIZ/"requirements.txt"
    if not p.exists():
        log("requirements.txt NO EXISTE — ejecuta: git checkout -- requirements.txt","WARN")
        STATS["manual"]+=1; return
    contenido = p.read_text(encoding="utf-8")
    if "python-dotenv" in contenido:
        log("requirements.txt: python-dotenv ya presente","SKIP"); STATS["saltado"]+=1; return
    escribir(p, contenido.rstrip() + "\npython-dotenv==1.0.1\n")
    log("requirements.txt: python-dotenv añadido","OK"); STATS["aplicado"]+=1

# ---------- MAIN ----------
def main():
    print(f"\n🔧 Reparaciones FASE 0 — ERP_Ferreteria_Pro")
    print(f"   Ruta: {RAIZ}")
    print(f"   Timestamp: {TS}\n")
    for nombre, fn in [
        (".gitignore", fix_gitignore),
        (".env", fix_env),
        ("app.py", fix_app),
        ("config.py", fix_config),
        ("models/__init__.py", fix_models_init),
        ("models/configuracion.py", fix_configuracion_traceback),
        ("models/gastos.py", fix_gastos_fecha),
        ("routes/productos.py", fix_productos_except),
        ("routes/usuarios.py", fix_usuarios),
        ("routes/facturacion.py", fix_facturacion_detalle),
        ("templates/base.html", fix_base_flash),
        ("templates/productos/list.html", fix_productos_precio),
        ("templates/facturacion/form.html", fix_facturacion_js),
        ("requirements.txt", fix_requirements),
    ]:
        try: fn()
        except Exception as e:
            log(f"{nombre}: EXCEPCIÓN {e}","ERR"); STATS["error"]+=1
    print(f"\n📊 Resumen: {STATS['aplicado']} aplicados, {STATS['saltado']} saltados, "
          f"{STATS['manual']} manuales, {STATS['error']} errores\n")
    print("🔎 Verifica con:  git diff --stat")
    print("🚀 Levanta con:   flask run --debug\n")

if __name__ == "__main__":
    main()