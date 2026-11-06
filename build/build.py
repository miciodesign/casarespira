#!/usr/bin/env python3
"""Generatore del sito statico casarespira.it (release 2, nuova veste grafica).

Output: /home/claude/casarespira/site  (bozze in /home/claude/casarespira/bozze)
"""
import html
import os
import re
import shutil
import hashlib

import pathlib
OUT = str(pathlib.Path(__file__).resolve().parent.parent / "site")
OUT_BOZZE = str(pathlib.Path(__file__).resolve().parent.parent / "bozze")
SITE = "https://casarespira.it"
DATA_ULTIMA_VERIFICA = "6 novembre 2026"
PUB_RFC822 = "Fri, 06 Nov 2026 10:00:00 +0100"

NAV = [
    ("/radon/", "Radon"),
    ("/muffa/", "Muffa e umidità"),
    ("/aria/", "Aria"),
    ("/ventilazione/", "Ventilazione"),
    ("/acqua/", "Acqua"),
    ("/news/", "News"),
    ("/come-lavoriamo/", "Come lavoriamo"),
    ("/chi-siamo/", "Chi siamo"),
]

TEMI = {  # path -> (classe, colore, colore chiaro)
    "/radon/": ("radon", "#C98A00", "#FBF3E0"),
    "/muffa/": ("muffa", "#5E7A3A", "#EEF3E6"),
    "/aria/": ("aria", "#2E7FB8", "#E6F1F9"),
    "/ventilazione/": ("ventilazione", "#7A5CB8", "#EFEAF8"),
    "/acqua/": ("acqua", "#1C8C8C", "#E3F3F3"),
}

# Sezioni: (path, nome, lead, guide previste)
SEZIONI = [
    ("/radon/", "Radon", "Un gas radioattivo che sale dal suolo. È regolato per legge, poco misurato, e si conosce solo con una misura.", [
        "I migliori rilevatori di radon per la casa (confronto)",
        "Radon alto: come si risana una casa e quanto costa",
        "Radon in Piemonte, Veneto, Lazio e nelle altre regioni"]),
    ("/muffa/", "Muffa e umidità", "Da dove viene la muffa, perché torna, e cosa funziona davvero tra deumidificatori, pitture e interventi.", [
        "Muffa in casa: da dove viene e come eliminarla davvero",
        "I migliori deumidificatori per la casa (confronto)",
        "Condensa sulle finestre: perché e cosa fare"]),
    ("/aria/", "Aria che respiri", "CO₂, polveri sottili, composti volatili e monossido: cosa misurare, con quali strumenti, e quando serve un purificatore.", [
        "La qualità dell'aria in casa: cosa misurare e come",
        "I migliori rilevatori di qualità dell'aria (CO₂, polveri)",
        "Purificatori d'aria: servono davvero? Confronto",
        "Monossido di carbonio in casa: rilevatori e caldaie"]),
    ("/ventilazione/", "Ventilazione", "Aprire le finestre bene, e quando conviene una ventilazione meccanica con recupero di calore.", [
        "Ventilazione meccanica controllata (VMC): come funziona e quanto costa",
        "Aprire le finestre bene: quanto, quando, in inverno"]),
    ("/acqua/", "Acqua di casa", "L'acqua del rubinetto è buona? Calcare, cloro, piombo nei tubi vecchi, pozzi privati, filtri e depuratori.", [
        "L'acqua del rubinetto è buona? Come saperlo",
        "Calcare nell'acqua: durezza, danni e soluzioni",
        "Caraffa, filtro al rubinetto o depuratore sotto il lavello: confronto",
        "Tubi vecchi e piombo nell'acqua: come capire se riguarda casa tua",
        "Acqua di pozzo privato: analisi, nitrati, potabilizzazione"]),
]

S = {
    "arpa_puglia_nota": ("ARPA Puglia, nota sul D.Lgs. 101/2020 e sul livello di 300 Bq/m³",
                         "https://arpa.puglia.it/moduli/output_immagine.php?id=5935"),
    "asl_roma3": ("ASL Roma 3, scheda Radon (PDF)",
                  "https://www.aslroma3.it/wp-content/uploads/2025/12/Radon.pdf"),
    "iss_epicentro": ("ISS, EpiCentro, pagina Radon",
                      "https://www.epicentro.iss.it/radon"),
    "ats_brescia_2025": ("ATS Brescia, presentazione su radon e buone pratiche (28 novembre 2025, PDF)",
                         "https://ats-brescia.it/system/files/news/files/28428/22908/Presentazione%20per%20incontro%2028%20novembre%20Mantegna%20Brescia_format%20ATS_RADON_Andrea%20Paladini.pdf"),
    "arpae_ecoscienza": ("ARPAE, Ecoscienza n. 4 del 2023 su radon e salute (PDF)",
                         "https://aggiornati.arpae.it/it/ecoscienza/numeri-ecoscienza/anno-2023/numero-4-anno-2023/ambiente-e-salute/todeschini_es2023_4.pdf"),
    "certifico_anr": ("Certifico, tabelle riassuntive radon su abitazioni e luoghi di lavoro (dati ISS)",
                      "https://certifico.com/sicurezza-lavoro/documenti-sicurezza/documenti-riservati-sicurezza/radon-abitazioni-e-luoghi-di-lavoro-tabelle-riassuntive"),
    "iss_riduzione": ("ISS, Come si riduce il livello di radon negli edifici (PDF)",
                      "https://www.iss.it/documents/20126/6944167/Come+si+riduce+il+livello+di+radon+negli+edifici.pdf"),
    "remetti": ("Università La Sapienza, R. Remetti, Misurazioni di radon (presentazione)",
                "https://amblav.it/wp-content/uploads/2026/05/3-REMETTI-Misurazioni.pdf"),
    "arpa_lomb_rusconi": ("ARPA Lombardia, R. Rusconi, Il radon: aree prioritarie, strumenti per la misura e servizi di dosimetria (PDF)",
                          "https://ats-brescia.it/system/files/field_blocco_redazionale/allegati/1523/paragrafi/24933/Rosella%20Rusconi.pdf"),
    "cni_rusconi": ("Rusconi, presentazione al Politecnico di Milano (8 febbraio 2023, PDF)",
                    "https://www.cni.it/images/eventi/2023/Rusconi_PoliMi_8_febbraio_2023.pdf"),
    "dpcm_2024": ("Certifico, DPCM 11 gennaio 2024 (Piano nazionale d'azione radon 2023-2032)",
                  "https://certifico.com/sicurezza-lavoro/legislazione-sicurezza/dpcm-11-gennaio-2024"),
    "certifico_9941": ("Certifico, D.Lgs. 101/2020 e livelli di riferimento per il radon",
                       "https://certifico.com/id/9941"),
    "regione_lomb": ("Regione Lombardia, campagna di monitoraggio radon 2024-2025",
                     "https://www.regione.lombardia.it/sanita/prevenzione-e-stili-di-vita/sicurezza-negli-ambienti-di-vita/campagna-monitoraggio-radon-2024-2025"),
    "certifico_lg_lomb": ("Certifico, linee guida regionali lombarde per la prevenzione dal radon, 2ª edizione (dicembre 2025)",
                          "https://www.certifico.com/id/25169"),
    "airthings": ("Airthings, programma di affiliazione",
                  "https://airthings.com/affiliate-program"),
}


def fonti(*k):
    return [S[x] for x in k]


PAGES = []


def add(path, title, desc, body, sources=(), status="live", section=None,
        breve=None, chiave=None, scala=False):
    PAGES.append(dict(path=path, title=title, desc=desc, body=body,
                      sources=list(sources), status=status, section=section,
                      breve=breve or [], chiave=chiave, scala=scala,
                      pubdate=PUB_RFC822))


# ------------------------------------------------------------- pagine fisse
add("/chi-siamo/", "Chi siamo",
    "Casa Respira è una guida indipendente su aria e acqua dentro casa.",
    """
<p>Casa Respira è una guida indipendente, in italiano, su aria e acqua dentro casa: come si misurano, quando sono un problema, cosa si può fare e quanto costa. Il tema di partenza è il radon, perché è regolato dalla legge, poco misurato e cercato da chi ha già un problema concreto.</p>
<h2>Per chi scriviamo</h2>
<p>Per proprietari e inquilini di case al piano terra o con seminterrato, famiglie con bambini piccoli o persone con allergie, chi compra o ristruttura casa, e piccoli datori di lavoro con locali a piano terra.</p>
<h2>Di cosa parliamo</h2>
<ul>
<li><strong>Aria</strong>: radon, muffa e umidità, CO₂ e ricambio d'aria, polveri sottili, composti organici volatili, monossido di carbonio, ventilazione meccanica e purificatori.</li>
<li><strong>Acqua</strong>: qualità dell'acqua del rubinetto, calcare, cloro, piombo nei tubi vecchi, nitrati nei pozzi, filtri e depuratori.</li>
<li><strong>Sostenibilità</strong>, come criterio e non come tema a sé: soluzioni che migliorano la salute e consumano meno.</li>
</ul>
<h2>Di cosa non parliamo</h2>
<p>Non trattiamo elettrosmog, detox, cure, diagnosi o consigli medici. Quando un tema tocca la salute di una persona, rimandiamo al medico o all'ASL.</p>
<h2>Chi scrive</h2>
<p>Il sito non ha firme personali: i testi sono della redazione. Il metodo e le fonti sono spiegati in <a href="/come-lavoriamo/">Come lavoriamo</a>. Come il sito si finanzia è scritto nella stessa pagina, nel paragrafo "Come ci sosteniamo".</p>
""", section="fissa")

add("/come-lavoriamo/", "Come lavoriamo",
    "Metodo, fonti, norme, prezzi e correzioni: le regole con cui scriviamo ogni pagina.",
    """
<p>Chi legge una guida su casa e salute deve poter controllare ogni numero. Per questo ogni pagina segue le stesse regole.</p>
<h2>Fonti</h2>
<ul>
<li>Fonti istituzionali sempre, con link e data: ISS, ARPA regionali, ISIN, Ministero della Salute, gestori dell'acqua.</li>
<li>Nessun numero senza fonte. Quando una cifra viene da una stima o da una presentazione, lo scriviamo.</li>
<li>Ogni pagina chiude con l'elenco delle fonti usate e la data di verifica.</li>
</ul>
<h2>Norme</h2>
<p>Le leggi sono citate per articolo. Per il radon: il D.Lgs. 101/2020, come modificato dal D.Lgs. 203/2022, e il Piano nazionale d'azione per il radon 2023-2032, con i livelli di riferimento.</p>
<h2>Prezzi</h2>
<p>Ogni prezzo ha la data di verifica e si aggiorna ogni tre mesi, a gennaio, aprile, luglio e ottobre. Una pagina con prezzi non verificati non viene pubblicata.</p>
<h2>Revisione tecnica</h2>
<p>Le guide sul radon saranno riviste da un esperto di radioprotezione. Finché la revisione non è fatta, non lo diciamo. Stato attuale: in cerca di un revisore.</p>
<h2>Correzioni</h2>
<p>Gli errori si correggono. La correzione è dichiarata in fondo alla pagina, con la data. Correzioni pubblicate finora: nessuna.</p>
<h2>Come ci sosteniamo</h2>
<p>Casa Respira si mantiene con due tipi di entrate, in quest'ordine di importanza. Le dichiariamo nelle pagine che ne sono toccate.</p>
<p><strong>Contatti per misura e risanamento.</strong> Chi scopre un valore alto di radon deve spendere per misurare e per risanare. Le imprese e i laboratori che fanno questi lavori pagano per un contatto qualificato. Il modulo "chiedi un preventivo", quando sarà attivo, gira la richiesta a una o tre imprese della zona, che ci pagano per il contatto. Te lo diciamo prima che tu invii i dati, e i dati passano alle imprese solo con il tuo consenso esplicito.</p>
<p><strong>Affiliazioni.</strong> Alcuni link portano a prodotti venduti da altri. Se compri tramite quei link, riceviamo una commissione. Per te il prezzo non cambia.</p>
<p>Oggi il programma attivo è quello di Airthings, per i rilevatori di radon e di aria. Altri programmi, per deumidificatori, purificatori e filtri, sono in verifica e non hanno ancora link attivi. Le pagine che contengono link affiliati lo dichiarano in testa.</p>
""", sources=fonti("airthings"), section="fissa")

# ------------------------------------------------------------- radon
add("/radon/guida-completa/", "Radon in casa: la guida completa",
    "Cos'è il radon, quali livelli di riferimento valgono in Italia, come si misura e come si riduce.",
    """
<p>Il radon è un gas radioattivo naturale, incolore e inodore. Esce dal suolo e si accumula negli ambienti chiusi, soprattutto dove la ventilazione è scarsa. In Italia è regolato per legge, ma poco misurato. Questa guida spiega cos'è, quali livelli di riferimento valgono, come si misura e cosa si fa se il valore è alto.</p>
<h2>Cos'è il radon e da dove viene</h2>
<p>Il radon nasce dal decadimento dell'uranio presente nel suolo e nelle rocce. Il gas entra negli edifici attraverso fessure, giunti, passaggi di tubazioni e pavimenti a contatto con il terreno. Per questo il piano terra e i seminterrati sono più esposti. Secondo l'ARPAE, il radon si concentra soprattutto quando la ventilazione degli edifici non è sufficiente.</p>
<h2>I livelli di riferimento</h2>
<p>Il D.Lgs. 101/2020 fissa livelli di riferimento come media annua della concentrazione in aria. Sono valori oltre i quali si suggeriscono azioni di risanamento.</p>
<table>
<thead><tr><th>Caso</th><th>Livello di riferimento (media annua)</th></tr></thead>
<tbody>
<tr><td>Abitazioni esistenti</td><td>300 Bq/m³</td></tr>
<tr><td>Abitazioni costruite dopo il 31 dicembre 2024</td><td>200 Bq/m³</td></tr>
<tr><td>Luoghi di lavoro</td><td>300 Bq/m³</td></tr>
</tbody>
</table>
<p>Il livello di riferimento non è una soglia sotto cui il rischio è zero: non esiste una concentrazione al di sotto della quale il rischio sia nullo. Per confronto, l'OMS raccomanda ai Paesi un livello di 100 Bq/m³, o comunque non superiore a 300 Bq/m³.</p>
<h2>Quanto radon c'è in Italia</h2>
<p>Una presentazione di ATS Brescia del novembre 2025 stima una concentrazione media italiana di circa 70 Bq/m³, con valori tra 100 e 120 in Lombardia. È una stima generale: il valore di una singola casa può essere molto diverso. L'Archivio Nazionale Radon raccoglie misure in oltre 50mila edifici tra abitazioni, scuole e luoghi di lavoro.</p>
<h2>Come si misura</h2>
<p>Non si sa quanto radon c'è in casa senza una misura. Il dato di riferimento è la media annua, e per questo la misura va fatta per un periodo lungo. Le indicazioni pratiche sono nella guida <a href="/radon/come-si-misura/">Come si misura il radon in casa</a>.</p>
<h2>Se il valore è alto</h2>
<p>Il radon si può ridurre. La tecnica più usata negli edifici con platea è la depressurizzazione del suolo: un pozzetto con un tubo e un ventilatore che aspira il gas dal sottosuolo e lo scarica all'esterno, secondo l'ISS. Le altre tecniche e i loro costi saranno trattati in una guida dedicata, in preparazione.</p>
<h2>Dove andare dopo</h2>
<ul>
<li><a href="/radon/come-si-misura/">Come si misura il radon in casa</a></li>
<li><a href="/radon/normativa/">Radon: cosa dice la legge per abitazioni e luoghi di lavoro</a></li>
<li><a href="/radon/lombardia/">Radon in Lombardia: aree prioritarie e misure</a></li>
</ul>
<p class="nota">Questa guida non sostituisce il parere di un tecnico o del medico. Per sintomi o dubbi sulla salute, rivolgiti al medico o all'ASL.</p>
""", sources=fonti("arpa_puglia_nota", "asl_roma3", "iss_epicentro", "ats_brescia_2025", "arpae_ecoscienza", "certifico_anr", "iss_riduzione"),
    section="radon", scala=True,
    breve=["È un gas radioattivo che sale dal suolo e si accumula nei locali bassi.",
           "Il livello di riferimento per le case esistenti è 300 Bq/m³ in media annua; 200 per quelle costruite dal 2025.",
           "Si conosce solo con una misura lunga; se è alto, si riduce con tecniche collaudate."],
    chiave=("300", "Bq/m³", "livello di riferimento per le abitazioni esistenti, media annua"))

add("/radon/come-si-misura/", "Come si misura il radon in casa",
    "Perché serve una misura di lunga durata, come leggerla e cosa considerare nella scelta dello strumento.",
    """
<p>Per sapere quanto radon c'è in casa serve una misura di lunga durata. Il valore che conta per la legge è la media annua, non il picco di un momento.</p>
<h2>Perché non basta una misura di pochi minuti</h2>
<p>La concentrazione di radon cambia nel giorno, tra una stagione e l'altra, e con il modo in cui si vive la casa. ARPA Lombardia lo dice in modo netto: l'unico modo per conoscere la concentrazione reale è misurare la media annuale. Un valore misurato in una mattina non dice molto.</p>
<h2>Dosimetri e rilevatori</h2>
<p>Ci sono due grandi famiglie di strumenti:</p>
<ul>
<li><strong>Dosimetri passivi</strong>: restano nell'ambiente per un periodo di misura, poi vanno analizzati in laboratorio. Sono il metodo più usato per la media annua.</li>
<li><strong>Rilevatori elettronici</strong>: mostrano l'andamento nel tempo e danno una lettura continua. Sono utili per capire quando il valore sale, ma la lettura va confrontata con una misura di riferimento.</li>
</ul>
<h2>Come fare una misura utile</h2>
<ul>
<li>Misura nel piano più frequentato, di solito la zona giorno al piano terra o nel locale abitato più basso.</li>
<li>Tieni lo strumento lontano da finestre, bocchette e fonti di calore.</li>
<li>Vivi la casa come di consueto: non aprire le finestre per l'occasione.</li>
<li>Per le regole di dettaglio, la norma di riferimento è la UNI ISO 11665-8.</li>
</ul>
<h2>Chi fa la misura</h2>
<p>In Lombardia, nelle campagne regionali, le misure sono fatte con dosimetri forniti da ARPA e posizionati dalle ATS. Dove non c'è una campagna pubblica, ci si rivolge a un laboratorio o a un servizio di misura qualificato. Il risultato va letto insieme alla data e alla durata della misura.</p>
<h2>Cosa fare con il risultato</h2>
<p>Se il valore è sotto il livello di riferimento, il controllo può essere ripetuto nel tempo. Se è sopra, il passo successivo è il risanamento, di cui parleremo in una guida dedicata.</p>
""", sources=fonti("arpa_lomb_rusconi", "arpae_ecoscianza" if False else "arpae_ecoscienza", "ats_brescia_2025"),
    section="radon",
    breve=["Conta la media annua: una misura breve non basta.",
           "Dosimetro passivo per la media di legge; rilevatore elettronico per seguire l'andamento.",
           "Si misura nel locale abitato più basso, vivendo la casa come sempre."],
    chiave=("12", "mesi", "durata di riferimento della misura, per ottenere una media annua"))

add("/radon/normativa/", "Radon: cosa dice la legge per abitazioni e luoghi di lavoro",
    "Il D.Lgs. 101/2020, i livelli di riferimento, le aree prioritarie e gli obblighi per i luoghi di lavoro.",
    """
<p>Il radon è regolato dal D.Lgs. 101/2020, che ha recepito la direttiva Euratom 2013/59. Il decreto è stato modificato dal D.Lgs. 203/2022. Questa pagina riassume cosa dice, articolo per articolo.</p>
<h2>I livelli di riferimento</h2>
<p>L'articolo 12 fissa i livelli di riferimento come media annua della concentrazione in aria: 300 Bq/m³ per le abitazioni esistenti e per i luoghi di lavoro, 200 Bq/m³ per le abitazioni costruite dopo il 31 dicembre 2024. Il quadro completo è nella <a href="/radon/guida-completa/">guida completa</a>.</p>
<h2>Le aree prioritarie</h2>
<p>L'articolo 11 chiede alle Regioni di individuare le zone in cui il livello di 300 Bq/m³ viene superato nel 15% degli edifici. Queste zone sono dette aree prioritarie. Il decreto prevede anche incentivi per i proprietari di case con locali al piano terra o seminterrati che misurano la concentrazione.</p>
<h2>Il Piano nazionale d'azione</h2>
<p>Il Piano nazionale d'azione per il radon 2023-2032 è stato approvato con DPCM dell'11 gennaio 2024 e pubblicato in Gazzetta Ufficiale il 21 febbraio 2024. Il piano punta a ridurre le concentrazioni negli edifici sopra i 200 Bq/m³, dando priorità a quelli sopra i 300.</p>
<h2>Luoghi di lavoro</h2>
<p>Per i luoghi di lavoro, il datore di lavoro, come esercente, deve valutare il radon. Se la concentrazione supera i 300 Bq/m³, deve adottare misure correttive per ridurla al livello più basso ragionevolmente ottenibile, con l'aiuto di un esperto in interventi di risanamento.</p>
<h2>Cosa la legge non fa</h2>
<p>La legge non obbliga il proprietario di una casa privata a misurare il radon. Stabilisce livelli di riferimento e incentivi, e rimanda alle Regioni la mappatura delle zone.</p>
<p class="nota">Le leggi sono riportate come pubblicate. Per un caso specifico, rivolgiti a un tecnico abilitato.</p>
""", sources=fonti("arpa_puglia_nota", "remetti", "dpcm_2024", "certifico_9941", "cni_rusconi"),
    section="radon", scala=True,
    breve=["D.Lgs. 101/2020, art. 12: 300 Bq/m³ per case esistenti e luoghi di lavoro, 200 per case costruite dal 2025.",
           "Art. 11: le Regioni individuano le aree prioritarie, dove il 15% degli edifici supera i 300.",
           "Per i privati non c'è obbligo di misura; per i datori di lavoro sì, con misure correttive sopra i 300."],
    chiave=("15%", "degli edifici", "sopra 300 Bq/m³: la soglia che definisce un'area prioritaria"))

add("/radon/lombardia/", "Radon in Lombardia: aree prioritarie e misure",
    "Dove si concentra il rischio radon in Lombardia, come sono state individuate le aree prioritarie e cosa fare.",
    """
<p>La Lombardia è tra le regioni italiane più interessate dal radon. L'ARPA regionale ha individuato 90 comuni in area prioritaria, con circa 200.000 abitanti. Questa pagina spiega come sono stati scelti e cosa significa per chi vive in Lombardia.</p>
<h2>Come sono stati scelti i comuni</h2>
<p>I comuni in area prioritaria sono quelli in cui la stima della percentuale di edifici sopra 300 Bq/m³ è pari o superiore al 15%. La prima individuazione è stata approvata con DGR 508 del 26 giugno 2023. Si basa su campagne di misura precedenti: tra il 2003 e il 2004 e tra il 2009 e il 2010 sono state fatte 3.933 misure in 551 comuni.</p>
<h2>Il quadro regionale</h2>
<p>Una presentazione di ATS Brescia del novembre 2025 indica una concentrazione media in Lombardia di 100-120 Bq/m³, contro una media italiana di circa 70. Sono valori di sintesi: la concentrazione in una casa dipende dalla zona, dalla costruzione, dai materiali e dalla ventilazione.</p>
<h2>Area prioritaria non vuol dire area esclusiva</h2>
<p>ARPA Lombardia lo ripete: la presenza di ambienti con concentrazioni elevate non è limitata alle aree prioritarie. Anche fuori dai 90 comuni il radon può superare il livello di riferimento. Per saperlo serve una misura.</p>
<h2>Le campagne regionali</h2>
<p>Regione Lombardia, con ARPA e le ATS, promuove campagne di mappatura e monitoraggio nei comuni coinvolti. Le campagne invitano a misurare il radon nei locali domestici, in particolare al piano terra. Per sapere se il tuo comune è coinvolto e come partecipare, consulta la pagina della Regione.</p>
<h2>Le linee guida regionali</h2>
<p>La Regione ha aggiornato le linee guida per la prevenzione dal radon in ambienti chiusi: la seconda edizione è del dicembre 2025. Riguardano comuni, progettisti e costruttori, e indicano come misurare e come intervenire.</p>
<p class="nota">I numeri di questa pagina vengono dalle fonti elencate in fondo. La lista completa dei comuni in area prioritaria va verificata sul sito della Regione o di ARPA, perché può essere aggiornata.</p>
""", sources=fonti("arpa_lomb_rusconi", "arpae_ecoscienza", "ats_brescia_2025", "regione_lomb", "certifico_lg_lomb"),
    section="radon",
    breve=["90 comuni lombardi sono in area prioritaria, circa 200.000 abitanti.",
           "La media regionale stimata è 100-120 Bq/m³, contro circa 70 in Italia.",
           "Anche fuori dai 90 comuni il radon può essere alto: solo la misura lo dice."],
    chiave=("90", "comuni", "in area prioritaria in Lombardia, prima individuazione del 2023"))

# ------------------------------------------------------------- bozze
add("/bozze/rilevatori-confronto/", "BOZZA: i migliori rilevatori di radon per la casa",
    "Bozza. Pagina in attesa di prezzi verificati.",
    """
<p class="nota"><strong>Bozza, non pubblicata.</strong> La tabella dei prezzi non è ancora verificata.</p>
<h2>Cosa confrontare</h2>
<ul>
<li>Tipo di misura: dosimetro passivo da laboratorio o rilevatore elettronico con lettura continua.</li>
<li>Uso previsto: misura annua per la media di legge, oppure controllo nel tempo.</li>
<li>Costi nel tempo: abbonamento, sostituzioni, analisi di laboratorio.</li>
</ul>
<h2>Tabella prodotti</h2>
<p>Da completare dopo la verifica dei prezzi.</p>
""", status="draft", section="bozza")

add("/bozze/risanamento/", "BOZZA: radon alto, come si risana una casa e quanto costa",
    "Bozza. Costi di risanamento da verificare prima della pubblicazione.",
    """
<p class="nota"><strong>Bozza, non pubblicata.</strong> I costi non sono ancora verificati.</p>
<h2>Le tecniche</h2>
<p>Secondo l'ISS, negli edifici con fondazione a platea la tecnica più usata è la depressurizzazione del suolo con un pozzetto installato dentro o accanto all'edificio. Altre tecniche sono meno frequenti: ventilazione delle cantine, pressurizzazione del suolo, sigillatura delle vie di ingresso.</p>
<h2>Costi</h2>
<p>Da completare con fonti verificate e data.</p>
""", sources=fonti("iss_riduzione", "remetti"), status="draft", section="bozza")


# ------------------------------------------------------------- news
# (slug, data ISO, data leggibile, titolo, cosa è successo, cosa cambia per chi legge, [(etichetta fonte, url)])
NEWS = [
    ("bergamo-campagna-radon-ottobre-2026", "2026-09-30", "30 settembre 2026",
     "Bergamo: dal 1° ottobre misura gratuita del radon in nove comuni",
     "ATS Bergamo, con ARPA Lombardia, ha avviato dal 1° ottobre 2026 una campagna gratuita di misura del radon nelle abitazioni di nove comuni della provincia. Ai cittadini che aderiscono viene consegnato un dosimetro passivo da posizionare in casa; la prima misura dura circa sei mesi e al termine ogni partecipante riceve il risultato della propria abitazione.",
     "Se abiti in uno dei comuni coinvolti, è l'occasione per una misura di qualità senza spesa. L'elenco dei comuni e il modulo di adesione sono sul sito di ATS Bergamo.",
     [("ATS Bergamo, comunicato del 30 settembre 2026", "https://www.ats-bg.it/news/radon-nelle-abitazioni-ats-bergamo-avvia-una-nuova-campagna-citizen-science-alcuni-comuni-bergamasachi")]),
    ("aree-prioritarie-italia-luglio-2026", "2026-07-22", "22 luglio 2026",
     "Aree prioritarie radon: a luglio 2026 il punto Regione per Regione",
     "ARPA Lombardia tiene aggiornata la mappa delle aree prioritarie a rischio radon in Italia. Al 22 luglio 2026 hanno completato la prima individuazione, con pubblicazione in Gazzetta Ufficiale, tra le altre: Lombardia (90 comuni), Liguria (16), Valle d'Aosta (11), Provincia di Bolzano (58) e Provincia di Trento (15). L'Emilia-Romagna ha preso atto che, dai dati disponibili, nessun comune rientra in area prioritaria. Al 31 gennaio 2026 i comuni classificati in Italia erano 394.",
     "Essere in area prioritaria non significa che ogni casa superi i 300 Bq/m³, e fuori da quelle aree il radon può comunque essere alto. Per i datori di lavoro con locali al piano terra, in area prioritaria scatta l'obbligo di misura.",
     [("ARPA Lombardia, aree prioritarie in Italia (aggiornata al 22 luglio 2026)", "https://www.arpalombardia.it/temi-ambientali/radioattivita/il-radon/aree-prioritarie-in-italia/"),
      ("ARPA Lombardia, notizia del 16 febbraio 2026", "https://www.arpalombardia.it/agenda/notizie/2026/aree-prioritarie-rischio-radon-lombardia-fra-le-otto-regioni-che-hanno-classificato-il-territorio/")]),
    ("trentino-misure-gratuite-maggio-2026", "2026-05-15", "15 maggio 2026",
     "Trentino: approvate le aree prioritarie e aperta la misura gratuita per tutti i cittadini",
     "La Giunta provinciale di Trento ha approvato il 15 maggio 2026 la prima individuazione delle aree prioritarie a rischio radon, basata su oltre 1.300 misure fatte da APPA tra il 1995 e il 2025. In parallelo APPA ha aperto una campagna di misura gratuita nelle abitazioni, con due o più dosimetri da tenere in casa per un anno; nei primi giorni erano già arrivate quasi 200 richieste.",
     "Chi vive in Trentino può candidarsi con un modulo online sul sito di APPA. Il ritiro e la riconsegna dei dosimetri, a Trento, sono a carico del cittadino.",
     [("Provincia autonoma di Trento, comunicato del 15 maggio 2026", "https://www.ufficiostampa.provincia.tn.it/Comunicati/Gas-radon-al-via-la-campagna-di-misurazioni-gratuite-per-i-cittadini"),
      ("APPA Trento, pagina della campagna", "https://www.appa.provincia.tn.it/News/Avvisi/Partecipa-alla-campagna-di-misurazione-del-gas-radon-in-Trentino")]),
]


# ------------------------------------------------------------- rendering
def esc(s):
    return html.escape(s, quote=True)


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[àá]", "a", s); s = re.sub(r"[èé]", "e", s); s = re.sub(r"[ìí]", "i", s)
    s = re.sub(r"[òó]", "o", s); s = re.sub(r"[ùú]", "u", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def add_ids(body):
    """Dà un id a ogni h2 e restituisce (body, [(id, titolo)])."""
    toc = []

    def rep(m):
        t = m.group(1)
        i = slugify(t)
        toc.append((i, re.sub(r"<[^>]+>", "", t)))
        return f'<h2 id="{i}">{t}</h2>'
    return re.sub(r"<h2>(.*?)</h2>", rep, body), toc


def scala_svg(compatta=False):
    """La scala del radon: 0-400 Bq/m³ con i tre livelli."""
    w, h = 720, 118
    x0, x1 = 24, 696
    y = 58

    def X(v):
        return x0 + (x1 - x0) * v / 400
    marks = [(100, "100", "OMS: livello consigliato"),
             (200, "200", "Case costruite dal 2025"),
             (300, "300", "Case esistenti e luoghi di lavoro")]
    out = [f'<svg class="scala" viewBox="0 0 {w} {h}" role="img" aria-label="Scala del radon da 0 a 400 becquerel per metro cubo con i livelli di riferimento 100, 200 e 300">']
    out.append(f'<line x1="{x0}" y1="{y}" x2="{X(300)}" y2="{y}" class="sc-base"/>')
    out.append(f'<line x1="{X(300)}" y1="{y}" x2="{x1}" y2="{y}" class="sc-over"/>')
    for v in (0, 400):
        out.append(f'<line x1="{X(v)}" y1="{y-6}" x2="{X(v)}" y2="{y+6}" class="sc-tick"/>')
        out.append(f'<text x="{X(v)}" y="{y+26}" class="sc-num" text-anchor="middle">{v}</text>')
    for v, lab, desc in marks:
        cls = "sc-mark sc-mark-over" if v == 300 else "sc-mark"
        out.append(f'<circle cx="{X(v)}" cy="{y}" r="7" class="{cls}"/>')
        out.append(f'<text x="{X(v)}" y="{y+26}" class="sc-num sc-num-b" text-anchor="middle">{lab}</text>')
        anchor = "middle"
        out.append(f'<text x="{X(v)}" y="{y-18}" class="sc-lab" text-anchor="{anchor}">{esc(desc)}</text>')
    out.append(f'<text x="{x1}" y="{y+48}" class="sc-unit" text-anchor="end">Bq/m³, media annua</text>')
    out.append('</svg>')
    return "".join(out)


def casa_svg(focus=None, cls="casa"):
    """Casa in sezione: radon dal suolo, muffa sul muro, aria dalla finestra, acqua nei tubi, ventilazione sul tetto."""
    f = f" focus-{focus}" if focus else ""
    return f"""<svg class="{cls}{f}" viewBox="0 0 640 420" role="img" aria-label="Casa in sezione: il radon sale dal terreno, la muffa sul muro del seminterrato, l'aria entra dalla finestra, l'acqua arriva dai tubi, la ventilazione esce dal tetto">
<defs>
<pattern id="terra" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="4" r="1.3" fill="#B59A74" opacity=".55"/><circle cx="10" cy="10" r="1" fill="#B59A74" opacity=".4"/></pattern>
</defs>
<!-- cielo e terreno -->
<rect x="0" y="0" width="640" height="420" fill="none"/>
<rect x="0" y="300" width="640" height="120" fill="#E9DFCF"/>
<rect x="0" y="300" width="640" height="120" fill="url(#terra)"/>
<path d="M0 300 H640" stroke="#C8B89C" stroke-width="2"/>
<circle cx="80" cy="80" r="26" fill="#F3C867" opacity=".9"/>
<path d="M520 60 a16 16 0 0 1 30 -8 a14 14 0 0 1 26 8 a10 10 0 0 1 -4 20 H524 a10 10 0 0 1 -4 -20z" fill="#FFFFFF" stroke="#DDE5EB" stroke-width="2"/>
<!-- casa: seminterrato -->
<rect x="150" y="300" width="340" height="80" fill="#F7F3EC" stroke="#4A4035" stroke-width="3"/>
<!-- piano terra -->
<rect x="150" y="190" width="340" height="110" fill="#FFFFFF" stroke="#4A4035" stroke-width="3"/>
<path d="M150 300 H490" stroke="#4A4035" stroke-width="3"/>
<!-- tetto -->
<path d="M130 190 L320 70 L510 190 Z" fill="#F0E6D8" stroke="#4A4035" stroke-width="3" stroke-linejoin="round"/>
<!-- camino / ventilazione -->
<g class="l-ventilazione">
<rect x="412" y="100" width="34" height="60" fill="#F7F3EC" stroke="#4A4035" stroke-width="3"/>
<path d="M429 92 c-10 -14 10 -22 0 -36" fill="none" stroke="#7A5CB8" stroke-width="4" stroke-linecap="round"/>
<path d="M443 86 c-8 -12 8 -18 0 -30" fill="none" stroke="#7A5CB8" stroke-width="3" stroke-linecap="round" opacity=".6"/>
<path d="M415 86 c-8 -12 8 -18 0 -30" fill="none" stroke="#7A5CB8" stroke-width="3" stroke-linecap="round" opacity=".6"/>
</g>
<!-- finestra e aria -->
<g class="l-aria">
<rect x="190" y="215" width="70" height="60" fill="#E6F1F9" stroke="#4A4035" stroke-width="3"/>
<path d="M225 215 V275 M190 245 H260" stroke="#4A4035" stroke-width="2"/>
<path d="M120 240 h50" stroke="#2E7FB8" stroke-width="4" stroke-linecap="round"/>
<path d="M160 232 l12 8 -12 8" fill="none" stroke="#2E7FB8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M110 258 h40" stroke="#2E7FB8" stroke-width="3" stroke-linecap="round" opacity=".55"/>
<path d="M110 222 h40" stroke="#2E7FB8" stroke-width="3" stroke-linecap="round" opacity=".55"/>
</g>
<!-- porta -->
<rect x="400" y="230" width="44" height="70" fill="#F0E6D8" stroke="#4A4035" stroke-width="3"/>
<!-- muffa sul muro del seminterrato -->
<g class="l-muffa">
<circle cx="163" cy="312" r="7" fill="#5E7A3A" opacity=".8"/><circle cx="175" cy="322" r="5" fill="#5E7A3A" opacity=".65"/><circle cx="160" cy="330" r="4" fill="#5E7A3A" opacity=".7"/><circle cx="170" cy="340" r="6" fill="#5E7A3A" opacity=".5"/><circle cx="158" cy="349" r="3" fill="#5E7A3A" opacity=".6"/>
</g>
<!-- tubo acqua -->
<g class="l-acqua">
<path d="M560 420 V340 H490" fill="none" stroke="#1C8C8C" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M490 340 V320" fill="none" stroke="#1C8C8C" stroke-width="7" stroke-linecap="round"/>
<path d="M470 312 c0 6 -4 9 -4 13 a4 4 0 0 0 8 0 c0 -4 -4 -7 -4 -13z" fill="#1C8C8C"/>
<path d="M458 330 c0 5 -3 7 -3 10 a3 3 0 0 0 6 0 c0 -3 -3 -5 -3 -10z" fill="#1C8C8C" opacity=".6"/>
</g>
<!-- radon dal suolo -->
<g class="l-radon">
<path d="M230 410 c-8 -16 8 -24 0 -40 c-8 -16 8 -24 0 -40" fill="none" stroke="#C98A00" stroke-width="4" stroke-linecap="round"/>
<path d="M300 414 c-8 -16 8 -24 0 -40 c-8 -16 8 -24 0 -40" fill="none" stroke="#C98A00" stroke-width="4" stroke-linecap="round" opacity=".75"/>
<path d="M370 410 c-8 -16 8 -24 0 -40 c-8 -16 8 -24 0 -40" fill="none" stroke="#C98A00" stroke-width="4" stroke-linecap="round"/>
<circle cx="250" cy="330" r="4" fill="#C98A00"/><circle cx="330" cy="318" r="3" fill="#C98A00" opacity=".7"/><circle cx="395" cy="336" r="4" fill="#C98A00"/><circle cx="280" cy="350" r="3" fill="#C98A00" opacity=".6"/><circle cx="350" cy="360" r="3" fill="#C98A00" opacity=".8"/>
<!-- fessura nel pavimento -->
<path d="M300 380 l6 -8 -4 -6 5 -6" fill="none" stroke="#4A4035" stroke-width="2"/>
</g>
</svg>"""


def nav_html(current):
    items = []
    for href, label in NAV:
        classes = []
        if current.startswith(href): classes.append("on")
        if href in TEMI: classes.append("t-" + TEMI[href][0])
        cls = f' class="{" ".join(classes)}"' if classes else ""
        items.append(f'<a href="{href}"{cls}>{esc(label)}</a>')
    return '<nav class="nav" aria-label="Sezioni">' + "".join(items) + "</nav>"


HEAD_COMMON = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site-{CSSV}.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
"""


def header(current):
    return f"""<header class="top">
<div class="wrap top-in">
<a class="brand" href="/"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 40 28" width="40" height="28"><path d="M4 22 A16 16 0 0 1 36 22" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/><path d="M11 22 A9 9 0 0 1 29 22" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" opacity=".45"/><rect x="8" y="24.5" width="24" height="3" rx="1.5" fill="#C98A00"/></svg></span><span class="brand-text"><span class="brand-name">Casa Respira</span><span class="brand-pay">aria e acqua di casa, misurate e spiegate</span></span></a>
{nav_html(current)}
</div>
</header>"""


FOOTER = """<footer class="foot">
<div class="wrap">
<p>Casa Respira è una guida indipendente su aria e acqua dentro casa. Nessuna firma: i testi sono della redazione. Alcuni link sono affiliati, come spiegato in <a href="/come-lavoriamo/#come-ci-sosteniamo">Come lavoriamo</a>. Non sostituisce il parere di un tecnico o del medico.</p>
<p><a href="/feed.xml">Feed RSS</a> · <a href="/chi-siamo/">Chi siamo</a> · <a href="/come-lavoriamo/">Come lavoriamo</a> · <a href="/come-lavoriamo/#come-ci-sosteniamo">Come ci sosteniamo</a></p>
</div>
</footer>"""


def tema_di(path):
    for k, v in TEMI.items():
        if path.startswith(k): return v[0]
    return ""


def render_page(p):
    body, toc = add_ids(p["body"])
    noindex = p["status"] == "draft"
    is_guide = p["section"] == "radon"

    aside = ""
    if is_guide:
        parts = []
        if p["chiave"]:
            n, u, d = p["chiave"]
            parts.append(f'<div class="chiave"><span class="chiave-n">{esc(n)}</span><span class="chiave-u">{esc(u)}</span><p>{esc(d)}</p></div>')
        if toc:
            lis = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
            parts.append(f'<nav class="indice" aria-label="In questa pagina"><p class="indice-t">In questa pagina</p><ol>{lis}</ol></nav>')
        aside = '<aside class="lato">' + "".join(parts) + "</aside>"

    breve = ""
    if p["breve"]:
        lis = "".join(f"<li>{esc(b)}</li>" for b in p["breve"])
        breve = f'<div class="breve"><p class="breve-t">In breve</p><ul>{lis}</ul></div>'

    scala = f'<figure class="scala-box">{scala_svg()}<figcaption>Livelli di riferimento del D.Lgs. 101/2020 e raccomandazione OMS. Oltre il livello della tua casa, si interviene.</figcaption></figure>' if p["scala"] else ""

    fonti_html = ""
    if p["sources"]:
        lis = "".join(f'<li><a href="{esc(u)}" rel="nofollow noopener">{esc(l)}</a></li>' for l, u in p["sources"])
        fonti_html = f'<section class="fonti" id="fonti"><h2>Fonti</h2><ul>{lis}</ul><p class="nota">Link controllati il {DATA_ULTIMA_VERIFICA}.</p></section>'

    layout_cls = "pagina pagina-guida" if is_guide else "pagina"
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>{esc(p['title'])} | Casa Respira</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{SITE}{p['path']}">
{'<meta name="robots" content="noindex, nofollow">' if noindex else ''}
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body class="tema-{tema_di(p['path'])}">
{header(p['path'])}
<main class="wrap {layout_cls}">
<article class="testo">
<p class="verifica">Fonti verificate il {DATA_ULTIMA_VERIFICA}</p>
<h1>{esc(p['title'])}</h1>
{breve}
{scala}
{body}
{fonti_html}
<section class="correzioni"><h2>Correzioni</h2><p>Nessuna correzione finora.</p></section>
</article>
{aside}
</main>
{FOOTER}
</body>
</html>
"""


def render_sezione(path, nome, lead, previste, radon):
    pubblicate = [p for p in radon] if path == "/radon/" else []
    pub_html = ""
    if pubblicate:
        lis = "".join(f'<li><a href="{p["path"]}"><strong>{esc(p["title"])}</strong><span>{esc(p["desc"])}</span></a></li>' for p in pubblicate)
        pub_html = f'<h2>Le guide pubblicate</h2><ul class="lista-guide">{lis}</ul>'
    prev = "".join(f"<li>{esc(t)}</li>" for t in previste)
    titolo_prev = "In preparazione" if pubblicate else "Le guide in preparazione"
    intro_vuota = "" if pubblicate else '<p>Questa sezione non ha ancora guide pubblicate. Le prime escono nelle prossime settimane, una alla volta, con le stesse regole delle altre: fonti istituzionali con link e data, prezzi verificati, correzioni dichiarate.</p>'
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>{esc(nome)} | Casa Respira</title>
<meta name="description" content="{esc(lead)}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body class="tema-{tema_di(path)}">
{header(path)}
<main class="wrap pagina">
<article class="testo sezione">
<div class="sezione-testa"><div><h1>{esc(nome)}</h1>
<p class="lead">{esc(lead)}</p></div><figure class="sezione-casa">{casa_svg(tema_di(path))}</figure></div>
{intro_vuota}
{pub_html}
<h2>{titolo_prev}</h2>
<ul class="previste">{prev}</ul>
<p class="nota">Per ricevere le nuove guide: <a href="/feed.xml">feed RSS</a>.</p>
</article>
</main>
{FOOTER}
</body>
</html>
"""


def render_news_item(n):
    slug, iso, data, titolo, fatto, cambia, fonti_ = n
    lis = "".join(f'<li><a href="{esc(u)}" rel="nofollow noopener">{esc(l)}</a></li>' for l, u in fonti_)
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>{esc(titolo)} | Casa Respira</title>
<meta name="description" content="{esc(fatto[:150])}">
<link rel="canonical" href="{SITE}/news/{slug}/">
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body>
{header('/news/')}
<main class="wrap pagina">
<article class="testo news-item">
<p class="verifica"><time datetime="{iso}">{esc(data)}</time> · Notizia</p>
<h1>{esc(titolo)}</h1>
<h2>Cosa è successo</h2>
<p>{esc(fatto)}</p>
<h2>Cosa cambia per te</h2>
<p>{esc(cambia)}</p>
<section class="fonti"><h2>Fonte</h2><ul>{lis}</ul></section>
<p class="nota"><a href="/news/">Tutte le notizie</a></p>
</article>
</main>
{FOOTER}
</body>
</html>
"""


def render_news_index():
    items = "".join(f'<li><time datetime="{n[1]}">{esc(n[2])}</time><a href="/news/{n[0]}/">{esc(n[3])}</a><p>{esc(n[5])}</p></li>' for n in NEWS)
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>News | Casa Respira</title>
<meta name="description" content="Notizie brevi su radon, aria e acqua di casa: campagne di misura, nuove aree prioritarie, norme. Solo con fonte istituzionale e data.">
<link rel="canonical" href="{SITE}/news/">
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body>
{header('/news/')}
<main class="wrap pagina">
<article class="testo sezione">
<h1>News</h1>
<p class="lead">Notizie brevi su radon, aria e acqua di casa: campagne di misura gratuite, nuove aree prioritarie, norme. Ogni notizia ha la fonte istituzionale con link e data, e dice cosa cambia per chi legge.</p>
<ul class="lista-news">{items}</ul>
<p class="nota">Le notizie escono anche nel <a href="/feed.xml">feed RSS</a>.</p>
</article>
</main>
{FOOTER}
</body>
</html>
"""


def render_home(radon):
    guide = "".join(
        f'<li><a href="{p["path"]}"><strong>{esc(p["title"])}</strong><span>{esc(p["desc"])}</span></a></li>'
        for p in radon)
    ultime = "".join(f'<li><time datetime="{n[1]}">{esc(n[2])}</time><a href="/news/{n[0]}/">{esc(n[3])}</a></li>' for n in NEWS[:3])
    temi = "".join(
        f'<li class="t-{TEMI[path][0]}"><a href="{path}"><strong>{esc(nome)}</strong><span>{esc(lead)}</span><em>{len(prev)} guide in preparazione</em></a></li>'
        for path, nome, lead, prev in SEZIONI if path != "/radon/")
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>Casa Respira | Aria e acqua di casa, misurate e spiegate</title>
<meta name="description" content="Guida indipendente su aria e acqua dentro casa. Il radon è il tema di partenza: livelli di legge, come si misura, come si riduce.">
<link rel="canonical" href="{SITE}/">
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body>
{header('/')}
<main>
<section class="hero">
<div class="wrap hero-in">
<div class="hero-testo">
<h1>Cosa respiri e cosa bevi dentro casa?</h1>
<p class="hero-p">Il radon che sale dal terreno, la muffa sui muri, l'aria che entra dalle finestre, l'acqua che arriva dai tubi. Casa Respira li spiega con i numeri delle fonti pubbliche: cosa misurare, quando è un problema, cosa fare e quanto costa.</p>
<p class="hero-temi"><a class="t-radon" href="/radon/">Radon</a><a class="t-muffa" href="/muffa/">Muffa e umidità</a><a class="t-aria" href="/aria/">Aria</a><a class="t-ventilazione" href="/ventilazione/">Ventilazione</a><a class="t-acqua" href="/acqua/">Acqua</a></p>
</div>
<figure class="hero-casa">{casa_svg()}</figure>
</div>
</section>
<section class="wrap radon-apre">
<h2>Si parte dal radon: nessuno sa quanto ce n'è in casa senza una misura</h2>
<figure class="scala-box scala-hero">{scala_svg()}<figcaption>La scala del radon: il valore medio annuo della tua casa si confronta con questi livelli, fissati dal D.Lgs. 101/2020 e dall'OMS.</figcaption></figure>
</section>
<section class="wrap guide">
<h2>Le guide sul radon</h2>
<ul class="lista-guide">{guide}</ul>
</section>
<section class="wrap temi">
<h2>Gli altri temi</h2>
<ul class="lista-temi">{temi}</ul>
<p class="nota">Le sezioni senza guide si riempiono nelle prossime settimane, una pagina alla volta. Le nuove pagine escono nel <a href="/feed.xml">feed RSS</a>.</p>
</section>
<section class="wrap ultime">
<h2>Ultime notizie</h2>
<ul class="lista-news compatta">{ultime}</ul>
<p><a href="/news/">Tutte le notizie</a></p>
</section>
<section class="wrap metodo">
<h2>Come lavoriamo</h2>
<dl>
<div><dt>Fonti istituzionali</dt><dd>ISS, ARPA, ISIN, Ministero della Salute. Ogni numero ha un link e una data.</dd></div>
<div><dt>Prezzi con data</dt><dd>Aggiornati a gennaio, aprile, luglio e ottobre. Senza verifica non si pubblica.</dd></div>
<div><dt>Correzioni dichiarate</dt><dd>In fondo a ogni pagina, con la data. Finora: nessuna.</dd></div>
<div><dt>Niente consigli medici</dt><dd>Per sintomi e dubbi sulla salute rimandiamo al medico o all'ASL.</dd></div>
</dl>
<p><a href="/come-lavoriamo/">Il metodo per esteso, e come ci sosteniamo</a>.</p>
</section>
</main>
{FOOTER}
</body>
</html>
"""


CSS = """
:root{
  --carta:#F7F9FA; --bianco:#FFFFFF; --inchiostro:#16222E; --testo:#2A3845; --grigio:#5F6E7B;
  --nebbia:#DDE5EB; --nebbia-chiara:#EEF2F5; --aria:#2E7FB8; --aria-scura:#1F5F8E; --ambra:#C98A00;
  --wrap:1040px; --misura:66ch;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--carta);color:var(--testo);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:17px;line-height:1.6}
a{color:var(--aria-scura);text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{color:var(--aria)}
:focus-visible{outline:2px solid var(--aria);outline-offset:3px}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 24px}
h1,h2,h3{color:var(--inchiostro);font-weight:600;line-height:1.2;letter-spacing:-0.01em;margin:0}
h1{font-family:"Fraunces",Georgia,serif;font-weight:500;letter-spacing:-0.015em;font-variation-settings:"opsz" 72}
h1{font-size:clamp(28px,4vw,40px)}
h2{font-size:22px;margin-top:40px;margin-bottom:10px}
p{margin:0 0 16px}
ul,ol{padding-left:22px;margin:0 0 16px}
li{margin:4px 0}
strong{font-weight:600;color:var(--inchiostro)}
table{width:100%;border-collapse:collapse;margin:16px 0 24px;font-size:15.5px;background:var(--bianco)}
th,td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--nebbia)}
th{font-weight:600;color:var(--inchiostro);background:var(--nebbia-chiara)}
.nota{color:var(--grigio);font-size:15px}

/* testata */
.top{background:var(--bianco);border-bottom:1px solid var(--nebbia)}
.top-in{display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:76px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}
.brand{display:inline-flex;align-items:center;gap:12px;text-decoration:none;color:var(--inchiostro)}
.brand-mark{color:var(--aria);display:inline-flex;flex:none}
.brand-mark svg{display:block}
.brand-text{display:flex;flex-direction:column;line-height:1.1}
.brand-name{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:27px;letter-spacing:-0.01em;color:var(--inchiostro);font-variation-settings:"opsz" 40}
.brand-pay{font-size:13.5px;color:var(--grigio);margin-top:2px;letter-spacing:0.01em}
.nav{display:flex;gap:4px;flex-wrap:wrap}
.nav a{padding:8px 12px;border-radius:6px;text-decoration:none;color:var(--testo);font-size:15.5px}
.nav a:hover{background:var(--nebbia-chiara);color:var(--inchiostro)}
.nav a.on{color:var(--inchiostro);box-shadow:inset 0 -2px 0 var(--aria)}

/* home */
.hero{background:var(--bianco);border-bottom:1px solid var(--nebbia);padding:56px 0 40px}
.hero h1{max-width:22ch;font-size:clamp(32px,4.8vw,50px);line-height:1.12}
.hero-p{max-width:var(--misura);font-size:18.5px;margin:18px 0 28px;color:var(--testo)}
.scala-box{margin:8px 0 24px;background:var(--bianco);border:1px solid var(--nebbia);border-radius:10px;padding:18px 18px 10px}
.scala-hero{max-width:820px}
.scala{width:100%;height:auto;display:block}
.scala-box figcaption{color:var(--grigio);font-size:14.5px;margin-top:8px;max-width:70ch}
.sc-base{stroke:var(--aria);stroke-width:6;stroke-linecap:round}
.sc-over{stroke:var(--ambra);stroke-width:6;stroke-linecap:round}
.sc-tick{stroke:var(--grigio);stroke-width:2}
.sc-mark{fill:var(--bianco);stroke:var(--aria);stroke-width:3}
.sc-mark-over{stroke:var(--ambra)}
.sc-num{font:400 14px "IBM Plex Sans",sans-serif;fill:var(--grigio)}
.sc-num-b{font-weight:600;fill:var(--inchiostro);font-size:16px}
.sc-lab{font:400 12.5px "IBM Plex Sans",sans-serif;fill:var(--testo)}
.sc-unit{font:400 12.5px "IBM Plex Sans",sans-serif;fill:var(--grigio)}
.guide{padding:44px 24px 8px}
.guide h2{margin-top:0}
.lista-guide{list-style:none;padding:0;margin:16px 0 20px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.lista-guide a{display:block;background:var(--bianco);border:1px solid var(--nebbia);border-left:4px solid #C98A00;border-radius:8px;padding:16px 18px;text-decoration:none;color:var(--testo);height:100%}
.lista-guide a:hover{border-left-color:var(--ambra);background:#FBFDFE}
.lista-guide strong{display:block;font-size:17.5px;margin-bottom:6px}
.lista-guide span{font-size:15px;color:var(--grigio)}
.metodo{padding:28px 24px 56px}
.metodo h2{margin-top:0}
.metodo dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px 28px;margin:16px 0 20px}
.metodo dt{font-weight:600;color:var(--inchiostro);margin-bottom:4px}
.metodo dd{margin:0;font-size:15.5px;color:var(--testo)}

/* pagine */
.pagina{padding:36px 24px 56px}
.pagina-guida{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:48px;align-items:start}
.testo{max-width:var(--misura)}
.testo.sezione{max-width:none}
.sezione .lead,.sezione .previste,.sezione>p{max-width:var(--misura)}
.testo>p,.testo>ul,.testo>ol{max-width:var(--misura)}
.verifica{color:var(--grigio);font-size:14.5px;margin-bottom:10px}
.verifica::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--aria);margin-right:8px;vertical-align:middle}
.testo h1{margin-bottom:18px}
.breve{background:var(--nebbia-chiara);border-radius:10px;padding:16px 20px 6px;margin:0 0 26px}
.breve-t{font-weight:600;color:var(--inchiostro);margin-bottom:6px}
.breve ul{margin-bottom:8px}
.breve li{margin:6px 0}
.lato{position:sticky;top:20px;display:flex;flex-direction:column;gap:20px}
.chiave{background:var(--bianco);border:1px solid var(--nebbia);border-top:4px solid var(--ambra);border-radius:8px;padding:16px 18px}
.chiave-n{display:block;font-family:"Fraunces",Georgia,serif;font-size:46px;font-weight:600;line-height:1;color:var(--inchiostro);letter-spacing:-0.02em}
.chiave-u{display:block;font-size:16px;font-weight:500;color:var(--aria-scura);margin:4px 0 8px}
.chiave p{margin:0;font-size:14.5px;color:var(--grigio)}
.indice{font-size:15px}
.indice-t{font-weight:600;color:var(--inchiostro);margin-bottom:6px}
.indice ol{list-style:none;padding:0;margin:0;border-left:2px solid var(--nebbia)}
.indice li{margin:0}
.indice a{display:block;padding:5px 0 5px 12px;text-decoration:none;color:var(--testo)}
.indice a:hover{color:var(--aria-scura);box-shadow:inset 2px 0 0 var(--aria)}
.fonti{margin-top:48px;padding-top:16px;border-top:1px solid var(--nebbia)}
.fonti h2{margin-top:0;font-size:19px}
.fonti li{font-size:15px;margin:6px 0}
.correzioni{margin-top:28px;padding-top:12px;border-top:1px solid var(--nebbia)}
.correzioni h2{margin-top:0;font-size:19px}
.correzioni p{color:var(--grigio);font-size:15px}

/* sezioni e temi */
.lead{font-size:18.5px;color:var(--testo);max-width:var(--misura)}
.sezione h2{margin-top:32px}
.previste{list-style:none;padding:0;margin:12px 0 20px;border-left:2px solid var(--nebbia)}
.previste li{padding:6px 0 6px 14px;color:var(--grigio);margin:0}
.previste li::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;border:2px solid var(--nebbia);margin-right:10px;vertical-align:middle}
.temi{padding:8px 24px 16px}
.temi h2{margin-top:0}
.lista-temi{list-style:none;padding:0;margin:16px 0 20px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.lista-temi a{display:block;background:var(--bianco);border:1px solid var(--nebbia);border-radius:8px;padding:16px 18px;text-decoration:none;color:var(--testo);height:100%}
.lista-temi a:hover{border-color:var(--aria)}
.lista-temi strong{display:block;font-size:17.5px;margin-bottom:6px}
.lista-temi span{display:block;font-size:15px;color:var(--grigio)}
.lista-temi em{display:block;font-style:normal;font-size:13.5px;color:var(--aria-scura);margin-top:8px}
.nav a{padding:8px 10px;font-size:15px}

/* news */
.lista-news{list-style:none;padding:0;margin:20px 0}
.lista-news li{padding:16px 0;border-top:1px solid var(--nebbia)}
.lista-news li:last-child{border-bottom:1px solid var(--nebbia)}
.lista-news time{display:block;font-size:13.5px;color:var(--grigio);margin-bottom:4px}
.lista-news a{font-weight:600;font-size:18px;text-decoration:none;color:var(--inchiostro);line-height:1.3}
.lista-news a:hover{color:var(--aria-scura)}
.lista-news p{margin:6px 0 0;font-size:15px;color:var(--testo);max-width:var(--misura)}
.lista-news.compatta li{padding:10px 0}
.lista-news.compatta a{font-size:16.5px;font-weight:500}
.ultime{padding:8px 24px 16px}
.ultime h2{margin-top:0}
.news-item h2{font-size:19px;margin-top:28px}

/* temi e illustrazione */
.t-radon{--tema:#C98A00;--tema-ch:#FBF3E0}
.t-muffa{--tema:#5E7A3A;--tema-ch:#EEF3E6}
.t-aria{--tema:#2E7FB8;--tema-ch:#E6F1F9}
.t-ventilazione{--tema:#7A5CB8;--tema-ch:#EFEAF8}
.t-acqua{--tema:#1C8C8C;--tema-ch:#E3F3F3}
body.tema-radon{--tema:#C98A00;--tema-ch:#FBF3E0}
body.tema-muffa{--tema:#5E7A3A;--tema-ch:#EEF3E6}
body.tema-aria{--tema:#2E7FB8;--tema-ch:#E6F1F9}
body.tema-ventilazione{--tema:#7A5CB8;--tema-ch:#EFEAF8}
body.tema-acqua{--tema:#1C8C8C;--tema-ch:#E3F3F3}
.nav a.on{box-shadow:inset 0 -3px 0 var(--tema,var(--aria))}
.nav a[class*="t-"]:hover{box-shadow:inset 0 -3px 0 var(--tema);background:var(--tema-ch)}
.hero{background:linear-gradient(180deg,#FFFFFF 0%,#F4EEE3 100%);border-bottom:1px solid var(--nebbia);padding:36px 0 0;overflow:hidden}
.hero-casa svg{margin-bottom:-6px}
.hero-in{display:grid;grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr);gap:40px;align-items:center}
.hero h1{max-width:16ch}
.hero-p{font-size:17.5px;margin:16px 0 20px}
.hero-temi{display:flex;flex-wrap:wrap;gap:8px;margin:0}
.hero-temi a{display:inline-block;padding:7px 14px;border-radius:999px;background:var(--tema-ch);color:var(--tema);font-weight:600;font-size:15px;text-decoration:none;border:1px solid transparent}
.hero-temi a:hover{border-color:var(--tema)}
.hero-casa{margin:0}
.casa{width:100%;height:auto;display:block}
.radon-apre{padding:36px 24px 8px}
.radon-apre h2{margin-top:0;max-width:30ch;font-family:"Fraunces",Georgia,serif;font-weight:500;font-size:26px}
.lista-temi a{border-top:5px solid var(--tema)}
.lista-temi a:hover{background:var(--tema-ch);border-color:var(--tema)}
.lista-temi em{color:var(--tema)}
.verifica::before{background:var(--tema,var(--aria))}
.chiave{border-top-color:var(--tema,var(--ambra))}
.chiave-u{color:var(--tema,var(--aria-scura))}
.breve{background:var(--tema-ch,var(--nebbia-chiara))}
.sezione-testa{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:32px;align-items:center;margin-bottom:12px}
.sezione-casa{margin:0}
.casa[class*="focus-"] g[class^="l-"]{opacity:.18}
.casa.focus-radon .l-radon,.casa.focus-muffa .l-muffa,.casa.focus-aria .l-aria,.casa.focus-ventilazione .l-ventilazione,.casa.focus-acqua .l-acqua{opacity:1}
.sezione .lead{border-left:4px solid var(--tema,var(--aria));padding-left:14px}

/* piè di pagina */
.foot{background:var(--bianco);border-top:1px solid var(--nebbia);padding:28px 0 36px;margin-top:20px;color:var(--grigio);font-size:14.5px}
.foot p{max-width:80ch}

@media (max-width:860px){
  .pagina-guida{grid-template-columns:1fr;gap:28px}
  .lato{position:static;order:-1}
  .indice{display:none}
  .hero{padding:36px 0 28px}
  .brand-name{font-size:23px}
  .brand-pay{font-size:12px}
  .lista-guide{grid-template-columns:1fr}
  .lista-temi{grid-template-columns:1fr}
  .hero-in{grid-template-columns:1fr}
  .hero-casa{max-width:420px}
  .sezione-testa{grid-template-columns:1fr}
  .sezione-casa{max-width:320px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#16222E"/><path d="M6 21a10 10 0 0 1 20 0" fill="none" stroke="#2E7FB8" stroke-width="3" stroke-linecap="round"/><rect x="9" y="23" width="14" height="3" rx="1.5" fill="#C98A00"/></svg>"""


def write(base, rel, content):
    full = os.path.join(base, rel.lstrip("/"))
    os.makedirs(os.path.dirname(full) or base, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def build():
    global HEAD_COMMON
    cssv = hashlib.md5(CSS.encode()).hexdigest()[:8]
    HEAD_COMMON = HEAD_COMMON.replace("{CSSV}", cssv)
    for d in (OUT, OUT_BOZZE):
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(OUT)
    write(OUT, f"/assets/site-{cssv}.css", CSS)
    write(OUT, "/assets/favicon.svg", FAVICON)

    live = [p for p in PAGES if p["status"] == "live"]
    radon = [p for p in live if p["section"] == "radon"]

    for p in PAGES:
        base = OUT if p["status"] == "live" else OUT_BOZZE
        rel = p["path"].replace("/bozze", "") if p["status"] != "live" else p["path"]
        write(base, rel + "index.html", render_page(p))
    if os.path.isdir(OUT_BOZZE):
        shutil.copytree(os.path.join(OUT, "assets"), os.path.join(OUT_BOZZE, "assets"), dirs_exist_ok=True)

    write(OUT, "/index.html", render_home(radon))
    write(OUT, "/news/index.html", render_news_index())
    for n in NEWS:
        write(OUT, f"/news/{n[0]}/index.html", render_news_item(n))
    for path, nome, lead, prev in SEZIONI:
        write(OUT, path + "index.html", render_sezione(path, nome, lead, prev, radon))

    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=1))
    news_items = "".join(f"""<item>
<title>{esc(n[3])}</title>
<link>{SITE}/news/{n[0]}/</link>
<guid isPermaLink="true">{SITE}/news/{n[0]}/</guid>
<pubDate>{format_datetime(datetime.fromisoformat(n[1]).replace(hour=9, tzinfo=tz))}</pubDate>
<description>{esc(n[4])}</description>
</item>""" for n in NEWS)
    items = news_items + "".join(f"""<item>
<title>{esc(p['title'])}</title>
<link>{SITE}{p['path']}</link>
<guid isPermaLink="true">{SITE}{p['path']}</guid>
<pubDate>{p['pubdate']}</pubDate>
<description>{esc(p['desc'])}</description>
</item>""" for p in radon)
    write(OUT, "/feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Casa Respira</title>
<link>{SITE}/</link>
<description>Guida indipendente su aria e acqua dentro casa. Il radon è il tema di partenza.</description>
<language>it</language>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
{items}
</channel>
</rss>
""")
    urls = [SITE + "/", SITE + "/news/"] + [SITE + f"/news/{n[0]}/" for n in NEWS] + [SITE + sz[0] for sz in SEZIONI] + [SITE + p["path"] for p in live]
    write(OUT, "/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write(OUT, "/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("live:", len(live), "| bozze:", len(PAGES) - len(live))


if __name__ == "__main__":
    build()
