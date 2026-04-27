import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def test_rangos_asimetricos():
    """Test para verificar que los rangos del eje Y sean asimétricos y basados en datos reales."""
    print("=== TEST RANGOS ASIMÉTRICOS DEL EJE Y ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    # Probar diferentes variables para ver cómo se comportan los rangos
    variables_test = [
        'Fuerza',           # Datos positivos
        'Potencia Pico',    # Datos negativos
        'Fuerza IMTP',      # Datos mixtos
        'RFD Dec',          # Datos negativos
    ]
    
    for variable in variables_test:
        print(f"\n--- Variable: {variable} ---")
        
        try:
            grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
            
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        valores_y = trace.y
                        puntos = len(valores_y)
                        
                        print(f"   Puntos generados: {puntos}")
                        print(f"   Valores Y: {[f'{y:.1f}' for y in valores_y]}")
                        
                        # Analizar el rango del eje Y
                        y_min = min(valores_y)
                        y_max = max(valores_y)
                        print(f"   Rango de datos: {y_min:.1f} a {y_max:.1f}")
                        
                        # Verificar el rango del gráfico
                        if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                            rango_grafico = fig.layout.yaxis.range
                            print(f"   Rango del gráfico: [{rango_grafico[0]:.1f}, {rango_grafico[1]:.1f}]")
                            
                            # Verificar si es asimétrico
                            if rango_grafico[0] != -rango_grafico[1]:
                                print(f"   Rango: ASIMÉTRICO (correcto)")
                            else:
                                print(f"   Rango: SIMÉTRICO (incorrecto)")
                            
                            # Verificar si todos los datos son visibles
                            if rango_grafico[0] <= y_min and rango_grafico[1] >= y_max:
                                print(f"   Visibilidad: CORRECTA - todos los datos visibles")
                            else:
                                print(f"   Visibilidad: PROBLEMA - algunos datos fuera del rango")
                            
                            # Verificar que las zonas SWC sean visibles
                            swc_estimado = abs(y_max - y_min) * 0.1  # Estimación aproximada
                            if abs(rango_grafico[0]) >= swc_estimado and abs(rango_grafico[1]) >= swc_estimado:
                                print(f"   Zonas SWC: CORRECTAS - visibles")
                            else:
                                print(f"   Zonas SWC: PROBLEMA - pueden no ser visibles")
                        else:
                            print(f"   Rango del gráfico: NO DEFINIDO")
                        
                        # Verificar título
                        if hasattr(fig.layout, 'title') and hasattr(fig.layout.title, 'text'):
                            titulo = fig.layout.title.text
                            print(f"   Título: {titulo}")
                        
                    else:
                        print(f"   RESULTADO: PROBLEMA - Sin datos Y")
                else:
                    print(f"   RESULTADO: PROBLEMA - Sin traces")
            else:
                # Verificar si es un mensaje de error
                if hasattr(grafico, 'children'):
                    mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                    print(f"   RESULTADO: ERROR - {mensaje[:50]}...")
                else:
                    print(f"   RESULTADO: TIPO INESPERADO")
                    
        except Exception as e:
            print(f"   RESULTADO: ERROR - {e}")
    
    print(f"\n=== ANÁLISIS DE CORRECCIONES ===")
    print("Cambios implementados:")
    print("1. Cálculo asimétrico basado en datos reales")
    print("   - y_plot_min = cambio_min - margen")
    print("   - y_plot_max = cambio_max + margen")
    print("2. Bandas ajustadas al rango real")
    print("   - y_banda_min = y_plot_min")
    print("   - y_banda_max = y_plot_max")
    print("3. Etiquetas de zona ajustadas")
    print("   - Usan y_banda_min y y_banda_max")
    print("4. Eliminación de simetría forzada")
    print("   - No más [-y_max_abs, y_max_abs]")
    print("   - Rango se ajusta a los datos reales")
    
    print(f"\nRESULTADO ESPERADO:")
    print("- Ejes Y asimétricos para datos negativos")
    print("- Zonas SWC siempre visibles")
    print("- Rangos optimizados para cada variable")
    print("- Sin espacios vacíos innecesarios")

if __name__ == "__main__":
    test_rangos_asimetricos()
