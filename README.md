# Casa Respira

Guida indipendente ad aria e acqua dentro casa. Sito statico: https://casarespira.it

## Struttura

- `build/build.py`: generatore. Contiene testi, notizie, sezioni e CSS. Produce la cartella `site/`.
- `site/`: il sito pronto, da pubblicare così com'è nella cartella `public_html` dell'hosting.

## Come si aggiorna

1. Modifica `build/build.py` (una guida, una notizia, il CSS).
2. Esegui `python3 build/build.py` con `OUT` impostato su `site/` (vedi in cima al file).
3. Commit e push. Hostinger pubblica la cartella `site/` dal repository.

Il foglio di stile ha un nome che cambia a ogni modifica (`site-<hash>.css`), così la cache dell'hosting non serve versioni vecchie.

## Regole editoriali

Fonti istituzionali con link e data, prezzi verificati e datati, correzioni dichiarate in fondo alla pagina, niente consigli medici. Sono scritte per esteso in `site/come-lavoriamo/`.
