' Создание ярлыка YouTube Analyzer на рабочем столе
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Пути
strDesktop = WshShell.SpecialFolders("Desktop")
strShortcut = strDesktop & "\YouTube Analyzer.lnk"
strCurrentDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Создание ярлыка
Set oShortcut = WshShell.CreateShortcut(strShortcut)
oShortcut.TargetPath = strCurrentDir & "\toggle_service.bat"
oShortcut.WorkingDirectory = strCurrentDir
oShortcut.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13"
oShortcut.Description = "YouTube Analyzer - Запуск/Остановка"
oShortcut.Hotkey = "CTRL+SHIFT+Y"
oShortcut.Save

MsgBox "Ярлык создан на рабочем столе!" & vbCrLf & _
       "Горячие клавиши: Ctrl+Shift+Y", vbInformation, "YouTube Analyzer"