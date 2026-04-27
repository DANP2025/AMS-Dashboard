import pandas as pd

RUTA = 'AMS.xlsx'  # ajustá si es necesario

xl = pd.ExcelFile(RUTA)
print("=" * 70)
print(f"HOJAS ENCONTRADAS: {xl.sheet_names}")
print("=" * 70)

for hoja in xl.sheet_names:
    df = xl.parse(hoja)
    print(f"\n📄 HOJA: '{hoja}' — {df.shape[0]} filas × {df.shape[1]} columnas")
    print(f"   Columnas: {df.columns.tolist()}")
    
    # Buscar columnas de interés
    for col in df.columns:
        col_lower = col.lower()
        
        if any(kw in col_lower for kw in ['fecha', 'mes', 'date', 'month', 'periodo']):
            vals = df[col].dropna().unique()[:5]
            print(f"   ⏰ Columna temporal '{col}': {vals.tolist()}")
        
        if any(kw in col_lower for kw in ['dni', 'id', 'jugador', 'nombre']):
            vals = df[col].dropna().unique()[:5]
            print(f"   👤 Columna ID/Nombre '{col}': {vals.tolist()}")
        
        if any(kw in col_lower for kw in ['categ', 'division', 'grupo']):
            vals = df[col].dropna().unique()
            print(f"   🏷️  Columna categoría '{col}': {vals.tolist()}")

print("\n" + "=" * 70)
print("Copiá esta salida y pegala en el chat para continuar el diagnóstico.")
print("=" * 70)
