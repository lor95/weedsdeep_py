# WEEDSDEEP PROJECT

#### Deep-learning per la classificazione di infestanti in scenari di agricoltura di precisione mediante immagini multi-spettrali.

## imglist_generator.py

__Utilizzo__: `imglist_generator.py [path/to/images/directory] [path/to/rawdat/directory] [mode]`  

`rawdat_generator.py` è uno script di supporto utile a generare il file `RAW.dat`, dove sono listati i path delle immagini da processare.  
Dati in input il path alla directory contenente i files immagini (al momento sono supportati __solo__ i _.jpg_) ed il path della directory che ospiterà il file creato, da in output il file `RAW.dat` nella relativa directory.  
Può funzionare in due modalità `[mode]`:  

* __w__: _write mode_ - genera un file ex-novo, eventualmente sovrascrivendo un file esistente nella stessa directory.  
* __a__: _append mode_ - genera o aggiorna il file `RAW.dat` (se già presente) aggiungendo path in coda.  

Ogni altro inserimento come terzo parametro determina il funzionamento in _default mode_ (_write mode_).

## images_processing_main.py

__Dipendenze esterne__: `opencv-python` - `pyexiftool` - `pyproj`  

__Utilizzo__: `images_processing_main.py [-h] [-rdir <rasters_directory>] [-fdir <file_directory>] config list`  

__Note aggiuntive__: E' necessario installare il tool _[Exiftool](https://www.sno.phy.queensu.ca/~phil/exiftool/)_ (aggiungerlo al system PATH, nel caso di un utilizzo del software su _Windows_).  

`images_processing_main.py` segmenta una serie di immagini in input, i quali path sono contenuti nel file `RAW.dat`, discriminando la vegetazione (_crop/weed_) dal terreno (_soil_). Individua elementi singoli per i quali ne calcola attributi dimensionali e prepara l'ambiente per operazioni di _deep learning_.  
Ogni immagine processata è salvata nella directory indicata come parametro in input, insieme ad un relativo _world file_, contenente le coordinate longitudinali e latitudinali estratte dai _metadata GPS_ (oltre al loro orientamento rispetto l'asse _N-S_), ed un _comma separated values file_ (_.csv_), dove sono salvati tutti gli attributi dimensionali di ogni elemento individuato come _crop/weed_.  
Gli stessi _world files_ sono copiati anche nella directory delle immagini di partenza.  
Al termine genera un file `TIFF.dat` nella directory passata come parametro contenente i path di ogni immagine processata.  
Tutte le operazioni possono essere configurate utilizzando il file _.xml_ di configurazione.  

## _QGIS_ WeedsDeep Plugin

Plugin _QGIS_ (utilizzabile solo dalla versione 3.0) utile a visualizzare il materiale ed i dati generati con gli script sopra descritti, oltre a renderne possibile la modifica, nel modo più semplice possibile.  
Genera gli shapefiles (_.shp_) delle immagini segmentate all'interno di subdirectories di una directory indicata ed un file `SHP.dat`, contenente i path per ogni vettore creato.  

Per installare il plugin è sufficiente __copiare__ la directory `/qgis_plugin/weedsdeep_processing` nella folder dedicata.  
Essa si individua facilmente, essendo contenuta nella _settings folder_ dell'ambiente _QGIS_:  

1. Aprire _QGIS_
2. Cliccare su _Console python_ (o premere _CTRL+ALT+P_)
3. Scrivere `QgsApplication.qgisSettingsDirPath() + "/python/plugins"`.

Alternativamente è possibile installare il plugin compresso in formato _.zip_ (`/qgis_plugin/weedsdeep_processing.zip`) __cliccando su__ `Plugins -> Gestisci ed Installa Plugin... -> Installa da ZIP`.

## data_augmentation_processing_main.py

__Dipendenze esterne__: `tensorflow` - `numpy` - `scipy` - `pillow`  

__Utilizzo__:  `data_augmentation_processing_main.py [path/to/RAW.dat] [path/to/destination/folder] [path/to/config.xml]`  

Utilizza il modulo `keras` per modificare _randomicamente_ immagini listate nel file `RAW.dat` e salvarle nella directory passata in input.  
Le impostazioni di modifica sono contenute nel file _.xml_ di configurazione.  
