import pandas as pd
from data_loader import load_data

def verificar_nombres_sub17():
    """Verificar si hay problemas con nombres de categoría 'Sub 17'."""
    print("=== VERIFICACIÓN DE NOMBRES - CATEGORÍA 'Sub 17' ===\n")
    
    # 1. Cargar directamente el Excel
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        print("1. CATEGORÍAS ENCONTRADAS EN EXCEL DIRECTO:")
        
        # Obtener todas las categorías únicas
        categorias_excel = df_fuerza['Categoria'].dropna().unique()
        print(f"   Total categorías: {len(categorias_excel)}")
        print(f"   Lista: {sorted(categorias_excel)}")
        
        # Buscar variaciones de 'Sub 17'
        variaciones_sub17 = [cat for cat in categorias_excel if 'sub 17' in cat.lower() or 'sub17' in cat.lower()]
        print(f"\n   Variaciones de 'Sub 17': {variaciones_sub17}")
        
        # Verificar cada variación
        for cat in variaciones_sub17:
            df_cat = df_fuerza[df_fuerza['Categoria'] == cat].copy()
            print(f"\n   Categoría '{cat}': {len(df_cat)} registros")
            
            if len(df_cat) > 0:
                # Verificar fechas
                fechas_unicas = df_cat['Fecha'].dropna().unique()
                print(f"   Fechas: {sorted(fechas_unicas)}")
                
                # Buscar diciembre 2025
                for fecha in fechas_unicas:
                    fecha_dt = pd.to_datetime(fecha)
                    if fecha_dt.year == 2025 and fecha_dt.month == 12:
                        print(f"   ¡DATOS EN {fecha} para '{cat}'!")
                        df_dic = df_cat[df_cat['Fecha'] == fecha]
                        print(df_dic[['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']].to_string())
        
    except Exception as e:
        print(f"Error cargando Excel: {e}")
    
    # 2. Verificar a través de data_loader
    print("\n2. CATEGORÍAS A TRAVÉS DE DATA_LOADER:")
    
    data = load_data()
    if 'pfza' in data:
        df_pfza = data['pfza']
        categorias_loader = df_pfza['Categoria'].dropna().unique()
        print(f"   Total categorías loader: {len(categorias_loader)}")
        print(f"   Lista: {sorted(categorias_loader)}")
        
        # Buscar variaciones
        variaciones_sub17_loader = [cat for cat in categorias_loader if 'sub 17' in cat.lower() or 'sub17' in cat.lower()]
        print(f"\n   Variaciones de 'Sub 17' en loader: {variaciones_sub17_loader}")
    
    # 3. Comparación
    print("\n3. COMPARACIÓN:")
    print(f"   Categorías Excel: {sorted(categorias_excel)}")
    print(f"   Categorías Loader: {sorted(categorias_loader)}")
    
    # Verificar si hay diferencias
    diferencias = set(categorias_excel) ^ set(categorias_loader)
    if diferencias:
        print(f"   Diferencias: {diferencias}")
    else:
        print("   Sin diferencias")
    
    # 4. Verificar si hay espacios o caracteres extra
    print("\n4. VERIFICACIÓN DE ESPACIOS/CHARACTERS:")
    for cat in categorias_excel:
        cat_limpia = cat.strip()
        if cat != cat_limpia:
            print(f"   '{cat}' -> '{cat_limpia}' (con espacios)")
        
        # Verificar caracteres especiales
        if any(ord(c) > 127 for c in cat):
            print(f"   '{cat}' contiene caracteres especiales")

if __name__ == "__main__":
    verificar_nombres_sub17()
