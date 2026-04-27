import pandas as pd
from data_loader import load_data

def verificar_datos_pmax():
    """Verificar datos específicos de Pmax para identificar el problema."""
    print("=== VERIFICACIÓN DE DATOS - PMAX ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Verificar datos de Pmax en rendimiento
    if 'rendimiento' in data:
        df_rend = data['rendimiento']
        print("1. DATOS EN HOJA 'rendimiento':")
        
        if 'Pmax' in df_rend.columns:
            print(f"   Columna 'Pmax' encontrada")
            
            # Verificar por categoría
            for categoria in ['Primera', 'Sub 15', 'Sub 16']:
                df_cat = df_rend[df_rend['Categoria'] == categoria].copy()
                print(f"\n   --- Categoría: {categoria} ---")
                print(f"   Registros totales: {len(df_cat)}")
                
                # Verificar fechas y valores
                if 'Fecha' in df_cat.columns and 'Pmax' in df_cat.columns:
                    print(f"   Datos por fecha:")
                    fechas_unicas = df_cat['Fecha'].dropna().unique()
                    
                    for fecha in sorted(fechas_unicas):
                        fecha_dt = pd.to_datetime(fecha)
                        periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                        
                        df_fecha = df_cat[df_cat['Fecha'] == fecha]
                        valores_pmax = df_fecha['Pmax'].dropna()
                        
                        print(f"     {periodo}: {len(valores_pmax)} valores")
                        if len(valores_pmax) > 0:
                            print(f"       Rango: {valores_pmax.min():.2f} - {valores_pmax.max():.2f}")
                            print(f"       Valores únicos: {sorted(valores_pmax.unique())}")
                            
                            # Mostrar datos detallados
                            print(f"       Detalles:")
                            for _, row in df_fecha.iterrows():
                                print(f"         {row['Apellido']}: {row['Pmax']:.2f}")
        else:
            print("   Columna 'Pmax' NO encontrada en rendimiento")
    
    # Comparar con Potencia Pico en pfza
    if 'pfza' in data:
        df_pfza = data['pfza']
        print(f"\n2. COMPARACIÓN CON 'Potencia Pico' en pfza:")
        
        if 'Potencia Pico' in df_pfza.columns:
            print(f"   Columna 'Potencia Pico' encontrada")
            
            for categoria in ['Primera', 'Sub 15', 'Sub 16']:
                df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
                print(f"\n   --- Categoría: {categoria} ---")
                print(f"   Registros totales: {len(df_cat)}")
                
                if 'Fecha' in df_cat.columns and 'Potencia Pico' in df_cat.columns:
                    fechas_unicas = df_cat['Fecha'].dropna().unique()
                    
                    for fecha in sorted(fechas_unicas):
                        fecha_dt = pd.to_datetime(fecha)
                        periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                        
                        df_fecha = df_cat[df_cat['Fecha'] == fecha]
                        valores_potencia = df_fecha['Potencia Pico'].dropna()
                        
                        print(f"     {periodo}: {len(valores_potencia)} valores")
                        if len(valores_potencia) > 0:
                            print(f"       Rango: {valores_potencia.min():.2f} - {valores_potencia.max():.2f}")
                            print(f"       Valores únicos: {sorted(valores_potencia.unique())}")
                            
                            # Mostrar datos detallados
                            print(f"       Detalles:")
                            for _, row in df_fecha.iterrows():
                                print(f"         {row['Apellido']}: {row['Potencia Pico']:.2f}")
        else:
            print("   Columna 'Potencia Pico' NO encontrada en pfza")
    
    # Verificar si hay problema de unidades o escala
    print(f"\n3. ANÁLISIS DE ESCALA Y UNIDADES:")
    print("   Pótesibles problemas:")
    print("   - Pmax podría estar en diferentes unidades (ej: m/s vs km/h)")
    print("   - Podría haber un error de conversión")
    print("   - Los datos podrían ser constantes por alguna razón")
    
    # Comparar Pmax vs Potencia Pico para mismos jugadores
    if 'rendimiento' in data and 'pfza' in data:
        df_rend = data['rendimiento']
        df_pfza = data['pfza']
        
        categoria = 'Primera'
        
        df_rend_cat = df_rend[df_rend['Categoria'] == categoria].copy()
        df_pfza_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
        
        print(f"\n4. COMPARACIÓN DIRECTA - {categoria}:")
        
        # Buscar mismos jugadores y fechas
        for fecha in ['2025-12-16', '2026-01-16']:
            fecha_dt = pd.to_datetime(fecha)
            
            df_rend_fecha = df_rend_cat[df_rend_cat['Fecha'] == fecha_dt]
            df_pfza_fecha = df_pfza_cat[df_pfza_cat['Fecha'] == fecha_dt]
            
            print(f"\n   Fecha: {fecha}")
            
            if len(df_rend_fecha) > 0 and 'Pmax' in df_rend_fecha.columns:
                print(f"   Pmax (rendimiento):")
                for _, row in df_rend_fecha.iterrows():
                    print(f"     {row['Apellido']}: {row['Pmax']:.2f}")
            
            if len(df_pfza_fecha) > 0 and 'Potencia Pico' in df_pfza_fecha.columns:
                print(f"   Potencia Pico (pfza):")
                for _, row in df_pfza_fecha.iterrows():
                    print(f"     {row['Apellido']}: {row['Potencia Pico']:.2f}")

if __name__ == "__main__":
    verificar_datos_pmax()
