# weedsdeep

La prima idea è quella di utilizzare due script:

```
image_segmentation_main.py
qgis_processing.py
```

il primo (necessita l'installazione di `opencv-python`) segmenta, dato un path, un'immagine che viene successivamente convertita in formato _TIFF_.  
il secondo script, lanciato all'interno dell'ambiente _QGIS_ (richiesta la versione _3_ o superiore) genera lo shapefile (work in progress)

![Alt diagram](https://i.ibb.co/w04s7rv/diag.png)

__si vogliono poi adattare gli script a ricevere in input una serie di immagini anziché una sola__