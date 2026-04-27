import pandas as pd

def verificar_nombres_excel_exactos():
    """Verificar nombres exactos en el Excel para 'Sub 17'."""
    print("=== VERIFICACIÓN DE NOMBRES EXACTOS EN EXCEL ===\n")
    
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        # Cargar todas las hojas para ver nombres exactos
        xls = pd.ExcelFile(archivo_excel)
        print(f"Hojas en Excel: {xls.sheet_names}")
        
        # Verificar hoja 'Plat de fuerza'
        if 'Plat de fuerza' in xls.sheet_names:
            df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
            print(f"\nHojas 'Plat de fuerza': {df_fuerza.shape}")
            print(f"Columnas: {list(df_fuerza.columns)}")
            
            # Verificar categorías exactas
            if 'Categoria' in df_fuerza.columns:
                categorias_exactas = df_fuerza['Categoria'].dropna().unique()
                print(f"Categorías exactas: {list(categorias_exactas)}")
                
                # Buscar 'Sub 17' o similares
                sub17_variants = [cat for cat in categorias_exactas if '17' in str(cat)]
                print(f"Variantes con '17': {sub17_variants}")
                
                # Verificar datos para cada variante
                for cat in sub17_variants:
                    df_cat = df_fuerza[df_fuerza['Categoria'] == cat].copy()
                    print(f"\nDatos para '{cat}': {len(df_cat)} registros")
                    
                    if len(df_cat) > 0:
                        # Verificar fechas
                        if 'Fecha' in df_cat.columns:
                            fechas = df_cat['Fecha'].dropna().unique()
                            print(f"Fechas: {sorted(fechas)}")
                            
                            # Buscar 2025-12
                            for fecha in fechas:
                                fecha_dt = pd.to_datetime(fecha)
                                if fecha_dt.year == 2025 and fecha_dt.month == 12:
                                    print(f"¡DATOS ENCONTRADOS EN 2025-12 para '{cat}'!")
                                    df_dic = df_cat[df_cat['Fecha'] == fecha]
                                    cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                                    print(df_dic[cols_mostrar].to_string())
        
        # Verificar si hay otras hojas con 'Sub 17'
        for sheet_name in xls.sheet_names:
            if 'fuerza' in sheet_name.lower() or 'plata' in sheet_name.lower():
                print(f"\nVerificando hoja: '{sheet_name}'")
                df = pd.read_excel(archivo_excel, sheet_name=sheet_name)
                
                if 'Categoria' in df.columns:
                    categorias = df['Categoria'].dropna().unique()
                    sub17_cats = [cat for cat in categorias if '17' in str(cat)]
                    if sub17_cats:
                        print(f"  Categorías con '17': {sub17_cats}")
                        
                        for cat in sub17_cats:
                            df_cat = df[df['Categoria'] == cat].copy()
                            print(f"  Registros '{cat}': {len(df_cat)}")
                            
                            if len(df_cat) > 0 and 'Fecha' in df_cat.columns:
                                fechas = df_cat['Fecha'].dropna().unique()
                                for fecha in fechas:
                                    fecha_dt = pd.to_datetime(fecha)
                                    if fecha_dt.year == 2025 and fecha_dt.month == 12:
                                        print(f"  ¡Datos en 2025-12 para '{cat}'!")
                                        df_dic = df_cat[df_cat['Fecha'] == fecha]
                                        cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                                        print(df_dic[cols_mostrar].to_string())
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_nombres_excel_exactos()
