import os
import psutil
import subprocess

def find_and_kill_blender():
    blender_process_name = "blender.exe" if os.name == "nt" else "blender"
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == blender_process_name and "miblend" in proc.info["cmdline"][-1].lower():
                print(f"Закрываю процесс Blender с PID: {proc.info['pid']}, в котором открыт файл MiBlend.blend")
                proc.terminate()
                return "Success"
        except psutil.AccessDenied:
            print(f"Нет доступа для завершения процесса с PID: {proc.info['pid']}")
        except Exception as e:
            print(f"Ошибка: {e}")

    print("Процесса Blender с открытым файлом MiBlend.blend не существует")
    return "Success"

def run_bab_in_script_directory(script_dir):
    config_file = os.path.join(script_dir, "bpy-build.yaml")
    if not os.path.exists(config_file):
        print(f"Файл {config_file} не найден в директории скрипта: {script_dir}")
        return "Failed"
    
    try:
        print(f"Переход в директорию скрипта: {script_dir}")
        os.chdir(script_dir)
        print("Запускаю команду 'bab'...")
        process = subprocess.Popen(
            "bab",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Команда 'bab' выполнена успешно.")
            print("Результат:", stdout.decode().strip())
            return "Success"
        else:
            print("Ошибка выполнения команды 'bab':", stderr.decode().strip())
    except FileNotFoundError:
        print("Команда 'bab' не найдена. Убедитесь, что она доступна в PATH.")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    return "Failed"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Директория скрипта: {script_dir}")
    
    kill_result = find_and_kill_blender()
    if kill_result == "Failed":
        print("Не удалось закрыть процесс Blender. Продолжение выполнения скрипта.")
    
    build_result = run_bab_in_script_directory(script_dir)
    if build_result == "Failed":
        print("Не удалось выполнить команду 'bab'. Ошибка.")
    
    if kill_result == "Failed" or build_result == "Failed":
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
