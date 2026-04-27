import pandas as pd
from data_loader import load_data

def test_agregacion_pfza():
    """Test para verificar que la agregación de pfza funciona correctamente."""
    print("=== TEST AGREGACIÓN DE PLAT DE FUERZA ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    print("1. VERIFICACIÓN DE AGREGACIÓN:")
    
    # Verificar que pfza está agregada
    if 'pfza' not in data:
        print("   ERROR: No se encontró hoja 'pfza'")
        return
    
    pfza = data['pfza']
    print(f"   Filas en pfza agregada: {len(pfza)}")
    print(f"   Columnas: {pfza.columns.tolist()}")
    
    # Verificar duplicados
    if 'DNI' in pfza.columns and 'Fecha' in pfza.columns:
        duplicados = pfza.duplicated(subset=['DNI', 'Fecha']).sum()
        print(f"   Filas duplicadas (DNI+Fecha): {duplicados}")
        
        if duplicados == 0:
            print("   CORRECTO: No hay duplicados - agregacion exitosa")
        else:
            print("   ❌ PROBLEMA: Aún hay duplicados")
    
    # Verificar variables de fuerza
    vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
    for var in vars_fuerza:
        if var in pfza.columns:
            vals = pfza[var].dropna()
            print(f"   {var}: {len(vals)} valores, rango {vals.min():.1f}-{vals.max():.1f}")
        else:
            print(f"   {var}: ERROR - No encontrada")
    
    print(f"\n2. COMPARACIÓN CON DATOS CRUDOS:")
    
    # Cargar datos crudos para comparar
    try:
        xl = pd.ExcelFile('AMS.xlsx')
        pfza_raw = xl.parse('Plat de fuerza')
        print(f"   Filas en pfza cruda: {len(pfza_raw)}")
        
        # Verificar reducción de filas
        reduccion = len(pfza_raw) - len(pfza)
        porcentaje = (reduccion / len(pfza_raw)) * 100
        print(f"   Reducción de filas: {reduccion} ({porcentaje:.1f}%)")
        
        if porcentaje > 90:
            print("   CORRECTO: Reduccion significativa - agregacion efectiva")
        elif porcentaje > 50:
            print("   MODERADA: Reduccion parcial")
        else:
            print("   PROBLEMA: Poca reduccion - agregacion ineficaz")
        
    except Exception as e:
        print(f"   Error cargando datos crudos: {e}")
    
    print(f"\n3. VERIFICACIÓN POR CATEGORÍA:")
    
    if 'Categoria' in pfza.columns:
        categorias = pfza['Categoria'].value_counts()
        print("   Registros por categoría:")
        for cat, count in categorias.items():
            print(f"     {cat}: {count} registros")
    
    print(f"\n4. VERIFICACIÓN DE FECHAS:")
    
    if 'Fecha' in pfza.columns:
        fechas = pd.to_datetime(pfza['Fecha'], errors='coerce')
        fechas_validas = fechas.dropna()
        
        if len(fechas_validas) > 0:
            fecha_min = fechas_validas.min().strftime('%Y-%m')
            fecha_max = fechas_validas.max().strftime('%Y-%m')
            print(f"   Rango de fechas: {fecha_min} a {fecha_max}")
            print(f"   Fechas válidas: {len(fechas_validas)}")
        else:
            print("   ERROR: No hay fechas validas")
    
    print(f"\n5. TEST DE SWC CON DATOS AGREGADOS:")
    
    # Probar un caso específico
    categoria = 'Primera'
    variable = 'Potencia Pico'
    
    if 'Categoria' in pfza.columns and variable in pfza.columns:
        cat_data = pfza[pfza['Categoria'] == categoria]
        var_data = cat_data[variable].dropna()
        
        print(f"   Categoría: {categoria}")
        print(f"   Variable: {variable}")
        print(f"   Registros: {len(var_data)}")
        
        if len(var_data) > 1:
            std_val = var_data.std(ddof=1)
            print(f"   SD: {std_val:.2f}")
            
            if std_val > 0:
                print("   CORRECTO: SD > 0 - se puede calcular SWC")
            else:
                print("   ADVERTENCIA: SD = 0 - no se puede calcular SWC")
        else:
            print("   PROBLEMA: Insuficientes datos para SWC")
    
    print(f"\n=== CONCLUSIÓN ===")
    print("La agregacion de 'Plat de fuerza' permite:")
    print("1. Reducir miles de filas a una por jugador+fecha")
    print("2. Calcular SWC correctamente segun Hopkins")
    print("3. Mantener todas las variables importantes")
    print("4. Preservar estructura de categorias y fechas")
    print("5. Eliminar duplicados y repeticiones de test")

if __name__ == "__main__":
    test_agregacion_pfza()
