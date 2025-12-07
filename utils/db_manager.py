import sqlite3
from config import DB_NAME, TABLE_NAME, TABLE_CATEGORIAS
from utils.helpers import imprimir_error

def conectar_db():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    """Inicializa la base de datos con las tablas necesarias"""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            
            # Tabla de productos
            sql_productos = f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                categoria TEXT
            )
            '''
            cursor.execute(sql_productos)
            
            # Tabla de categorías
            sql_categorias = f'''
            CREATE TABLE IF NOT EXISTS {TABLE_CATEGORIAS} (
                categoria TEXT PRIMARY KEY,
                mean REAL NOT NULL,
                min_price REAL NOT NULL,
                max_price REAL NOT NULL,
                stock_global INTEGER NOT NULL,
                demanda_semanal INTEGER NOT NULL,
                stock_de_proteccion INTEGER NOT NULL,
                status_stock TEXT NOT NULL
            )
            '''
            cursor.execute(sql_categorias)
            
            conn.commit()
            print("✓ Tablas inicializadas correctamente")
    except sqlite3.Error as e:
        imprimir_error(f"Error al inicializar la BD: {e}")

# ========================================
# FUNCIONES PARA PRODUCTOS
# ========================================

def registrar_producto(nombre, descripcion, cantidad, precio, categoria):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            # Normalizar categoría a mayúsculas
            categoria_upper = categoria.strip().upper() if categoria else None
            cursor.execute(f"INSERT INTO {TABLE_NAME} (nombre, descripcion, cantidad, precio, categoria) VALUES (?, ?, ?, ?, ?)",
                           (nombre, descripcion, cantidad, precio, categoria_upper))
            conn.commit()
            return True
    except sqlite3.Error as e:
        imprimir_error(f"Error al registrar: {e}")
        return False

def obtener_productos():
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")
            return cursor.fetchall()
    except sqlite3.Error as e:
        imprimir_error(f"Error al leer datos: {e}")
        return []

def buscar_producto_id(id_prod):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (id_prod,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        imprimir_error(f"Error al buscar: {e}")
        return None

def buscar_producto_texto(termino):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            # Normalizar término de búsqueda a mayúsculas
            termino_upper = termino.strip().upper()
            query = f"SELECT * FROM {TABLE_NAME} WHERE UPPER(nombre) LIKE ? OR UPPER(categoria) LIKE ?"
            cursor.execute(query, (f'%{termino_upper}%', f'%{termino_upper}%'))
            return cursor.fetchall()
    except sqlite3.Error as e:
        imprimir_error(f"Error al buscar: {e}")
        return []

def actualizar_producto(id_prod, nombre, descripcion, cantidad, precio, categoria):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            # Normalizar categoría a mayúsculas
            categoria_upper = categoria.strip().upper() if categoria else None
            sql = f'''UPDATE {TABLE_NAME} SET 
                      nombre=?, descripcion=?, cantidad=?, precio=?, categoria=? 
                      WHERE id=?'''
            cursor.execute(sql, (nombre, descripcion, cantidad, precio, categoria_upper, id_prod))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al actualizar: {e}")
        return False

def eliminar_producto(id_prod):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (id_prod,))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al eliminar: {e}")
        return False

def reporte_bajo_stock(limite):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE cantidad <= ?", (limite,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        imprimir_error(f"Error en reporte: {e}")
        return []

# ========================================
# FUNCIONES PARA CATEGORÍAS
# ========================================

def registrar_categoria(categoria, mean, min_price, max_price, stock_global, demanda_semanal, status_stock):
    """Registra o actualiza una categoría en la BD. Normaliza a mayúsculas."""
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = categoria.strip().upper()
        
        # Calcular stock de protección como 20% de la demanda semanal
        stock_proteccion = int(demanda_semanal * 0.2)
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            sql = f'''INSERT OR REPLACE INTO {TABLE_CATEGORIAS} 
                     (categoria, mean, min_price, max_price, stock_global, demanda_semanal, stock_de_proteccion, status_stock) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            cursor.execute(sql, (categoria_upper, mean, min_price, max_price, stock_global, demanda_semanal, stock_proteccion, status_stock))
            conn.commit()
            return True
    except sqlite3.Error as e:
        imprimir_error(f"Error al registrar categoría: {e}")
        return False

def obtener_categorias():
    """Obtiene todas las categorías"""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_CATEGORIAS}")
            return cursor.fetchall()
    except sqlite3.Error as e:
        imprimir_error(f"Error al leer categorías: {e}")
        return []

def buscar_categoria(nombre_categoria):
    """Busca una categoría específica. Búsqueda case-insensitive."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            # Normalizar a mayúsculas para búsqueda
            categoria_upper = nombre_categoria.strip().upper()
            cursor.execute(f"SELECT * FROM {TABLE_CATEGORIAS} WHERE categoria = ?", (categoria_upper,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        imprimir_error(f"Error al buscar categoría: {e}")
        return None

def actualizar_categoria(categoria, mean, min_price, max_price, stock_global, demanda_semanal, status_stock):
    """Actualiza los datos de una categoría. Normaliza a mayúsculas."""
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = categoria.strip().upper()
        
        # Recalcular stock de protección como 20% de la demanda semanal
        stock_proteccion = int(demanda_semanal * 0.2)
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            sql = f'''UPDATE {TABLE_CATEGORIAS} SET 
                     mean=?, min_price=?, max_price=?, stock_global=?, 
                     demanda_semanal=?, stock_de_proteccion=?, status_stock=? 
                     WHERE categoria=?'''
            cursor.execute(sql, (mean, min_price, max_price, stock_global, demanda_semanal, stock_proteccion, status_stock, categoria_upper))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al actualizar categoría: {e}")
        return False

def actualizar_status_categoria(nombre_categoria, nuevo_status):
    """Actualiza solo el status de una categoría (para llamar desde el main). Normaliza a mayúsculas."""
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = nombre_categoria.strip().upper()
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {TABLE_CATEGORIAS} SET status_stock=? WHERE categoria=?", (nuevo_status, categoria_upper))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al actualizar status: {e}")
        return False

def eliminar_categoria(nombre_categoria):
    """Elimina una categoría. Normaliza a mayúsculas."""
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = nombre_categoria.strip().upper()
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {TABLE_CATEGORIAS} WHERE categoria = ?", (categoria_upper,))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al eliminar categoría: {e}")
        return False

def calcular_estadisticas_categoria(nombre_categoria):
    """Calcula estadísticas automáticas para una categoría basándose en sus productos. Búsqueda case-insensitive."""
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = nombre_categoria.strip().upper()
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            
            # Obtener estadísticas de productos de esta categoría
            sql = f'''SELECT 
                     AVG(precio) as mean,
                     MIN(precio) as min_price,
                     MAX(precio) as max_price,
                     SUM(cantidad) as stock_global
                     FROM {TABLE_NAME}
                     WHERE categoria = ?'''
            
            cursor.execute(sql, (categoria_upper,))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] is not None:
                mean, min_price, max_price, stock_global = resultado
                return {
                    'mean': round(mean, 2),
                    'min_price': min_price,
                    'max_price': max_price,
                    'stock_global': stock_global or 0
                }
            return None
    except sqlite3.Error as e:
        imprimir_error(f"Error al calcular estadísticas: {e}")
        return None

def determinar_status_stock(stock_global, stock_proteccion, demanda_semanal):
    """
    Determina el status del stock según la lógica:
    - BAJO STOCK: stock_global == 0 O stock_global <= stock_proteccion (20% de demanda semanal)
    - STOCK NORMAL: stock_proteccion < stock_global <= demanda_semanal
    - EXCESO DE STOCK: stock_global > demanda_semanal
    """
 
    
    if stock_global == 0 or stock_global <= stock_proteccion:
       
        return "BAJO STOCK"
    elif stock_global <= demanda_semanal:
        
        return "STOCK NORMAL"
    else:
        
        return "EXCESO DE STOCK"

def actualizar_stock_categoria(nombre_categoria, nuevo_stock_global):
    """
    Actualiza el stock global de una categoría y recalcula automáticamente su status.
    Usar esta función después de ventas o compras. Normaliza a mayúsculas.
    """
    try:
        # Normalizar categoría a mayúsculas
        categoria_upper = nombre_categoria.strip().upper()
        
        # Obtener datos actuales de la categoría
        categoria_actual = buscar_categoria(categoria_upper)
        if not categoria_actual:
            return False
        
        # categoria_actual es una tupla: (categoria, mean, min_price, max_price, stock_global, demanda_semanal, stock_proteccion, status_stock)
        demanda_semanal = categoria_actual[5]
        stock_proteccion = int(demanda_semanal * 0.2)
        
        # Determinar nuevo status
        nuevo_status = determinar_status_stock(nuevo_stock_global, stock_proteccion, demanda_semanal)
        
        # Actualizar en la BD
        with conectar_db() as conn:
            cursor = conn.cursor()
            sql = f'''UPDATE {TABLE_CATEGORIAS} SET 
                     stock_global=?, stock_de_proteccion=?, status_stock=? 
                     WHERE categoria=?'''
            cursor.execute(sql, (nuevo_stock_global, stock_proteccion, nuevo_status, categoria_upper))
            if cursor.rowcount > 0:
                conn.commit()
                return True
            return False
    except sqlite3.Error as e:
        imprimir_error(f"Error al actualizar stock de categoría: {e}")
        return False

def actualizar_estadisticas_todas_categorias(demanda_semanal_default=1):
    """
    Actualiza automáticamente las estadísticas de todas las categorías.
    Calcula el status según la lógica definida.
    """
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            
            # Obtener TODAS las categorías registradas (no solo las que tienen productos)
            cursor.execute(f"SELECT categoria, demanda_semanal FROM {TABLE_CATEGORIAS}")
            todas_categorias = cursor.fetchall()
            
            for cat_info in todas_categorias:
                cat = cat_info[0]
                demanda_semanal = cat_info[1]
                
                stats = calcular_estadisticas_categoria(cat)
                
                if stats and stats['stock_global'] > 0:
                    # Categoría con productos
                    stock_proteccion = int(demanda_semanal * 0.2)
                    status = determinar_status_stock(stats['stock_global'], stock_proteccion, demanda_semanal)
                    
                    registrar_categoria(
                        categoria=cat,
                        mean=stats['mean'],
                        min_price=stats['min_price'],
                        max_price=stats['max_price'],
                        stock_global=stats['stock_global'],
                        demanda_semanal=demanda_semanal,
                        status_stock=status
                    )
                else:
                    # Categoría sin productos o con stock = 0
                    stock_proteccion = int(demanda_semanal_default * 0.2)
                    status = "BAJO STOCK"  # Sin productos = crítico
                    
                    registrar_categoria(
                        categoria=cat,
                        mean=0.0,
                        min_price=0.0,
                        max_price=0.0,
                        stock_global=0,
                        demanda_semanal=demanda_semanal_default,
                        status_stock=status
                    )
            
            print(f"✓ Estadísticas actualizadas para {len(todas_categorias)} categorías")
            return True
    except sqlite3.Error as e:
        imprimir_error(f"Error al actualizar estadísticas: {e}")
        return False