# carbon-stock-simulation

Generación de datos LiDAR y carbon stock a partir de bosques 3D simulados

## Crear catalogo de árboles

Primero hay que conseguir los assets de árboles que se usarán para crear el bosque, por el momento estamos usando los modelos del [Kit lowpoly shapespark](https://sketchfab.com/3d-models/shapespark-low-poly-plants-kit-de9e79fc07b748d1a6ac055b49ee5c67) que contiene arboles de distinto tipo y tamaño, estos modelos se guardaron en el archivo **data/main.blend**. Para cada modelo se anota manualmente su nombre, tipo y altura en metros en el archivo **data/catalog.csv**

|name|type|height|
|---|----|------|
|Flowers-02|low|0.890973|
|Flowers-04|low|0.914986|
|Tree-02-2|mid|7.9601|

![Tree Examples](./docs/tree_measure_h.png?raw=true "Tree Examples")

## Crear lista de rasters

La idea es generar un bosque 3D a partir de imagenes de CHM reales, en el archivo **data/dataset_info.csv** contiene los nombres sin extension y dimensiones de los rasters, este archivo se puede generar con el script **src/prepare/make_dataset_info.py**

```bash
python src/prepare/make_dataset_info.py
```

## Generar seed de árboles

El script **src/prepare/forest-seed.py** realiza una individualización de los árboles detectando los máximos locales dentro de una ventana móvil en las imagenes de CHM, se almacena cada punto detectado, su altura y su diametro (estimado con funciones alométricas) en un .csv con el mismo nombre del ráster, también se guardan .html con las detecciones de cada imagen en **data/plots/**
```bash
python src/prepare/forest-seed.py
```

![Detected Trees](./docs/chm_peaks.png?raw=true "Detected Trees")

## CSV2JSON

Por el momento no he logrado instalar librerias extras al python de blender, por lo que no podemos usar pandas para leer los .csv generados, por esta razón se deben transformar archivos .json, estos se crean en la carpeta **/data/json/**

```bash
python src/prepare/csv_to_json.py
```

## Generar Bosque 3D
Abrir el archivo **data/main.blend** en blender y ejecutar el script **src/generate/blender-generate-dataset.py** esto generará un .obj y .mtl en **data/export/obj/**

![Blender Forest 3D](./docs/blender_forest.jpg?raw=true "Blender Forest 3D")

## Paths .mtl a relativos
Los path a los archivos de texturas estan definidos en los archivos .mtl de cada modelo, estos por defecto estan en como path absoluto, el script **src/postprocessing/fix_mtl.py** modifica los path de los .mtl para dejarlos en formato relativo

```bash
python src/postprocessing/fix_mtl.py
```

## OBJ2LAS
El software opensource [CloudCompare](https://www.cloudcompare.org/) se puede [ejecutar por linea de comandos](https://www.cloudcompare.org/doc/wiki/index.php?title=Command_line_mode) si su ejecutable se agrega a las variables de entorno, el script **src/postprocessing/cloudcompare_obj2las.py** transforma cada .obj en un archivo .las usando CloudCompare por defecto con una densidad de 10 pts por metro cuadrado
```bash
python src/postprocessing/cloudcompare_obj2las.py
```

## LAS2CHM
El script **src/postprocessing/lidar2chm_laspy.py** genera los raster CHM en formato .tif a partir de los archivos .las usando laspy por defecto a una resolución de 0.12 mts
```bash
python src/postprocessing/lidar2chm_laspy.py
```

## Agregar información geoespacial
El script **src/postprocessing/lidar2chm_laspy.py** copia la información geoespacial de los raster originales, y también le aplica un Crop y resize a los raster generados para que queden del mismo tamaño que los originales, los rasters generados se guardan en **data/export/chm_fixed**
```bash
python src/postprocessing/chm_clone_geometadata.py
```

![Fake Oncol CHM](./docs/oncol_gen_blender.png?raw=true "Fake Oncol CHM")