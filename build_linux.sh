#!/bin/bash

bab

target_file="MiBlend.blend"

process_info=$(ps aux | grep -v grep | grep "blender")

if [[ -n "$process_info" ]]; then
    file_path=$(echo "$process_info" | awk '{for(i=12;i<=NF;i++) printf $i" ";}' | xargs)

    echo "Найден процесс Blender с аргументами: $file_path"

    if [[ "$file_path" == *"$target_file"* ]]; then
        echo "Файл $target_file открыт в Blender. Перезапускаем Blender..."

        blender_pid=$(echo "$process_info" | awk '{print $2}')
        kill "$blender_pid"

        while kill -0 "$blender_pid" 2>/dev/null; do
            echo "Ожидание завершения процесса Blender..."
        done

    fi
        echo "Процесс Blender завершен."
else
    echo "Blender не запущен."
fi
