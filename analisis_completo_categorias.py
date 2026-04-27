import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto

def analisis_completo_categorias():
    """Análisis exhaustivo de todas las categorías y sus datos."""
    print("=== ANÁLISIS EXHAUSTIVO - TODAS LAS CATEGORÍAS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Analizar hoja pfza (donde están los datos de fuerza)
    if 'pfza' not in data:
        print("Hoja 'pfza' no encontrada")
        return
    
    df_pfza = data['pfza']
    print(f"Total registros hoja pfza: {len(df_pfza)}")
    
    # Obtener todas las categorías únicas
    if 'Categoria' in df_pfza.columns:
        categorias = df_pfza['Categoria'].dropna().unique()
        print(f"Categorías encontradas: {len(categorias)}")
        print(f"Lista: {sorted(categorias)}")
        
        # Analizar cada categoría
        print("\n" + "="*80)
        print("ANÁLISIS POR CATEGORÍA")
        print("="*80)
        
        for categoria in sorted(categorias):
            print(f"\n--- CATEGORÍA: '{categoria}' ---")
            
            # Filtrar por categoría
            df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
            print(f"Total registros: {len(df_cat)}")
            
            # Analizar fechas disponibles
            if 'Fecha' in df_cat.columns:
                try:
                    df_cat['Fecha'] = pd.to_datetime(df_cat['Fecha'], errors='coerce')
                    fechas_validas = df_cat[df_cat['Fecha'].notna()]
                    
                    if len(fechas_validas) > 0:
                        # Agrupar por mes
                        fechas_validas['mes_periodo'] = fechas_validas['Fecha'].dt.to_period('M').astype(str)
                        meses_disponibles = fechas_validas['mes_periodo'].value_counts().sort_index()
                        
                        print(f"Meses con datos:")
                        for mes, count in meses_disponibles.items():
                            print(f"  {mes}: {count} registros")
                        
                        # Verificar específicamente 2025-12
                        if '2025-12' in meses_disponibles.index:
                            df_2025_12 = fechas_validas[fechas_validas['mes_periodo'] == '2025-12']
                            print(f"\n  DATOS 2025-12: {len(df_2025_12)} registros")
                            
                            # Verificar variables de fuerza
                            vars_fuerza = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP', 'RFD Dec', 'RFD 100', 'RFD 150', 'RFD 250']
                            print(f"  Variables de fuerza:")
                            for var in vars_fuerza:
                                if var in df_2025_12.columns:
                                    valores = df_2025_12[var].dropna()
                                    if len(valores) > 0:
                                        print(f"    {var}: {len(valores)} valores (rango: {valores.min():.2f} - {valores.max():.2f})")
                                    else:
                                        print(f"    {var}: 0 valores (todos NaN)")
                                else:
                                    print(f"    {var}: Columna no existe")
                            
                            # Probar filtrado estricto
                            df_filtrado = _filtrar_mes_estricto(df_cat, '2025-12')
                            print(f"  Filtrado estricto: {len(df_filtrado)} registros")
                            
                            if len(df_filtrado) == 0:
                                print(f"  ¡ERROR! Filtrado estricto falló para '{categoria}'")
                        else:
                            print(f"  Sin datos en 2025-12")
                    else:
                        print("  Sin fechas válidas")
                        
                except Exception as e:
                    print(f"  Error procesando fechas: {e}")
            else:
                print("  No existe columna 'Fecha'")
        
        # Análisis específico para 'Sub 17'
        print("\n" + "="*80)
        print("ANÁLISIS ESPECÍFICO: CATEGORÍA 'Sub 17'")
        print("="*80)
        
        if 'Sub 17' in categorias:
            df_sub17 = df_pfza[df_pfza['Categoria'] == 'Sub 17'].copy()
            print(f"Registros 'Sub 17': {len(df_sub17)}")
            
            if len(df_sub17) > 0:
                print("\nDatos completos de 'Sub 17':")
                cols_mostrar = ['DNI', 'Apellido', 'Fecha', 'Categoria', 'Fuerza', 'Potencia Pico', 'Altura Salto']
                print(df_sub17[cols_mostrar].to_string())
                
                # Verificar filtrado
                df_filtrado = _filtrar_mes_estricto(df_sub17, '2025-12')
                print(f"\nFiltrado 'Sub 17' por 2025-12: {len(df_filtrado)} registros")
                
                if len(df_filtrado) > 0:
                    print("Filtrado exitoso:")
                    print(df_filtrado[cols_mostrar].to_string())
                else:
                    print("Filtrado falló - investigando causa...")
                    
                    # Depuración detallada
                    print("\nDepuración:")
                    if 'Fecha' in df_sub17.columns:
                        try:
                            df_sub17['Fecha'] = pd.to_datetime(df_sub17['Fecha'], errors='coerce')
                            periodos = df_sub17['Fecha'].dt.to_period('M').astype(str)
                            print(f"Períodos en 'Sub 17': {periodos.dropna().unique()}")
                            
                            mask_2025_12 = periodos == '2025-12'
                            print(f"Registros con período 2025-12: {mask_2025_12.sum()}")
                            
                            if mask_2025_12.sum() > 0:
                                print("Datos encontrados pero filtrado falló")
                                print(df_sub17[mask_2025_12][cols_mostrar].to_string())
                            else:
                                print("Realmente no hay datos en 2025-12")
                                
                        except Exception as e:
                            print(f"Error en depuración: {e}")
        else:
            print("Categoría 'Sub 17' no encontrada")
    
    else:
        print("No existe columna 'Categoria'")

if __name__ == "__main__":
    analisis_completo_categorias()
