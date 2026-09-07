@echo off
rem Windows 一键复现：等价于 python run_all.py %*
setlocal
set PYTHONUTF8=1
cd /d "%~dp0"
where py >nul 2>nul && (py -3 run_all.py %* & goto :done)
where python >nul 2>nul && (python run_all.py %* & goto :done)
echo 未找到 Python，请安装 Python 3.10+ 并勾选 "Add to PATH"。
:done
if "%1"=="" pause
endlocal
