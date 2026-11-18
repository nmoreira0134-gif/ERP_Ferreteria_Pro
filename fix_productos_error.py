from pathlib import Path

p = Path("routes/productos.py")
if not p.exists():
    print("❌ No se encontró routes/productos.py")
    exit(1)

content = p.read_text(encoding="utf-8")

# El error quedó así (12 espacios en traceback, 8 en proveedores)
bad_block = """    except Exception:
            traceback.print_exc()
        proveedores = []"""

# Lo correcto es (8 espacios en ambos)
good_block = """    except Exception:
        traceback.print_exc()
        proveedores = []"""

if bad_block in content:
    content = content.replace(bad_block, good_block)
    p.write_text(content, encoding="utf-8")
    print("✅ Indentación corregida en routes/productos.py")
else:
    print("⚠️ No se encontró el bloque exacto. Revisa manualmente.")