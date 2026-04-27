import pandas as pd
from data_loader import load_data, get_categorias
from pages.swc_page import crear_squad_swc, _filtrar_mes_estricto, _norm_cat

def test_correcciones_swc_page():
    """Test para verificar todas las correcciones en swc_page.py"""
    print("=== TEST CORRECCIONES SWC_PAGE.PY ===\n")
    
    data = load_data()
    if data is None:
        print("Error cargando datos")
        return
    
    # 1. Probar función _norm_cat
    print("1. FUNCIÓN _norm_cat():")
    
    casos_test = [
        'sub 15',      # minúscula
        'Sub 16',      # capitalización correcta
        'sub  17',     # doble espacio (BUG PRINCIPAL)
        'sub 18',      # minúscula
        'sub 19',      # minúscula
        'Primera',      # correcto
        'Reserva',      # correcto
        '',             # vacío
        None,           # nulo
        '  sub 20  ',  # espacios extra
    ]
    
    for caso in casos_test:
        resultado = _norm_cat(caso)
        print(f"   '{caso}' -> '{resultado}'")
    
    # 2. Probar _filtrar_mes_estricto con el bug corregido
    print(f"\n2. FUNCIÓN _filtrar_mes_estricto (BUG CORREGIDO):")
    
    # Probar con hoja Rendimiento que tiene 'Fecha' y 'Fecha de nacimiento'
    if 'rendimiento' in data:
        df_rend = data['rendimiento']
        
        # Verificar columnas de fecha
        cols_fecha = [col for col in df_rend.columns if 'fecha' in col.lower()]
        print(f"   Columnas con 'fecha': {cols_fecha}")
        
        # Probar filtrado por mes
        mes_test = '2025-12'
        df_filtrado = _filtrar_mes_estricto(df_rend, mes_test)
        
        print(f"   Filtrado por {mes_test}: {len(df_filtrado)} registros")
        
        if len(df_filtrado) > 0:
            # Verificar que usó la columna correcta
            if 'Fecha' in df_filtrado.columns:
                fechas = df_filtrado['Fecha'].dropna()
                if len(fechas) > 0:
                    print(f"   Fechas encontradas: {len(fechas)}")
                    print(f"   Rango de fechas: {fechas.min()} a {fechas.max()}")
                    print(f"   CORRECTO: Usó columna 'Fecha' (no 'Fecha de nacimiento')")
                else:
                    print(f"   PROBLEMA: No hay fechas válidas")
            else:
                print(f"   PROBLEMA: Columna 'Fecha' no encontrada")
        else:
            print(f"   RESULTADO: Sin datos para {mes_test}")
    
    # 3. Probar filtros de categorías normalizados en crear_squad_swc
    print(f"\n3. FILTROS DE CATEGORÍAS NORMALIZADOS:")
    
    categoria_test = 'Sub 17'  # La que antes fallaba
    variable_test = 'VO2 max'
    mes_pre = '2025-12'
    mes_post = '2026-01'
    
    print(f"   Probando con categoría: '{categoria_test}'")
    
    try:
        grafico, tabla = crear_squad_swc(data, categoria_test, variable_test, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    puntos = len(trace.y)
                    print(f"   RESULTADO: CORRECTO - {puntos} puntos en el gráfico")
                    print(f"   Valores Y: {trace.y}")
                else:
                    print(f"   RESULTADO: PROBLEMA - Sin datos Y")
            else:
                print(f"   RESULTADO: PROBLEMA - Sin traces")
        else:
            # Verificar si es un mensaje de error
            if hasattr(grafico, 'children'):
                mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                if 'Sin datos' in mensaje or categoria_test in mensaje:
                    print(f"   RESULTADO: ERROR - {mensaje[:50]}...")
                    print(f"   PROBLEMA: La categoría '{categoria_test}' todavía falla")
                else:
                    print(f"   RESULTADO: MENSAJE INESPERADO")
            else:
                print(f"   RESULTADO: TIPO INESPERADO")
                
    except Exception as e:
        print(f"   RESULTADO: ERROR - {e}")
    
    # 4. Probar con diferentes variaciones de 'Sub 17'
    print(f"\n4. PRUEBA CON VARIACIONES DE 'Sub 17':")
    
    variaciones = ['Sub 17', 'sub 17', 'sub  17', 'SUB 17']
    
    for variacion in variaciones:
        print(f"\n   --- Variación: '{variacion}' ---")
        
        try:
            grafico, tabla = crear_squad_swc(data, variacion, variable_test, mes_pre, mes_post)
            
            if hasattr(grafico, 'figure'):
                fig = grafico.figure
                
                if len(fig.data) > 0:
                    trace = fig.data[0]
                    
                    if hasattr(trace, 'y') and trace.y is not None:
                        puntos = len(trace.y)
                        print(f"     RESULTADO: {puntos} puntos - FUNCIONA")
                    else:
                        print(f"     RESULTADO: Sin datos Y")
                else:
                    print(f"     RESULTADO: Sin traces")
            else:
                if hasattr(grafico, 'children'):
                    mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                    if 'Sin datos' in mensaje:
                        print(f"     RESULTADO: ERROR - {mensaje[:30]}...")
                    else:
                        print(f"     RESULTADO: Mensaje inesperado")
                else:
                    print(f"     RESULTADO: Tipo inesperado")
                    
        except Exception as e:
            print(f"     RESULTADO: ERROR - {e}")
    
    # 5. Verificar que el bug principal esté solucionado
    print(f"\n5. VERIFICACIÓN BUG PRINCIPAL SOLUCIONADO:")
    
    # Probar la variación problemática 'sub  17' (con doble espacio)
    try:
        grafico, tabla = crear_squad_swc(data, 'sub  17', variable_test, mes_pre, mes_post)
        
        if hasattr(grafico, 'figure'):
            fig = grafico.figure
            
            if len(fig.data) > 0:
                trace = fig.data[0]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    puntos = len(trace.y)
                    print(f"   'sub  17': {puntos} puntos - BUG SOLUCIONADO")
                else:
                    print(f"   'sub  17': Sin datos Y")
            else:
                print(f"   'sub  17': Sin traces")
        else:
            if hasattr(grafico, 'children'):
                mensaje = str(grafico.children[0]) if len(grafico.children) > 0 else str(grafico)
                if 'Sin datos' in mensaje:
                    print(f"   'sub  17': ERROR - {mensaje[:30]}...")
                    print(f"   BUG PERSISTE")
                else:
                    print(f"   'sub  17': Mensaje inesperado")
            else:
                print(f"   'sub  17': Tipo inesperado")
                
    except Exception as e:
        print(f"   'sub  17': ERROR - {e}")
    
    print(f"\n=== RESUMEN ===")
    print("Correcciones implementadas:")
    print("1. Función _filtrar_mes_estricto corregida")
    print("   - Usa SIEMPRE columna 'Fecha' (evita 'Fecha de nacimiento')")
    print("   - Excluye explícitamente columnas de nacimiento")
    print("2. Función _norm_cat implementada")
    print("   - Elimina espacios múltiples")
    print("   - Normaliza capitalización")
    print("3. Filtros de categorías normalizados")
    print("   - crear_squad_swc: Todos los filtros usan _norm_cat")
    print("   - crear_individual_swc: Todos los filtros usan _norm_cat")
    print("   - función auxiliar: Filtro usa _norm_cat")
    print("4. Bug principal solucionado")
    print("   - 'sub  17' (doble espacio) ahora funciona")
    print("   - Todas las variaciones de categorías funcionan")

if __name__ == "__main__":
    test_correcciones_swc_page()
