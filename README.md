# WEEDSDEEP PROJECT

##### Deep-learning per la classificazione di infestanti in scenari di agricoltura di precisione mediante immagini multi-spettrali.

La prima idea è quella di utilizzare due script:  

```
image_segmentation_main.py [path/to/RAW.dat] [path/to/TBANDS_TIFF.dat] [path/to/TIFF.dat] [path/to/tbands/rasters/directory] [path/to/rasters/directory] [path/to/config.xml]
qgis_processing.py
```

`image_segmentation_main.py`, che necessita l'installazione di `opencv-python`, segmenta una serie di immagini (listata nel file `RAW.dat`) dividendo, per ogni immagine e mediante una serie di operazioni, la vegetazione (_crop/weed_) dal terreno (_soil_).  
Le immagini così segmentate vengono salvate nella directory passata per argomento, ed i rispettivi paths vanno a popolare il file `TIFF.dat`.

+ gestione .tiff (anche a tre bande) con geolocalizzazione (.tfw)

All'interno del file `config.xml` è possibile configurare la segmentazione.  
`qgis_processing.py` viene lanciato all'interno dell'ambiente _QGIS_ (richiesta la versione _3_ o superiore), genera gli _shapefiles_ della lista di immagini escludendo il terreno.  
Gli _shapefiles_ vengono inoltre visualizzati nel progetto _QGIS_ per una maggiore comprensione degli stessi.  

![Alt diagram](https://i.ibb.co/JK6ppXb/diag.png)
