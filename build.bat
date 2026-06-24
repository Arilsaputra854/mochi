@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building Mochi.exe...
pyinstaller mochi.spec --clean

echo.
if exist "dist\Mochi.exe" (
    echo BUILD SUCCESS: dist\Mochi.exe
) else (
    echo BUILD FAILED. Check output above.
)
pause
