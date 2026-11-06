# Casa Respira

Guida indipendente ad aria e acqua dentro casa. Sito statico: https://casarespira.it

## Struttura

- `_build/grafica.py`: logo e copertine social (assets/og). Si lancia dopo build.py.
- `_build/build.py`: generatore. Contiene testi, notizie, sezioni e CSS. Produce il sito nella radice del repository.
- tutto il resto: il sito pronto. Hostinger lo pubblica dalla radice del repository in `public_html`.

## Come si aggiorna

1. Modifica `_build/build.py` (una guida, una notizia, il CSS).
2. Esegui `python3 _build/build.py`.
3. Commit e push. Hostinger pubblica in automatico.

Il foglio di stile ha un nome che cambia a ogni modifica (`site-<hash>.css`), così la cache dell'hosting non serve versioni vecchie.

## Regole editoriali

Fonti istituzionali con link e data, prezzi verificati e datati, correzioni dichiarate in fondo alla pagina, niente consigli medici. Sono scritte per esteso in `come-lavoriamo/`.
