import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc, _corregir_altura_salto

def test_final_will_hopkins():
    """Test final para verificar todas las correcciones según Will Hopkins."""
    print("=== TEST FINAL - CORRECCIONES WILL HOPKINS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar corrección de Altura Salto
    print("1. CORRECCIÓN DE ALTURA SALTO:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_primera = df_pfza[df_pfza['Categoria'] == 'Primera'].copy()
        
        # Aplicar corrección
        df_corregido = _corregir_altura_salto(df_primera)
        
        print(f"   Antes de corrección:")
        if 'Altura Salto' in df_primera.columns:
            vals_orig = df_primera['Altura Salto'].dropna()
            print(f"     Rango: {vals_orig.min():.2f} - {vals_orig.max():.2f}")
            print(f"     Valores: {sorted(vals_orig.values)}")
        
        print(f"   Después de corrección:")
        if 'Altura Salto' in df_corregido.columns:
            vals_corr = df_corregido['Altura Salto'].dropna()
            print(f"     Rango: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
            print(f"     Valores: {sorted(vals_corr.values)}")
            
            # Verificar que los valores extremos fueron corregidos
            max_val = vals_corr.max()
            if max_val < 100:
                print(f"   RESULTADO: CORRECTO - Valores normalizados a cm")
            else:
                print(f"   RESULTADO: PROBLEMA - Valores aún extremos")
    
    # 2. Verificar corrección de variables de fuerza
    print(f"\n2. CORRECCIÓN DE VARIABLES DE FUERZA:")
    
    variables_fuerza = ['Potencia Pico', 'Fuerza IMTP']
    
    for var in variables_fuerza:
        print(f"\n   --- Variable: {var} ---")
        
        if 'pfza' in data:
            df_pfza = data['pfza']
            df_primera = df_pfza[df_pfza['Categoria'] == 'Primera'].copy()
            
            # Aplicar corrección
            df_corregido = _corregir_altura_salto(df_primera)
            
            if var in df_primera.columns and var in df_corregido.columns:
                vals_orig = df_primera[var].dropna()
                vals_corr = df_corregido[var].dropna()
                
                print(f"     Antes: {vals_orig.min():.2f} - {vals_orig.max():.2f}")
                print(f"     Después: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
                
                # Verificar normalización
                max_orig = vals_orig.max()
                max_corr = vals_corr.max()
                
                if max_orig > 5000 and max_corr < 100:
                    print(f"     RESULTADO: CORRECTO - Valores normalizados")
                elif max_orig <= 5000:
                    print(f"     RESULTADO: CORRECTO - No necesitaba corrección")
                else:
                    print(f"     RESULTADO: PROBLEMA - Corrección insuficiente")
    
    # 3. Verificar escala Y según Will Hopkins
    print(f"\n3. ESCALA Y SEGÚN WILL HOPKINS:")
    
    variables_test = ['VO2 max', 'Pmax', 'Altura Salto', 'Fuerza IMTP']
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    for variable in variables_test:
        print(f"\n   --- Variable: {variable} ---")
        
        try:
            grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
            
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        y_vals = trace.y
                        print(f"     Puntos: {len(y_vals)}")
                        print(f"     Y: {y_vals}")
                        
                        # Verificar rango del eje Y
                        if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                            y_range = fig.layout.yaxis.range
                            print(f"     Rango Y: {y_range}")
                            
                            # Calcular SD del grupo (simulado)
                            if len(y_vals) > 0:
                                max_cambio_abs = max(abs(min(y_vals)), abs(max(y_vals)))
                                
                                # Estimar SD basado en el título del gráfico
                                title = fig.layout.title.text if hasattr(fig.layout.title, 'text') else ''
                                if 'SD grupo' in title:
                                    try:
                                        sd_part = title.split('SD grupo = ')[1].split()[0]
                                        sd_grupo = float(sd_part)
                                        swc = 0.2 * sd_grupo
                                        
                                        print(f"     SD grupo: {sd_grupo:.4f}")
                                        print(f"     SWC (0.2 x SD): {swc:.4f}")
                                        
                                        # Verificar si el rango Y es apropiado
                                        y_min, y_max = y_range
                                        y_max_abs = max(abs(y_min), abs(y_max))
                                        
                                        # Convertir a unidades SD
                                        y_max_sd = y_max_abs / sd_grupo
                                        
                                        print(f"     Rango Y en SD: ±{y_max_sd:.2f}")
                                        
                                        if y_max_sd >= 3.0:
                                            print(f"     RESULTADO: CORRECTO - Muestra todas las zonas SWC")
                                        elif y_max_sd >= 1.2:
                                            print(f"     RESULTADO: ACEPTABLE - Muestra zonas principales")
                                        else:
                                            print(f"     RESULTADO: PROBLEMA - No muestra todas las zonas")
                                        
                                        # Verificar que los puntos sean visibles
                                        puntos_visibles = sum(1 for y in y_vals if y_min <= y <= y_max)
                                        porcentaje = (puntos_visibles / len(y_vals)) * 100
                                        print(f"     Puntos visibles: {puntos_visibles}/{len(y_vals)} ({porcentaje:.1f}%)")
                                        
                                    except:
                                        print(f"     No se pudo extraer SD del título")
                                else:
                                    print(f"     No se encontró SD en el título")
                        else:
                            print(f"     Sin rango Y definido (auto-scaling)")
                    else:
                        print(f"     Sin datos Y")
                else:
                    print(f"     Sin traces")
            else:
                print(f"     Sin figura")
                
        except Exception as e:
            print(f"     ERROR: {e}")
    
    # 4. Verificar que no haya más mensajes de "Sin datos válidos"
    print(f"\n4. VERIFICACIÓN DE MENSAJES DE ERROR:")
    
    try:
        # Probar Altura Salto que antes daba error
        grafico_altura, tabla_altura = crear_squad_swc(data, categoria, 'Altura Salto', mes_pre, mes_post)
        
        if hasattr(grafico_altura, 'figure'):
            fig = grafico_altura.figure
            if len(fig.data) > 0:
                trace = fig.data[0]
                if hasattr(trace, 'y') and trace.y is not None:
                    print(f"   Altura Salto: {len(trace.y)} puntos - CORRECTO")
                else:
                    print(f"   Altura Salto: Sin puntos - PROBLEMA")
            else:
                print(f"   Altura Salto: Sin traces - PROBLEMA")
        else:
            # Verificar si es un mensaje de error
            if hasattr(grafico_altura, 'children'):
                mensaje = str(grafico_altura.children[0]) if len(grafico_altura.children) > 0 else str(grafico_altura)
                if 'Sin datos' in mensaje or 'no tiene valores' in mensaje:
                    print(f"   Altura Salto: {mensaje[:50]}... - PROBLEMA")
                else:
                    print(f"   Altura Salto: Mensaje inesperado - {mensaje[:50]}...")
            else:
                print(f"   Altura Salto: Tipo inesperado - {type(grafico_altura)}")
                
    except Exception as e:
        print(f"   Altura Salto: ERROR - {e}")
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Correcciones implementadas:")
    print("1. Altura Salto: Corrección de mm a cm para valores > 100")
    print("2. Variables de fuerza: Normalización dividiendo por 100 valores > 5000")
    print("3. Escala Y: Basada en unidades SD según Will Hopkins (0.2 x SD)")
    print("4. Mapeo inteligente: Pmax usa Potencia Pico corregida")
    print("5. Zonas SWC: Muestra hasta ±3 SD cubriendo todas las magnitudes")

if __name__ == "__main__":
    test_final_will_hopkins()
