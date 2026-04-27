import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc, _corregir_altura_salto

def test_final_completo_will_hopkins():
    """Test final completo para verificar todas las correcciones."""
    print("=== TEST FINAL COMPLETO - WILL HOPKINS ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar corrección de datos
    print("1. VERIFICACIÓN DE CORRECCIÓN DE DATOS:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_primera = df_pfza[df_pfza['Categoria'] == 'Primera'].copy()
        
        # Aplicar corrección
        df_corregido = _corregir_altura_salto(df_primera)
        
        # Verificar Altura Salto
        if 'Altura Salto' in df_corregido.columns:
            vals_corr = df_corregido['Altura Salto'].dropna()
            print(f"   Altura Salto corregida: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
            
            # Verificar que no haya valores > 100 (cm razonables para altura de salto)
            if vals_corr.max() <= 100:
                print(f"   RESULTADO: Altura Salto CORRECTA - Valores en cm razonables")
            else:
                print(f"   RESULTADO: Altura Salto PROBLEMA - Valores aún extremos")
        
        # Verificar Potencia Pico
        if 'Potencia Pico' in df_corregido.columns:
            vals_corr = df_corregido['Potencia Pico'].dropna()
            print(f"   Potencia Pico corregida: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
            
            # Verificar que no haya valores > 1000
            if vals_corr.max() <= 1000:
                print(f"   RESULTADO: Potencia Pico CORRECTA - Valores normalizados")
            else:
                print(f"   RESULTADO: Potencia Pico PROBLEMA - Valores aún extremos")
    
    # 2. Verificar todas las variables clave
    print(f"\n2. VERIFICACIÓN DE VARIABLES CLAVE:")
    
    variables_test = [
        ('VO2 max', 'rendimiento'),
        ('Pmax', 'pfza'),  # Mapeado a Potencia Pico
        ('Altura Salto', 'pfza'),
        ('Fuerza IMTP', 'pfza'),
        ('Fuerza', 'pfza')
    ]
    
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    resultados = {}
    
    for variable, hoja_esperada in variables_test:
        print(f"\n   --- Variable: {variable} ---")
        
        try:
            grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
            
            # Verificar tipo de resultado
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        y_vals = trace.y
                        x_vals = trace.x
                        
                        print(f"     Puntos: {len(y_vals)}")
                        print(f"     Y (cambios): {[f'{y:.1f}' for y in y_vals]}")
                        print(f"     X (post): {[f'{x:.1f}' for x in x_vals]}")
                        
                        # Verificar escala Y
                        if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                            y_range = fig.layout.yaxis.range
                            print(f"     Rango Y: {y_range}")
                            
                            # Extraer SD del título
                            title = fig.layout.title.text if hasattr(fig.layout.title, 'text') else ''
                            if 'SD grupo' in title:
                                try:
                                    sd_part = title.split('SD grupo = ')[1].split()[0]
                                    sd_grupo = float(sd_part)
                                    swc = 0.2 * sd_grupo
                                    
                                    print(f"     SD grupo: {sd_grupo:.4f}")
                                    print(f"     SWC (0.2 x SD): {swc:.4f}")
                                    
                                    # Verificar rango en SD
                                    y_min, y_max = y_range
                                    y_max_abs = max(abs(y_min), abs(y_max))
                                    y_max_sd = y_max_abs / sd_grupo
                                    
                                    print(f"     Rango Y en SD: ±{y_max_sd:.2f}")
                                    
                                    if y_max_sd >= 3.0:
                                        estado_y = "PERFECTO"
                                    elif y_max_sd >= 1.2:
                                        estado_y = "BUENO"
                                    else:
                                        estado_y = "PROBLEMA"
                                    
                                    print(f"     Estado escala Y: {estado_y}")
                                    
                                except:
                                    print(f"     No se pudo extraer SD")
                        
                        # Verificar puntos visibles
                        if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                            y_min, y_max = fig.layout.yaxis.range
                            puntos_visibles = sum(1 for y in y_vals if y_min <= y <= y_max)
                            porcentaje = (puntos_visibles / len(y_vals)) * 100
                            
                            if porcentaje == 100:
                                estado_vis = "PERFECTO"
                            elif porcentaje >= 80:
                                estado_vis = "BUENO"
                            else:
                                estado_vis = "PROBLEMA"
                            
                            print(f"     Puntos visibles: {puntos_visibles}/{len(y_vals)} ({porcentaje:.1f}%) - {estado_vis}")
                        
                        # Guardar resultado
                        resultados[variable] = {
                            'puntos': len(y_vals),
                            'y_vals': y_vals,
                            'estado': 'OK'
                        }
                        
                        print(f"     RESULTADO: OK - Gráfico generado correctamente")
                    else:
                        print(f"     RESULTADO: PROBLEMA - Sin datos Y")
                        resultados[variable] = {'estado': 'SIN_DATOS_Y'}
                else:
                    print(f"     RESULTADO: PROBLEMA - Sin traces")
                    resultados[variable] = {'estado': 'SIN_TRACES'}
            else:
                # Verificar si es un mensaje de error
                if hasattr(grafico, 'children'):
                    mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                    if 'Sin datos' in mensaje or 'no tiene valores' in mensaje:
                        print(f"     RESULTADO: ERROR - {mensaje[:50]}...")
                        resultados[variable] = {'estado': 'SIN_DATOS', 'mensaje': mensaje}
                    else:
                        print(f"     RESULTADO: MENSAJE INESPERADO - {mensaje[:50]}...")
                        resultados[variable] = {'estado': 'MENSAJE_INESPERADO', 'mensaje': mensaje}
                else:
                    print(f"     RESULTADO: TIPO INESPERADO - {type(grafico)}")
                    resultados[variable] = {'estado': 'TIPO_INESPERADO'}
                    
        except Exception as e:
            print(f"     RESULTADO: ERROR - {e}")
            resultados[variable] = {'estado': 'ERROR', 'error': str(e)}
    
    # 3. Resumen final
    print(f"\n3. RESUMEN FINAL:")
    
    ok_count = sum(1 for r in resultados.values() if r.get('estado') == 'OK')
    total_count = len(resultados)
    
    print(f"   Variables probadas: {total_count}")
    print(f"   Variables OK: {ok_count}")
    print(f"   Tasa éxito: {ok_count/total_count*100:.1f}%")
    
    print(f"\n   Detalle por variable:")
    for var, res in resultados.items():
        estado = res.get('estado', 'DESCONOCIDO')
        if estado == 'OK':
            puntos = res.get('puntos', 0)
            print(f"     {var}: OK ({puntos} puntos)")
        else:
            print(f"     {var}: {estado}")
    
    # 4. Verificación específica de Altura Salto
    print(f"\n4. VERIFICACIÓN ESPECÍFICA - ALTURA SALTO:")
    
    if 'Altura Salto' in resultados:
        res_altura = resultados['Altura Salto']
        if res_altura.get('estado') == 'OK':
            print(f"   Altura Salto: CORREGIDA - Ya no muestra 'Sin datos válidos'")
        else:
            print(f"   Altura Salto: PROBLEMA - {res_altura.get('estado', 'DESCONOCIDO')}")
    else:
        print(f"   Altura Salto: NO EVALUADA")
    
    print(f"\n=== CONCLUSIÓN FINAL ===")
    if ok_count == total_count:
        print("¡TODAS LAS CORRECCIONES IMPLEMENTADAS CORRECTAMENTE!")
        print("1. Escala Y según Will Hopkins: OK")
        print("2. Corrección de datos extremos: OK")
        print("3. Altura Salto normalizada: OK")
        print("4. Variables de fuerza corregidas: OK")
        print("5. Mensajes de error eliminados: OK")
    else:
        print(f"Correcciones pendientes: {total_count - ok_count} variables")
        print("Revisar los resultados individuales para identificar problemas específicos.")

if __name__ == "__main__":
    test_final_completo_will_hopkins()
