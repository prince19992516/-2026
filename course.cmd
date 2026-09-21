@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" course.py %*
) else (
  echo Please create .venv and install packages first. Read tutorial 01.
  if "%~1"=="" pause
  exit /b 1
)
set "course_exit=%errorlevel%"
if not "%course_exit%"=="0" echo See the error above. Read the environment tutorial before continuing.
if "%~1"=="" pause
exit /b %course_exit%
