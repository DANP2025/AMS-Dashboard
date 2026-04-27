import pandas as pd
import openpyxl

def analizar_excel_directo():
    """Analiza directamente el archivo AMS.xlsx para verificar datos."""
    print("=== ANÁLISIS DIRECTO DE AMS.XLSX ===\n")
    
    # Ruta al archivo
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        # Cargar con openpyxl para ver hojas
        wb = openpyxl.load_workbook(archivo_excel, read_only=True)
        print(f"Hojas en el Excel: {wb.sheetnames}")
        
        # Analizar específicamente hoja de fuerza
        if 'Plat de fuerza' in wb.sheetnames:
            print("\n=== ANÁLISIS HOJA 'Plat de fuerza' ===")
            ws = wb['Plat de fuerza']
            
            # Mostrar primeras filas para estructura
            print("\nPrimeras 10 filas (encabezados y datos):")
            for i, row in enumerate(ws.iter_rows(values_only=True, max_row=10)):
                if i == 0:
                    print(f"Fila {i+1} (encabezados): {row}")
                else:
                    print(f"Fila {i+1}: {row}")
                if i >= 9:  # Limitar a 10 filas
                    break
        
        # Cargar con pandas para análisis de datos
        print("\n=== ANÁLISIS CON PANDAS ===")
        
        # Hoja de fuerza
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        print(f"\nHoja 'Plat de fuerza': {df_fuerza.shape}")
        print(f"Columnas: {list(df_fuerza.columns)}")
        
        # Filtrar por categoría 'Primera'
        if 'Categoria' in df_fuerza.columns:
            df_primera = df_fuerza[df_fuerza['Categoria'] == 'Primera']
            print(f"\nRegistros categoría 'Primera': {len(df_primera)}")
            
            if len(df_primera) > 0:
                print("\nDatos de 'Primera':")
                print(df_primera[['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']].head(10))
                
                # Verificar fechas
                if 'Fecha' in df_primera.columns:
                    print(f"\nFechas únicas en 'Primera':")
                    fechas_unicas = df_primera['Fecha'].dropna().unique()
                    for fecha in sorted(fechas_unicas):
                        count = len(df_primera[df_primera['Fecha'] == fecha])
                        print(f"  {fecha}: {count} registros")
                
                # Verificar datos para diciembre 2025
                if 'Fecha' in df_primera.columns:
                    df_primera['Fecha'] = pd.to_datetime(df_primera['Fecha'], errors='coerce')
                    mask = (df_primera['Fecha'].dt.year == 2025) & (df_primera['Fecha'].dt.month == 12)
                    df_dic_2025 = df_primera[mask]
                    
                    print(f"\nRegistros 'Primera' en Diciembre 2025: {len(df_dic_2025)}")
                    
                    if len(df_dic_2025) > 0:
                        print("DATOS ENCONTRADOS:")
                        cols_muestra = ['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                        print(df_dic_2025[cols_muestra])
                        
                        # Verificar variables de fuerza
                        vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
                        print(f"\nVariables de fuerza:")
                        for var in vars_fuerza:
                            if var in df_dic_2025.columns:
                                valores = df_dic_2025[var].dropna()
                                if len(valores) > 0:
                                    print(f"  {var}: {len(valores)} valores válidos")
                                    print(f"    Rango: {valores.min():.2f} - {valores.max():.2f}")
                                else:
                                    print(f"  {var}: Sin valores válidos")
                            else:
                                print(f"  {var}: Columna no existe")
                    else:
                        print("NO HAY DATOS para 'Primera' en Diciembre 2025")
            else:
                print("No hay registros para categoría 'Primera'")
        else:
            print("No existe columna 'Categoria' en hoja 'pfza'")
        
    except Exception as e:
        print(f"Error analizando Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_excel_directo()
