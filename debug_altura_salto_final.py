import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc, _corregir_altura_salto

def debug_altura_salto_final():
    """Debug específico para Altura Salto."""
    print("=== DEBUG ALTURA SALTO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    variable = 'Altura Salto'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Variables: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    # 1. Verificar datos crudos
    print(f"\n1. DATOS CRUDOS:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_cat = df_pfza[df_pfza['Categoria'] == categoria].copy()
        
        print(f"   Registros totales: {len(df_cat)}")
        
        if 'Altura Salto' in df_cat.columns:
            vals_orig = df_cat['Altura Salto'].dropna()
            print(f"   Valores originales: {len(vals_orig)}")
            print(f"   Rango: {vals_orig.min():.2f} - {vals_orig.max():.2f}")
            print(f"   Valores: {sorted(vals_orig.values)}")
        else:
            print(f"   ERROR: 'Altura Salto' no encontrada en pfza")
            return
    
    # 2. Verificar datos corregidos
    print(f"\n2. DATOS CORREGIDOS:")
    
    df_corregido = _corregir_altura_salto(df_cat)
    
    if 'Altura Salto' in df_corregido.columns:
        vals_corr = df_corregido['Altura Salto'].dropna()
        print(f"   Valores corregidos: {len(vals_corr)}")
        print(f"   Rango: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
        print(f"   Valores: {sorted(vals_corr.values)}")
        
        # Verificar si la corrección fue efectiva
        max_orig = vals_orig.max() if len(vals_orig) > 0 else 0
        max_corr = vals_corr.max() if len(vals_corr) > 0 else 0
        
        if max_orig > 200 and max_corr < 200:
            print(f"   CORRECCIÓN: EFECTIVA - Valores extremos normalizados")
        elif max_orig <= 200:
            print(f"   CORRECCIÓN: NO NECESARIA - Valores ya razonables")
        else:
            print(f"   CORRECCIÓN: INEFECTIVA - Valores aún extremos")
    
    # 3. Simular el proceso completo
    print(f"\n3. SIMULACIÓN DEL PROCESO COMPLETO:")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        print(f"   Tipo de gráfico: {type(grafico)}")
        
        if hasattr(grafico, 'figure'):
            print(f"   TIPO: Figura Plotly - DEBERÍA FUNCIONAR")
            fig = grafico.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                if hasattr(trace, 'y') and trace.y is not None:
                    print(f"   Puntos: {len(trace.y)}")
                    print(f"   Y: {trace.y}")
                    print(f"   RESULTADO: GRÁFICO FUNCIONANDO")
                else:
                    print(f"   RESULTADO: SIN DATOS Y")
            else:
                print(f"   RESULTADO: SIN TRACES")
        else:
            print(f"   TIPO: Componente Dash - VERIFICANDO MENSAJE")
            
            if hasattr(grafico, 'children'):
                print(f"   Hijos: {len(grafico.children)}")
                
                for i, hijo in enumerate(grafico.children):
                    print(f"   Hijo {i}: {type(hijo)}")
                    if hasattr(hijo, 'children'):
                        print(f"      Subhijos: {len(hijo.children)}")
                        for j, subhijo in enumerate(hijo.children):
                            if hasattr(subhijo, 'children') and len(subhijo.children) > 0:
                                texto = str(subhijo.children[0])
                                print(f"      Subhijo {j}: {texto}")
                                if 'Sin datos' in texto or 'válidos' in texto:
                                    print(f"      ¡MENSAJE DE ERROR ENCONTRADO!")
                                    print(f"      Texto completo: {texto}")
                                    
                                    # Analizar el problema
                                    if 'no tiene valores válidos' in texto:
                                        print(f"      CAUSA: La variable no tiene valores válidos")
                                    elif 'Sin datos válidos para los meses' in texto:
                                        print(f"      CAUSA: No hay datos en ambos meses")
                                    elif 'Solo' in texto and 'dato' in texto:
                                        print(f"      CAUSA: Insuficientes datos (< 2)")
                                    
                                    # Verificar valores válidos
                                    vals_corr = df_corregido['Altura Salto'].dropna()
                                    print(f"      Valores válidos en datos corregidos: {len(vals_corr)}")
                                    
                                    if len(vals_corr) == 0:
                                        print(f"      ¡PROBLEMA! Todos los valores son NaN después de corrección")
                                    else:
                                        print(f"      Valores válidos encontrados: {sorted(vals_corr.values)}")
                                        
                                        # Verificar filtrado por mes
                                        from pages.swc_page import _filtrar_mes_estricto
                                        
                                        pre_cat = _filtrar_mes_estricto(df_corregido, mes_pre)
                                        post_cat = _filtrar_mes_estricto(df_corregido, mes_post)
                                        
                                        print(f"      Registros Pre: {len(pre_cat)}")
                                        print(f"      Registros Post: {len(post_cat)}")
                                        
                                        if len(pre_cat) > 0:
                                            pre_vals = pre_cat['Altura Salto'].dropna()
                                            print(f"      Valores Pre válidos: {len(pre_vals)}")
                                        
                                        if len(post_cat) > 0:
                                            post_vals = post_cat['Altura Salto'].dropna()
                                            print(f"      Valores Post válidos: {len(post_vals)}")
                                        
                                        if len(pre_vals) < 2:
                                            print(f"      ¡PROBLEMA! Menos de 2 valores Pre para calcular SD")
                                        
                                        if len(pre_vals) == 0 or len(post_vals) == 0:
                                            print(f"      ¡PROBLEMA! No hay datos en Pre o Post")
                            
                            break
                    elif hasattr(hijo, 'props') and 'children' in hijo.props:
                        texto = str(hijo.props['children'])
                        print(f"      Texto props: {texto[:100]}...")
            else:
                print(f"   Sin hijos - Componente vacío")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_altura_salto_final()
