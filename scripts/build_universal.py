import os, subprocess, psutil, sys
from colorama import init, Fore, Style

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
        print(Fore.RED + f"Файл {config_file} не найден в директории скрипта: {script_dir}" + Style.RESET_ALL)
        return "Failed"
    
    try:
        print(Fore.CYAN + f"Переход в директорию скрипта: {script_dir}" + Style.RESET_ALL)
        os.chdir(script_dir)
        print(Fore.YELLOW + "Запускаю команду 'bab'..." + Style.RESET_ALL)

        use_shell = (os.name == "nt")
        cmd = "bab" if use_shell else ["bab"]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=use_shell,
            text=True,
            bufsize=1
        )

        prev_line = ""
        if process.stdout is not None:
            for raw_line in process.stdout:
                line = raw_line.rstrip("\n").replace("\r", "")
                if prev_line and not prev_line.endswith(("\\", ":", "]")) and not line.startswith(" "):
                    sys.stdout.write(Fore.GREEN + prev_line + line + Style.RESET_ALL + "\n")
                    prev_line = ""
                else:
                    if prev_line:
                        sys.stdout.write(Fore.GREEN + prev_line + Style.RESET_ALL + "\n")
                    prev_line = line
                sys.stdout.flush()
            if prev_line:
                sys.stdout.write(Fore.GREEN + prev_line + Style.RESET_ALL + "\n")
                sys.stdout.flush()

        process.wait()
        if process.returncode == 0:
            print(Fore.LIGHTGREEN_EX + "Команда 'bab' выполнена успешно." + Style.RESET_ALL)
            return "Success"
        else:
            print(Fore.LIGHTRED_EX + f"Команда 'bab' завершилась с кодом {process.returncode}." + Style.RESET_ALL)
            return "Failed"

    except FileNotFoundError:
        print(Fore.RED + "Команда 'bab' не найдена. Убедитесь, что она доступна в PATH или установлена." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Неожиданная ошибка: {e}" + Style.RESET_ALL)
    return "Failed"

def main():
    init()
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
