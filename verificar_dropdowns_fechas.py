import sys
import pandas as pd
sys.path.append('.')
from pages.swc_page import layout
import dash_bootstrap_components as dbc

def verificar_dropdowns_fechas():
    """Verifica que los dropdowns muestren las fechas correctas del Excel."""
    print("=== VERIFICACIÓN DE DROPDOWNS - FECHAS CORRECTAS ===\n")
    
    try:
        layout_component = layout()
        
        # Buscar los dropdowns de mes en el layout
        def buscar_dropdowns(component, path=""):
            dropdowns = []
            if hasattr(component, 'children') and component.children:
                children = component.children if isinstance(component.children, list) else [component.children]
                for i, child in enumerate(children):
                    dropdowns.extend(buscar_dropdowns(child, f"{path}[{i}]"))
            
            # Verificar si es un dropdown de mes
            if hasattr(component, 'id'):
                if component.id in ['mes-pre-dropdown', 'mes-post-dropdown']:
                    if hasattr(component, 'options'):
                        opciones = component.options
                        print(f"Dropdown '{component.id}':")
                        print(f"  Opciones: {len(opciones)} meses")
                        for opt in opciones:
                            print(f"    - {opt['label']} (value: {opt['value']})")
                        print()
                    else:
                        print(f"Dropdown '{component.id}': Sin opciones")
            
            return dropdowns
        
        dropdowns = buscar_dropdowns(layout_component)
        print(f"Total dropdowns encontrados: {len(dropdowns)}")
        
        # También verificar meses disponibles directamente
        from data_loader import load_data
        data = load_data()
        
        print("\n=== VERIFICACIÓN DIRECTA DE MESES ===")
        
        # Verificar meses específicos por hoja
        for hoja in ['rendimiento', 'pfza']:
            if hoja not in data:
                continue
                
            df = data[hoja]
            print(f"\n--- Hoja: {hoja} ---")
            
            # Buscar columna 'Fecha' específica
            if 'Fecha' in df.columns:
                try:
                    fechas = pd.to_datetime(df['Fecha'], errors='coerce')
                    periodos = fechas.dt.to_period('M').astype(str).dropna()
                    meses_unicos = sorted(periodos.unique())
                    
                    print(f"  Columna 'Fecha': {len(meses_unicos)} meses únicos")
                    for mes in meses_unicos:
                        count = (periodos == mes).sum()
                        print(f"    {mes}: {count} registros")
                        
                except Exception as e:
                    print(f"  Error procesando 'Fecha': {e}")
            else:
                print(f"  No existe columna 'Fecha'")
                # Mostrar otras columnas de fecha
                for col in df.columns:
                    if any(kw in col.lower() for kw in ['fecha', 'mes', 'date', 'month']):
                        print(f"  Otra columna de fecha: '{col}'")
        
    except Exception as e:
        print(f"Error verificando dropdowns: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_dropdowns_fechas()
