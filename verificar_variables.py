import pandas as pd
from data_loader import load_data

def verificar_variables_por_mes():
    """Verifica que todas las variables tengan valores para cada mes disponible."""
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Variables exactas del Excel
    VARS_RENDIMIENTO_EXCEL = ['VO2 max', 'Vmax', 'F0', 'V0', 'Pmax', 'RF', 'DRF']
    VARS_PFZA_EXCEL = [
        'Fuerza', 'Potencia Pico', 'Altura Salto',
        'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250'
    ]
    
    todas_vars = VARS_RENDIMIENTO_EXCEL + VARS_PFZA_EXCEL
    
    # Detectar meses disponibles
    meses_set = set()
    for hoja in ['rendimiento', 'pfza']:
        if hoja not in data:
            continue
        df_h = data[hoja]
        for col in df_h.columns:
            if any(kw in col.lower() for kw in 
                   ['fecha', 'mes', 'date', 'month', 'periodo']):
                try:
                    m = (pd.to_datetime(df_h[col], errors='coerce')
                         .dt.to_period('M')
                         .astype(str)
                         .dropna())
                    meses_set.update(m[m != 'NaT'].tolist())
                except Exception:
                    pass
                break
    
    meses = sorted([m for m in meses_set if m and m != 'NaT'])
    print(f"Meses detectados: {meses}")
    
    # Verificar cada variable para cada mes
    for hoja in ['rendimiento', 'pfza']:
        if hoja not in data:
            continue
            
        df = data[hoja]
        vars_hoja = VARS_RENDIMIENTO_EXCEL if hoja == 'rendimiento' else VARS_PFZA_EXCEL
        
        print(f"\n=== HOJA: {hoja.upper()} ====")
        print(f"Variables a verificar: {vars_hoja}")
        
        for mes in meses:
            print(f"\n--- MES: {mes} ---")
            
            # Filtrar por mes
            fecha_col = None
            for col in df.columns:
                if any(kw in col.lower() for kw in 
                       ['fecha', 'mes', 'date', 'month', 'periodo']):
                    fecha_col = col
                    break
            
            if fecha_col is None:
                print(f"  [ERROR] No se encontró columna de fecha")
                continue
            
            try:
                periodos = (pd.to_datetime(df[fecha_col], errors='coerce')
                            .dt.to_period('M')
                            .astype(str))
                df_mes = df[periodos == mes].copy()
                
                if df_mes.empty:
                    print(f"  [ERROR] No hay datos para este mes")
                    continue
                
                print(f"  [OK] Total registros: {len(df_mes)}")
                
                # Verificar cada variable
                for var in vars_hoja:
                    if var in df_mes.columns:
                        valores = df_mes[var].dropna()
                        if len(valores) > 0:
                            print(f"  [OK] {var}: {len(valores)} valores (min: {valores.min():.2f}, max: {valores.max():.2f})")
                        else:
                            print(f"  [ERROR] {var}: SIN VALORES (todos NaN)")
                    else:
                        print(f"  [ERROR] {var}: COLUMNA NO EXISTE")
                        
            except Exception as e:
                print(f"  [ERROR] Error procesando mes {mes}: {e}")

if __name__ == "__main__":
    verificar_variables_por_mes()
