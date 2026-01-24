@echo off
echo ============================
echo  SUBIENDO CAMBIOS A GITHUB
echo ============================

cd C:\Users\lfpmd\proyectos\imperyo_django

echo Añadiendo cambios...
git add .

echo Escribe el mensaje para el commit:
set /p msg=Mensaje: 

git commit -m "%msg%"

echo Haciendo push a GitHub...
git push

echo ============================
echo   CAMBIOS SUBIDOS CON ÉXITO
echo ============================
pause
