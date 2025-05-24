"""
Установка YouTube Analyzer как Windows Service
Позволяет автозапуск при включении компьютера
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess
import time
from pathlib import Path
from security import safe_command

class YouTubeAnalyzerService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'YouTubeAnalyzer'
    _svc_display_name_ = 'YouTube Analyzer Service'
    _svc_description_ = 'YouTube Content Analysis Service'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        # Путь к проекту
        project_dir = Path(__file__).parent
        venv_python = project_dir / "venv" / "Scripts" / "python.exe"
        main_script = project_dir / "backend" / "main.py"
        
        # Запуск сервера
        process = safe_command.run(subprocess.Popen, [str(venv_python), str(main_script)],
            cwd=str(project_dir),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Ожидание остановки
        while self.is_running:
            if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                break
                
        # Остановка процесса
        process.terminate()
        process.wait()

def install_service():
    """Установка сервиса"""
    if len(sys.argv) == 1:
        # Установка с автозапуском
        sys.argv.append('--startup=auto')
        sys.argv.append('install')
        
    win32serviceutil.HandleCommandLine(YouTubeAnalyzerService)

if __name__ == '__main__':
    # Для установки: python install_service.py install
    # Для удаления: python install_service.py remove
    # Для запуска: python install_service.py start
    # Для остановки: python install_service.py stop
    
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(YouTubeAnalyzerService)
    else:
        print("YouTube Analyzer Service Manager")
        print("================================")
        print("Команды:")
        print("  install - Установить сервис")
        print("  remove  - Удалить сервис")
        print("  start   - Запустить сервис")
        print("  stop    - Остановить сервис")
        print("  restart - Перезапустить сервис")
        print("\nПример: python install_service.py install")
