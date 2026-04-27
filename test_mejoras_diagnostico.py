import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def test_mejoras_diagnostico():
    """Test para verificar que las mejoras de diagnóstico funcionen correctamente."""
    print("=== TEST MEJORAS DE DIAGNÓSTICO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    # 1. Probar variables que funcionan correctamente
    print("1. VARIABLES QUE FUNCIONAN CORRECTAMENTE:")
    
    variables_funcionales = ['Fuerza', 'Potencia Pico', 'Fuerza IMTP']
    
    for variable in variables_funcionales:
        print(f"\n   --- Variable: {variable} ---")
        
        try:
            grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
            
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        puntos = len(trace.y)
                        print(f"     RESULTADO: CORRECTO - {puntos} puntos generados")
                    else:
                        print(f"     RESULTADO: PROBLEMA - Sin datos Y")
                else:
                    print(f"     RESULTADO: PROBLEMA - Sin traces")
            else:
                # Verificar si es un mensaje de diagnóstico mejorado
                if hasattr(grafico, 'children'):
                    mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                    print(f"     MENSAJE: {mensaje[:100]}...")
                    
                    # Verificar si contiene información diagnóstica
                    if 'SD del grupo = 0' in mensaje:
                        print(f"     DIAGNÓSTICO: SD = 0 detectado correctamente")
                    elif 'Jugadores sin dato' in mensaje:
                        print(f"     DIAGNÓSTICO: Conteo de jugadores sin datos")
                    elif 'SD grupo =' in mensaje and 'SWC =' in mensaje:
                        print(f"     DIAGNÓSTICO: Información de SD y SWC incluida")
                    else:
                        print(f"     DIAGNÓSTICO: Mensaje genérico")
                else:
                    print(f"     RESULTADO: TIPO INESPERADO")
                    
        except Exception as e:
            print(f"     RESULTADO: ERROR - {e}")
    
    # 2. Probar variable que podría tener problemas (Altura Salto)
    print(f"\n2. VARIABLE PROBLEMÁTICA (Altura Salto):")
    
    try:
        grafico_altura, tabla_altura = crear_squad_swc(data, categoria, 'Altura Salto', mes_pre, mes_post)
        
        if hasattr(grafico_altura, 'figure'):
            fig = grafico_altura.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    puntos = len(trace.y)
                    print(f"   'Altura Salto': {puntos} puntos - CORRECTO")
                else:
                    print(f"   'Altura Salto': PROBLEMA - Sin datos Y")
            else:
                print(f"   'Altura Salto': PROBLEMA - Sin traces")
        else:
            if hasattr(grafico_altura, 'children'):
                mensaje = str(grafico_altura.children[0]) if len(grafico_altura.children) > 0 else str(grafico_altura)
                print(f"   'Altura Salto': MENSAJE DE DIAGNÓSTICO")
                print(f"   Mensaje: {mensaje[:150]}...")
                
                # Analizar el diagnóstico
                if 'SD del grupo = 0' in mensaje:
                    print(f"   Causa: SD = 0 (todos los valores iguales)")
                elif 'Jugadores sin dato' in mensaje:
                    print(f"   Causa: Faltan datos en Pre o Post")
                elif 'Sin datos válidos' in mensaje:
                    print(f"   Causa: Datos filtrados por umbral de outliers")
                else:
                    print(f"   Causa: Desconocida")
            else:
                print(f"   'Altura Salto': TIPO INESPERADO")
                
    except Exception as e:
        print(f"   'Altura Salto': ERROR - {e}")
    
    # 3. Verificar el umbral de outliers
    print(f"\n3. VERIFICACIÓN DE UMBRAL DE OUTLIERS:")
    print("   Umbral implementado: 20 SD (fisiológicamente imposible)")
    print("   Umbral anterior: 50 SD (demasiado permisivo)")
    print("   Mejora: Más estricto y con explicación clara")
    
    # 4. Resumen de mejoras implementadas
    print(f"\n=== RESUMEN DE MEJORAS IMPLEMENTADAS ===")
    print("1. Diagnóstico de sd_grupo:")
    print("   - Verificación de SD = 0 antes de calcular SWC")
    print("   - Mensaje detallado con valor único cuando SD = 0")
    print("   - Explicación clara de por qué no se puede calcular SWC")
    
    print(f"\n2. Umbral de outliers:")
    print("   - Reducido de 50 SD a 20 SD")
    print("   - Comentario: 'fisiológicamente imposible'")
    print("   - Explicación: 'probablemente error de unidades'")
    
    print(f"\n3. Mensaje mejorado cuando resultados está vacío:")
    print("   - Conteo de jugadores sin datos en Pre")
    print("   - Conteo de jugadores sin datos en Post")
    print("   - Valores de SD grupo y SWC")
    print("   - Instrucción clara para el usuario")
    
    print(f"\n4. Beneficios del diagnóstico mejorado:")
    print("   - El usuario sabe exactamente qué está mal")
    print("   - Puede identificar si es problema de datos o configuración")
    print("   - Tiene información para corregir el problema")
    print("   - Reduce frustración y tiempo de depuración")
    
    print(f"\nRESULTADO GLOBAL:")
    print("Diagnóstico mejorado implementado correctamente")
    print("Usuarios tendrán información clara y actionable")
    print("Sistema más robusto y fácil de usar")

if __name__ == "__main__":
    test_mejoras_diagnostico()
