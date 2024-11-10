@echo off
setlocal

rem Вставьте вашу команду или утилиту (если она нужна)
rem bab

set targetFile=MiBlend.blend

rem Получаем PID процесса Blender
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq blender.exe" /FO LIST ^| find "PID"') do (
    set blenderPID=%%a
)

rem Если процесс Blender запущен
if defined blenderPID (
    echo Найден процесс Blender с PID: %blenderPID%

    rem Проверяем, открыт ли файл MiBlend.blend
    for /f "tokens=*" %%b in ('wmic process where "ProcessId=%blenderPID%" get CommandLine ^| find /I "%targetFile%"') do (
        echo Файл %targetFile% открыт в Blender. Перезапускаем Blender...

        rem Завершаем процесс Blender
        taskkill /PID %blenderPID% /F
        echo Ожидание завершения процесса Blender...

        rem Ждем завершения процесса
        :waitLoop
        tasklist /FI "PID eq %blenderPID%" 2>NUL | find "%blenderPID%" > NUL
        if %ERRORLEVEL% equ 0 (
            timeout /T 1 > NUL
            goto waitLoop
        )

        rem Перезапуск Blender
        echo Перезапуск Blender...
        start "" "C:\Program Files\Blender Foundation\Blender\blender.exe" "C:\path\to\your\MiBlend.blend"
        exit /B 0
    )
) else (
    echo Blender не запущен.
)

endlocal
