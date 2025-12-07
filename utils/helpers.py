from colorama import init, Fore, Style, Back

init(autoreset=True)

def imprimir_titulo(texto):
    print(f"\n{Back.LIGHTBLACK_EX+Fore.CYAN}{Style.DIM}=== {texto.upper()} ==={Style.RESET_ALL}")

def imprimir_error(texto):
    print(f"{Back.LIGHTBLACK_EX+Fore.BLUE}❌ Error: {texto}{Style.RESET_ALL}")

def imprimir_exito(texto):
    print(f"{Back.LIGHTBLACK_EX+Fore.LIGHTGREEN_EX}✅ {texto}{Style.RESET_ALL}")

def validar_input_string(prompt):
    while True:
        dato = input(f"{Fore.MAGENTA}{prompt}: {Style.RESET_ALL}").strip()
        if dato:
            return dato
        imprimir_error("El campo no puede estar vacío.")

def validar_descripcion(prompt):
    while True:
        dato = input(f"{Fore.MAGENTA}{prompt}: {Style.RESET_ALL}").strip()
        return dato

def validar_input_float(prompt):
    while True:
        try:
            dato = float(input(f"{Fore.MAGENTA}{prompt}: {Style.RESET_ALL}"))
            if dato >= 0:
                return dato
            imprimir_error("El número debe ser positivo.")
        except ValueError:
            imprimir_error("Debe ingresar un número válido (ej: 10.50).")

def validar_input_int(prompt):
    while True:
        try:
            dato = int(input(f"{Fore.MAGENTA}{prompt}: {Style.RESET_ALL}"))
            if dato >= 0:
                return dato
            imprimir_error("El número debe ser positivo.")
        except ValueError:
            imprimir_error("Debe ingresar un número entero.")

def validar_categoria(categoria_nombre, mostrar_error=True):
    """
    Valida si una categoría existe en la base de datos.
    Normaliza a mayúsculas para comparación case-insensitive.
    
    Args:
        categoria_nombre (str): Nombre de la categoría a validar
        mostrar_error (bool): Si es True, muestra mensaje de error cuando no existe
    
    Returns:
        bool: True si la categoría existe, False si no existe
    """
    from utils.db_manager import buscar_categoria
    
    # Normalizar a mayúsculas
    categoria_normalizada = categoria_nombre.strip().upper()
    categoria = buscar_categoria(categoria_normalizada)
    
    if categoria is None:
        if mostrar_error:
            imprimir_error(f"La categoría '{categoria_nombre}' no existe en el sistema.")
        return False
    
    return True

def validar_categoria_con_reintento(prompt, permitir_vacio=False):
    """
    Solicita una categoría al usuario y valida que exista, con reintentos.
    Normaliza la entrada a mayúsculas automáticamente.
    Útil para cuando el usuario está ingresando datos.
    
    Args:
        prompt (str): Mensaje a mostrar al usuario
        permitir_vacio (bool): Si es True, permite dejar el campo vacío
    
    Returns:
        str: Nombre de la categoría válida EN MAYÚSCULAS o cadena vacía si se permitió
    """
    from utils.db_manager import obtener_categorias
    
    while True:
        categoria = input(f"{Fore.MAGENTA}{prompt}: {Style.RESET_ALL}").strip()
        
        # Si se permite vacío y el usuario no ingresó nada
        if permitir_vacio and not categoria:
            return categoria
        
        # Si no se permite vacío y el usuario no ingresó nada
        if not categoria:
            imprimir_error("El campo no puede estar vacío.")
            continue
        
        # Normalizar a mayúsculas
        categoria_normalizada = categoria.upper()
        
        # Validar que la categoría exista
        if validar_categoria(categoria_normalizada, mostrar_error=False):
            return categoria_normalizada  # Retorna en mayúsculas
        else:
            # Mostrar categorías disponibles
            imprimir_error(f"La categoría '{categoria}' no existe.")
            categorias_disponibles = obtener_categorias()
            
            if categorias_disponibles:
                print(f"{Fore.YELLOW}Categorías disponibles:{Style.RESET_ALL}")
                for cat in categorias_disponibles:
                    print(f"  • {cat[0]}")  # cat[0] es el nombre de la categoría
            else:
                print(f"{Fore.YELLOW}No hay categorías registradas aún.{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}Intente nuevamente o escriba el nombre exacto.{Style.RESET_ALL}")

def listar_categorias_disponibles():
    """
    Muestra una lista formateada de todas las categorías disponibles.
    Útil para mostrar antes de solicitar una categoría.
    """
    from utils.db_manager import obtener_categorias
    
    categorias = obtener_categorias()
    
    if categorias:
        print(f"\n{Fore.CYAN}Categorías disponibles:{Style.RESET_ALL}")
        for cat in categorias:
            # cat es una tupla: (categoria, mean, min_price, max_price, stock_global, demanda_semanal, stock_proteccion, status_stock)
            nombre = cat[0]
            stock = cat[4]
            status = cat[7]
            
            # Color según el status
            if status == "BAJO STOCK":
                color_status = Fore.RED
            elif status == "STOCK NORMAL":
                color_status = Fore.GREEN
            else:  # EXCESO DE STOCK
                color_status = Fore.YELLOW
            
            print(f"  • {Fore.WHITE}{nombre}{Style.RESET_ALL} - Stock: {stock} - {color_status}{status}{Style.RESET_ALL}")
    else:
        imprimir_error("No hay categorías registradas en el sistema.")
    
    return categorias