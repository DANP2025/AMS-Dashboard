import sys
sys.path.append('.')
from pages.swc_page import DISPLAY_NAMES, VARS_PFZA_EXCEL

print("=== VERIFICACION DISPLAY_NAMES ===")
print(f"VARS_PFZA_EXCEL: {VARS_PFZA_EXCEL}")
print(f"\nDISPLAY_NAMES para variables de fuerza:")
for var in VARS_PFZA_EXCEL:
    display_name = DISPLAY_NAMES.get(var, var)
    print(f"  {var} -> '{display_name}'")

print(f"\n=== VERIFICACION ESPECIFICA ===")
if 'Altura Salto' in DISPLAY_NAMES:
    print(f"Altura Salto -> '{DISPLAY_NAMES['Altura Salto']}'")
else:
    print("ERROR: 'Altura Salto' no encontrado en DISPLAY_NAMES")
