import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def debug_eje_y_asimetrico():
    """Debug específico para verificar problema del eje Y asimétrico."""
    print("=== DEBUG EJE Y ASIMÉTRICO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    categoria = 'Primera'
    variable = 'Potencia Pico'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"Parámetros: {categoria} / {variable} / {mes_pre} > {mes_post}")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            print("1. ANÁLISIS DEL GRÁFICO:")
            
            # Verificar datos del gráfico
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'x') and hasattr(trace, 'y'):
                    x_vals = trace.x
                    y_vals = trace.y
                    
                    print(f"   Puntos generados: {len(x_vals)}")
                    print(f"   Valores X (Post): {[f'{x:.1f}' for x in x_vals]}")
                    print(f"   Valores Y (Cambio): {[f'{y:.1f}' for y in y_vals]}")
                    
                    # Verificar rangos del eje Y
                    if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                        rango_y = fig.layout.yaxis.range
                        print(f"   Rango del eje Y: [{rango_y[0]:.1f}, {rango_y[1]:.1f}]")
                        
                        # Verificar si es simétrico
                        if abs(rango_y[0]) == abs(rango_y[1]):
                            print("   PROBLEMA: Rango simetrico detectado")
                        else:
                            print("   CORRECTO: Rango asimetrico")
                        
                        # Verificar si incluye valores muy negativos
                        if rango_y[0] <= -1200:
                            print("   ❌ PROBLEMA: Rango incluye valores <= -1200")
                            print("   Esto indica que el cálculo de rangos es incorrecto")
                        elif rango_y[0] <= -1000:
                            print("   ⚠️  ADVERTENCIA: Rango incluye valores <= -1000")
                        else:
                            print("   ✅ CORRECTO: Rango no incluye valores extremadamente negativos")
                        
                        # Verificar si el rango es proporcional a los datos
                        datos_min = min(y_vals)
                        datos_max = max(y_vals)
                        rango_total = abs(rango_y[1] - rango_y[0])
                        datos_range = abs(datos_max - datos_min)
                        
                        if rango_total > datos_range * 3:
                            print("   ❌ PROBLEMA: Rango demasiado grande para los datos")
                            print(f"   Rango del gráfico: {rango_total:.1f} vs datos: {datos_range:.1f}")
                        else:
                            print("   ✅ CORRECTO: Rango proporcional a los datos")
                        
                        # Verificar si las zonas SWC son visibles
                        print(f"\n2. VERIFICACIÓN DE ZONAS SWC:")
                        
                        # Calcular SWC
                        sd_grupo = pd.Series(y_vals).std(ddof=1)
                        SWC = 0.2 * sd_grupo
                        
                        print(f"   SD del grupo: {sd_grupo:.2f}")
                        print(f"   SWC: {SWC:.2f}")
                        print(f"   Líneas SWC: ±{SWC:.2f}")
                        
                        # Verificar si las líneas SWC están dentro del rango
                        if rango_y[0] <= -SWC and rango_y[1] >= SWC:
                            print("   ✅ CORRECTO: Zonas SWC visibles")
                        else:
                            print("   ❌ PROBLEMA: Zonas SWC no visibles")
                        
                        # Verificar bandas de fondo
                        print(f"\n3. VERIFICACIÓN DE BANDAS:")
                        for shape in fig.layout.shapes:
                            if hasattr(shape, 'y0') and hasattr(shape, 'y1'):
                                print(f"   Banda: [{shape.y0:.1f}, {shape.y1:.1f}] - {shape.fillcolor}")
                        
                        # Verificar título
                        if hasattr(fig.layout, 'title') and hasattr(fig.layout.title, 'text'):
                            print(f"\n4. TÍTULO DEL GRÁFICO:")
                            print(f"   {fig.layout.title.text}")
                        
                        # Verificar altura y márgenes
                        if hasattr(fig.layout, 'height'):
                            print(f"\n5. DIMENSIONES:")
                            print(f"   Altura: {fig.layout.height}px")
                        
                        if hasattr(fig.layout, 'margin'):
                            margin = fig.layout.margin
                            print(f"   Márgenes: L={margin.l}, R={margin.r}, T={margin.t}, B={margin.b}")
                    
                    else:
                        print("   ERROR: No hay datos Y")
                else:
                    print("   ERROR: No hay datos X")
            else:
                print("   ERROR: No hay traces en el grafico")
        else:
            print("   ❌ ERROR: El gráfico no tiene figure")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Si el eje Y muestra valores de -1200, el problema puede ser:")
    print("1. Cálculo incorrecto del margen en rangos asimétricos")
    print("2. SD demasiado alta para variables de fuerza")
    print("3. Valores inconsistentes entre Pre y Post")
    print("4. Problema en la agregación de datos de fuerza")

if __name__ == "__main__":
    debug_eje_y_asimetrico()
