@echo off
chcp 65001 >nul
title DACHANG Reader - Diagnostic Mode

echo ============================================
echo DACHANG Reader - Diagnostic Mode
echo ============================================
echo.

rem Check Windows version
echo [1/10] Checking Windows version...
ver
echo.

rem Check if running as admin
echo [2/10] Checking admin rights...
net session >nul 2>&1 && echo ADMIN: YES || echo ADMIN: NO
echo.

rem Check current directory
echo [3/10] Current directory...
cd
echo Current path: %CD%
echo.

rem Check path (special chars)
echo [4/10] Checking path for special chars...
echo Path: %CD%
echo.

rem List files in current directory
echo [5/10] Files in current directory...
dir /b
echo.

rem Check Python presence
echo [6/10] Checking Python...
where python >nul 2>&1 && echo Python found || echo Python NOT found
where python3 >nul 2>&1 && echo python3 found || echo python3 NOT found
echo.

rem Check PowerShell
echo [7/10] Checking PowerShell...
powershell -Command "Write-Host 'PowerShell OK'"
echo.

rem Test batch echo
echo [8/10] Testing batch basic commands...
echo English test - should show properly
echo.

rem Check disk space
echo [9/10] Checking disk space (C drive)...
wmic logicaldisk get name,size,freespace 2>nul | findstr "C:"
echo.

echo [10/10] Diagnostic complete!
echo.
echo If this window closed immediately, the issue is BEFORE this script runs.
echo If you see this, press any key to close.
pause
