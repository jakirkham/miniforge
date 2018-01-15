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

conda info --json > info.json
if errorlevel 1 exit 1

conda list > spec.txt && type spec.txt
if errorlevel 1 exit 1

conda update -c conda-forge --quiet --dry-run --all
if errorlevel 1 exit 1

call .\prefix\Scripts\deactivate.bat
if errorlevel 1 exit 1
