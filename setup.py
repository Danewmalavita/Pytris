import sys
from cx_Freeze import setup, Executable

# Dependencias
build_exe_options = {
    "packages": ["pygame", "time", "random", "json", "os"],
    "include_files": ["assets/", "gamescript/", "highscores.json", "keybindings.json"]
}

# Configuración del ejecutable
setup(
    name="PyTris 2.0",
    version="2.0",
    description="Versión mejorada del clásico juego Tetris",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI" if sys.platform == "win32" else None)]
)