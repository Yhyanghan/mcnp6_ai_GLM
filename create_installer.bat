@echo off
chcp 65001 >nul
echo ========================================
echo MCNP6 AI Assistant Installer Creator
echo ========================================
echo.

set VERSION=1.1.0
set PACKAGE_NAME=MCNP6_AI_Assistant_v%VERSION%

echo [1/5] Creating installation directory...
if exist "%PACKAGE_NAME%" rd /s /q "%PACKAGE_NAME%"
mkdir "%PACKAGE_NAME%"
mkdir "%PACKAGE_NAME%\MCNP6_AI_Assistant"

echo [2/5] Copying files...
xcopy /e /i /y "dist\MCNP6_AI_Assistant\*" "%PACKAGE_NAME%\MCNP6_AI_Assistant\"
copy /y "????.md" "%PACKAGE_NAME%\"
copy /y "README.md" "%PACKAGE_NAME%\"
copy /y "MCNP6_CONFIGURATION_GUIDE.md" "%PACKAGE_NAME%\"

echo [3/5] Creating startup script...
(
echo @echo off
echo chcp 65001 ^>^&^&gt; nul
echo cd /d "%%~dp0"
echo start MCNP6_AI_Assistant.exe
) > "%PACKAGE_NAME%\??MCNP6 AI??.bat"

echo [4/5] Creating README.txt...
(
echo MCNP6 AI Assistant v%VERSION%
echo ================================
echo.
echo ????:
echo 1. ???????????
echo 2. ?? "??MCNP6 AI??.bat" ????
echo 3. ?????? MCNP6_AI_Assistant.exe
echo.
echo ????:
echo 1. ???????? "??" ??
echo 2. ?? AI ???API Key??
echo 3. ?? MCNP6 ????????????
echo 4. ?? "????.md" ????????
echo.
echo ????:
echo - ?????? MCNP6 ??
echo - ?????? OpenAI API Key??????AI???
echo - ????????????AI????
echo.
echo ????:
echo - ?? "????.md" ????????
echo - ?? "MCNP6_CONFIGURATION_GUIDE.md" ??MCNP6??
echo.
echo ??: %VERSION%
echo ??: %date%
) > "%PACKAGE_NAME%\README.txt"

echo [5/5] Installation package created!
echo.
echo Package location: %PACKAGE_NAME%
echo.
echo ========================================
echo Installation package created successfully!
echo ========================================
echo.
echo Please compress the %PACKAGE_NAME% directory to ZIP file for distribution.
pause
