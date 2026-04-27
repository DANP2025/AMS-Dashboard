import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc
import plotly.graph_objects as go

def verificar_datos_grafico():
    """Verificar los datos dentro del gráfico generado."""
    print("=== VERIFICACIÓN DE DATOS DEL GRÁFICO ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Generar el gráfico
    categoria = 'Primera'
    variable = 'Pmax'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
    
    print(f"Gráfico generado: {type(grafico)}")
    
    # Extraer la figura de Plotly
    if hasattr(grafico, 'figure'):
        fig = grafico.figure
        print(f"\nFigura Plotly extraída:")
        print(f"  Tipo: {type(fig)}")
        print(f"  Número de traces: {len(fig.data)}")
        
        if len(fig.data) > 0:
            for i, trace in enumerate(fig.data):
                print(f"\n  Trace {i}:")
                print(f"    Tipo: {trace.type}")
                print(f"    Nombre: {trace.name}")
                
                if hasattr(trace, 'x') and trace.x is not None:
                    print(f"    X ({len(trace.x)} valores): {trace.x}")
                else:
                    print(f"    X: None o vacío")
                
                if hasattr(trace, 'y') and trace.y is not None:
                    print(f"    Y ({len(trace.y)} valores): {trace.y}")
                else:
                    print(f"    Y: None o vacío")
                
                if hasattr(trace, 'marker') and trace.marker is not None:
                    print(f"    Marker: {trace.marker}")
                
                if hasattr(trace, 'text') and trace.text is not None:
                    print(f"    Text ({len(trace.text)} valores): {trace.text}")
                
                if hasattr(trace, 'customdata') and trace.customdata is not None:
                    print(f"    CustomData: {len(trace.customdata)} elementos")
                    if len(trace.customdata) > 0:
                        print(f"      Primer elemento: {trace.customdata[0]}")
        else:
            print("  No hay traces en la figura")
        
        # Verificar el layout
        print(f"\n  Layout:")
        if hasattr(fig, 'layout'):
            layout = fig.layout
            print(f"    Título: {layout.title.text if hasattr(layout.title, 'text') else 'Sin título'}")
            
            if hasattr(layout, 'xaxis'):
                print(f"    Eje X:")
                print(f"      Título: {layout.xaxis.title.text if hasattr(layout.xaxis, 'title') else 'Sin título'}")
                print(f"      Rango: {layout.xaxis.range}")
            
            if hasattr(layout, 'yaxis'):
                print(f"    Eje Y:")
                print(f"      Título: {layout.yaxis.title.text if hasattr(layout.yaxis, 'title') else 'Sin título'}")
                print(f"      Rango: {layout.yaxis.range}")
            
            print(f"    Altura: {layout.height}")
            print(f"    Márgenes: {layout.margin}")
        
        # Verificar si hay un problema con los datos
        if len(fig.data) > 0:
            trace = fig.data[0]
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                if len(trace.x) == 0 or len(trace.y) == 0:
                    print(f"\n  ¡PROBLEMA! Los traces están vacíos")
                    print(f"  Posibles causas:")
                    print(f"    - Los resultados están vacíos")
                    print(f"    - Error en la generación de datos")
                    print(f"    - Problema en el cálculo de cambios")
                else:
                    print(f"\n  DATOS CORRECTOS - El gráfico debería mostrar {len(trace.x)} puntos")
                    
                    # Verificar si los puntos están fuera del rango visible
                    x_min, x_max = min(trace.x), max(trace.x)
                    y_min, y_max = min(trace.y), max(trace.y)
                    
                    print(f"  Rango de datos:")
                    print(f"    X: {x_min:.2f} a {x_max:.2f}")
                    print(f"    Y: {y_min:.2f} a {y_max:.2f}")
                    
                    # Verificar el rango del eje Y
                    if hasattr(fig.layout, 'yaxis') and hasattr(fig.layout.yaxis, 'range'):
                        yaxis_range = fig.layout.yaxis.range
                        print(f"  Rango del eje Y: {yaxis_range}")
                        
                        if yaxis_range:
                            y_axis_min, y_axis_max = yaxis_range
                            
                            # Verificar si los puntos están fuera del rango visible
                            if y_max < y_axis_min or y_min > y_axis_max:
                                print(f"  ¡PROBLEMA! Los puntos están fuera del rango visible del eje Y")
                                print(f"    Puntos Y: {y_min:.2f} a {y_max:.2f}")
                                print(f"    Eje Y visible: {y_axis_min:.2f} a {y_axis_max:.2f}")
                            else:
                                print(f"  Rango Y correcto - Los puntos deberían ser visibles")
        
        # Crear una versión simplificada para probar
        print(f"\n  Creando versión simplificada para prueba:")
        if len(fig.data) > 0 and hasattr(fig.data[0], 'x') and hasattr(fig.data[0], 'y'):
            x_vals = fig.data[0].x
            y_vals = fig.data[0].y
            
            fig_simple = go.Figure()
            fig_simple.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers+text',
                text=[f'P{i+1}' for i in range(len(x_vals))],
                textposition='top center',
                marker=dict(size=10, color='blue')
            ))
            
            fig_simple.update_layout(
                title='Gráfico Simplificado para Prueba',
                xaxis_title='X',
                yaxis_title='Y',
                showlegend=False
            )
            
            print(f"  Gráfico simplificado creado con {len(x_vals)} puntos")
            
            # Guardar el gráfico para inspección
            try:
                fig_simple.write_html('C:/Dany/AMS/Dash/grafico_prueba.html')
                print(f"  Gráfico guardado en: C:/Dany/AMS/Dash/grafico_prueba.html")
            except Exception as e:
                print(f"  Error guardando gráfico: {e}")
    
    else:
        print("El gráfico no tiene atributo 'figure'")

if __name__ == "__main__":
    verificar_datos_grafico()
