# weedsdeep

La prima idea è quella di utilizzare due script:  

```
image_segmentation_main.py -[path/to/img]
qgis_processing.py
```

Il primo (necessita l'installazione di `opencv-python`) segmenta un'immagine che viene successivamente convertita in formato _TIFF_.  
All'interno del file `config.xml` è possibile configurare la segmentazione.  
Il secondo script, lanciato all'interno dell'ambiente _QGIS_ (richiesta la versione _3_ o superiore), genera lo shapefile. (work in progress)

![Alt diagram](https://i.ibb.co/f8FRF2r/ter.png)