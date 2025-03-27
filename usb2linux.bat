@echo off
setlocal enabledelayedexpansion

:: Request administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath 'cmd' -ArgumentList '/c cd /d %cd% && %~dpnx0 %*'"
    exit /b
)

echo Scanning USB devices...
echo.
echo Available devices list:
set count=0

:: Parse usbipd output and generate menu
for /f "skip=1 tokens=1,*" %%i in ('usbipd list') do (
    set /a count+=1
    set "busid[!count!]=%%i"
    echo [!count!] %%i - %%j
)

if %count%==0 (
    echo No available devices found
    pause
    exit /b
)

echo.
set /p "choice=Please enter device number (1-%count%): "

:: Input validation
if %choice% lss 1 (
    echo Invalid input
    pause
    exit /b
)
if %choice% gtr %count% (
    echo Invalid input
    pause
    exit /b
)

set selected_busid=!busid[%choice%]!

:: Add operation selection menu
echo.
echo Select operation type:
echo 1) Bind and attach device
echo 2) Detach device
set /p "operation=Enter operation number (1-2): "

:: Execute selected operation
if "!operation!"=="1" (
    echo.
    echo Binding device %selected_busid%...
    usbipd bind --busid %selected_busid%
    echo Attaching to WSL...
    usbipd attach --wsl --busid %selected_busid%
) else if "!operation!"=="2" (
    echo.
    echo Detaching device %selected_busid%...
    usbipd detach --busid %selected_busid%
) else (
    echo Invalid operation
    pause
    exit /b
)

echo Operation completed!
pause