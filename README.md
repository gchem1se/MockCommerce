# Welcome to MockCommerce!

## Requisiti

I requisiti si trovano nel file `requirements.txt` e si possono installare rapidamente con `pip install -r requirements.txt`. In particolare, ho utilizzato:
- `Flask-WTF` (per la quale ho anche installato l'add-on `email-validator`) per gestire i form
- `Pillow` per gestire le immagini prima di caricarle sul server 
- `SQLalchemy`: non ho utilizzato le funzioni di ORM della libreria, per cui il codice è praticamente identico ad utilizzare direttamente la libreria `sqlite3`, con in aggiunta alcune possibilità di migliore organizzazione del codice. In particolare, l'ho utilizzata:
-- per avere un log nel terminale delle query eseguite
-- per poter inizializzare l'engine nel modulo `__init__` , caricando così una sola volta la URI del DB dal file di configurazione di istanza

## Struttura del progetto

Ho strutturato il progetto secondo la struttura *Package* descritta su [ExploreFlask/organizing](http://exploreflask.com/en/latest/organizing.html). 
```
├── instance
│    ├── config.py
│    └── db
├── mockcommerce
│    ├── static
│    ├── templates
│    ├── utils.py
│    ├── views
│    ├── dao.py
│    ├── models.py
│    ├── forms.py
│    └── __init__.py
├── requirements.txt
├── run.py
└── venv
```
Ho quindi separato in più moduli le funzionalità della webapp. In particolare, le `views` sono separate in più moduli ed esportate verso l'applicazione tramite i `Blueprint` di `Flask`.
Il webserver di test può essere lanciato con `python run.py`. L'app è interamente contenuta nella cartella `mockcommerce` mentre un file di configurazione e il database SQLite sono nella cartella `instance`, pensata per contenere dati sensibili per l'applicazione (es. chiavi segrete).

## Utenti di prova

All'interno dell'applicazione sono registrati degli utenti di prova con "ruoli" specifici che ho creato per testare gli utilizzi abituali della piattaforma rispetto al tipo di utente.

| Nome utente | Password  | Ruolo |
|---|----|---|
| compratore99 | Password1- | Ha solo fatto acquisti |
| venditore88 | Password1- | Ha solo prodotti in vendita |
| utenteditest | Password1- | Sia venditore che compratore |
oltre a vari utenti "fittizi", venditori degli altri prodotti visibili sul sito.
