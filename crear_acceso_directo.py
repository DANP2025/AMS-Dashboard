import os
import winshell
from win32com.client import Dispatch

desktop = winshell.desktop()
path = os.path.join(desktop, "AMS Dashboard.lnk")
target = r"C:\Dany\AMS\Dash\iniciar_dashboard.bat"
wDir = r"C:\Dany\AMS\Dash"
icon = r"C:\Dany\AMS\Dash\iniciar_dashboard.bat"

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()

print("Acceso directo creado en el escritorio: AMS Dashboard.lnk")
