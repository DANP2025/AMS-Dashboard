import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def analisis_exhaustivo_datos():
    """Análisis exhaustivo para identificar problemas de datos."""
    print("=== ANÁLISIS EXHAUSTIVO - PROBLEMAS DE DATOS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar estructura general de datos
    print("1. ESTRUCTURA GENERAL DE DATOS:")
    print(f"   Hojas disponibles: {list(data.keys())}")
    
    for hoja in ['rendimiento', 'pfza']:
        if hoja in data:
            df = data[hoja]
            print(f"\n   Hoja '{hoja}': {df.shape}")
            print(f"   Columnas: {list(df.columns)}")
            
            # Verificar categorías
            if 'Categoria' in df.columns:
                categorias = df['Categoria'].dropna().unique()
                print(f"   Categorías: {sorted(categorias)}")
                
                # Verificar fechas por categoría
                if 'Fecha' in df.columns:
                    print(f"   Fechas por categoría:")
                    for cat in sorted(categorias):
                        df_cat = df[df['Categoria'] == cat].copy()
                        fechas = df_cat['Fecha'].dropna().unique()
                        if len(fechas) > 0:
                            periodos = []
                            for fecha in fechas:
                                fecha_dt = pd.to_datetime(fecha)
                                periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                                periodos.append(periodo)
                            periodos_unicos = sorted(set(periodos))
                            print(f"     {cat}: {periodos_unicos}")
                        else:
                            print(f"     {cat}: Sin fechas")
    
    # 2. Verificar problema específico con 'Sub 17'
    print(f"\n2. ANÁLISIS ESPECÍFICO - 'Sub 17':")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_sub17 = df_pfza[df_pfza['Categoria'] == 'Sub 17'].copy()
        print(f"   Registros 'Sub 17': {len(df_sub17)}")
        
        if len(df_sub17) > 0:
            print(f"\n   Datos completos de 'Sub 17':")
            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
            print(df_sub17[cols_mostrar].to_string())
            
            # Verificar fechas específicas
            if 'Fecha' in df_sub17.columns:
                fechas_unicas = df_sub17['Fecha'].dropna().unique()
                print(f"\n   Fechas únicas en 'Sub 17': {sorted(fechas_unicas)}")
                
                for fecha in sorted(fechas_unicas):
                    fecha_dt = pd.to_datetime(fecha)
                    periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                    count = len(df_sub17[df_sub17['Fecha'] == fecha])
                    print(f"     {fecha} -> {periodo}: {count} registros")
                    
                    # Verificar datos de fuerza
                    df_fecha = df_sub17[df_sub17['Fecha'] == fecha]
                    vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                    print(f"     Variables de fuerza:")
                    for var in vars_fuerza:
                        if var in df_fecha.columns:
                            valores = df_fecha[var].dropna()
                            if len(valores) > 0:
                                print(f"       {var}: {len(valores)} valores")
                            else:
                                print(f"       {var}: Sin valores")
        else:
            print("   No hay registros para 'Sub 17'")
    
    # 3. Simular el proceso exacto del sistema
    print(f"\n3. SIMULACIÓN DEL PROCESO DEL SISTEMA:")
    
    categorias = ['Primera', 'Sub 15', 'Sub 16', 'Sub 17']
    variables = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    for categoria in categorias:
        print(f"\n   --- Categoría: {categoria} ---")
        
        if 'pfza' in data:
            df_pfza = data['pfza']
            df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
            print(f"   Registros totales: {len(df_cat)}")
            
            # Aplicar filtros como lo hace el sistema
            pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
            post_cat = _filtrar_mes_estricto(df_cat, mes_post)
            
            print(f"   Registros Pre ({mes_pre}): {len(pre_cat)}")
            print(f"   Registros Post ({mes_post}): {len(post_cat)}")
            
            if len(pre_cat) > 0:
                print(f"   Datos Pre:")
                for _, row in pre_cat.iterrows():
                    print(f"     {row['Apellido']}: {row['Fecha']}")
            
            if len(post_cat) > 0:
                print(f"   Datos Post:")
                for _, row in post_cat.iterrows():
                    print(f"     {row['Apellido']}: {row['Fecha']}")
            
            # Verificar variables
            for variable in variables:
                if variable in df_cat.columns:
                    pre_vals = pre_cat[variable].dropna() if len(pre_cat) > 0 else pd.Series()
                    post_vals = post_cat[variable].dropna() if len(post_cat) > 0 else pd.Series()
                    
                    print(f"   {variable}: Pre={len(pre_vals)}, Post={len(post_vals)}")
                    
                    if len(pre_vals) == 0 and len(post_vals) > 0:
                        print(f"     ¡PROBLEMA! Hay datos Post pero no hay datos Pre")
                    elif len(pre_vals) > 0 and len(post_vals) == 0:
                        print(f"     ¡PROBLEMA! Hay datos Pre pero no hay datos Post")
                    elif len(pre_vals) > 0 and len(post_vals) > 0:
                        print(f"     OK: Hay datos en ambos meses")
                        
                        # Verificar correspondencia de jugadores
                        jugadores_pre = set(pre_cat['Apellido'].unique())
                        jugadores_post = set(post_cat['Apellido'].unique())
                        jugadores_comunes = jugadores_pre & jugadores_post
                        
                        print(f"     Jugadores Pre: {jugadores_pre}")
                        print(f"     Jugadores Post: {jugadores_post}")
                        print(f"     Jugadores comunes: {jugadores_comunes}")
                        
                        if len(jugadores_comunes) == 0:
                            print(f"     ¡PROBLEMA! No hay jugadores comunes entre Pre y Post")
                        else:
                            print(f"     OK: {len(jugadores_comunes)} jugadores comunes")
                    else:
                        print(f"     Sin datos para esta variable")
    
    # 4. Verificar directamente el Excel
    print(f"\n4. VERIFICACIÓN DIRECTA DEL EXCEL:")
    
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        # Cargar hoja 'Plat de fuerza'
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        print(f"   Hoja 'Plat de fuerza' directa: {df_fuerza.shape}")
        
        # Verificar 'Sub 17' directamente
        df_sub17_excel = df_fuerza[df_fuerza['Categoria'] == 'Sub 17'].copy()
        print(f"   Registros 'Sub 17' directos: {len(df_sub17_excel)}")
        
        if len(df_sub17_excel) > 0:
            print(f"\n   Datos directos de 'Sub 17':")
            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
            print(df_sub17_excel[cols_mostrar].to_string())
            
            # Verificar fechas
            if 'Fecha' in df_sub17_excel.columns:
                fechas_unicas = df_sub17_excel['Fecha'].dropna().unique()
                print(f"\n   Fechas directas en 'Sub 17': {sorted(fechas_unicas)}")
                
                for fecha in sorted(fechas_unicas):
                    fecha_dt = pd.to_datetime(fecha)
                    periodo = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                    if periodo == '2025-12':
                        print(f"   ¡HAY DATOS DIRECTOS EN 2025-12!")
                        df_dic = df_sub17_excel[df_sub17_excel['Fecha'] == fecha]
                        print(df_dic[cols_mostrar].to_string())
                    elif periodo == '2026-01':
                        print(f"   Hay datos en 2026-01")
        
    except Exception as e:
        print(f"   Error cargando Excel directo: {e}")
    
    print(f"\n=== CONCLUSIONES ===")
    print("Posibles problemas identificados:")
    print("1. Los datos pueden existir pero el filtrado no los encuentra")
    print("2. Puede haber problemas con los nombres de categorías")
    print("3. Puede haber problemas con los formatos de fecha")
    print("4. Puede haber inconsistencias entre data_loader y Excel directo")

if __name__ == "__main__":
    analisis_exhaustivo_datos()
