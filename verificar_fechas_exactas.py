import pandas as pd
from data_loader import load_data

def analizar_fechas_excel():
    """Analiza exactamente qué fechas existen en el Excel y cómo se detectan."""
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    print("=== ANÁLISIS COMPLETO DE FECHAS EN EXCEL ===\n")
    
    # Analizar cada hoja en detalle
    for hoja in ['rendimiento', 'pfza']:
        if hoja not in data:
            print(f"HOJA '{hoja}': NO EXISTE\n")
            continue
            
        df = data[hoja]
        print(f"=== HOJA: {hoja.upper()} ===")
        print(f"Total filas: {len(df)}")
        
        # Buscar todas las columnas que podrían contener fechas
        fecha_cols = []
        for col in df.columns:
            if any(kw in col.lower() for kw in ['fecha', 'mes', 'date', 'month', 'periodo']):
                fecha_cols.append(col)
        
        print(f"Columnas de fecha encontradas: {fecha_cols}")
        
        if not fecha_cols:
            print("  No se encontraron columnas de fecha\n")
            continue
            
        # Analizar cada columna de fecha
        for fecha_col in fecha_cols:
            print(f"\n--- Columna: '{fecha_col}' ---")
            
            # Mostrar valores únicos sin procesar
            valores_unicos = df[fecha_col].dropna().unique()
            print(f"Valores únicos ({len(valores_unicos)}):")
            for i, val in enumerate(valores_unicos[:10]):  # Primeros 10 valores
                print(f"  [{i}] {val} (tipo: {type(val)})")
            if len(valores_unicos) > 10:
                print(f"  ... y {len(valores_unicos) - 10} más")
            
            # Intentar convertir a datetime y extraer periodos
            try:
                fechas_convertidas = pd.to_datetime(df[fecha_col], errors='coerce')
                periodos = fechas_convertidas.dt.to_period('M').astype(str)
                periodos_validos = periodos[fechas_convertidas.notna()]
                
                print(f"\nPeriodos detectados ({len(periodos_validos.unique())}):")
                periodos_unicos = sorted(periodos_validos.unique())
                for p in periodos_unicos:
                    count = (periodos_validos == p).sum()
                    print(f"  {p}: {count} registros")
                    
            except Exception as e:
                print(f"Error convirtiendo fechas: {e}")
        
        print("\n" + "="*60 + "\n")
    
    # Verificar específicamente para categoría 'Primera' y mes '2025-12'
    print("=== VERIFICACIÓN ESPECÍFICA: Categoría 'Primera' - Mes '2025-12' ===")
    
    for hoja in ['rendimiento', 'pfza']:
        if hoja not in data:
            continue
            
        df = data[hoja]
        print(f"\n--- Hoja: {hoja} ---")
        
        # Filtrar por categoría 'Primera'
        if 'Categoria' in df.columns:
            df_primera = df[df['Categoria'] == 'Primera']
            print(f"Registros categoría 'Primera': {len(df_primera)}")
            
            if len(df_primera) > 0:
                # Buscar columna de fecha
                fecha_col = None
                for col in df_primera.columns:
                    if any(kw in col.lower() for kw in ['fecha', 'mes', 'date', 'month', 'periodo']):
                        fecha_col = col
                        break
                
                if fecha_col:
                    print(f"Columna de fecha: '{fecha_col}'")
                    
                    # Filtrar por mes 2025-12
                    try:
                        fechas_convertidas = pd.to_datetime(df_primera[fecha_col], errors='coerce')
                        periodos = fechas_convertidas.dt.to_period('M').astype(str)
                        mask = periodos == '2025-12'
                        df_2025_12 = df_primera[mask]
                        
                        print(f"Registros 'Primera' en 2025-12: {len(df_2025_12)}")
                        
                        if len(df_2025_12) > 0:
                            print("DATOS ENCONTRADOS:")
                            print(f"  Columnas disponibles: {list(df_2025_12.columns)}")
                            
                            # Mostrar algunas variables de fuerza
                            vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                            for var in vars_fuerza:
                                if var in df_2025_12.columns:
                                    valores = df_2025_12[var].dropna()
                                    print(f"  {var}: {len(valores)} valores")
                                    if len(valores) > 0:
                                        print(f"    Rango: {valores.min():.2f} - {valores.max():.2f}")
                        else:
                            print("NO HAY DATOS para 'Primera' en 2025-12")
                            
                            # Mostrar qué meses sí tienen datos
                            periodos_disponibles = periodos[fechas_convertidas.notna()].unique()
                            print(f"Meses disponibles para 'Primera': {sorted(periodos_disponibles)}")
                            
                    except Exception as e:
                        print(f"Error procesando fechas: {e}")
                else:
                    print("No se encontró columna de fecha")
            else:
                print("No hay registros para categoría 'Primera'")
        else:
            print("No existe columna 'Categoria'")

if __name__ == "__main__":
    analizar_fechas_excel()
