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

call .\prefix\Scripts\activate.bat
if errorlevel 1 exit 1

conda info
if errorlevel 1 exit 1

conda list
if errorlevel 1 exit 1

conda list --no-show-channel-urls --no-pip
if errorlevel 1 exit 1

call .\prefix\Scripts\deactivate.bat
if errorlevel 1 exit 1
