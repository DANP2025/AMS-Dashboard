def debug_calculo_rangos():
    """Debug del cálculo de rangos para identificar el problema."""
    print("=== DEBUG CÁLCULO DE RANGOS ===\n")
    
    # Datos del debug anterior
    todos_cambio = [-141.0, -449.0, -469.0, -906.0, -1199.0]
    SWC = 67.82  # Calculado con SD = 339.12
    
    print(f"Datos de entrada:")
    print(f"   Cambios: {todos_cambio}")
    print(f"   SWC: {SWC:.2f}")
    
    # Cálculo actual (problemático)
    cambio_min = min(todos_cambio)   # -1199.0
    cambio_max = max(todos_cambio)   # -141.0
    
    print(f"\nCálculo actual:")
    print(f"   cambio_min: {cambio_min}")
    print(f"   cambio_max: {cambio_max}")
    
    # Aquí está el problema
    rango_datos = abs(cambio_max - cambio_min)  # abs(-141 - (-1199)) = 1058
    margen = max(rango_datos * 0.25, SWC * 1.5)  # max(1058*0.25, 67.82*1.5) = max(264.5, 101.73) = 264.5
    
    print(f"   rango_datos: {rango_datos}")
    print(f"   margen (25%): {margen}")
    
    y_plot_min = cambio_min - margen  # -1199 - 264.5 = -1463.5
    y_plot_max = cambio_max + margen  # -141 + 264.5 = 123.5
    
    print(f"   y_plot_min: {y_plot_min}")
    print(f"   y_plot_max: {y_plot_max}")
    
    # Ajuste final con SWC
    y_plot_min = min(y_plot_min, -SWC * 2.0)  # min(-1463.5, -135.64) = -1463.5
    y_plot_max = max(y_plot_max,  SWC * 2.0)  # max(123.5, 135.64) = 135.64
    
    print(f"   y_plot_min final: {y_plot_min}")
    print(f"   y_plot_max final: {y_plot_max}")
    
    print(f"\nPROBLEMA IDENTIFICADO:")
    print(f"   El margen del 25% sobre un rango de 1058 es demasiado grande (264.5)")
    print(f"   Esto expande innecesariamente el rango hacia valores muy negativos")
    
    print(f"\nSOLUCIÓN PROPUESTA:")
    print(f"   Para datos todos negativos, el margen debería ser más pequeño")
    print(f"   O usar un margen absoluto basado en el valor máximo absoluto")
    
    # Solución: margen basado en el valor más extremo
    valor_extremo = max(abs(cambio_min), abs(cambio_max))  # max(1199, 141) = 1199
    margen_solucion = max(valor_extremo * 0.15, SWC * 1.0)  # max(1199*0.15, 67.82) = max(179.85, 67.82) = 179.85
    
    print(f"   valor_extremo: {valor_extremo}")
    print(f"   margen_solucion (15%): {margen_solucion}")
    
    y_plot_min_sol = cambio_min - margen_solucion  # -1199 - 179.85 = -1378.85
    y_plot_max_sol = cambio_max + margen_solucion  # -141 + 179.85 = 38.85
    
    print(f"   y_plot_min_sol: {y_plot_min_sol}")
    print(f"   y_plot_max_sol: {y_plot_max_sol}")
    
    print(f"\nCOMPARACIÓN:")
    print(f"   Rango actual: [{y_plot_min:.1f}, {y_plot_max:.1f}]")
    print(f"   Rango solución: [{y_plot_min_sol:.1f}, {y_plot_max_sol:.1f}]")
    print(f"   Mejora: {abs(y_plot_min) - abs(y_plot_min_sol):.1f} menos negativo")

if __name__ == "__main__":
    debug_calculo_rangos()
