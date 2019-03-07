# WEEDSDEEP PROJECT

##### Deep-learning per la classificazione di infestanti in scenari di agricoltura di precisione mediante immagini multi-spettrali.

La prima idea è quella di utilizzare due script:  

```
image_segmentation_main.py [path/to/RAW.dat] [path/to/TIFF] [path/to/rasters/directory] [path/to/config.xml]
qgis_processing.py
```

`image_segmentation_main.py` necessita l'installazione di `opencv-python`, segmenta una serie di immagini (listata nel file `RAW.dat`) escludendo per ogni immagine, mediante una serie di operazioni, la vegetazione (_crop/weed_) dal terreno (_soil_).  
Le immagini così segmentate vengono salvate nella directory di riferimento, ed i rispettivi paths vanno a popolare il file `TIFF.dat`.    
All'interno del file `config.xml` è possibile configurare la segmentazione.  
`qgis_processing.py` viene lanciato all'interno dell'ambiente _QGIS_ (richiesta la versione _3_ o superiore), genera gli _shapefiles_ della lista di immagini escludendo il terreno.  
Gli _shapefiles_ vengono inoltre visualizzati nel progetto _QGIS_ per una maggiore comprensione degli stessi.  

![Alt diagram](https://i.ibb.co/WsZKSJ4/diag.png)