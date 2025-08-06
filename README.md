# NanoVNA-UTN-Toolkit

UTN FRBA 2025 - MEDIDAS ELECTRÓNICAS II - Curso R5052

**Autores:**
- Axel Nathanel Nahum ([@Axel-Nahum](https://github.com/Axel-Nahum))
- Fernando Castro Canosa ([@fcascan](https://github.com/fcascan))
- Hugo Alejandro Gomez ([@hugomezok](https://github.com/hugomezok))
- Uriel Sandomir Laham ([@usandomir](https://github.com/usandomir))

## Pasos para la conexión a la PC
### 1. Instalar driver
- **Solo para Windows**: 
  1. Instalar el driver que se encuentra en "windows-driver": CypressDriverInstaller_1.exe
  2. Reiniciar el equipo

### 2. Configurar el baudrate en el nanoVNA
  1. Pulsar el botón rocker para desplegar el menú, navegar a Config / CONNECTION
  2. En el primer item configurar CONNECTION como "USB"
  3. En el segundo item configurar SERIAL SPEED a un baudrate de conveniencia (por ejemplo a 38400)

### 3. Configurar el baudrate en el sistema operativo
- **Windows**: 
  1. Conectar el nanoVNA a la PC sin pulsar ningun botón
  2. Abrir el Administrador de Dispositivos y buscar el nanoVNA en la sección "Puertos (COM y LPT)"
  3. En Propiedades / Configuración del puerto seleccionar el baudrate correspondiente en el menú desplegable de "Bits por segundo"

## Pasos para ejecutar el programa
### 1. Instalar Python
- **Windows**: 
  1. Abrir la terminal (cmd).
  2. Ejecutar el comando `python`. Esto redirigirá a la tienda de Windows para instalar la última versión de **Python Interpreter & Runtime**.

### 2. Actualizar `pip`
Ejecutar el siguiente comando en la terminal para actualizar `pip` a su última versión:
```bash
pip install --upgrade pip
```

### 3. Instalar dependencias
Instalar las dependencias necesarias para el programa:
```bash
pip install PyQt5
```

### 4. Ejecutar el programa
Ejecutar el programa en un entorno Python:
```bash
python -m src.NanoVNA_UTN_Toolkit.main
```

## Pasos para compilar una versión ejecutable
### 1. Instalar PyInstaller
Instalar el paquete PyInstaller con el siguiente comando:
```bash
pip install pyinstaller
```

### 2. Construir el ejecutable
Ejecutar el siguiente comando para generar un archivo ejecutable:
```bash
python -m PyInstaller --onefile ./src/NanoVNA_UTN_Toolkit/main.py --name "NanoVNA-UTN-Toolkit" --icon=icon.ico --hidden-import=PyQt5
```

### 3. Ejecutar el programa compilado
El ejecutable generado estará en el directorio dist/. Para ejecutarlo:
```bash
dist/NanoVNA-UTN-Toolkit.exe
```

## Créditos
Este proyecto fue desarrollado como parte de los requisitos de la materia **Medidas Electrónicas II** en la UTN FRBA durante el ciclo lectivo 2025.
