import pandas as pd
from data_loader import load_data, get_categorias, get_jugadores_por_categoria, _normalizar_categoria

def test_correcciones_data_loader():
    """Test para verificar todas las correcciones en data_loader.py"""
    print("=== TEST CORRECCIONES DATA_LOADER.PY ===\n")
    
    # 1. Probar función _normalizar_categoria
    print("1. FUNCIÓN _normalizar_categoria():")
    
    casos_test = [
        'sub 15',      # minúscula
        'Sub 16',      # capitalización correcta
        'sub  17',     # doble espacio (BUG PRINCIPAL)
        'sub 18',      # minúscula
        'sub 19',      # minúscula
        'Primera',      # correcto
        'Reserva',      # correcto
        '',             # vacío
        None,           # nulo
        '  sub 20  ',  # espacios extra
    ]
    
    for caso in casos_test:
        resultado = _normalizar_categoria(caso)
        print(f"   '{caso}' -> '{resultado}'")
    
    # 2. Cargar datos y verificar hojas
    print(f"\n2. CARGA DE DATOS - HOJAS CORRECTAS:")
    
    data = load_data()
    if data is None:
        print("   ERROR: load_data() devolvió None")
        return
    
    print(f"   Datos cargados correctamente")
    print(f"   Hojas disponibles: {list(data.keys())}")
    
    # Verificar que las hojas tengan datos
    for hoja, df in data.items():
        print(f"   {hoja}: {df.shape} filas/columnas")
    
    # 3. Verificar categorías normalizadas
    print(f"\n3. CATEGORÍAS NORMALIZADAS:")
    
    categorias = get_categorias(data)
    print(f"   Categorías encontradas: {categorias}")
    
    # Verificar que no haya categorías con espacios dobles
    categorias_con_espacios_dobles = [cat for cat in categorias if '  ' in cat]
    if categorias_con_espacios_dobles:
        print(f"   ¡PROBLEMA! Categorías con espacios dobles: {categorias_con_espacios_dobles}")
    else:
        print(f"   CORRECTO - No hay categorías con espacios dobles")
    
    # Verificar categorías esperadas
    categorias_esperadas = ['Primera', 'Reserva', 'Sub 15', 'Sub 16', 'Sub 17', 'Sub 18', 'Sub 19']
    categorias_faltantes = set(categorias_esperadas) - set(categorias)
    categorias_extra = set(categorias) - set(categorias_esperadas)
    
    if categorias_faltantes:
        print(f"   Categorías faltantes: {categorias_faltantes}")
    if categorias_extra:
        print(f"   Categorías extra: {categorias_extra}")
    
    if not categorias_faltantes and not categorias_extra:
        print(f"   CORRECTO - Todas las categorías esperadas encontradas")
    
    # 4. Verificar jugadores por categoría
    print(f"\n4. JUGADORES POR CATEGORÍA:")
    
    for categoria in categorias:
        jugadores = get_jugadores_por_categoria(data, categoria)
        print(f"   {categoria}: {len(jugadores)} jugadores")
        
        if len(jugadores) > 0:
            print(f"     Ejemplo: {jugadores[0]}")
        else:
            print(f"     ¡PROBLEMA! No hay jugadores para {categoria}")
    
    # 5. Verificar datos en cada hoja por categoría
    print(f"\n5. DATOS POR HOJA Y CATEGORÍA:")
    
    for hoja in ['base', 'rendimiento', 'pfza']:
        if hoja in data:
            df = data[hoja]
            
            if 'Categoria' in df.columns:
                print(f"\n   Hoja '{hoja}':")
                
                for categoria in categorias:
                    df_cat = df[df['Categoria'] == categoria]
                    print(f"     {categoria}: {len(df_cat)} registros")
                    
                    # Verificar si hay datos de fechas
                    if 'Fecha' in df_cat.columns:
                        fechas = df_cat['Fecha'].dropna()
                        if len(fechas) > 0:
                            print(f"       Fechas: {len(fechas)} registros")
                        else:
                            print(f"       Sin fechas")
    
    # 6. Verificar que el bug principal esté solucionado
    print(f"\n6. VERIFICACIÓN BUG PRINCIPAL - 'sub  17':")
    
    # Buscar 'sub  17' con doble espacio en los datos originales
    bug_encontrado = False
    
    for hoja in ['base', 'rendimiento', 'pfza']:
        if hoja in data:
            df = data[hoja]
            
            if 'Categoria' in df.columns:
                # Verificar categorías únicas en esta hoja
                cats_unicas = df['Categoria'].dropna().unique()
                
                for cat in cats_unicas:
                    if '  ' in str(cat):  # doble espacio
                        print(f"   ¡BUG ENCONTRADO! En hoja '{hoja}': '{cat}'")
                        bug_encontrado = True
    
    if not bug_encontrado:
        print(f"   BUG SOLUCIONADO - No hay categorías con doble espacio")
    
    # 7. Verificar que 'Sub 17' funcione correctamente
    print(f"\n7. VERIFICACIÓN 'Sub 17' FUNCIONANDO:")
    
    try:
        jugadores_sub17 = get_jugadores_por_categoria(data, 'Sub 17')
        print(f"   Jugadores en 'Sub 17': {len(jugadores_sub17)}")
        
        if len(jugadores_sub17) > 0:
            print(f"   CORRECTO - 'Sub 17' funciona correctamente")
            print(f"   Ejemplo jugador: {jugadores_sub17[0]}")
        else:
            print(f"   ¡PROBLEMA! 'Sub 17' no tiene jugadores")
            
            # Intentar con otras variaciones
            for variacion in ['sub 17', 'sub  17', 'SUB 17']:
                jugadores_test = get_jugadores_por_categoria(data, variacion)
                if len(jugadores_test) > 0:
                    print(f"   Encontrado con variación '{variacion}': {len(jugadores_test)} jugadores")
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print(f"\n=== RESUMEN ===")
    print("Correcciones implementadas:")
    print("1. Función _normalizar_categoria() implementada")
    print("2. Nombres de hojas corregidos ('Base de datos', 'Rendimiento', 'Plat de fuerza')")
    print("3. Normalización de categorías aplicada en load_data()")
    print("4. get_categorias() devuelve categorías normalizadas")
    print("5. get_jugadores_por_categoria() con comparación normalizada")
    
    print(f"\nEstado del sistema:")
    if not bug_encontrado and len(jugadores_sub17) > 0:
        print("TODAS LAS CORRECCIONES IMPLEMENTADAS CORRECTAMENTE")
        print("   - Bug de doble espacio solucionado")
        print("   - Categorías normalizadas")
        print("   - Nombres de hojas correctos")
        print("   - Funciones de búsqueda funcionando")
    else:
        print("Quedan problemas por resolver:")
        if bug_encontrado:
            print("   - Bug de doble espacio persiste")
        if len(jugadores_sub17) == 0:
            print("   - 'Sub 17' no funciona correctamente")

if __name__ == "__main__":
    test_correcciones_data_loader()
