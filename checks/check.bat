@echo off

call deactivate.bat
if errorlevel 1 exit 1

@echo on

start /wait "" %cd%\miniforge.exe /InstallationType=JustMe    ^
                                  /AddToPath=0                ^
                                  /RegisterPython=0           ^
                                  /S                          ^
                                  /D=%cd%\prefix
if errorlevel 1 exit 1
