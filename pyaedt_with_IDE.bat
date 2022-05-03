@echo off

set env_vars=ANSYSEM_ROOT222 ANSYSEM_ROOT221 ANSYSEM_ROOT212 ANSYSEM_ROOT211
setlocal enableextensions enabledelayedexpansion
set latest_env_var_present=
for %%c in (%env_vars%) do (
    set env_var_name=%%c
    set ver=!env_var_name:ANSYSEM_ROOT=!
    if defined !env_var_name! (
        set latest_env_var_present=!env_var_name!
        GOTO :FOUND_ENV_VAR
    )
)
endlocal
echo AEDT 21R1 or greater has to be installed
pause
EXIT /B

:FOUND_ENV_VAR
endlocal && set aedt_var=%latest_env_var_present%
set version=%aedt_var:ANSYSEM_ROOT=%
set version_r=%version:~0,2%R%version:~2,1%
set cmd=call echo %%%aedt_var%%%
for /f "delims=" %%i in ('%cmd%') do set aedt_path=%%i
echo Found AEDT Version %version_r% at %aedt_path%

set /p run=Python or Jupyter?(0=Spyder, 1=Jupyter, 2=Console)
setlocal enableDelayedExpansion

if not exist "%APPDATA%\pyaedt_env_ide\" (
    echo Installing Pyaedt
    cd "%APPDATA%"
    "%aedt_path%\commonfiles\CPython\3_7\winx64\Release\python\python.exe" -m venv "%APPDATA%\pyaedt_env_ide"
    "%APPDATA%\pyaedt_env_ide\Scripts\python.exe" -m pip install --upgrade pip
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install pyaedt
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install jupyterlab
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install spyder
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install ipython -U
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install ipyvtklink
    call "%APPDATA%\pyaedt_env_ide\Scripts\python" "%APPDATA%\pyaedt_env_ide\Lib\site-packages\pyaedt\misc\aedtlib_personalib_install.py" %aedt_var%
)
if [%1%]==[-update] ( 
    echo Updating Pyaedt
    "%APPDATA%\pyaedt_env_ide\Scripts\pip" install pyaedt -U
)
if %run%==1 (
     echo Launching Jupyter Lab
    "%APPDATA%\pyaedt_env_ide\Scripts\jupyter.exe" lab
) else ( if %run%==0 (
    echo Launching Spyder
    "%APPDATA%\pyaedt_env_ide\Scripts\spyder.exe"
    ) else (
    "%APPDATA%\pyaedt_env_ide\Scripts\ipython.exe"
    )
)

