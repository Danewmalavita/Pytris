# Instrucciones para la Plantilla de Sprites Tetris

## Archivos Generados

- `sprite_template.png`: Plantilla base de sprites (240x30 píxeles)
- `sprite_template_grid.png`: Plantilla con cuadrícula para facilitar la edición
- `sprite_template_large.png`: Versión ampliada para facilitar la edición

## Estructura de la Plantilla

La plantilla consiste en 8 bloques de 30x30 píxeles organizados horizontalmente:

1. **Posición 0**: Bloque vacío (transparente) - No requiere edición
2. **Posición 1**: Bloque Z (Rojo - #FF0000)
3. **Posición 2**: Bloque S (Verde - #00FF00)
4. **Posición 3**: Bloque J (Azul - #0000FF)
5. **Posición 4**: Bloque O (Amarillo - #FFFF00)
6. **Posición 5**: Bloque I (Cian - #00FFFF)
7. **Posición 6**: Bloque T (Magenta - #FF00FF)
8. **Posición 7**: Bloque L (Naranja - #FF8000)

## Instrucciones para Photoshop (PSD)

1. **Crear el archivo PSD**:
   - Abre uno de los archivos PNG generados en Photoshop
   - Guarda como PSD
   - Configura un lienzo de 240x30 píxeles (8 bloques de 30x30)

2. **Estructura de capas recomendada**:
   ```
   - Guías y Cuadrícula (desactivar para exportar)
   - Bloque L (Naranja)
   - Bloque T (Magenta)
   - Bloque I (Cian)
   - Bloque O (Amarillo)
   - Bloque J (Azul)
   - Bloque S (Verde)
   - Bloque Z (Rojo)
   - Bloque Vacío (transparente)
   - Fondo (transparente)
   ```

3. **Para cada bloque**:
   - Mantén la posición exacta de cada bloque (30x30 píxeles)
   - Añade efectos de capa para crear profundidad:
     - Sombra interior para los bordes inferiores y derechos
     - Resplandor interior para los bordes superiores e izquierdos
     - Borde/stroke fino para mejorar la visibilidad

4. **Consideraciones de diseño**:
   - El fondo del juego es oscuro (#141428), asegúrate de que los bloques sean visibles
   - Mantén alto contraste en los bordes de los bloques
   - Puedes añadir texturas sutiles, pero mantén la identificación clara del color

5. **Exportación**:
   - Exporta como PNG con transparencia
   - Mantén el tamaño exacto de 240x30 píxeles
   - Guarda como `sprites.png` para reemplazar el archivo original

## Implementación en el juego

Una vez creados los nuevos sprites:
1. Reemplaza el archivo `assets/img/sprites.png` existente con tu nueva versión
2. Asegúrate de que cada sprite ocupe exactamente 30x30 píxeles y esté en la posición correcta
3. La primera posición (bloque vacío) debe ser totalmente transparente

## Ejemplo de estilos para bloques

Para cada bloque puedes aplicar estas capas de estilo:

```
Estilo de capa:
- Sombra interior: Modo Multiplicar, Color Negro, Opacidad 40%, Ángulo 120°
- Resplandor interior: Modo Pantalla, Color Blanco, Opacidad 75%, Ángulo 45°
- Trazo: 1px, Posición Interior, Color ligeramente más oscuro que el color base
- Bisel y relieve: Estilo Cincel Duro, Profundidad 100%, Dirección Arriba
```

Estos estilos te ayudarán a crear bloques con aspecto tridimensional que sean fácilmente visibles en el juego.