@echo off
chcp 65001 >nul
echo ========================================
echo MCNP6 AI Assistant Build Tool
echo ========================================
echo.

echo [1/4] Checking environment...
python --version
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo Error: PyInstaller installation failed
    pause
    exit /b 1
)

echo.
echo [3/4] Building executable...
pyinstaller mcnp6_ai_assistant.spec --clean
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Build completed!
echo.
echo Executable location: dist\MCNP6_AI_Assistant\MCNP6_AI_Assistant.exe
echo.
echo ========================================
echo Build successful!
echo ========================================
pause
