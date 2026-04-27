import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto

def test_filtrado_primera():
    """Prueba específica para categoría 'Primera' y mes '2025-12'."""
    print("=== TEST ESPECÍFICO: Categoría 'Primera' - Mes '2025-12' ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Probar con hoja pfza (donde están los datos de fuerza)
    if 'pfza' not in data:
        print("Hoja 'pfza' no encontrada")
        return
    
    df_pfza = data['pfza']
    print(f"Total registros hoja pfza: {len(df_pfza)}")
    
    # Filtrar por categoría 'Primera'
    df_primera = df_pfza[df_pfza['Categoria'] == 'Primera'].copy()
    print(f"Registros categoría 'Primera': {len(df_primera)}")
    
    # Aplicar filtro estricto por mes 2025-12
    df_filtrado = _filtrar_mes_estricto(df_primera, '2025-12')
    print(f"Registros 'Primera' filtrados por 2025-12: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        print("\nDATOS ENCONTRADOS - EXITOSO:")
        print(f"Columnas disponibles: {list(df_filtrado.columns)}")
        
        # Verificar variables de fuerza
        vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
        for var in vars_fuerza:
            if var in df_filtrado.columns:
                valores = df_filtrado[var].dropna()
                print(f"  {var}: {len(valores)} valores")
                if len(valores) > 0:
                    print(f"    Rango: {valores.min():.2f} - {valores.max():.2f}")
        
        # Mostrar fechas encontradas
        if 'Fecha' in df_filtrado.columns:
            fechas = pd.to_datetime(df_filtrado['Fecha'], errors='coerce')
            print(f"\nFechas encontradas:")
            for fecha in fechas.dropna().unique():
                print(f"  {fecha.strftime('%Y-%m-%d')}")
        
        print("\n=== CONCLUSIÓN ===")
        print("El filtrado funciona correctamente.")
        print("Los datos SÍ existen para 'Primera' en 2025-12.")
        print("El problema debe estar en los dropdowns o en la UI.")
        
    else:
        print("NO HAY DATOS - ERROR")
        
        # Depurar: ver qué meses sí tienen datos
        if 'Fecha' in df_primera.columns:
            try:
                fechas = pd.to_datetime(df_primera['Fecha'], errors='coerce')
                periodos = fechas.dt.to_period('M').astype(str).dropna()
                meses_disponibles = sorted(periodos.unique())
                print(f"\nMeses disponibles para 'Primera': {meses_disponibles}")
            except Exception as e:
                print(f"Error procesando fechas: {e}")

if __name__ == "__main__":
    test_filtrado_primera()
