import pandas as pd
from data_loader import load_data
from pages.swc_page import crear_squad_swc

def test_callback_grafico():
    """Test directo del callback para verificar si genera el gráfico correctamente."""
    print("=== TEST DIRECTO DEL CALLBACK ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # Simular los parámetros que recibiría el callback
    vista = 'squad'
    categoria = 'Primera'
    variable = 'Pmax'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    dni_jugador = None
    n_intervals = 0
    
    print(f"Parámetros de prueba:")
    print(f"  vista: {vista}")
    print(f"  categoria: {categoria}")
    print(f"  variable: {variable}")
    print(f"  mes_pre: {mes_pre}")
    print(f"  mes_post: {mes_post}")
    
    try:
        # Llamar directamente a la función que genera el gráfico
        grafico, tabla = crear_squad_swc(data, categoria, variable, mes_pre, mes_post)
        
        print(f"\nResultado:")
        print(f"  Tipo de gráfico: {type(grafico)}")
        print(f"  Tipo de tabla: {type(tabla)}")
        
        if hasattr(grafico, 'data'):
            print(f"  Figura tiene datos: {len(grafico.data)} traces")
            
            if len(grafico.data) > 0:
                trace = grafico.data[0]
                print(f"  Primer trace:")
                print(f"    Tipo: {trace.type}")
                print(f"    X values: {len(trace.x) if hasattr(trace, 'x') else 'N/A'}")
                print(f"    Y values: {len(trace.y) if hasattr(trace, 'y') else 'N/A'}")
                
                if hasattr(trace, 'x') and hasattr(trace, 'y'):
                    print(f"    X: {trace.x}")
                    print(f"    Y: {trace.y}")
                
                print(f"  RESULTADO: El gráfico SÍ tiene datos")
            else:
                print(f"  RESULTADO: El gráfico NO tiene datos")
        else:
            print(f"  No es una figura Plotly, es: {str(grafico)[:100]}...")
            
            # Verificar si es un mensaje de error
            if hasattr(grafico, 'children'):
                print(f"  Es un componente Dash con {len(grafico.children)} hijos")
                if len(grafico.children) > 0:
                    print(f"  Primer hijo: {str(grafico.children[0])[:100]}...")
        
        # Verificar la tabla
        if tabla:
            print(f"\nTabla generada: {type(tabla)}")
            if hasattr(tabla, 'children'):
                print(f"  Tabla tiene {len(tabla.children)} elementos")
        else:
            print(f"\nTabla: Vacía")
        
    except Exception as e:
        print(f"\nERROR en la generación del gráfico:")
        print(f"  Tipo: {type(e).__name__}")
        print(f"  Mensaje: {str(e)}")
        
        import traceback
        print(f"\nTraceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    test_callback_grafico()
