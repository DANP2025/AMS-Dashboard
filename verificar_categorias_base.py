import pandas as pd
from data_loader import load_data

def verificar_categorias_base():
    """Verificar las categorías en la hoja 'base' vs 'Plat de fuerza'."""
    print("=== VERIFICACIÓN CATEGORÍAS - BASE vs PLAT DE FUERZA ===\n")
    
    # Cargar directamente el Excel
    archivo_excel = r"C:\Dany\AMS\AMS.xlsx"
    
    try:
        # Cargar ambas hojas
        df_base = pd.read_excel(archivo_excel, sheet_name='Base de datos')
        df_fuerza = pd.read_excel(archivo_excel, sheet_name='Plat de fuerza')
        
        print("1. CATEGORÍAS EN HOJA 'Base de datos':")
        if 'Categoria' in df_base.columns:
            cats_base = df_base['Categoria'].dropna().unique()
            print(f"   Total: {len(cats_base)}")
            print(f"   Lista: {sorted(cats_base)}")
        
        print("\n2. CATEGORÍAS EN HOJA 'Plat de fuerza':")
        if 'Categoria' in df_fuerza.columns:
            cats_fuerza = df_fuerza['Categoria'].dropna().unique()
            print(f"   Total: {len(cats_fuerza)}")
            print(f"   Lista: {sorted(cats_fuerza)}")
        
        # Comparar
        print("\n3. COMPARACIÓN:")
        set_base = set(cats_base) if 'Categoria' in df_base.columns else set()
        set_fuerza = set(cats_fuerza) if 'Categoria' in df_fuerza.columns else set()
        
        if set_base == set_fuerza:
            print("   Las categorías son idénticas en ambas hojas")
        else:
            print("   Diferencias encontradas:")
            solo_base = set_base - set_fuerza
            solo_fuerza = set_fuerza - set_base
            if solo_base:
                print(f"   Solo en Base: {solo_base}")
            if solo_fuerza:
                print(f"   Solo en Fuerza: {solo_fuerza}")
        
        # Verificar específicamente 'Sub 17'
        print("\n4. VERIFICACIÓN ESPECÍFICA 'Sub 17':")
        
        # En base
        if 'Categoria' in df_base.columns:
            sub17_base = [cat for cat in cats_base if '17' in str(cat)]
            print(f"   En Base: {sub17_base}")
        
        # En fuerza
        if 'Categoria' in df_fuerza.columns:
            sub17_fuerza = [cat for cat in cats_fuerza if '17' in str(cat)]
            print(f"   En Fuerza: {sub17_fuerza}")
            
            # Verificar datos para cada variación
            for cat in sub17_fuerza:
                df_cat = df_fuerza[df_fuerza['Categoria'] == cat].copy()
                print(f"\n   Datos para '{cat}': {len(df_cat)} registros")
                
                if len(df_cat) > 0:
                    # Verificar fechas
                    fechas_unicas = df_cat['Fecha'].dropna().unique()
                    for fecha in sorted(fechas_unicas):
                        fecha_dt = pd.to_datetime(fecha)
                        if fecha_dt.year == 2025 and fecha_dt.month == 12:
                            print(f"     ¡Datos en 2025-12 para '{cat}'!")
                            df_dic = df_cat[df_cat['Fecha'] == fecha]
                            cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                            print(df_dic[cols_mostrar].to_string())
        
        # Verificar a través de data_loader
        print("\n5. VERIFICACIÓN A TRAVÉS DE DATA_LOADER:")
        data = load_data()
        
        if 'base' in data and 'pfza' in data:
            cats_loader = get_categorias(data)
            print(f"   Categorías desde loader: {sorted(cats_loader)}")
            
            # Verificar qué hay en pfza
            df_pfza = data['pfza']
            cats_pfza_loader = df_pfza['Categoria'].dropna().unique()
            print(f"   Categorías en pfza desde loader: {sorted(cats_pfza_loader)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def get_categorias(data):
    """Función copiada de data_loader para verificar."""
    cats = data['base']['Categoria'].dropna().unique().tolist()
    return sorted(cats)

if __name__ == "__main__":
    verificar_categorias_base()
