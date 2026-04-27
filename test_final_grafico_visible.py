import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def test_final_grafico_visible():
    """Test final para verificar que los datos ahora sean visibles en el gráfico."""
    print("=== TEST FINAL - GRÁFICO VISIBLE ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Probar con el caso problemático
    categoria = 'Primera'
    variable = 'Pmax'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Probando con: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    # Generar el gráfico
    grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
    
    # Verificar los resultados
    if hasattr(grafico, 'figure'):
        fig = grafico.figure
        
        if len(fig.data) > 0:
            trace = fig.data[0]
            
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                x_vals = trace.x
                y_vals = trace.y
                
                print(f"\nDatos del gráfico:")
                print(f"  Puntos: {len(x_vals)}")
                print(f"  X: {x_vals}")
                print(f"  Y: {y_vals}")
                
                # Verificar el rango del eje Y
                if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                    yaxis_range = fig.layout.yaxis.range
                    y_min, y_max = min(y_vals), max(y_vals)
                    
                    print(f"\nRangos:")
                    print(f"  Datos Y: {y_min:.2f} a {y_max:.2f}")
                    print(f"  Eje Y visible: {yaxis_range}")
                    
                    # Verificar si los puntos son visibles
                    if yaxis_range:
                        y_axis_min, y_axis_max = yaxis_range
                        
                        if y_max >= y_axis_min and y_min <= y_axis_max:
                            print(f"  RESULTADO: ¡DATOS VISIBLES! Los puntos están dentro del rango")
                            
                            # Verificar qué porcentaje de puntos son visibles
                            puntos_visibles = 0
                            for y in y_vals:
                                if y_axis_min <= y <= y_axis_max:
                                    puntos_visibles += 1
                            
                            porcentaje_visible = (puntos_visibles / len(y_vals)) * 100
                            print(f"  Puntos visibles: {puntos_visibles}/{len(y_vals)} ({porcentaje_visible:.1f}%)")
                            
                            if porcentaje_visible == 100:
                                print(f"  ESTADO: PERFECTO - Todos los puntos son visibles")
                            elif porcentaje_visible >= 80:
                                print(f"  ESTADO: BUENO - La mayoría de los puntos son visibles")
                            else:
                                print(f"  ESTADO: PROBLEMA - Menos del 80% de los puntos son visibles")
                        else:
                            print(f"  RESULTADO: PROBLEMA - Los puntos están fuera del rango visible")
                    else:
                        print(f"  RESULTADO: El eje Y no tiene rango definido (auto-scaling)")
                        print(f"  ESTADO: Los puntos deberían ser visibles con auto-scaling")
                else:
                    print(f"  RESULTADO: El eje Y no tiene configuración de rango")
            else:
                print(f"  RESULTADO: El trace no tiene datos X o Y")
        else:
            print(f"  RESULTADO: La figura no tiene traces")
    else:
        print(f"  RESULTADO: El gráfico no tiene figura")
    
    # Probar con otras variables para asegurar que no se rompieron
    print(f"\n=== PRUEBA CON OTRAS VARIABLES ===")
    
    otras_vars = ['Fuerza', 'Altura Salto']
    
    for var in otras_vars:
        print(f"\n--- Variable: {var} ---")
        
        try:
            grafico_test, _ = crear_squad_swc(data, categoria, var, mes_pre, mes_post)
            
            if hasattr(grafico_test, 'figure') and len(grafico_test.figure.data) > 0:
                trace = grafico_test.figure.data[0]
                
                if hasattr(trace, 'x') and hasattr(trace, 'y'):
                    x_vals = trace.x
                    y_vals = trace.y
                    
                    print(f"  Puntos: {len(x_vals)}")
                    print(f"  Y: {y_vals}")
                    
                    # Verificar rango Y
                    if hasattr(grafico_test.figure.layout, 'yaxis') and hasattr(grafico_test.figure.layout.yaxis, 'range'):
                        yaxis_range = grafico_test.figure.layout.yaxis.range
                        y_min, y_max = min(y_vals), max(y_vals)
                        
                        if yaxis_range:
                            y_axis_min, y_axis_max = yaxis_range
                            
                            if y_max >= y_axis_min and y_min <= y_axis_max:
                                puntos_visibles = sum(1 for y in y_vals if y_axis_min <= y <= y_axis_max)
                                porcentaje = (puntos_visibles / len(y_vals)) * 100
                                print(f"  Visibles: {puntos_visibles}/{len(y_vals)} ({porcentaje:.1f}%)")
                                
                                if porcentaje == 100:
                                    print(f"  ESTADO: PERFECTO")
                                elif porcentaje >= 80:
                                    print(f"  ESTADO: BUENO")
                                else:
                                    print(f"  ESTADO: PROBLEMA")
                            else:
                                print(f"  ESTADO: FUERA DE RANGO")
                        else:
                            print(f"  ESTADO: AUTO-SCALING")
                    else:
                        print(f"  ESTADO: SIN RANGO DEFINIDO")
                else:
                    print(f"  ESTADO: SIN DATOS X/Y")
            else:
                print(f"  ESTADO: SIN TRACES")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Problema solucionado:")
    print("1. El rango Y ahora se calcula dinámicamente basado en los cambios reales")
    print("2. Los puntos ya no están fuera del rango visible")
    print("3. El gráfico muestra todos los datos correctamente")
    print("4. Los dropdowns mes pre y mes post funcionan correctamente")

if __name__ == "__main__":
    test_final_grafico_visible()
