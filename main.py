from utils.helpers import (
    imprimir_titulo, imprimir_exito, imprimir_error,
    validar_input_string, validar_input_float, validar_input_int, validar_descripcion,
    validar_categoria_con_reintento, listar_categorias_disponibles
)
from utils import db_manager
import sys

# FUNCIONES AUXILIARES

def mostrar_tabla_productos(productos):
    """Muestra los productos"""
    if not productos:
        print("No se encontraron productos.")
        return

    print(f"\n{'ID':<5} {'NOMBRE':<20} {'CATEGORIA':<15} {'PRECIO':<10} {'CANTIDAD':<10}")
    print("-" * 70)
    for prod in productos:
        print(f"{prod[0]:<5} {prod[1][:18]:<20} {prod[5][:13]:<15} ${prod[4]:<9.2f} {prod[3]:<10}")
    print("-" * 70)

def mostrar_tabla_categorias(categorias):
    """Muestra las categorías"""
    if not categorias:
        print("No se encontraron categorías.")
        return
    
    print(f"\n{'CATEGORÍA':<20} {'STOCK':<10} {'DEMANDA/SEM':<15} {'PROTECCIÓN':<12} {'STATUS':<20}")
    print("-" * 85)
    for cat in categorias:
        # cat: (categoria, mean, min_price, max_price, stock_global, demanda_semanal, stock_proteccion, status_stock)
        nombre = cat[0]
        stock = cat[4]
        demanda = cat[5]
        proteccion = cat[6]
        status = cat[7]
        print(f"{nombre[:18]:<20} {stock:<10} {demanda:<15} {proteccion:<12} {status:<20}")
    print("-" * 85)

def actualizar_stats_categoria(categoria_nombre):
    """Actualiza las estadísticas de una categoría después de modificar productos"""
    stats = db_manager.calcular_estadisticas_categoria(categoria_nombre)
    if stats:
        db_manager.actualizar_stock_categoria(categoria_nombre, stats['stock_global'])

# ========================================
# MENÚ DE PRODUCTOS
# ========================================

def menu_registrar_producto():
    """Registra un nuevo producto con validación de categoría"""
    imprimir_titulo("Registrar Nuevo Producto")
    
    nombre = validar_input_string("Nombre")
    desc = validar_descripcion("Descripción (opcional)").strip()
    
    # Mostrar categorías disponibles
    print("\nCategorías registradas:")
    listar_categorias_disponibles()
    
    # Bucle para validar o crear categoría
    while True:
        categ = input("Categoría (o escriba 'salir' para cancelar): ").strip().upper()
        
        if categ.lower() == 'salir':
            imprimir_error("Registro de producto cancelado.")
            return
        
        if not categ:
            imprimir_error("Debe ingresar una categoría.")
            continue
        
        # Verificar si existe la categoría
        if db_manager.buscar_categoria(categ):
            break  # Categoría válida, continuar
        else:
            # Categoría no existe - preguntar si quiere crearla
            imprimir_error(f"La categoría '{categ}' no existe.")
            crear = input("¿Desea crear esta categoría ahora? (s/n): ").lower()
            
            if crear == 's':
                # Crear la categoría
                demanda_semanal = validar_input_int("Demanda semanal estimada para esta categoría")
                
                # Determinar el status correcto para stock inicial = 0
                stock_proteccion = int(demanda_semanal * 0.2)
                status_inicial = "BAJO STOCK"  # Stock 0 siempre es bajo
                
                if db_manager.registrar_categoria(categ, 0.0, 0.0, 0.0, 0, demanda_semanal, status_inicial):
                    imprimir_exito(f"Categoría '{categ}' creada correctamente.")
                    print(f"Stock de protección: {stock_proteccion} unidades")
                    break  # Categoría creada, continuar con el producto
                else:
                    imprimir_error("No se pudo crear la categoría. Intente nuevamente.")
            else:
                print("Por favor, seleccione una categoría existente o escriba 'salir'.")
                listar_categorias_disponibles()
    
    # Continuar con el registro del producto
    cantidad = validar_input_int("Cantidad inicial")
    precio = validar_input_float("Precio unitario")
    
    if db_manager.registrar_producto(nombre, desc, cantidad, precio, categ):
        imprimir_exito("Producto registrado correctamente.")
        # Actualizar estadísticas de la categoría
        actualizar_stats_categoria(categ)
    else:
        imprimir_error("No se pudo registrar el producto.")

def menu_mostrar_productos():
    """Muestra todos los productos"""
    imprimir_titulo("Listado de Productos")
    productos = db_manager.obtener_productos()
    mostrar_tabla_productos(productos)

def menu_actualizar_producto():
    """Actualiza un producto existente"""
    imprimir_titulo("Actualizar Producto")
    menu_mostrar_productos()
    id_prod = validar_input_int("Ingrese el ID del producto a modificar")
    
    producto_actual = db_manager.buscar_producto_id(id_prod)
    if not producto_actual:
        imprimir_error("Producto no encontrado.")
        return

    print(f"\nEditando: {producto_actual[1]}")
    print("Deje vacío si no desea modificar el campo.")
    
    nuevo_nombre = input(f"Nombre [{producto_actual[1]}]: ").strip() or producto_actual[1]
    nueva_desc = input(f"Descripción [{producto_actual[2]}]: ").strip() or producto_actual[2]
    
    # Validar categoría si el usuario quiere cambiarla
    categoria_actual = producto_actual[5]
    print(f"\nCategoría actual: {categoria_actual}")
    cambiar_cat = input("¿Desea cambiar la categoría? (s/n): ").lower()
    
    if cambiar_cat == 's':
        listar_categorias_disponibles()
        nueva_cat = validar_categoria_con_reintento("Nueva categoría")
    else:
        nueva_cat = categoria_actual
    
    cant_str = input(f"Cantidad [{producto_actual[3]}]: ").strip()
    nuevo_cant = int(cant_str) if cant_str.isdigit() else producto_actual[3]
    
    precio_str = input(f"Precio [{producto_actual[4]}]: ").strip()
    nuevo_precio = float(precio_str) if precio_str else producto_actual[4]

    if db_manager.actualizar_producto(id_prod, nuevo_nombre, nueva_desc, nuevo_cant, nuevo_precio, nueva_cat):
        imprimir_exito("Producto actualizado.")
        # Actualizar estadísticas de ambas categorías si cambió
        if categoria_actual != nueva_cat:
            actualizar_stats_categoria(categoria_actual)
        actualizar_stats_categoria(nueva_cat)
    else:
        imprimir_error("No se pudo actualizar.")

def menu_eliminar_producto():
    """Elimina un producto"""
    imprimir_titulo("Eliminar Producto")
    menu_mostrar_productos()

    id_prod = validar_input_int("ID del producto a eliminar")
    
    # Obtener el producto para saber su categoría
    producto = db_manager.buscar_producto_id(id_prod)
    if not producto:
        imprimir_error("Producto no encontrado.")
        return
    
    categoria = producto[5]
    
    confirm = input(f"¿Seguro que desea eliminar '{producto[1]}'? (s/n): ").lower()
    if confirm == 's':
        if db_manager.eliminar_producto(id_prod):
            imprimir_exito("Producto eliminado.")
            # Actualizar estadísticas de la categoría
            actualizar_stats_categoria(categoria)
        else:
            imprimir_error("No se pudo eliminar.")

def menu_buscar_producto():
    """Busca productos por ID o texto"""
    imprimir_titulo("Búsqueda de Productos")
    print("1. Buscar por ID")
    print("2. Buscar por Nombre o Categoría")
    opcion = input("Opción: ")
    
    if opcion == "1":
        id_prod = validar_input_int("ID")
        res = db_manager.buscar_producto_id(id_prod)
        if res:
            mostrar_tabla_productos([res])
        else:
            imprimir_error("No encontrado.")
    elif opcion == "2":
        termino = validar_input_string("Término de búsqueda")
        res = db_manager.buscar_producto_texto(termino)
        mostrar_tabla_productos(res)
    else:
        imprimir_error("Opción inválida.")

# ========================================
# MENÚ DE CATEGORÍAS
# ========================================

def menu_registrar_categoria():
    """Registra una nueva categoría"""
    imprimir_titulo("Registrar Nueva Categoría")
    
    nombre = validar_input_string("Nombre de la categoría").upper()
    
    # Verificar si ya existe
    if db_manager.buscar_categoria(nombre):
        imprimir_error(f"La categoría '{nombre}' ya existe.")
        return
    
    demanda_semanal = validar_input_int("Demanda semanal estimada")
    
    # Valores iniciales por defecto
    mean = 0.0
    min_price = 0.0
    max_price = 0.0
    stock_global = 0
    status_stock = "STOCK NORMAL"
    
    if db_manager.registrar_categoria(nombre, mean, min_price, max_price, stock_global, demanda_semanal, status_stock):
        imprimir_exito(f"Categoría '{nombre}' registrada correctamente.")
        stock_prot = int(demanda_semanal * 0.2)
        print(f"Stock de protección calculado: {stock_prot} unidades (20% de {demanda_semanal})")
    else:
        imprimir_error("No se pudo registrar la categoría.")

def menu_mostrar_categorias():
    """Muestra todas las categorías con sus estadísticas"""
    imprimir_titulo("Listado de Categorías")
    
    # Primero actualizar estadísticas automáticamente
    db_manager.actualizar_estadisticas_todas_categorias()
    
    categorias = db_manager.obtener_categorias()
    
    if not categorias:
        print("No hay categorías registradas.")
        return
    
    mostrar_tabla_categorias(categorias)
    
    # Mostrar detalles adicionales
    print("\nDetalle de precios:")
    for cat in categorias:
        nombre = cat[0]
        mean = cat[1]
        min_price = cat[2]
        max_price = cat[3]
        
        if mean > 0:  # Solo mostrar si hay datos
            print(f"  {nombre}: Precio promedio ${mean:.2f} | Rango: ${min_price:.2f} - ${max_price:.2f}")
        else:
            print(f"  {nombre}: Sin productos registrados aún")

def menu_actualizar_categoria():
    """Actualiza la demanda semanal de una categoría"""
    imprimir_titulo("Actualizar Categoría")
    
    listar_categorias_disponibles()
    
    nombre_input = input("Nombre de la categoría (o 'salir' para cancelar): ").strip().upper()
    
    if nombre_input.lower() == 'salir':
        imprimir_error("Actualización cancelada.")
        return
    
    if not nombre_input:
        imprimir_error("Debe ingresar una categoría.")
        return
    
    cat_actual = db_manager.buscar_categoria(nombre_input)
    if not cat_actual:
        imprimir_error("Categoría no encontrada.")
        return
    
    print(f"\nDemanda semanal actual: {cat_actual[5]}")
    demanda_input = input("Nueva demanda semanal (o Enter para cancelar): ").strip()
    
    if not demanda_input:
        imprimir_error("Actualización cancelada.")
        return
    
    try:
        nueva_demanda = int(demanda_input)
        if nueva_demanda < 0:
            imprimir_error("La demanda debe ser un número positivo.")
            return
    except ValueError:
        imprimir_error("Debe ingresar un número válido.")
        return
    
    # Mantener los otros valores
    if db_manager.actualizar_categoria(
        nombre_input, 
        cat_actual[1],  # mean
        cat_actual[2],  # min_price
        cat_actual[3],  # max_price
        cat_actual[4],  # stock_global
        nueva_demanda,  # demanda_semanal
        cat_actual[7]   # status_stock
    ):
        imprimir_exito("Categoría actualizada.")
        nuevo_stock_prot = int(nueva_demanda * 0.2)
        print(f"Nuevo stock de protección: {nuevo_stock_prot} unidades")
        # Recalcular status con nueva demanda
        actualizar_stats_categoria(nombre_input)
    else:
        imprimir_error("No se pudo actualizar.")

def menu_eliminar_categoria():
    """Elimina una categoría (solo si no tiene productos)"""
    imprimir_titulo("Eliminar Categoría")
    
    listar_categorias_disponibles()
    nombre = validar_categoria_con_reintento("Nombre de la categoría a eliminar")
    
    # Verificar si tiene productos asociados
    productos = db_manager.buscar_producto_texto(nombre)
    if productos:
        imprimir_error(f"No se puede eliminar '{nombre}' porque tiene {len(productos)} productos asociados.")
        print("Elimine primero los productos o cámbieles la categoría.")
        return
    
    confirm = input(f"¿Seguro que desea eliminar la categoría '{nombre}'? (s/n): ").lower()
    if confirm == 's':
        if db_manager.eliminar_categoria(nombre):
            imprimir_exito("Categoría eliminada.")
        else:
            imprimir_error("No se pudo eliminar.")

def menu_actualizar_estadisticas():
    """Actualiza automáticamente las estadísticas de todas las categorías"""
    imprimir_titulo("Actualizar Estadísticas de Categorías")
    
    print("Esta operación recalculará:")
    print("  • Stock global por categoría")
    print("  • Precios promedio, mínimo y máximo")
    print("  • Status de stock")
    
    confirm = input("\n¿Continuar? (s/n): ").lower()
    if confirm == 's':
        if db_manager.actualizar_estadisticas_todas_categorias():
            imprimir_exito("Estadísticas actualizadas correctamente.")
        else:
            imprimir_error("Hubo un error al actualizar.")

# ========================================
# MENÚ DE REPORTES
# ========================================

def menu_reporte_bajo_stock():
    """Reporte de productos cuya categoría está por debajo del stock de seguridad"""
    imprimir_titulo("Reporte de Productos con Bajo Stock")
    
    categorias = db_manager.obtener_categorias()
    if not categorias:
        print("No hay categorías registradas.")
        return
    
    # Filtrar categorías con bajo stock
    categorias_criticas = [cat for cat in categorias if cat[7] == "BAJO STOCK"]
    
    if not categorias_criticas:
        imprimir_exito("No hay categorías en estado crítico.")
        return
    
    print("\nCategorías con BAJO STOCK (por debajo del stock de seguridad):")
    for cat in categorias_criticas:
        print(f"  • {cat[0]} - Stock actual: {cat[4]} | Protección: {cat[6]}")
    
    # Obtener productos de esas categorías
    productos_bajo_stock = []
    for cat in categorias_criticas:
        prods = db_manager.buscar_producto_texto(cat[0])
        productos_bajo_stock.extend(prods)
    
    if productos_bajo_stock:
        print(f"\nTotal de productos en categorías críticas: {len(productos_bajo_stock)}")
        mostrar_tabla_productos(productos_bajo_stock)
    else:
        print("\nNo hay productos en estas categorías.")

def menu_reporte_categorias_criticas():
    """Reporte de categorías con bajo stock"""
    imprimir_titulo("Reporte de Categorías Críticas")
    
    categorias = db_manager.obtener_categorias()
    if not categorias:
        print("No hay categorías registradas.")
        return
    
    criticas = [cat for cat in categorias if cat[7] == "BAJO STOCK"]
    
    if criticas:
        imprimir_error(f"¡ALERTA! {len(criticas)} categorías con BAJO STOCK:")
        mostrar_tabla_categorias(criticas)
    else:
        imprimir_exito("No hay categorías en estado crítico.")
    
    # Mostrar también las normales
    normales = [cat for cat in categorias if cat[7] == "STOCK NORMAL"]
    if normales:
        print(f"\nCategorías con stock normal: {len(normales)}")
    
    exceso = [cat for cat in categorias if cat[7] == "EXCESO DE STOCK"]
    if exceso:
        print(f"Categorías con exceso de stock: {len(exceso)}")

def menu_reporte_por_categoria():
    """Muestra productos de una categoría específica"""
    imprimir_titulo("Productos por Categoría")
    
    listar_categorias_disponibles()
    nombre = validar_categoria_con_reintento("Categoría a consultar")
    
    productos = db_manager.buscar_producto_texto(nombre)
    
    if productos:
        print(f"\nProductos en categoría '{nombre}': {len(productos)}")
        mostrar_tabla_productos(productos)
        
        # Mostrar info de la categoría
        cat = db_manager.buscar_categoria(nombre)
        if cat:
            print(f"\nEstadísticas de '{nombre}':")
            print(f"  Stock total: {cat[4]} unidades")
            print(f"  Demanda semanal: {cat[5]} unidades")
            print(f"  Stock de protección: {cat[6]} unidades")
            print(f"  Status: {cat[7]}")
    else:
        print(f"No hay productos en la categoría '{nombre}'.")

def menu_dashboard():
    """Dashboard con resumen general"""
    imprimir_titulo("Dashboard - Resumen General")
    
    # Productos
    productos = db_manager.obtener_productos()
    total_productos = len(productos)
    
    # Categorías
    categorias = db_manager.obtener_categorias()
    total_categorias = len(categorias)
    
    print(f"\n📦 Total de productos: {total_productos}")
    print(f"📁 Total de categorías: {total_categorias}")
    
    if categorias:
        bajo_stock = sum(1 for cat in categorias if cat[7] == "BAJO STOCK")
        normal = sum(1 for cat in categorias if cat[7] == "STOCK NORMAL")
        exceso = sum(1 for cat in categorias if cat[7] == "EXCESO DE STOCK")
        
        print("\n📊 Estado de categorías:")
        print(f"  🔴 Bajo stock: {bajo_stock}")
        print(f"  🟢 Stock normal: {normal}")
        print(f"  🟡 Exceso de stock: {exceso}")
        
        if bajo_stock > 0:
            print(f"\n⚠️  ¡ATENCIÓN! Hay {bajo_stock} categorías con bajo stock")

# ========================================
# MENÚS PRINCIPALES
# ========================================

def menu_productos():
    """Submenú de gestión de productos"""
    while True:
        print("\n" + "="*40)
        print("   GESTIÓN DE PRODUCTOS")
        print("="*40)
        print("1. Registrar Producto")
        print("2. Mostrar Todos los Productos")
        print("3. Actualizar Producto")
        print("4. Eliminar Producto")
        print("5. Buscar Producto")
        print("6. Volver al Menú Principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            menu_registrar_producto()
        elif opcion == '2':
            menu_mostrar_productos()
        elif opcion == '3':
            menu_actualizar_producto()
        elif opcion == '4':
            menu_eliminar_producto()
        elif opcion == '5':
            menu_buscar_producto()
        elif opcion == '6':
            break
        else:
            imprimir_error("Opción no válida.")

def menu_categorias():
    """Submenú de gestión de categorías"""
    while True:
        print("\n" + "="*40)
        print("   GESTIÓN DE CATEGORÍAS")
        print("="*40)
        print("1. Registrar Categoría")
        print("2. Mostrar Todas las Categorías")
        print("3. Actualizar Demanda Semanal")
        print("4. Eliminar Categoría")
        print("5. Actualizar Estadísticas Automáticas")
        print("6. Volver al Menú Principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            menu_registrar_categoria()
        elif opcion == '2':
            menu_mostrar_categorias()
        elif opcion == '3':
            menu_actualizar_categoria()
        elif opcion == '4':
            menu_eliminar_categoria()
        elif opcion == '5':
            menu_actualizar_estadisticas()
        elif opcion == '6':
            break
        else:
            imprimir_error("Opción no válida.")

def menu_reportes():
    """Submenú de reportes"""
    while True:
        print("\n" + "="*40)
        print("   REPORTES Y ANÁLISIS")
        print("="*40)
        print("1. Dashboard General")
        print("2. Productos con Bajo Stock")
        print("3. Categorías Críticas")
        print("4. Productos por Categoría")
        print("5. Volver al Menú Principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            menu_dashboard()
        elif opcion == '2':
            menu_reporte_bajo_stock()
        elif opcion == '3':
            menu_reporte_categorias_criticas()
        elif opcion == '4':
            menu_reporte_por_categoria()
        elif opcion == '5':
            break
        else:
            imprimir_error("Opción no válida.")

def main():
    """Función principal"""
    db_manager.inicializar_db()
    
    while True:
        print("\n" + "="*40)
        print("   SISTEMA DE GESTIÓN DE INVENTARIO")
        print("="*40)
        print("1. Gestión de Productos")
        print("2. Gestión de Categorías")
        print("3. Reportes y Análisis")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            menu_productos()
        elif opcion == '2':
            menu_categorias()
        elif opcion == '3':
            menu_reportes()
        elif opcion == '4':
            print("\n¡Gracias por usar el sistema!")
            print("Saliendo...")
            sys.exit()
        else:
            imprimir_error("Opción no válida, intente nuevamente.")

if __name__ == "__main__":
    main()