import pandas as pd
from data_loader import load_data
from pages.swc_page import _filtrar_mes_estricto, _corregir_altura_salto

def investigar_eje_y_1500():
    """Investigar por qué el eje Y muestra rangos de 1500 a -1500."""
    print("=== INVESTIGACIÓN - EJE Y CON RANGO 1500 A -1500 ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Simular el cálculo que hace el sistema para diferentes variables
    categorias = ['Primera', 'Sub 15', 'Sub 16']
    variables = ['Fuerza', 'Potencia Pico', 'Altura Salto', 'Fuerza IMTP']
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    for categoria in categorias:
        print(f"=== CATEGORÍA: {categoria} ===")
        
        if 'pfza' in data:
            df_pfza = data['pfza']
            df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
            
            pre_cat = _filtrar_mes_estricto(df_cat, mes_pre)
            post_cat = _filtrar_mes_estricto(df_cat, mes_post)
            
            print(f"Registros Pre: {len(pre_cat)}, Post: {len(post_cat)}")
            
            if len(pre_cat) > 0 and len(post_cat) > 0:
                for variable in variables:
                    if variable in pre_cat.columns and variable in post_cat.columns:
                        print(f"\n--- Variable: {variable} ---")
                        
                        # Calcular cambios como lo hace el sistema
                        cambios = []
                        for _, row_pre in pre_cat.iterrows():
                            apellido = row_pre['Apellido']
                            pre_val = row_pre[variable]
                            
                            if pd.notna(pre_val):
                                row_post = post_cat[post_cat['Apellido'] == apellido]
                                if len(row_post) > 0:
                                    post_val = row_post.iloc[0][variable]
                                    if pd.notna(post_val):
                                        cambio = post_val - pre_val
                                        cambios.append(cambio)
                                        print(f"  {apellido}: {post_val:.2f} - {pre_val:.2f} = {cambio:+.2f}")
                        
                        if cambios:
                            # Simular el cálculo del rango Y
                            SWC = 0.2
                            max_cambio_abs = max(abs(c) for c in cambios)
                            min_swc_range = 6 * SWC  # 1.2
                            
                            print(f"  Cambios: {min(cambios):+.2f} a {max(cambios):+.2f}")
                            print(f"  Máximo cambio absoluto: {max_cambio_abs:.2f}")
                            print(f"  Mínimo rango SWC: {min_swc_range:.2f}")
                            
                            # Lógica actual del sistema
                            if max_cambio_abs > min_swc_range * 10:  # > 12
                                y_max_abs = max(min_swc_range * 3, max_cambio_abs * 0.1)
                                print(f"  Cambios grandes -> Y range: ±{y_max_abs:.2f}")
                            else:
                                y_max_abs = max(max_cambio_abs, min_swc_range) * 1.3
                                print(f"  Cambios normales -> Y range: ±{y_max_abs:.2f}")
                            
                            # Verificar si esto explica el rango de 1500
                            if y_max_abs >= 1500:
                                print(f"  ¡PROBLEMA! Rango Y demasiado grande: {y_max_abs:.2f}")
                                print(f"  Causa: max_cambio_abs ({max_cambio_abs:.2f}) * 0.1 = {max_cambio_abs * 0.1:.2f}")
                                print(f"  O min_swc_range * 3 = {min_swc_range * 3:.2f}")
                            else:
                                print(f"  Rango Y aceptable: ±{y_max_abs:.2f}")
                        else:
                            print(f"  Sin cambios válidos para {variable}")
                    else:
                        print(f"\n--- Variable: {variable} ---")
                        print(f"  No existe en las columnas")
            else:
                print("No hay datos para comparar")
        print()

def proponer_solucion():
    """Proponer solución para el problema del rango Y."""
    print("\n=== SOLUCIÓN PROPUESTA ===\n")
    print("Problema identificado:")
    print("1. Para cambios muy grandes (> 12), el sistema usa: max(min_swc_range * 3, max_cambio_abs * 0.1)")
    print("2. Si max_cambio_abs es 15000, entonces max_cambio_abs * 0.1 = 1500")
    print("3. Esto causa rangos Y de ±1500 que son demasiado grandes")
    print("\nSolución:")
    print("1. Limitar el rango Y máximo a un valor razonable (ej: ±50 para cambios normales)")
    print("2. Usar una escala logarítmica para cambios muy grandes")
    print("3. Ajustar el factor de 0.1 a un valor más pequeño")
    print("4. Validar los datos antes de calcular cambios")

if __name__ == "__main__":
    investigar_eje_y_1500()
    proponer_solucion()
