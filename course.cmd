@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" course.py %*
) else (
  py -3.12 course.py %*
)
set "course_exit=%errorlevel%"
if not "%course_exit%"=="0" echo See the error above. Read the environment tutorial before continuing.
if "%~1"=="" pause
exit /b %course_exit%
