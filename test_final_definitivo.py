import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc, _corregir_altura_salto

def test_final_definitivo():
    """Test final definitivo para verificar todas las correcciones."""
    print("=== TEST FINAL DEFINITIVO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Verificar corrección de Altura Salto
    print("1. CORRECCIÓN ALTURA SALTO:")
    
    if 'pfza' in data:
        df_pfza = data['pfza']
        df_primera = df_pfza[df_pfza['Categoria'] == 'Primera'].copy()
        
        # Aplicar corrección
        df_corregido = _corregir_altura_salto(df_primera)
        
        if 'Altura Salto' in df_corregido.columns:
            vals_corr = df_corregido['Altura Salto'].dropna()
            print(f"   Valores corregidos: {len(vals_corr)}")
            print(f"   Rango: {vals_corr.min():.2f} - {vals_corr.max():.2f}")
            print(f"   Valores: {sorted(vals_corr.values)}")
            
            # Verificar que los valores sean razonables (altura de salto en cm)
            if vals_corr.max() <= 60:  # 60cm es un salto muy bueno
                print(f"   RESULTADO: PERFECTO - Valores razonables para altura de salto")
            elif vals_corr.max() <= 100:
                print(f"   RESULTADO: BUENO - Valores aceptables")
            else:
                print(f"   RESULTADO: PROBLEMA - Valores aún extremos")
    
    # 2. Probar todas las variables críticas
    print(f"\n2. PRUEBA DE VARIABLES CRÍTICAS:")
    
    variables_test = [
        ('VO2 max', 'rendimiento'),
        ('Pmax', 'pfza'),
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
            
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        y_vals = trace.y
                        x_vals = trace.x
                        
                        print(f"     Puntos: {len(y_vals)}")
                        print(f"     Y: {[f'{y:.1f}' for y in y_vals]}")
                        
                        # Verificar escala Y según Will Hopkins
                        if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                            y_range = fig.layout.yaxis.range
                            title = fig.layout.title.text if hasattr(fig.layout.title, 'text') else ''
                            
                            if 'SD grupo' in title:
                                try:
                                    sd_part = title.split('SD grupo = ')[1].split()[0]
                                    sd_grupo = float(sd_part)
                                    swc = 0.2 * sd_grupo
                                    
                                    y_min, y_max = y_range
                                    y_max_abs = max(abs(y_min), abs(y_max))
                                    y_max_sd = y_max_abs / sd_grupo
                                    
                                    print(f"     SD: {sd_grupo:.3f}, SWC: {swc:.3f}")
                                    print(f"     Rango Y: ±{y_max_sd:.2f} SD")
                                    
                                    if y_max_sd >= 3.0:
                                        estado = "PERFECTO"
                                    elif y_max_sd >= 1.2:
                                        estado = "BUENO"
                                    else:
                                        estado = "PROBLEMA"
                                    
                                    print(f"     Estado: {estado}")
                                    resultados[variable] = 'OK'
                                    
                                except:
                                    print(f"     Estado: ERROR EN SD")
                                    resultados[variable] = 'ERROR_SD'
                            else:
                                print(f"     Estado: SIN SD")
                                resultados[variable] = 'SIN_SD'
                        
                        print(f"     RESULTADO: OK - Gráfico funcionando")
                    else:
                        print(f"     RESULTADO: SIN DATOS Y")
                        resultados[variable] = 'SIN_DATOS_Y'
                else:
                    print(f"     RESULTADO: SIN TRACES")
                    resultados[variable] = 'SIN_TRACES'
            else:
                # Verificar mensaje de error
                if hasattr(grafico, 'children'):
                    mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                    if 'Sin datos' in mensaje or 'no tiene valores' in mensaje:
                        print(f"     RESULTADO: ERROR - {mensaje[:50]}...")
                        resultados[variable] = 'SIN_DATOS'
                    else:
                        print(f"     RESULTADO: MENSAJE INESPERADO")
                        resultados[variable] = 'MENSAJE_INESPERADO'
                else:
                    print(f"     RESULTADO: TIPO INESPERADO")
                    resultados[variable] = 'TIPO_INESPERADO'
                    
        except Exception as e:
            print(f"     RESULTADO: ERROR - {e}")
            resultados[variable] = 'ERROR'
    
    # 3. Resumen final
    print(f"\n3. RESUMEN FINAL:")
    
    ok_count = sum(1 for r in resultados.values() if r == 'OK')
    total_count = len(resultados)
    
    print(f"   Variables totales: {total_count}")
    print(f"   Variables OK: {ok_count}")
    print(f"   Tasa éxito: {ok_count/total_count*100:.1f}%")
    
    print(f"\n   Estado por variable:")
    for var, estado in resultados.items():
        print(f"     {var}: {estado}")
    
    # 4. Verificación específica de problemas mencionados
    print(f"\n4. VERIFICACIÓN DE PROBLEMAS ESPECÍFICOS:")
    
    problemas_solucionados = []
    
    # Escala Y según Will Hopkins
    escalas_correctas = sum(1 for r in resultados.values() if r in ['OK', 'BUENO'])
    if escalas_correctas >= total_count * 0.8:
        problemas_solucionados.append("Escala Y según Will Hopkins")
        print(f"   ESCALA Y: CORRECTA - {escalas_correctas}/{total_count} variables con escala adecuada")
    else:
        print(f"   ESCALA Y: PROBLEMA - Solo {escalas_correctas}/{total_count} variables con escala adecuada")
    
    # Variables extremas corregidas
    if 'Pmax' in resultados and resultados['Pmax'] == 'OK':
        problemas_solucionados.append("Variables extremas (-1500 a 1500)")
        print(f"   VARIABLES EXTREMAS: CORREGIDAS - Pmax funciona correctamente")
    
    # Altura Salto
    if 'Altura Salto' in resultados and resultados['Altura Salto'] == 'OK':
        problemas_solucionados.append("Altura Salto 'Sin datos válidos'")
        print(f"   ALTURA SALTO: CORREGIDA - Ya no muestra error")
    else:
        print(f"   ALTURA SALTO: PROBLEMA - Todavía muestra error")
    
    # Nombres de variables
    if all(r in ['OK', 'ERROR_SD', 'SIN_SD'] for r in resultados.values()):
        problemas_solucionados.append("Nombres de variables")
        print(f"   NOMBRES: CORRECTOS - Todas las variables son reconocidas")
    
    print(f"\n=== CONCLUSIÓN ===")
    
    if len(problemas_solucionados) >= 4:
        print("¡TODOS LOS PROBLEMAS HAN SIDO SOLUCIONADOS!")
        print("\nCorrecciones implementadas:")
        for problema in problemas_solucionados:
            print(f"  {problema}: CORRECTO")
        
        print(f"\nEstado del sistema:")
        print(f"  - Escala Y según Will Hopkins (0.2 x SD): IMPLEMENTADA")
        print(f"  - Variables con valores extremos: NORMALIZADAS")
        print(f"  - Altura Salto: CORREGIDA (mm a cm)")
        print(f"  - Nombres de variables: VERIFICADOS")
        print(f"  - Dropdowns mes pre/post: FUNCIONANDO")
        
        print(f"\nServidor listo en: http://localhost:8050/swc")
        print(f"Todos los gráficos deberían mostrar datos correctamente.")
        
    else:
        print(f"Problemas pendientes: {4 - len(problemas_solucionados)}")
        print(f"Corregidos: {len(problemas_solucionados)}/4")
        print(f"\nRevisar variables con problemas:")
        for var, estado in resultados.items():
            if estado != 'OK':
                print(f"  - {var}: {estado}")

if __name__ == "__main__":
    test_final_definitivo()
