@echo on

conda.exe install -yq constructor jinja2
if errorlevel 1 exit 1

build.py --python "%PYVER%" --hash md5 sha1 sha256
if errorlevel 1 exit 1
