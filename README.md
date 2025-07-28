# PyTris 2.0 - Guía de Funciones
<img width="1024" height="1024" alt="logo full" src="https://github.com/user-attachments/assets/699df78c-4d97-485b-a297-4ef834c394b9" />

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Compilación a Ejecutable](#compilación-a-ejecutable)
4. [Controles Básicos](#controles-básicos)
5. [Mecánicas de Juego](#mecánicas-de-juego)
6. [Sistema de Puntuación](#sistema-de-puntuación)
7. [Efectos Visuales](#efectos-visuales)
8. [Sistema de Audio](#sistema-de-audio)
9. [Opciones y Personalización](#opciones-y-personalización)
10. [Funciones Avanzadas](#funciones-avanzadas)

## Introducción

PyTris 2.0 es una versión mejorada del clásico juego Tetris, implementada en Python utilizando la biblioteca Pygame. El juego incluye todas las funciones del Tetris clásico y añade características modernas como efectos visuales, sistema de combo, y técnicas avanzadas como el T-Spin.

## Instalación

### Requisitos Previos
- Python 3.7 o superior
- Pygame 2.0 o superior

### Instalación desde el Repositorio
1. Clona el repositorio de GitHub:
   ```bash
   git clone https://github.com/Danewmalavita/Pytris.git
   cd pytris-2.0
   ```

2. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el juego:
   ```bash
   python main.py
   ```

### Estructura de Directorios
```
pytris-2.0/
├── main.py                # Punto de entrada principal
├── highscores.json        # Archivo de puntuaciones altas
├── keybindings.json       # Configuración de teclas
├── requirements.txt       # Dependencias del proyecto
├── assets/                # Recursos del juego
│   ├── images/            # Imágenes y sprites
│   └── sounds/            # Archivos de audio
│       ├── bgm/           # Música de fondo
│       └── sfx/           # Efectos de sonido
└── gamescript/            # Módulos del juego
    ├── controls.py        # Sistema de controles
    ├── debug_utils.py     # Utilidades de depuración
    ├── game.py            # Lógica principal del juego
    ├── graphics.py        # Sistema de renderizado
    ├── highscore.py       # Sistema de puntuaciones
    ├── options.py         # Menú de opciones
    ├── tetris_logic.py    # Lógica específica del Tetris
    └── visual_effects.py  # Efectos visuales
```

## Compilación a Ejecutable

Para crear un archivo ejecutable (.exe) del juego, puedes utilizar PyInstaller o cx_Freeze.

### Usando PyInstaller

1. Instala PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Compila el ejecutable:
   ```bash
   pyinstaller --onefile --windowed --add-data "assets;assets" main.py
   ```

3. El ejecutable se creará en la carpeta `dist`.

### Usando cx_Freeze

1. Instala cx_Freeze:
   ```bash
   pip install cx_Freeze
   ```

2. Crea un archivo `setup.py`:
   ```python
   import sys
   from cx_Freeze import setup, Executable

   # Dependencias
   build_exe_options = {
       "packages": ["pygame", "time", "random", "json", "os"],
       "include_files": ["assets/", "highscores.json", "keybindings.json"]
   }

   # Configuración del ejecutable
   setup(
       name="PyTris 2.0",
       version="2.0",
       description="Versión mejorada del clásico juego Tetris",
       options={"build_exe": build_exe_options},
       executables=[Executable("main.py", base="Win32GUI" if sys.platform == "win32" else None)]
   )
   ```

3. Compila el ejecutable:
   ```bash
   python setup.py build
   ```

4. Los archivos compilados se encontrarán en la carpeta `build`.

## Controles Básicos

| Acción | Teclado Predeterminado | Gamepad |
|--------|------------------------|---------|
| Mover Izquierda | Flecha Izquierda | D-pad Izquierda |
| Mover Derecha | Flecha Derecha | D-pad Derecha |
| Caída Suave | Flecha Abajo | D-pad Abajo |
| Caída Rápida | Espacio | Botón A |
| Rotación Horaria | Flecha Arriba | Botón X |
| Rotación Antihoraria | Z | Botón B |
| Guardar Pieza | C | Botón Y |
| Pausar | Escape | Start |

*Nota: Los controles se pueden personalizar en el menú de opciones.*

## Mecánicas de Juego

### Piezas (Tetrominos)
- **I**: Pieza larga de 4 bloques
- **O**: Cuadrado de 2x2 bloques
- **T**: Pieza en forma de T
- **S**: Pieza en forma de S
- **Z**: Pieza en forma de Z
- **J**: Pieza en forma de J
- **L**: Pieza en forma de L

### Sistema de Retención (Hold)
- Permite guardar una pieza para usarla posteriormente
- Se activa con la tecla C o el botón Y del gamepad
- Solo puede utilizarse una vez por pieza

### Vista Previa
- Muestra las siguientes piezas que aparecerán
- Ayuda a planificar estratégicamente tus movimientos

### Sistema DAS/ARR
- **DAS (Delayed Auto Shift)**: Retraso antes de que la pieza se mueva continuamente al mantener una tecla
- **ARR (Auto Repeat Rate)**: Velocidad a la que la pieza se mueve después de activar el DAS
- Optimizado para un control preciso de las piezas

### Ghost Piece (Pieza Fantasma)
- Muestra dónde caerá la pieza actual
- Ayuda a realizar colocaciones precisas

## Sistema de Puntuación

### Puntos por Líneas
- **1 Línea**: 100 × nivel
- **2 Líneas**: 300 × nivel
- **3 Líneas**: 500 × nivel
- **4 Líneas (Tetris)**: 800 × nivel

### Técnicas Especiales
- **T-Spin**: Rotación especial de la pieza T que encaja en espacios difíciles
  - **T-Spin Single**: 800 × nivel
  - **T-Spin Double**: 1200 × nivel
  - **T-Spin Triple**: 1600 × nivel

### Sistema de Combo
- Puntos adicionales por eliminar líneas consecutivamente
- Cada combo incrementa el multiplicador de puntos

### Sistema de Nivel
- El nivel aumenta cada 10 líneas eliminadas
- A mayor nivel, mayor velocidad de caída de las piezas
- Los puntos obtenidos se multiplican por el nivel actual

## Efectos Visuales

### Sistema de Partículas
- Efectos visuales cuando se eliminan líneas
- Partículas especiales para Tetris y T-Spin

### Animaciones de Combo
- Texto animado mostrando el combo actual
- Efectos visuales que aumentan con combos más largos

### Sacudidas de Pantalla
- Efecto de sacudida cuando se logra un Tetris o un T-Spin
- La intensidad varía según la acción

### Fondo Dinámico
- El fondo cambia según el nivel
- Efectos visuales que se intensifican con niveles más altos

## Sistema de Audio

### Música de Fondo
- Varias pistas disponibles
- Se puede cambiar en el menú de pausa
- Opciones de volumen ajustables

### Efectos de Sonido
- Movimiento de piezas
- Rotación
- Caída de piezas (suave y rápida)
- Eliminación de líneas
- Tetris y T-Spin
- Subida de nivel
- Game Over

## Opciones y Personalización

### Configuración de Audio
- Volumen general
- Volumen de música
- Volumen de efectos
- Opción de silencio

### Configuración de Video
- Resolución
- Opciones de visualización

### Controles
- Personalización de teclas
- Soporte para gamepad
- Ajustes de sensibilidad

## Funciones Avanzadas

### Sistema de Puntuaciones Altas
- Guarda las mejores puntuaciones
- Muestra tabla de clasificación

### Debug Mode
- Accesible para desarrolladores
- Muestra información detallada del juego

### Técnicas de Juego Avanzadas
- T-Spin (rotación especial de la pieza T)
- Perfectos (limpieza completa del tablero)
- Back-to-back bonus (bonificación por Tetris/T-Spin consecutivos)
