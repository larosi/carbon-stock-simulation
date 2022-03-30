# carbon-stock-simulation

Generación de datos LiDAR y carbon stock a partir de bosques 3D simulados

## TLDR resumen y orden de ejecucción de scripts
```bash
# generar dataset_info.csv
*python src/prepare/make_dataset_info.py

# generar seeds/*.csv con los centroides de arboles
python src/prepare/forest-seed.py

# asignar un nombre de modelo 3D a cada arbol y escala que se usará en blender
python src/prepare/assign_tree_names_and_scale.py

# transformar los dataset_info.csv, catalog.csv y seeds/*.csv a json
python src/prepare/csv_to_json.py

# generar un bosque 3D .obj a partir de un seeds/*.csv
python src/generate/blender-generate-dataset.py

# pasar de .obj a LiDAR .las
python src/postprocessing/cloudcompare_obj2las.py

# generar CHM a partir de archivo .las
python src/postprocessing/lidar2chm_laspy.py

# agregar info geoespacial y hacer crop de bordes sobrantes
python src/postprocessing/chm_clone_geometadata.py

# pasar cada asset de arbol a .obj
*python src/segmentation/save_each_tree_as_obj.py

# pasar cada asset de arbol a .obj
*python src/segmentation/create_mask_from_each_las_tree.py

# generar mapa de segmentación para cada CHM generado
python src/segmentation/create_mask_dataset.py

* opcionales o bien solo se deben ejecutar la primera vez
```

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

El script **src/prepare/forest-seed.py** realiza una individualización de los árboles detectando los máximos locales dentro de una ventana móvil en las imagenes de CHM, se almacena cada punto detectado en un .csv con el mismo nombre del ráster en **data/seeds/**, también se guardan .html con las detecciones de cada imagen en **data/plots/** para propositos de visualización.
```bash
python src/prepare/forest-seed.py
```

![Detected Trees](./docs/chm_peaks.png?raw=true "Detected Trees")

## Asignar modelos 3D y escala
A cada árbol detectado en el paso anterior se le asigna un modelo 3D del catalogo **catalog.csv**, con la altura indicada en el CHM se calcula cual es el factor de escala que se le debería aplicar posteriormente al modelo en blender.
```bash
python src/prepare/assign_tree_names_and_scale.py
```

## CSV2JSON

Por el momento no he logrado instalar librerias extras al python de blender, por lo que no podemos usar pandas para leer los .csv generados, por esta razón se deben transformar archivos .json, estos se crean en la carpeta **/data/json/**

```bash
python src/prepare/csv_to_json.py
```

## Generar Bosque 3D
Abrir el archivo **data/main.blend** con blender, luego abrir y ejecutar el script **src/generate/blender-generate-dataset.py** esto generará un .obj y .mtl en **data/export/obj/**, este script también genera un flag *.txt* para evitar generar un mismo bosque dos veces en caso de que se quiera ejecutar varios script en paralelo.

![Blender Forest 3D](./docs/blender_forest.jpg?raw=true "Blender Forest 3D")

## OBJ2LAS
El software opensource [CloudCompare](https://www.cloudcompare.org/) se puede [ejecutar por linea de comandos](https://www.cloudcompare.org/doc/wiki/index.php?title=Command_line_mode) si su ejecutable se agrega a las variables de entorno, el script **src/postprocessing/cloudcompare_obj2las.py** transforma cada .obj en un archivo .las usando CloudCompare, por defecto con una densidad de 10 pts por metro cuadrado pero este valor se puede modificar en el archivo **config.json**
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

# Generar mapa de segmentación

![Tree instance segmentation](./docs/segm_zoom_in_out.gif?raw=true "Tree instance segmentation")

## Generar .obj de cada árbol
Abrir el archivo **data/main.blend** con blender, luego abrir y ejecutar el script **src/segmentation/save_each_tree_as_obj.py** esto generará un .obj y .mtl por cada árbol en **data/export/trees_obj/**
```bash
python src/segmentation/save_each_tree_as_obj.py
```

## Generar .las de cada árbol
Hay que modificar los paths del script **src/postprocessing/cloudcompare_obj2las.py** para que transforme los .obj de **data/export/trees_obj/** en archivos .las para cada árbol en **data/export/trees_las/**, se recomienda usar una densidad de puntos alta de **100** o más. Queda pendiente modificar este script para que use argparse.
```bash
python src/postprocessing/cloudcompare_obj2las.py
```

## Generar máscara para cada .las de árbol
Para cada cada árbol de **data/export/trees_las/** genera una máscara binaria en **data/export/trees_mask/** a una resolución de **0.01** metros por pixel, esto se hace filtrando los puntos muy oscuros según el **color_th** definido en **config.json** y luego projectar los puntos restantes sobre el plano XY, posteriormente se aplican operaciones morfológicas y binarización.
```bash
python src/segmentation/create_mask_from_each_las_tree.py
```

## generar mapa de segmentación para cada CHM generado
Usando un raster CHM de referencia dibuja una máscara para cada árbol, según el nombre de árbol asignado y su escala. Las máscaras de agregan siguiendo el [algoritmo del pintor](https://es.wikipedia.org/wiki/Algoritmo_del_pintor), es decir se pintan en orden de menor a mayor altura, de manera tal que los árboles más grandes tapan a los demás. Las máscaras generadas se guardan en **data/export/chm_mask**
```bash
python src/segmentation/create_mask_dataset.py
```