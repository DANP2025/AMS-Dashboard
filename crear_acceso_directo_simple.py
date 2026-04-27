import os
import sys

def crear_acceso_directo():
    try:
        # Rutas
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "AMS Dashboard.lnk")
        target_path = r"C:\Dany\AMS\Dash\iniciar_dashboard.bat"
        
        # Crear acceso directo usando PowerShell
        import subprocess
        powershell_script = f'''
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        $Shortcut.WorkingDirectory = "C:\\Dany\\AMS\\Dash"
        $Shortcut.Save()
        '''
        
        result = subprocess.run(["powershell", "-Command", powershell_script], 
                            capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Acceso directo creado exitosamente en el escritorio:")
            print(f"   {shortcut_path}")
            print("\nInstrucciones:")
            print("1. Busca 'AMS Dashboard.lnk' en tu escritorio")
            print("2. Doble clic para iniciar el dashboard")
            print("3. Espera a que aparezca 'Dash is running on http://127.0.0.1:8050/'")
            print("4. Abre tu navegador y ve a http://localhost:8050/")
        else:
            print("Error al crear acceso directo:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nAlternativa manual:")
        print("1. Ve a C:\\Dany\\AMS\\Dash\\")
        print("2. Doble clic en 'iniciar_dashboard.bat'")

if __name__ == "__main__":
    crear_acceso_directo()
