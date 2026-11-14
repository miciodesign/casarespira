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
OUT = str(pathlib.Path(__file__).resolve().parent.parent)
OUT_BOZZE = str(pathlib.Path(__file__).resolve().parent / "bozze")
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
        "Radon alto: come si risana una casa e quanto costa",
        "Radon in Piemonte, Veneto, Lazio e nelle altre regioni"]),
    ("/muffa/", "Muffa e umidità", "Da dove viene la muffa, perché torna, e cosa funziona davvero tra deumidificatori, pitture e interventi.", [
        "I migliori deumidificatori per la casa (confronto)"]),
    ("/aria/", "Aria che respiri", "CO₂, polveri sottili, composti volatili e monossido: cosa misurare, con quali strumenti, e quando serve un purificatore.", [
        "I migliori rilevatori di qualità dell'aria (CO₂, polveri)",
        "Purificatori d'aria: servono davvero? Confronto",
        "Monossido di carbonio in casa: rilevatori e caldaie"]),
    ("/ventilazione/", "Ventilazione", "Aprire le finestre bene, e quando conviene una ventilazione meccanica con recupero di calore.", [
        "Ventilazione meccanica controllata (VMC): come funziona e quanto costa"]),
    ("/acqua/", "Acqua di casa", "L'acqua del rubinetto è buona? Calcare, cloro, piombo nei tubi vecchi, pozzi privati, filtri e depuratori.", [
        "Calcare nell'acqua: durezza, danni e soluzioni",
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
    "minsal_muffe": ("Ministero della Salute, opuscolo Umidità e muffe (2015, PDF, copia su ingenio-web.it)",
                     "https://www.ingenio-web.it/files/umidita-e-muffe-opuscolo-ministero-della-salute.pdf"),
    "oms_dampness": ("OMS Europa, WHO guidelines for indoor air quality: dampness and mould (2009, PDF)",
                     "http://www.euro.who.int/__data/assets/pdf_file/0017/43325/E92645.pdf"),
    "iss_co2_nota": ("ISS, nota tecnica sul monitoraggio della CO₂ negli ambienti indoor (PDF)",
                     "https://www.iss.it/documents/20126/6703853/NT_co2_DEF.pdf/"),
    "istisan_16_15": ("ISS, Rapporto ISTISAN 16/15, Presenza di CO₂ e H₂S in ambienti indoor (PDF)",
                      "https://www.iss.it/documents/20126/45616/16_15_web.pdf/a9142047-b81d-3e0b-6e6f-10860f855b67?t=1581095582421"),
    "epicentro_co": ("ISS, EpiCentro, Monossido di carbonio: informazioni generali",
                     "https://www.epicentro.iss.it/ambiente/monossido-carbonio"),
    "iss_co_poster": ("ISS, Gruppo di Studio Nazionale Inquinamento Indoor, poster Stop al CO (PDF)",
                      "https://www.epicentro.iss.it/ambiente/pdf/Monossido%20Carbonio_%20Poster_A3_V2.pdf"),
    "iss_covid_11": ("ISS, Rapporto ISS COVID-19 n. 11/2021, Indicazioni per la prevenzione e gestione degli ambienti indoor (18 aprile 2021)",
                     "https://www.iss.it/rapporti-covid-19/-/asset_publisher/btw1J82wtYzH/content/id/5750232"),
    "enea_faq_vmc": ("ENEA, FAQ Ecobonus, sezione D impianti termici (FAQ 16D sulla ventilazione meccanica controllata)",
                     "https://www.efficienzaenergetica.enea.it/detrazioni-fiscali/ecobonus/faq-ecobonus/d-impianti-termici-comma-347.html"),
    "dlgs_18_2023": ("Normattiva, D.Lgs. 23 febbraio 2023, n. 18, qualità delle acque destinate al consumo umano (testo vigente)",
                     "https://www.normattiva.it/eli/stato/DECRETO_LEGISLATIVO/2023/02/23/18/CONSOLIDATED"),
    "dlgs_102_2025": ("Normattiva, D.Lgs. 19 giugno 2025, n. 102, correttivo del D.Lgs. 18/2023",
                      "https://www.normattiva.it/eli/id/2025/07/04/25G00106/CONSOLIDATED/"),
    "ispra_sintai": ("ISPRA, SINTAI, acque destinate al consumo umano: quadro del D.Lgs. 18/2023",
                     "https://www.sintai.isprambiente.it/umano/index_dett.html"),
    "aulss9_pfas": ("AULSS 9 Scaligera (Regione Veneto), Inquinamento PFAS: storia, parere ISS 2013, area rossa",
                    "https://sian.aulss9.veneto.it/Inquinamento-PFAS"),
    "aulss8_pfas": ("AULSS 8 Berica (Regione Veneto), PFAS, sostanze perfluoroalchiliche: cosa sono e misure adottate",
                    "https://www.aulss8.veneto.it/pfas-sostanze-perfluroalchiliche"),
    "veneto_pfas_report": ("Regione Veneto, PFAS, monitoraggio della contaminazione nell'acqua destinata al consumo umano (report, PDF)",
                           "https://salute.regione.veneto.it/contents/2025-12/2022_08_report_rete.pdf?VersionId=9J_AfoBDcs54ujaUcrCkcAZUGzWQKS5H"),
    "dlgs_102_pdf": ("D.Lgs. 19 giugno 2025, n. 102, testo pubblicato in Gazzetta Ufficiale (PDF, copia su unionalimentari.com)",
                     "https://www.unionalimentari.com/wp-content/uploads/2025/07/DLGS-102.2025-qualita-acque-destinate-consumo-umano.pdf"),
    "greenpeace_rinvio": ("Greenpeace Italia, L'Italia rinvia i limiti più severi per i PFAS nell'acqua potabile (legge di bilancio 2026, commi 622-623)",
                          "https://www.greenpeace.org/italy/storia/30124/italia-rinvia-limiti-piu-severi-per-pfas-acqua-potabile/"),
    "fattoalimentare_filtri": ("Il Fatto Alimentare, I filtri domestici riducono i PFAS? Lo studio di Duke University e NC State (Environmental Science & Technology Letters)",
                               "https://ilfattoalimentare.it/filtri-acqua-pfas.html"),
    "savonanews_pfas": ("Savonanews, PFAS nell'acqua a Borgio Verezzi e Pietra Ligure: gli interventi di Servizi Ambientali (6 novembre 2026)",
                        "https://www.savonanews.it/2026/11/06/leggi-notizia/argomenti/attualit/articolo/pfas-nellacqua-servizi-ambientali-accelera-sugli-interventi-necessario-il-sostegno-economico-di.html"),
    "ispra_best_practice": ("ISPRA, Quaderno Ambiente e Società, Buone pratiche per la riduzione del radon negli edifici (PDF)",
                            "https://www.isprambiente.gov.it/files2024/pubblicazioni/quaderni/best-practice-riduzione-radon_quaderno-ispra_18_12_rev1.pdf"),
    "lomb_lg_2025": ("Regione Lombardia, DGR XII/5469 del 9 dicembre 2025, Linee guida per la prevenzione delle esposizioni al gas radon (PDF)",
                     "https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/01-sanita/05-prevenzione-e-stili-di-vita/01-sicurezza-negli-ambienti-di-vita/red-campagna-gas-radon/DGR%205469_2025_linee_guida_radon_all.pdf"),
    "lomb_ddg_2011": ("Regione Lombardia, DDG 12678 del 21 dicembre 2011, Linee guida radon, capitolo 3 Tecniche di prevenzione e mitigazione (PDF)",
                      "https://www.radon.it/site/download/ddg_lombardia_12678_21-12-2011.pdf"),
    "ediltecnico_2025": ("Ediltecnico, Gas radon: cosa cambia per le nuove costruzioni dal 1° gennaio 2025",
                         "https://ediltecnico.it/gas-radon-cosa-cambia-nuove-costruzioni-dal-1-gennaio-2025/"),
    "inail_radon": ("INAIL, Prevenzione e protezione dall'esposizione al radon nei luoghi di lavoro secondo la normativa vigente (PDF, copia su lavoripubblici.it)",
                    "https://lavoripubblici.it/documenti2024/lvpb2/inail-rischio-radon-luoghi-lavoro.pdf"),
    "airthings_ch2": ("Airthings, Corentium Home 2, pagina prodotto con prezzo EU (letta l'11 novembre 2026)",
                      "https://www.airthings.com/en/products/corentium-home-2"),
    "amazon_ch1": ("Amazon.it, Corentium Home by Airthings (prezzo letto l'11 novembre 2026)",
                   "https://www.amazon.it/Airthings-Corentium-Radon-Rivelatore-digitale/dp/B0G7MJ9VF8"),
    "radonmarket_fido": ("RadonMarket (Niton Srl), Radon test kit FIDOtrack, rivelatori passivi CR-39 (prezzi letti l'11 novembre 2026)",
                         "https://www.radonmarket.com/it/misurazione-radon-rivelatori-passivi-fidotrack/"),
    "radonmarket_eye": ("RadonMarket (Niton Srl), RadonEye Bluetooth, versione internazionale (prezzo letto l'11 novembre 2026)",
                        "https://www.radonmarket.com/it/product/radoneye-bluetooth-rilevatore-gas-radon-versione-internazionale-in-bq-m3-guida-rapida-e-manuale-operativo-in-italiano/"),
    "radonshop_eye": ("Radonshop.com (Germania), RadonEye RD200 (prezzo letto l'11 novembre 2026)",
                      "https://www.radonshop.com/ftlab-radoneye-rd200-radon-gas-detector-r222-testing"),
    "radonoff": ("Radonoff, Dosimetro passivo CR-39 (prezzo letto l'11 novembre 2026)",
                 "https://www.radonoff.com/prodotto/dosimetro-passivo-cr-39/"),
    "fem2": ("FEM2 Ambiente, Dosimetro passivo CR-39 (prezzo letto l'11 novembre 2026)",
             "https://acqua.fem2ambiente.com/prodotto/dosimetro-passivo-cr-39/"),
    "altroconsumo_filtri_2026": ("Altroconsumo, Impianti per filtrare l'acqua di casa: funzionano davvero? Inchiesta su 12 impianti installati (25 febbraio 2026)",
                                 "https://www.altroconsumo.it/alimentazione/acqua/news/indagine-filtri-acqua"),
    "altroconsumo_bonus": ("Altroconsumo, Bonus acqua e depuratore gratis: attenzione alle offerte poco trasparenti",
                           "https://www.altroconsumo.it/alimentazione/acqua/news/bonus-acqua-spot-ingannevole"),
    "altroconsumo_caraffe_2026": ("Altroconsumo, Qual è la miglior caraffa filtrante (30 ottobre 2026)",
                                  "https://www.altroconsumo.it/alimentazione/acqua/news/miglior-caraffa-filtrante"),
    "amazon_brita": ("Amazon.it, BRITA Marella 2,4 l con 1 cartuccia Maxtra Pro (prezzo letto l'11 novembre 2026)",
                     "https://www.amazon.it/BRITA-Caraffa-filtrante-MARELLA-cartuccia/dp/B0D8PB9P92"),
    "amazon_laica": ("Trovaprezzi, Caraffa filtrante Laica Stream Line, offerte Amazon.it (prezzi letti l'11 novembre 2026)",
                     "https://www.trovaprezzi.it/prezzo_depuratori-trattamento-acqua_caraffa_filtrante_laica_stream_line.aspx"),
    "waterdrop_t3": ("Waterdrop EU, sistemi a osmosi inversa sotto lavello, prezzi T3-M e X12 (letti l'11 novembre 2026)",
                     "https://www.waterdropfilter.eu/it-it/collections/systems-osmosi-inversa"),
    "waterdrop_ro": ("Waterdrop EU, Sistema ad osmosi inversa serie X, X12, costi annui dichiarati dei filtri",
                     "https://www.waterdropfilter.eu/it/products/sistema-osmosi-inversa-x12"),
    "kaufland_g3p600": ("Kaufland.it, Waterdrop G3P600 sistema a osmosi inversa NSF/ANSI 58 (prezzo letto l'11 novembre 2026)",
                        "https://www.kaufland.it/product/477545297/"),
    "trovaprezzi_philips": ("Trovaprezzi, Philips AUT2015 sotto lavello, offerta ForHome (prezzo letto l'11 novembre 2026)",
                            "https://www.trovaprezzi.it/prezzo_depuratori-trattamento-acqua_philips_osmosi_inversa.aspx"),
    "airthings": ("Airthings, programma di affiliazione",
                  "https://airthings.com/affiliate-program"),
}


def fonti(*k):
    return [S[x] for x in k]


PAGES = []


def add(path, title, desc, body, sources=(), status="live", section=None,
        breve=None, chiave=None, scala=False, lang="it", data=None):
    PAGES.append(dict(path=path, title=title, desc=desc, body=body,
                      sources=list(sources), status=status, section=section,
                      breve=breve or [], chiave=chiave, scala=scala,
                      pubdate=PUB_RFC822, lang=lang, data=data))


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
<p><strong>Affiliazioni.</strong> Alcuni link portano a prodotti venduti da altri. Se compri tramite quei link o con un nostro codice, riceviamo una commissione. Per te il prezzo non cambia o, dove c'è un codice sconto, scende.</p>
<p>Oggi il programma attivo è quello di Airthings, per i rilevatori di radon e di aria: il codice <strong>CASARESPIRA-10OFF</strong> dà il 10% di sconto su discount.airthings.com e a noi una commissione. Dal novembre 2026 è attivo anche il programma di Waterdrop, per i sistemi a osmosi inversa, nella guida ai filtri per l'acqua. Altri programmi, per deumidificatori, purificatori e filtri, sono in verifica e non hanno ancora link attivi. Le pagine che contengono link affiliati lo dichiarano in testa.</p>
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
<aside class="aff"><p class="aff-t">Codice sconto Airthings, con affiliazione</p><p>Per i rilevatori di radon e di qualità dell'aria Airthings, il codice <strong>CASARESPIRA-10OFF</strong> su <a href="https://discount.airthings.com/" rel="nofollow sponsored noopener">discount.airthings.com</a> dà il 10% di sconto. Casa Respira riceve una commissione sugli acquisti fatti con il codice. Il codice non cambia il nostro giudizio sui prodotti: nel <a href="/radon/rilevatori/">confronto tra rilevatori di radon</a>, con prezzi verificati, per la maggior parte delle case consigliamo un kit da laboratorio su cui non guadagniamo nulla.</p></aside>
<h2>Dove andare dopo</h2>
<ul>
<li><a href="/radon/come-si-misura/">Come si misura il radon in casa</a></li>
<li><a href="/radon/normativa/">Radon: cosa dice la legge per abitazioni e luoghi di lavoro</a></li>
<li><a href="/radon/lombardia/">Radon in Lombardia: aree prioritarie e misure</a></li>
<li><a href="/radon/vespaio-aerato/">Vespaio aerato: com'è fatto e perché protegge da radon e umidità</a></li>
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
<aside class="aff"><p class="aff-t">Codice sconto Airthings, con affiliazione</p><p>Per i rilevatori di radon e di qualità dell'aria Airthings, il codice <strong>CASARESPIRA-10OFF</strong> su <a href="https://discount.airthings.com/" rel="nofollow sponsored noopener">discount.airthings.com</a> dà il 10% di sconto. Casa Respira riceve una commissione sugli acquisti fatti con il codice. Il codice non cambia il nostro giudizio sui prodotti: nel <a href="/radon/rilevatori/">confronto tra rilevatori di radon</a>, con prezzi verificati, per la maggior parte delle case consigliamo un kit da laboratorio su cui non guadagniamo nulla.</p></aside>
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

VESPAIO_SVG = """<figure class="schema"><svg viewBox="0 0 760 360" role="img" aria-label="Sezione di un vespaio aerato con numeri: 1 terreno, 2 casseri a cupola, 3 soletta, 4 membrana, 5 pavimento, 6 bocchette su lati opposti" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, system-ui, sans-serif">
<rect width="760" height="360" fill="#fff"/>
<rect x="0" y="250" width="760" height="110" fill="#E9DFC9"/>
<g fill="#C9B894"><circle cx="60" cy="290" r="2.5"/><circle cx="150" cy="330" r="2.5"/><circle cx="330" cy="310" r="2.5"/><circle cx="520" cy="335" r="2.5"/><circle cx="700" cy="300" r="2.5"/><circle cx="430" cy="280" r="2.5"/></g>
<rect x="100" y="40" width="36" height="210" fill="#F3EEE3" stroke="#16222E" stroke-width="2"/>
<rect x="624" y="40" width="36" height="210" fill="#F3EEE3" stroke="#16222E" stroke-width="2"/>
<rect x="78" y="250" width="80" height="32" fill="#D9D4C8" stroke="#16222E" stroke-width="2"/>
<rect x="602" y="250" width="80" height="32" fill="#D9D4C8" stroke="#16222E" stroke-width="2"/>
<rect x="136" y="232" width="488" height="18" fill="#D9D4C8" stroke="#16222E" stroke-width="1.5"/>
<path d="M136 232 h6 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h7 a27 40 0 0 1 54 0 h6 v-14 h-488 z" fill="#EEF2F5" stroke="#16222E" stroke-width="2"/>
<rect x="136" y="174" width="488" height="16" fill="#CFD6DC" stroke="#16222E" stroke-width="2"/>
<path d="M136 172 H624 M136 172 V128 M624 172 V128" stroke="#C98A00" stroke-width="5" fill="none"/>
<rect x="136" y="150" width="488" height="20" fill="#F3EEE3" stroke="#16222E" stroke-width="1.5"/>
<rect x="136" y="142" width="488" height="8" fill="#16222E"/>
<rect x="100" y="212" width="36" height="16" fill="#fff" stroke="#16222E" stroke-width="2"/>
<rect x="624" y="192" width="36" height="16" fill="#fff" stroke="#16222E" stroke-width="2"/>
<g stroke="#2E7FB8" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M40 220 H92"/><path d="M84 213 l9 7 -9 7"/>
<path d="M250 214 c25 -9 50 9 75 0 s50 9 75 0 s50 9 75 0"/><path d="M468 207 l9 7 -9 7"/>
<path d="M668 200 H720"/><path d="M712 193 l9 7 -9 7"/>
</g>
<g stroke="#C98A00" stroke-width="2.5" fill="none" stroke-dasharray="3 5"><path d="M260 282 v-44"/><path d="M380 282 v-44"/><path d="M500 282 v-44"/></g>
<g font-size="13" fill="#2E7FB8" font-weight="600"><text x="40" y="206">aria entra</text><text x="668" y="232">aria esce</text></g>
<g font-size="12" fill="#5F6E7B"><text x="40" y="242">lato freddo, in basso</text><text x="668" y="247">lato caldo, in alto</text></g>
<g font-size="12" fill="#8A5F00"><text x="380" y="322" text-anchor="middle">umidità e radon salgono dal terreno</text></g>
<g font-family="Fraunces, Georgia, serif" font-size="15" font-weight="600">
<g><circle cx="380" cy="300" r="12" fill="#16222E"/><text x="380" y="305" text-anchor="middle" fill="#fff">1</text></g>
<g><circle cx="380" cy="214" r="12" fill="#16222E"/><text x="380" y="219" text-anchor="middle" fill="#fff">2</text></g>
<g><circle cx="744" cy="182" r="12" fill="#16222E"/><text x="744" y="187" text-anchor="middle" fill="#fff">3</text></g>
<g><circle cx="744" cy="150" r="12" fill="#C98A00"/><text x="744" y="155" text-anchor="middle" fill="#fff">4</text></g>
<g><circle cx="744" cy="118" r="12" fill="#16222E"/><text x="744" y="123" text-anchor="middle" fill="#fff">5</text></g>
<g><circle cx="118" cy="190" r="12" fill="#2E7FB8"/><text x="118" y="195" text-anchor="middle" fill="#fff">6</text></g>
</g>
<g stroke="#16222E" stroke-width="1.2" fill="none"><path d="M732 182 H660"/><path d="M732 150 H690 V172 H626"/><path d="M732 118 H676 V160 H626"/></g>
</svg><figcaption><strong>1</strong> terreno e magrone · <strong>2</strong> casseri a cupola (igloo): la camera d'aria continua · <strong>3</strong> soletta in calcestruzzo armato · <strong>4</strong> membrana antiradon, risvoltata sui muri · <strong>5</strong> massetto e pavimento · <strong>6</strong> bocchette su lati opposti, a quote diverse. L'aria entra dal lato freddo, attraversa la camera ed esce dal lato caldo portando con sé umidità e radon.</figcaption></figure>"""

add("/radon/vespaio-aerato/", "Vespaio aerato: cos'è, come è fatto e perché protegge da radon e umidità",
    "Com'è fatto un vespaio aerato (igloo, soletta, bocchette, membrana), come funziona la ventilazione, cosa dicono ISPRA e le linee guida regionali sul radon, e quando non basta.",
    """
<p>Chi costruisce o ristruttura un piano terra si sente dire che "ci vuole il vespaio aerato". È la soluzione che le linee guida sul radon raccomandano per le nuove costruzioni, ed è anche la difesa classica contro l'umidità di risalita. Questa guida spiega com'è fatto, come funziona e quando da solo non basta.</p>
<h2>Cos'è un vespaio</h2>
<p>Il vespaio è un'intercapedine tra il terreno e il pavimento del piano terra: una camera d'aria che stacca fisicamente la casa dal suolo. Si chiama "aerato" o "ventilato" quando quella camera è collegata all'esterno da aperture, così che l'aria la attraversi. Senza aperture è solo un vuoto chiuso, che fa poco contro l'umidità e nulla contro il radon.</p>
<p>Il vespaio tradizionale era fatto di pietrame o ghiaia, oppure di muretti e tavelloni. Oggi si realizza quasi sempre con <strong>casseri a perdere</strong>: cupole in plastica riciclata, note con i nomi commerciali di igloo, cupolex o granchio, che si agganciano tra loro, reggono il getto di calcestruzzo e lasciano sotto un reticolo continuo di canali d'aria.</p>
""" + VESPAIO_SVG + """
<h2>Com'è fatto, strato per strato</h2>
<ol>
<li><strong>Terreno e magrone.</strong> Il fondo dello scavo viene livellato con un getto magro di calcestruzzo, su cui appoggiano i casseri.</li>
<li><strong>Casseri a cupola.</strong> Le cupole creano la camera d'aria. Le altezze in commercio vanno da pochi centimetri a oltre un metro; nei vespai alti possono passare anche i tubi degli impianti.</li>
<li><strong>Soletta in calcestruzzo armato.</strong> Gettata sopra le cupole, con una rete elettrosaldata; il calcestruzzo scende tra le gambe dei casseri e forma i pilastrini che reggono la soletta.</li>
<li><strong>Membrana.</strong> Sopra la soletta, una guaina impermeabile, meglio se specifica antiradon, risvoltata sui muri perimetrali e sigillata intorno ai passaggi dei tubi. Secondo il Quaderno ISPRA sulle buone pratiche, una membrana che copre tutta la superficie è la protezione migliore contro il radon, e va posata tra la parte alta del vespaio e il massetto.</li>
<li><strong>Massetto e pavimento.</strong></li>
<li><strong>Bocchette di aerazione.</strong> Tubi che attraversano i muri perimetrali e collegano la camera d'aria all'esterno, protetti da griglie contro insetti e roditori.</li>
</ol>
<h2>Come funziona la ventilazione</h2>
<p>Il principio è l'effetto camino. Le bocchette vanno messe su lati opposti della casa e a quote diverse: più basse sul lato freddo (nord), più alte sul lato caldo (sud). L'aria entra dal lato freddo, si scalda attraversando la camera, si carica di umidità e di radon che salgono dal terreno, ed esce dal lato caldo. Nelle linee guida lombarde il vespaio con casseri è "fortemente raccomandato" per le nuove costruzioni, a condizione che la camera d'aria sia collegata con l'esterno.</p>
<p>Per questo la ventilazione non si improvvisa. Le bocchette devono essere distribuite lungo il perimetro, con una sezione complessiva proporzionata alla superficie del vespaio: i regolamenti edilizi e di igiene comunali fissano i minimi, e vanno verificati in fase di progetto. Due errori frequenti: bocchette tutte sullo stesso lato (l'aria non circola) e bocchette tappate dopo la costruzione, per esempio da un marciapiede, un'aiuola o un intonaco.</p>
<h2>Cosa fa contro il radon</h2>
<p>Il radon entra in casa dal terreno attraverso fessure, giunti e passaggi degli impianti nel solaio a terra, spinto dalla differenza di pressione tra il suolo e l'interno riscaldato. Un vespaio ventilato interrompe questo percorso in due modi: diluisce il gas nella camera d'aria e lo porta fuori prima che raggiunga il pavimento, e con la membrana sopra la soletta chiude la via di ingresso. ISPRA lo riassume così: da una parte impermeabilizzare l'edificio al radon, dall'altra favorire la ventilazione del suolo.</p>
<p>Le linee guida di Regione Lombardia (aggiornate a dicembre 2025) aggiungono una terza cosa per le nuove costruzioni: la <strong>predisposizione passiva</strong>. Si lascia un pozzetto o una tubazione di captazione nel vespaio o nel ghiaione sotto la platea, collegati a un tubo di sfiato che arriva sopra il tetto. Se a casa finita la misura del radon è alta, basta installare un ventilatore nel pozzetto per aspirare il gas dal sottosuolo, senza rompere i pavimenti. Costa poco in cantiere, molto dopo.</p>
<p>La ragione pratica: dal 1° gennaio 2025 per le case nuove il livello di riferimento è 200 Bq/m³, più basso dei 300 delle case esistenti (<a href="/radon/normativa/">cosa dice la legge</a>). Prevenire in fase di costruzione è l'unico modo economico per starci sotto con margine.</p>
<h2>Cosa fa contro l'umidità</h2>
<p>L'umidità di risalita arriva dal terreno per capillarità attraverso i materiali porosi. La camera d'aria la interrompe: il pavimento non tocca più il suolo umido, e l'aria che circola porta via il vapore. Vale per il pavimento; i muri perimetrali, che scendono fino alle fondazioni, restano a contatto con il terreno e hanno bisogno di una barriera propria (taglio orizzontale, guaina alla base del muro). Un vespaio perfetto con muri senza barriera dà pavimenti asciutti e pareti con la macchia a un metro da terra. Per riconoscere questo tipo di umidità: <a href="/muffa/muffa-in-casa/">Muffa in casa: da dove viene</a>.</p>
<h2>Quando il vespaio non basta</h2>
<ul>
<li><strong>Radon molto alto nel terreno.</strong> La ventilazione naturale dipende da vento e temperatura e nelle notti d'inverno senza vento può rallentare. Nelle aree prioritarie le linee guida prevedono la ventilazione meccanica del vespaio o la depressurizzazione del suolo con ventilatore.</li>
<li><strong>Vespaio interrato.</strong> Se il piano terra è sotto il livello del terreno, le bocchette non possono stare sui muri: servono condotti che risalgono all'esterno, e spesso un ventilatore.</li>
<li><strong>Membrana forata o non sigillata.</strong> Ogni tubo che attraversa il solaio è una via d'ingresso se intorno non è sigillato. La posa conta quanto il materiale.</li>
<li><strong>Edifici esistenti.</strong> Un vespaio non si aggiunge sotto una casa costruita. Chi ha radon alto in una casa esistente interviene con la depressurizzazione del suolo, di cui parliamo nella <a href="/radon/guida-completa/">guida completa</a>; il risanamento avrà una guida dedicata.</li>
</ul>
<h2>Cosa chiedere al progettista</h2>
<ul>
<li>Altezza e tipo di casseri, e come sarà ventilata la camera: posizione, quota e sezione delle bocchette, e il regolamento comunale a cui rispondono.</li>
<li>Se la membrana è antiradon, come viene risvoltata sui muri e sigillata ai passaggi impiantistici.</li>
<li>Se è prevista la predisposizione passiva (pozzetto e tubo di sfiato sopra il tetto), soprattutto in area prioritaria.</li>
<li>Una misura del radon a casa finita, nel primo inverno: è l'unico modo per sapere se ha funzionato (<a href="/radon/come-si-misura/">come si misura</a>).</li>
</ul>
<p class="nota">Questa guida descrive la tecnica, non sostituisce un progetto. Dimensioni, altezze e sezioni di ventilazione dipendono dal terreno, dal clima e dal regolamento del Comune. I costi del vespaio saranno trattati quando verificati.</p>
""", sources=fonti("ispra_best_practice", "lomb_lg_2025", "lomb_ddg_2011", "ediltecnico_2025"),
    section="radon",
    breve=["Il vespaio aerato è una camera d'aria tra terreno e pavimento, collegata all'esterno: stacca la casa dal suolo umido e porta fuori il radon prima che entri.",
           "Oggi si fa con casseri a cupola (igloo), soletta armata, membrana antiradon e bocchette su lati opposti a quote diverse.",
           "ISPRA e le linee guida regionali lo raccomandano per le nuove case, insieme a un pozzetto predisposto per un eventuale ventilatore."],
    chiave=("200", "Bq/m³", "livello di riferimento per le case costruite dal 2025: il vespaio serve a starci sotto"))

# ------------------------------------------------------------- guide per tema
add("/muffa/muffa-in-casa/", "Muffa in casa: da dove viene e come eliminarla davvero",
    "Condensa, infiltrazioni o risalita: come riconoscere la causa della muffa, cosa dice il Ministero della Salute e cosa funziona oltre alla candeggina.",
    """
<p>La muffa sui muri è il segno che una superficie è rimasta umida abbastanza a lungo. Pulirla serve, ma se non si toglie l'umidità torna sempre nello stesso punto. Questa guida spiega come capire da dove viene l'acqua e cosa fare in ordine di efficacia.</p>
<h2>Cos'è la muffa e perché cresce in casa</h2>
<p>Le muffe sono funghi microscopici. Secondo l'opuscolo del Ministero della Salute dedicato a umidità e muffe, in casa si trovano soprattutto dove c'è umidità in eccesso e poca ventilazione, e crescono più in fretta con temperature miti. Hanno bisogno di tre cose: acqua, una superficie su cui attaccarsi e tempo. Di queste, l'unica su cui si può agire davvero è l'acqua.</p>
<h2>Le tre cause, e come distinguerle</h2>
<ul>
<li><strong>Condensa su superfici fredde.</strong> È la causa più comune. L'aria calda di casa contiene vapore (respiro, cucina, doccia, bucato steso); quando tocca una parete fredda il vapore diventa acqua. Con 20 °C e umidità relativa del 60%, una superficie a circa 12 °C è già bagnata. Succede negli angoli alti delle pareti esterne, dietro gli armadi addossati ai muri perimetrali, intorno alle finestre: i punti in cui l'isolamento è più debole, detti ponti termici. La muffa compare d'inverno e sempre nello stesso posto.</li>
<li><strong>Infiltrazioni.</strong> Acqua che entra da fuori: tetto, terrazzo, davanzali, tubi che perdono. La macchia segue la pioggia o l'uso di un bagno al piano di sopra, e spesso è umida al tatto anche in estate.</li>
<li><strong>Risalita dal terreno.</strong> Riguarda piani terra e seminterrati, soprattutto in edifici vecchi. La macchia parte dal pavimento e sale con un fronte orizzontale, spesso con efflorescenze bianche di sali.</li>
</ul>
<p>Un igrometro da pochi euro aiuta a capire quale caso è il tuo: se l'umidità relativa in stanza sta spesso sopra il 60%, la condensa è la spiegazione più probabile. Il Ministero della Salute indica di mantenere l'umidità interna sotto il 50%.</p>
<h2>Cosa consiglia il Ministero della Salute</h2>
<p>L'opuscolo ministeriale elenca comportamenti concreti. I principali:</p>
<ul>
<li>mantenere l'umidità interna sotto il 50%;</li>
<li>isolare e ventilare muri esterni, fondazioni, sottotetti;</li>
<li>non lasciare i panni ad asciugare a lungo in ambienti chiusi e poco ventilati;</li>
<li>non usare tappeti o moquette in bagno, cucina e lavanderia;</li>
<li>eliminare la condensa arieggiando spesso;</li>
<li>togliere le macchie con prodotti antimuffa a base d'acqua;</li>
<li>fare manutenzione a umidificatori, condizionatori e ventilazione meccanica, in particolare bocchette esterne e filtri.</li>
</ul>
<h2>Cosa fare, in ordine di efficacia</h2>
<ol>
<li><strong>Ridurre il vapore prodotto.</strong> Coperchio sulle pentole, cappa accesa, finestra del bagno aperta dopo la doccia, bucato steso fuori o in una stanza ventilata con la porta chiusa.</li>
<li><strong>Arieggiare bene.</strong> Pochi minuti, più volte al giorno, con finestre su lati opposti aperte insieme. Come e quando, in <a href="/ventilazione/aprire-le-finestre/">Aprire le finestre bene</a>.</li>
<li><strong>Riscaldare in modo uniforme.</strong> Una stanza tenuta fredda e chiusa, in una casa riscaldata, è quella dove condensa il vapore delle altre. Scostare i mobili dalle pareti esterne di qualche centimetro lascia circolare l'aria.</li>
<li><strong>Deumidificatore</strong>, come tampone quando le prime tre misure non bastano o nei periodi più umidi. Riduce l'umidità dell'aria, non ripara un ponte termico. Il confronto tra modelli è in preparazione.</li>
<li><strong>Intervenire sull'involucro.</strong> Se la muffa torna sempre nello stesso angolo, il problema è una superficie troppo fredda: isolamento del ponte termico, cappotto, sostituzione degli infissi. Per infiltrazioni e risalita serve prima eliminare l'ingresso dell'acqua; nessuna pittura lo fa.</li>
</ol>
<h2>Pulire la muffa senza sbagliare</h2>
<p>Su piccole superfici si pulisce con un prodotto antimuffa, con guanti e finestra aperta, senza spazzolare a secco (le spore si disperdono nell'aria). I prodotti vanno usati uno alla volta: mescolare candeggina e ammoniaca, o candeggina e detergenti acidi, libera gas irritanti. Le pitture antimuffa rallentano la ricomparsa, ma su una parete che resta fredda e umida la muffa torna.</p>
<h2>Quando chiamare un tecnico</h2>
<p>Se la muffa copre superfici estese, torna dopo ogni pulizia, o si accompagna a intonaco che si sfalda, serve una diagnosi: una termocamera mostra i ponti termici, un igrometro a contatto misura l'umidità nel muro. In affitto, la muffa da difetti dell'edificio va segnalata per iscritto al proprietario.</p>
<h2>Muffa e salute</h2>
<p>Le linee guida dell'OMS del 2009 su umidità e muffe negli edifici concludono che vivere in ambienti umidi o con muffa si associa a più sintomi respiratori e asma. Il Ministero della Salute riprende la stessa indicazione. Questa guida si ferma qui: per sintomi, allergie o dubbi sulla salute, il riferimento è il medico o l'ASL.</p>
<p class="nota">Questa guida non sostituisce il parere di un tecnico o del medico. Prezzi di deumidificatori e interventi saranno trattati in guide dedicate, dopo la verifica.</p>
""", sources=fonti("minsal_muffe", "oms_dampness"),
    section="muffa",
    breve=["La muffa cresce dove una superficie resta umida: condensa su pareti fredde, infiltrazioni o risalita dal terreno.",
           "Il Ministero della Salute indica di tenere l'umidità interna sotto il 50% e di arieggiare spesso.",
           "Pulire serve, ma se non si toglie la causa la muffa torna nello stesso punto."],
    chiave=("50%", "umidità relativa", "il valore sotto cui il Ministero della Salute consiglia di tenere l'aria di casa per prevenire le muffe"))

add("/aria/qualita-aria-casa/", "La qualità dell'aria in casa: cosa misurare e come",
    "CO₂, umidità, polveri sottili, composti volatili e monossido di carbonio: quali parametri contano in casa, con quali strumenti si misurano e quali numeri usare come riferimento.",
    """
<p>L'aria di casa non si vede, ma si misura. Non tutto però va misurato, e non tutti gli strumenti misurano bene. Questa guida dice quali parametri contano davvero in un'abitazione, quali valori prendere come riferimento e come leggere i numeri senza farsi ingannare.</p>
<h2>Cinque parametri che contano in casa</h2>
<h3>Anidride carbonica (CO₂)</h3>
<p>La CO₂ in sé non è un inquinante pericoloso ai livelli di casa, ma è il miglior indicatore del ricambio d'aria: la producono le persone, e sale quando si sta in tanti in una stanza chiusa. L'Istituto Superiore di Sanità, nel Rapporto ISTISAN 16/15 e nella nota tecnica dedicata, prende come riferimento 1.000 ppm: valori stabilmente sopra questa soglia durante l'occupazione indicano che il ricambio d'aria è insufficiente e va migliorato. All'aperto si sta intorno a 400-500 ppm. L'ISS ricorda anche che la legge italiana non fissa valori limite per l'aria delle abitazioni: 1.000 ppm è un riferimento gestionale, non un limite sanitario.</p>
<h3>Umidità relativa</h3>
<p>Troppo alta favorisce muffe e acari, troppo bassa secca le vie respiratorie. Il Ministero della Salute consiglia di tenerla sotto il 50% per prevenire le muffe; il dettaglio è nella guida <a href="/muffa/muffa-in-casa/">Muffa in casa</a>.</p>
<h3>Polveri sottili (PM10 e PM2,5)</h3>
<p>Entrano dall'esterno con il traffico e il riscaldamento, ma in casa le produce soprattutto cucinare, in particolare friggere e grigliare, accendere candele, incensi, camini e stufe a legna, e fumare. Per le abitazioni non esistono limiti di legge italiani. Il modo più efficace per abbassarle è alla fonte: cappa aspirante verso l'esterno e ricambio d'aria dopo aver cucinato.</p>
<h3>Composti organici volatili (COV) e formaldeide</h3>
<p>Li rilasciano mobili nuovi, vernici, colle, detergenti e profumatori. L'odore di "nuovo" è un indizio. Si riducono scegliendo prodotti a bassa emissione, lasciando arieggiare per giorni ciò che si è appena comprato e non accumulando spray e profumatori.</p>
<h3>Monossido di carbonio (CO)</h3>
<p>È l'unico parametro di questa lista che riguarda la sicurezza immediata. Secondo l'ISS, il CO è un gas inodore e incolore prodotto dalla combustione: caldaie, stufe, camini, fornelli, scaldabagni a gas. Le cause principali degli avvelenamenti sono la mancata manutenzione di apparecchi e canne fumarie, una combustione con poco ossigeno e la cattiva evacuazione dei fumi. La prevenzione è la manutenzione periodica fatta da personale abilitato e l'ingresso d'aria libero nei locali con apparecchi a fiamma. Un rilevatore di CO è un'aggiunta utile, non un sostituto della manutenzione. Una guida dedicata è in preparazione.</p>
<p>Il sesto parametro, il <a href="/radon/">radon</a>, ha una sezione tutta sua: è regolato per legge e si misura in modo diverso.</p>
<h2>Con cosa si misura</h2>
<ul>
<li><strong>CO₂</strong>: serve un sensore a infrarossi (sigla NDIR nelle schede tecniche). I sensori "eCO₂" stimano la CO₂ dai COV e non sono affidabili per questo scopo.</li>
<li><strong>Umidità e temperatura</strong>: un igrometro digitale da pochi euro basta; vale la pena metterlo nella stanza più fredda.</li>
<li><strong>Polveri sottili</strong>: i monitor domestici usano un sensore ottico. Sono utili per vedere i picchi (quando si cucina, quando si accende una candela) e la tendenza, meno per il valore assoluto.</li>
<li><strong>COV</strong>: i sensori domestici danno un indice relativo, non una concentrazione. Vanno letti come "più o meno di prima", non come un numero da confrontare con una soglia.</li>
<li><strong>CO</strong>: un rilevatore con allarme acustico, conforme alla norma EN 50291, nel locale della caldaia o della stufa, con batterie controllate. Non è un monitor di qualità dell'aria: è un allarme.</li>
</ul>
<p>Il confronto tra rilevatori di qualità dell'aria, con prezzi verificati, è in preparazione.</p>
<aside class="aff"><p class="aff-t">Codice sconto Airthings, con affiliazione</p><p>Per i rilevatori di radon e di qualità dell'aria Airthings, il codice <strong>CASARESPIRA-10OFF</strong> su <a href="https://discount.airthings.com/" rel="nofollow sponsored noopener">discount.airthings.com</a> dà il 10% di sconto. Casa Respira riceve una commissione sugli acquisti fatti con il codice. Il codice non cambia il nostro giudizio sui prodotti: nel <a href="/radon/rilevatori/">confronto tra rilevatori di radon</a>, con prezzi verificati, per la maggior parte delle case consigliamo un kit da laboratorio su cui non guadagniamo nulla.</p></aside>
<h2>Come leggere i numeri</h2>
<ul>
<li>Guarda l'andamento, non il singolo valore. Una stanza da letto che la mattina segna 2.000 ppm di CO₂ dice che la notte l'aria non si è ricambiata.</li>
<li>Collega i picchi alle attività: cucina, doccia, bucato, pulizie, un mobile nuovo.</li>
<li>Un numero alto non è una diagnosi. Se ti preoccupa la salute, il riferimento è il medico; per la casa, un tecnico.</li>
</ul>
<h2>Cosa fare se i valori sono alti</h2>
<p>Nell'ordine: togliere la fonte (cappa, meno candele, prodotti a bassa emissione), ricambiare l'aria (guida <a href="/ventilazione/aprire-le-finestre/">Aprire le finestre bene</a>), e solo dopo pensare a un apparecchio. Un purificatore con filtro HEPA abbassa le polveri sottili nella stanza in cui sta, ma non toglie CO₂ né monossido: per quelli serve aria esterna. Una guida sui purificatori è in preparazione.</p>
<p class="nota">Questa guida non sostituisce il parere di un tecnico o del medico. Per sintomi o dubbi sulla salute, rivolgiti al medico o all'ASL. In caso di sospetto avvelenamento da monossido di carbonio, l'ISS indica di rivolgersi subito al pronto soccorso.</p>
""", sources=fonti("iss_co2_nota", "istisan_16_15", "epicentro_co", "iss_co_poster", "minsal_muffe"),
    section="aria",
    breve=["La CO₂ è l'indicatore del ricambio d'aria: l'ISS prende come riferimento 1.000 ppm.",
           "Polveri sottili e COV si abbassano soprattutto alla fonte: cucina, candele, mobili nuovi, spray.",
           "Il monossido di carbonio è una questione di sicurezza: manutenzione degli apparecchi a fiamma, poi un rilevatore con allarme."],
    chiave=("1.000", "ppm di CO₂", "il riferimento ISS: valori stabilmente più alti indicano un ricambio d'aria insufficiente"))

add("/ventilazione/aprire-le-finestre/", "Aprire le finestre bene: quanto, quando, in inverno",
    "Quanto tenere aperto, a che ora, come fare in inverno senza buttare via calore, e quando ha senso una ventilazione meccanica con recupero di calore.",
    """
<p>Arieggiare è la misura più economica per l'aria di casa, e quella che si fa peggio: finestre a ribalta per ore d'inverno, o chiuse per settimane per non disperdere calore. Questa guida riassume cosa indica l'Istituto Superiore di Sanità e come applicarlo in una casa normale.</p>
<h2>Perché serve ricambiare l'aria</h2>
<p>In una stanza chiusa si accumulano CO₂, umidità, odori, composti volatili dei materiali e, al piano terra, radon. L'ISS, nei documenti del suo gruppo di lavoro sulla qualità dell'aria indoor, ricorda che molte persone trascurano i ricambi d'aria perché considerano prevalente il comfort termico o il risparmio energetico. Il risultato è aria "già respirata" che gira nella casa senza scambio con l'esterno. Il segnale più semplice è la CO₂: sopra i 1.000 ppm l'ISS considera il ricambio insufficiente (guida <a href="/aria/qualita-aria-casa/">La qualità dell'aria in casa</a>).</p>
<h2>Come arieggiare: le indicazioni ISS</h2>
<p>Il Rapporto ISS COVID-19 n. 11/2021, scritto per il contagio ma valido per l'aria di casa in generale, dà indicazioni pratiche:</p>
<ul>
<li><strong>pochi minuti, più volte al giorno</strong>, con una ventilazione intermittente e incrociata (finestre su lati opposti aperte insieme), piuttosto che una sola apertura lunga;</li>
<li>in inverno, quando la differenza di temperatura tra dentro e fuori è grande, bastano pochi minuti per lo stesso ricambio che d'estate richiede tempi più lunghi;</li>
<li>preferire le finestre che danno sulle strade meno trafficate ed evitare le ore di punta del traffico;</li>
<li>evitare correnti d'aria e disagio da freddo o caldo durante l'apertura.</li>
</ul>
<h2>Tradotto in una giornata</h2>
<ul>
<li><strong>Appena svegli</strong>: camera da letto spalancata, insieme a una finestra sul lato opposto della casa. È la stanza con più CO₂ e umidità della casa.</li>
<li><strong>Dopo doccia, cucina e bucato</strong>: la finestra della stanza interessata, con la porta chiusa, finché lo specchio o i vetri non sono asciutti.</li>
<li><strong>Prima di dormire</strong>: un ricambio breve in camera.</li>
<li><strong>Quando si è in tanti</strong>: ospiti a cena, riunione in casa: un'apertura ogni ora o due.</li>
</ul>
<h2>In inverno senza sprecare calore</h2>
<p>Il calore di una casa sta soprattutto nei muri, nei pavimenti e nei mobili, non nell'aria. Un'apertura completa di pochi minuti cambia l'aria ma raffredda poco le superfici, che riscaldano la nuova aria in fretta. Una finestra a ribalta lasciata aperta per ore fa il contrario: raffredda il muro intorno alla finestra, dove poi condensa il vapore, e ricambia l'aria lentamente. Durante l'apertura conviene chiudere i termosifoni della stanza, se hanno valvola termostatica, e riaprirli dopo.</p>
<h2>Quando conviene la ventilazione meccanica</h2>
<p>La ventilazione meccanica controllata (VMC) ricambia l'aria in modo continuo e, nei modelli a doppio flusso, recupera il calore dell'aria espulsa per preriscaldare quella in entrata. Ha senso quando arieggiare a mano non basta: case molto isolate dopo una ristrutturazione, stanze con muffa ricorrente, zone rumorose o inquinate dove aprire le finestre è un problema, persone con allergie che vogliono filtrare l'aria in ingresso. L'ENEA, nella FAQ 16D sull'Ecobonus, ammette alle detrazioni per la riqualificazione energetica i soli sistemi di VMC dotati di recupero di calore, quando sono realizzati insieme alla coibentazione dell'involucro o integrati in un impianto di climatizzazione ad aria, con una relazione tecnica che dimostri il risparmio energetico. Le aliquote e le condizioni cambiano con le leggi di bilancio: vanno verificate sul sito dell'Agenzia delle Entrate per l'anno in cui si paga la spesa. Costi di acquisto e installazione saranno trattati in una guida dedicata, dopo la verifica.</p>
<p>Anche con la VMC, i filtri vanno puliti o sostituiti con la frequenza indicata dal produttore: il Ministero della Salute lo elenca tra le misure contro le muffe.</p>
<h2>Due errori comuni</h2>
<ul>
<li><strong>Chiudere tutto per risparmiare.</strong> L'umidità che non esce condensa sulle pareti fredde, e la muffa che ne segue costa più del calore risparmiato.</li>
<li><strong>Affidarsi a un purificatore.</strong> Filtra le polveri, ma non toglie CO₂, umidità né radon: quelli escono solo con aria esterna.</li>
</ul>
<p class="nota">Questa guida non sostituisce il parere di un tecnico. Per impianti di VMC, un progettista termotecnico dimensiona il sistema sui metri cubi reali della casa.</p>
""", sources=fonti("iss_covid_11", "iss_co2_nota", "enea_faq_vmc", "minsal_muffe"),
    section="ventilazione",
    breve=["L'ISS consiglia aperture brevi, ripetute più volte al giorno, con finestre su lati opposti aperte insieme.",
           "In inverno bastano pochi minuti: il calore è nei muri e nei mobili, non nell'aria.",
           "La VMC con recupero di calore ha senso dove arieggiare a mano non basta; le detrazioni richiedono condizioni precise (ENEA, FAQ 16D)."],
    chiave=("2", "lati opposti", "finestre aperte insieme, pochi minuti più volte al giorno: la ventilazione incrociata indicata dall'ISS"))

add("/acqua/acqua-del-rubinetto/", "L'acqua del rubinetto è buona? Come saperlo",
    "Chi controlla l'acqua di rete, dove leggere i dati del tuo comune, cosa significano durezza, nitrati, cloro e piombo, e quando ha senso un'analisi privata.",
    """
<p>In Italia l'acqua del rubinetto è controllata per legge dalla sorgente al contatore. Se è "buona" dipende da due cose: i valori che il gestore pubblica per il tuo comune e lo stato dei tubi dentro casa, che sono responsabilità tua. Questa guida spiega dove guardare e cosa guardare.</p>
<h2>Chi controlla, e con quale legge</h2>
<p>La norma è il D.Lgs. 18/2023, che ha recepito la direttiva europea 2020/2184 ed è in vigore dal 21 marzo 2023; è stato corretto e integrato dal D.Lgs. 102/2025. Il decreto fissa i valori di parametro che l'acqua deve rispettare (Allegato I), prevede i controlli interni del gestore e i controlli esterni delle aziende sanitarie, e introduce la valutazione del rischio lungo tutta la filiera, dalla captazione al rubinetto.</p>
<p>Fino al punto di consegna, cioè il contatore, risponde il gestore. Dal contatore al rubinetto rispondono il proprietario e, nei condomini, l'amministratore: è il tratto dove contano i tubi vecchi.</p>
<h2>Dove leggere i valori del tuo comune</h2>
<p>L'articolo 18 del decreto obbliga a informare il pubblico sulla qualità dell'acqua. In pratica: il sito del gestore idrico (il nome è sulla bolletta) pubblica per ogni comune, spesso per ogni zona, i valori misurati. Molti gestori riportano anche una "etichetta dell'acqua" con i parametri principali. Se non trovi i dati, puoi chiederli al gestore per iscritto.</p>
<h2>Cosa guardare nei valori</h2>
<ul>
<li><strong>Nitrati</strong>: valore di parametro 50 mg/L. Vengono soprattutto dall'agricoltura; nelle reti pubbliche sono monitorati e di solito ben sotto il limite. Contano molto di più nei pozzi privati.</li>
<li><strong>Durezza</strong>: espressa in gradi francesi (°F), misura calcio e magnesio. Non è un parametro di salute: il D.Lgs. 18/2023 non le assegna un valore di parametro. Dice quanto calcare si deposita in lavatrice, bollitore e caldaia.</li>
<li><strong>Residuo fisso</strong>: i sali disciolti totali. Alto o basso è una questione di gusto e di uso, non di potabilità.</li>
<li><strong>Cloro residuo</strong>: il disinfettante che il gestore lascia nell'acqua perché resti sicura nei tubi. Il sapore di cloro non è un difetto di qualità: sparisce lasciando l'acqua in una caraffa aperta in frigorifero per un po'.</li>
<li><strong>pH</strong>: tra 6,5 e 9,5.</li>
<li><strong>Piombo</strong>: valore di parametro 10 µg/L, che il decreto abbassa a 5 µg/L dal 12 gennaio 2036. Riguarda gli edifici con tubazioni o raccordi in piombo, in genere costruiti fino ai primi anni Ottanta, soprattutto dopo lunghe ore di acqua ferma nei tubi. Una guida dedicata è in preparazione.</li>
<li><strong>PFAS</strong>: i composti "eterni" di origine industriale, con limiti di legge dal 2026 (somma di PFAS 0,10 µg/L). Cosa sono, dove si trovano in Italia e cosa fanno i filtri: <a href="/acqua/pfas/">guida ai PFAS nell'acqua</a>.</li>
<li><strong>Parametri microbiologici</strong> (Escherichia coli, enterococchi): devono essere assenti. Un superamento fa scattare provvedimenti del gestore e dell'ASL, con avviso ai cittadini.</li>
</ul>
<p>La regola generale: un valore entro il parametro dell'Allegato I significa acqua conforme per quel parametro. Nessun singolo numero "buono" o "cattivo" fuori da questo confronto.</p>
<h2>Quando ha senso un'analisi privata</h2>
<ul>
<li>L'acqua viene da un <strong>pozzo privato</strong>: nessun gestore la controlla, e chi la usa per bere ne è responsabile. Nitrati e batteri sono i primi parametri da verificare.</li>
<li>L'edificio è <strong>vecchio</strong> e i tubi non sono mai stati sostituiti: piombo e, in condomini con serbatoi, parametri microbiologici.</li>
<li>Cambiano <strong>colore, odore o sapore</strong> dell'acqua, o compaiono sedimenti, e il gestore non segnala nulla.</li>
</ul>
<p>Le analisi vanno fatte da un laboratorio accreditato (norma ISO/IEC 17025): il referto riporta il valore misurato accanto al valore di parametro di legge. Il campione per il piombo va prelevato dal rubinetto usato per bere, di prima mattina, senza far scorrere l'acqua. I costi delle analisi variano per numero di parametri; li pubblicheremo quando verificati.</p>
<h2>E i filtri?</h2>
<p>Per un'acqua di rete conforme, un filtro non serve alla potabilità: serve al gusto (cloro) o al calcare (durezza). Caraffe, filtri al rubinetto e depuratori sotto il lavello fanno cose diverse e hanno costi di gestione diversi: li mettiamo a confronto, con i prezzi, in <a href="/acqua/filtri-confronto/">Caraffa, filtro al rubinetto o depuratore</a>. Un apparecchio non mantenuto, con cartucce scadute, peggiora l'acqua invece di migliorarla.</p>
<p class="nota">Questa guida non sostituisce il parere di un tecnico né del medico. Per avvisi di non potabilità vale sempre la comunicazione del gestore e del Comune.</p>
""", sources=fonti("dlgs_18_2023", "dlgs_102_2025", "ispra_sintai"),
    section="acqua",
    breve=["L'acqua di rete è controllata dal gestore e dalle ASL secondo il D.Lgs. 18/2023; dal contatore in poi rispondono proprietario e condominio.",
           "I valori del tuo comune sono sul sito del gestore: nitrati 50 mg/L, piombo 10 µg/L (5 dal 2036), pH 6,5-9,5; durezza e cloro riguardano calcare e gusto.",
           "Un'analisi privata ha senso con pozzo, tubi vecchi o cambiamenti di odore e sapore; va fatta da un laboratorio accreditato."],
    chiave=("50", "mg/L", "valore di parametro dei nitrati nell'acqua potabile (D.Lgs. 18/2023, Allegato I)"))

add("/acqua/pfas/", "PFAS nell'acqua del rubinetto: cosa sono, dove si trovano e cosa dice la legge",
    "Cosa sono i PFAS, perché si chiamano inquinanti eterni, i limiti di legge in vigore dal 2026 in Italia, i casi del Veneto e della Liguria, come leggere i dati del tuo comune e cosa possono fare i filtri domestici.",
    """
<p>PFAS è una sigla che da qualche anno compare nei titoli sull'acqua potabile: prima per il Veneto, dall'autunno 2026 per la Liguria. Questa guida spiega cosa sono, perché preoccupano, cosa dice la legge italiana dal 2026 e cosa può fare, in concreto, chi apre il rubinetto.</p>
<h2>Cosa sono i PFAS</h2>
<p>PFAS sta per sostanze per- e polifluoroalchiliche. Sono composti chimici prodotti dall'uomo, non presenti in natura, fatti di catene di carbonio legate ad atomi di fluoro. Il legame carbonio-fluoro è tra i più stabili della chimica: per questo i PFAS resistono al calore, ai grassi e all'acqua, e per questo dagli anni Cinquanta sono stati usati in padelle antiaderenti, tessuti impermeabili, imballaggi per alimenti, schiume antincendio, cosmetici e processi industriali.</p>
<p>La stessa stabilità li rende un problema: non si degradano nell'ambiente, si spostano con l'acqua e si accumulano negli organismi. Da qui il soprannome di "inquinanti eterni". Le aziende sanitarie venete, che se ne occupano dal 2013, li descrivono così: notevole persistenza, notevole mobilità, capacità di bioaccumulo non trascurabile.</p>
<p>La famiglia è grande: migliaia di molecole. Le più studiate sono quattro, PFOA, PFOS, PFNA e PFHxS, dette "a catena lunga". Le più recenti, "a catena corta" come il TFA (acido trifluoroacetico), sono più difficili da trattenere con i filtri e sono state regolate solo ora.</p>
<h2>Come arrivano nell'acqua del rubinetto</h2>
<p>Dagli scarichi industriali e dalle schiume antincendio i PFAS finiscono nei fiumi e nelle falde. Gli acquedotti che attingono da quelle falde li portano ai rubinetti, a meno che l'acqua non venga trattata. Per chi vive in un'area contaminata, l'acqua potabile è la principale via di esposizione, come ricordano le aziende sanitarie del Veneto; gli alimenti prodotti localmente sono la seconda.</p>
<h2>Il caso del Veneto</h2>
<p>Nel 2013, durante un monitoraggio di contaminanti emergenti commissionato dal Ministero dell'Ambiente, i PFAS sono stati trovati in acque sotterranee, superficiali e potabili tra le province di Vicenza, Verona e Padova. La fonte è stata individuata in uno stabilimento chimico della zona. Allora non esistevano limiti di legge: la Regione chiese un parere all'Istituto Superiore di Sanità, che il 7 giugno 2013 escluse un rischio immediato ma consigliò, in via cautelativa, di trattare le acque potabili e di fissare "livelli di performance" provvisori. Sugli acquedotti sono stati installati filtri a carboni attivi; la Regione ha poi delimitato un'area di massima esposizione, la cosiddetta area rossa, di 30 comuni, e avviato dal 2016 un piano di sorveglianza sanitaria sulla popolazione, con il biomonitoraggio del sangue coordinato dall'ISS. Il monitoraggio dell'acqua di rete nell'area rossa è pubblicato dalla Regione.</p>
<h2>Il caso della Liguria, autunno 2026</h2>
<p>Nell'ottobre 2026 i PFAS sono stati trovati oltre i limiti nell'acqua di Borgio Verezzi e Pietra Ligure, in provincia di Savona. Il gestore ha dichiarato prioritaria l'installazione di filtri a carboni attivi per ripristinare la potabilità, la Regione Liguria ha istituito una cabina di regia e la Procura di Savona ha aperto un fascicolo. È uno dei primi casi gestiti con i nuovi limiti di legge in vigore: lo seguiamo nelle <a href="/news/">notizie</a>.</p>
<h2>Cosa dice la legge dal 2026</h2>
<p>Fino al 2023 in Italia non c'era un limite nazionale per i PFAS nell'acqua potabile. La direttiva europea 2020/2184, recepita con il <a href="/acqua/acqua-del-rubinetto/">D.Lgs. 18/2023</a> e completata dal D.Lgs. 102/2025, ha introdotto parametri specifici. Riassunti:</p>
<ul>
<li><strong>Somma di PFAS</strong>: 0,10 µg/L (cioè 100 nanogrammi per litro), calcolata su un elenco di 30 sostanze. Il controllo è obbligatorio dal 13 gennaio 2026.</li>
<li><strong>Somma di 4 PFAS</strong> (PFOA, PFOS, PFNA, PFHxS): 0,02 µg/L, cioè 20 nanogrammi per litro. È un limite italiano, più severo di quello europeo. Doveva applicarsi da gennaio 2026; la legge di bilancio 2026 (L. 199/2025, commi 622 e 623) lo ha rinviato di sei mesi, a luglio 2026. Fino alla stessa data sei molecole dette ADV, prodotte in uno stabilimento di Alessandria, non concorrono alla somma.</li>
<li><strong>TFA</strong> (acido trifluoroacetico): 10 µg/L, con controllo obbligatorio dal 13 gennaio 2027.</li>
</ul>
<p>Un chiarimento sulle unità: 0,10 µg/L sono 100 ng/L. I laboratori e i gestori usano spesso i nanogrammi, i decreti i microgrammi. Il numero è lo stesso.</p>
<p>Un valore sotto il parametro significa acqua conforme per quel parametro. Un superamento obbliga il gestore a intervenire (trattamento, cambio di fonte) e, se serve, a limitare l'uso dell'acqua con avviso ai cittadini.</p>
<h2>Come sapere se riguarda il tuo comune</h2>
<ul>
<li>Il sito del tuo gestore idrico pubblica i valori per comune. Dal 2026 tra i parametri deve comparire la "somma di PFAS"; dove è segnalato "&lt; LOQ" o "&lt; LQ" significa sotto il limite di quantificazione del laboratorio, cioè non rilevato.</li>
<li>Se il tuo gestore non pubblica ancora i PFAS, puoi chiederli per iscritto: l'articolo 18 del D.Lgs. 18/2023 prevede l'informazione al pubblico.</li>
<li>Chi beve acqua di pozzo privato non è coperto da nessun controllo: in zone con attività industriali, aeroporti o caserme dei vigili del fuoco (schiume antincendio) un'analisi dei PFAS in un laboratorio accreditato è la sola risposta. Serve un laboratorio con limite di quantificazione adeguato ai nuovi parametri.</li>
</ul>
<h2>Cosa possono fare i filtri domestici</h2>
<p>Uno studio della Duke University e della North Carolina State University, pubblicato su Environmental Science &amp; Technology Letters, ha misurato i PFAS prima e dopo 89 filtri domestici. I sistemi a osmosi inversa e quelli a doppio stadio li riducevano in media del 94%; i filtri a carboni attivi (caraffe, filtri da rubinetto, sotto lavello) del 73% in media, ma con una variabilità enorme: alcuni non toglievano nulla, e una cartuccia esaurita può rilasciare quello che ha trattenuto.</p>
<p>In pratica:</p>
<ul>
<li>Se l'acqua di rete è conforme, un filtro per i PFAS non è necessario: il gestore ha già l'obbligo di rispettare il parametro al contatore.</li>
<li>Se vivi in un'area con superamenti o hai un pozzo con PFAS, l'osmosi inversa è la tecnologia con i risultati più costanti; i carboni attivi funzionano solo con cartucce certificate per i PFAS e cambiate nei tempi indicati.</li>
<li>Nessun filtro domestico è stato ancora provato in modo affidabile sul TFA, la molecola a catena corta più diffusa.</li>
<li>L'osmosi inversa toglie anche i sali minerali e scarta una parte dell'acqua: va scelta sapendolo. Il confronto tra caraffe, filtri al rubinetto e depuratori, con prezzi verificati, è in <a href="/acqua/filtri-confronto/">Caraffa, filtro al rubinetto o depuratore</a>.</li>
</ul>
<h2>Cosa non trovi in questa pagina</h2>
<p>Non diamo valutazioni sugli effetti dei PFAS sulla salute delle singole persone né consigli su esami del sangue: sono temi del medico, dell'ASL e, nelle aree interessate, dei piani di sorveglianza regionali. Riportiamo i limiti di legge e come controllare l'acqua della propria casa.</p>
<p class="nota">Le date e i valori di questa pagina vengono dal D.Lgs. 102/2025 e dalla legge di bilancio 2026 come riportati dalle fonti in fondo; le tabelle dell'Allegato I del decreto sono pubblicate in Gazzetta Ufficiale in formato grafico. Se trovi una differenza, scrivici: la correzione viene dichiarata qui sotto.</p>
""", sources=fonti("aulss9_pfas", "aulss8_pfas", "veneto_pfas_report", "dlgs_18_2023", "dlgs_102_pdf", "greenpeace_rinvio", "fattoalimentare_filtri", "savonanews_pfas"),
    section="acqua",
    breve=["I PFAS sono composti industriali che non si degradano: persistenti, mobili nell'acqua, accumulabili negli organismi.",
           "Dal 13 gennaio 2026 la somma di PFAS nell'acqua potabile ha un limite di 0,10 µg/L; il limite italiano di 0,02 µg/L sui 4 PFAS più studiati è stato rinviato a luglio 2026.",
           "I valori del tuo comune sono sul sito del gestore. I filtri a osmosi inversa li riducono in modo costante, i carboni attivi solo a volte."],
    chiave=("0,10", "µg/L", "valore di parametro per la somma di PFAS nell'acqua potabile, obbligatorio dal 13 gennaio 2026"))

# ------------------------------------------------------------- English section
add("/en/", "Indoor air and water in Italy: guides in English",
    "Casa Respira in English: radon, water quality and indoor-air rules in Italy, for foreign home buyers, tenants and property investors.",
    """
<p>Casa Respira is an independent Italian guide to the air and water inside homes. Most of it is written in Italian, for Italian readers. These pages are the exception: short, sourced guides in English for people who buy, rent or invest in property in Italy and need to understand the Italian rules.</p>
<ul class="lista-guide">
<li><a href="/en/radon-in-italy/"><strong>Radon in Italy: what foreign home buyers and tenants should know</strong><span>Legal reference levels, priority areas, why the seller is not required to test, and how to get a measurement before you sign.</span></a></li>
<li><a href="/en/property-due-diligence/"><strong>Air and water due diligence for property in Italy</strong><span>For investors and funds: mandatory radon testing in workplaces, drinking-water rules in buildings, mould and ground-floor construction.</span></a></li>
</ul>
<h2>How these pages are written</h2>
<p>Same method as the Italian site: every figure comes from an institutional source (Italian law, the National Institute of Health, regional environmental agencies) with a link and a date; no prices unless verified; corrections are declared on the page. We do not give medical advice. Where a topic has a full Italian guide, we link to it.</p>
<p>The Italian site starts at <a href="/">casarespira.it</a>.</p>
""", section="en", lang="en")

add("/en/radon-in-italy/", "Radon in Italy: what foreign home buyers and tenants should know",
    "Italian radon reference levels (300 and 200 Bq/m³), priority areas by region, why sellers are not required to test, and how to get a proper measurement before buying or renting.",
    """
<p>Radon is a naturally occurring radioactive gas that rises from the ground and collects in basements and ground floors. Italy's estimated national average is around 70 Bq/m³, with wide regional variation (100-120 in Lombardy, according to a 2025 ATS Brescia presentation); it has a specific law, and no obligation for a seller or landlord to test. If you are buying a farmhouse in Piedmont, a flat in Milan or a villa on a lake, this is what you need to know.</p>
<h2>The legal reference levels</h2>
<p>Italian Legislative Decree 101/2020, which implements the Euratom directive 2013/59, sets reference levels for the annual average radon concentration in air (article 12):</p>
<ul>
<li><strong>300 Bq/m³</strong> for existing homes and for workplaces;</li>
<li><strong>200 Bq/m³</strong> for homes built under permits issued after 31 December 2024.</li>
</ul>
<p>The World Health Organization recommends 100 Bq/m³. A reference level is not a safety threshold: above it, the law expects remediation; below it, lower is still better.</p>
<h2>Priority areas</h2>
<p>Article 11 of the decree asks each region to identify "priority areas": municipalities where more than 15% of buildings are estimated to exceed 300 Bq/m³. The National Radon Action Plan 2023-2032 (approved in January 2024) set the method. Lombardy was first, with 90 municipalities; by early 2026 several regions had published their lists (Lombardy, Liguria, Aosta Valley, the autonomous provinces of Bolzano and Trento, among others), for a total of several hundred municipalities. Lists are updated: check the region's or the regional environmental agency's (ARPA) website for the municipality you are looking at. Our Italian page on <a href="/radon/lombardia/">Lombardy</a> explains how the areas were chosen.</p>
<p>Being outside a priority area does not mean low radon. ARPA Lombardy says it plainly: high concentrations are found outside the mapped municipalities too. Only a measurement tells you.</p>
<h2>Why the seller will not tell you</h2>
<p>Italian law does not require a private seller or landlord to measure radon or to disclose a measurement. The energy performance certificate (APE) that every sale and lease must include says nothing about radon. Radon clauses in preliminary contracts are rare. So the burden is on you, and the time to act is before the deed (rogito), not after.</p>
<h2>How to get a measurement</h2>
<ul>
<li><strong>What counts is the annual average.</strong> A reading taken in one afternoon with a consumer device is not a legal measurement. The reference method is a passive detector left in place for months and analysed by a laboratory.</li>
<li><strong>Who does it.</strong> A recognised dosimetry service or an ARPA-type laboratory. Ask for a report that states the measurement period, the room, the floor and the method (the technical standard is UNI ISO 11665-8).</li>
<li><strong>Timing for a purchase.</strong> If you have months before the deed, place detectors now; a winter measurement of at least three months is far more informative than nothing. If you have weeks, an electronic monitor gives you a trend and a first warning, and you can write a radon condition into the preliminary contract, with a price adjustment or a right to withdraw above an agreed level.</li>
<li><strong>Where to measure.</strong> The lowest lived-in floor, with the house used normally, windows closed as in daily life.</li>
</ul>
<p>Our Italian guide <a href="/radon/come-si-misura/">Come si misura il radon</a> has the details; the <a href="/radon/guida-completa/">full guide</a> covers remediation.</p>
<h2>If the result is high</h2>
<p>Radon can be reduced. The most common technique in houses on a concrete slab is soil depressurisation: a sump under or beside the building with a fan that draws the gas from the ground and vents it outside. Costs depend on the building; we publish them only when verified. For new builds, Italian regional guidelines recommend a ventilated crawl space (vespaio aerato) with a radon membrane and a passive sump that can take a fan later; see our page on the <a href="/radon/vespaio-aerato/">vespaio aerato</a> (in Italian).</p>
<h2>Questions to ask your notary, surveyor or agent</h2>
<ul>
<li>Is the municipality in a regional radon priority area?</li>
<li>Has the property ever been measured? Can I see the report?</li>
<li>Does the ground floor sit on a ventilated crawl space, a slab on grade, or a basement?</li>
<li>If the building was permitted after 31 December 2024: what radon-proofing was designed in?</li>
<li>Can we add a radon condition to the preliminary contract (compromesso)?</li>
</ul>
<p class="nota">This page describes the Italian rules as published; it is not legal, technical or medical advice. For a specific property, rely on a qualified surveyor (geometra or engineer) and, for health questions, on a doctor.</p>
""", sources=fonti("certifico_9941", "dpcm_2024", "arpa_lomb_rusconi", "ats_brescia_2025", "iss_epicentro", "iss_riduzione", "lomb_lg_2025"),
    section="en", lang="en",
    breve=["Italy sets 300 Bq/m³ (existing homes) and 200 Bq/m³ (homes permitted after 2024) as annual-average reference levels; the WHO recommends 100.",
           "Sellers and landlords are not required to test or disclose radon: test before the deed, with a laboratory measurement of several months.",
           "Priority areas are published by each region, but high radon is found outside them too."],
    chiave=("300", "Bq/m³", "reference level for existing homes in Italy, annual average (Legislative Decree 101/2020, art. 12)"))

add("/en/property-due-diligence/", "Air and water due diligence for property in Italy",
    "What investors, funds and asset managers should check in Italian buildings: mandatory radon testing in workplaces, drinking-water obligations under Decree 18/2023, mould, ventilation and ground-floor construction.",
    """
<p>Environmental due diligence on Italian property usually covers soil, asbestos and energy performance. Two items are often missed because the rules are recent: radon in workplaces, which became a legal obligation for employers with Legislative Decree 101/2020, and drinking water inside buildings, reorganised by Legislative Decree 18/2023. This page lists what to check and where the obligations sit.</p>
<h2>Radon: where testing is mandatory</h2>
<p>Article 16 of Decree 101/2020 applies the radon rules to these workplaces:</p>
<ul>
<li>underground workplaces (rooms with at least three walls fully below ground);</li>
<li>workplaces in semi-basements or on the ground floor located in a regional <strong>priority area</strong>;</li>
<li>specific activities listed by the National Radon Action Plan (for example water treatment plants with open tanks, mineral-water bottling, hydroelectric plants);</li>
<li>spas.</li>
</ul>
<p>Article 17 puts the obligation on the operator (esercente, in practice the employer or occupier): complete a measurement of the annual average concentration within 24 months of starting the activity, or, for ground-floor premises in a priority area, within 18 months of the area being published in the Official Gazette. The measurement must be done by a recognised dosimetry service and becomes part of the risk assessment document under the health-and-safety code. Above 300 Bq/m³ the operator must reduce the concentration within two years with a certified radon remediation expert, then re-measure. INAIL, the national accident insurance institute, has published a guide for employers.</p>
<p><strong>What this means for an acquisition.</strong> If the asset has ground-floor or basement space used as workplaces, in a priority area or in one of the listed activities, ask for the radon measurement reports and the risk assessment. Their absence is a compliance gap and a possible capital expense; a result above 300 Bq/m³ is a remediation obligation that transfers with the occupier. Priority-area lists are regional and still being completed: the regional environmental agency (ARPA) is the source.</p>
<h2>Drinking water inside buildings</h2>
<p>Decree 18/2023, implementing EU directive 2020/2184, moved from end-of-pipe compliance to risk management along the whole supply chain. The water utility is responsible up to the meter; from the meter to the tap, responsibility lies with the owner or the building manager. Two points matter for buildings:</p>
<ul>
<li><strong>Priority buildings</strong> (hospitals, care homes, hotels, schools, sports facilities, large public buildings and similar) must assess and manage the risk of their internal distribution systems, with specific attention to Legionella and lead.</li>
<li><strong>Lead.</strong> The parameter value is 10 µg/L today and drops to 5 µg/L on 12 January 2036. Buildings with lead pipes or fittings, typically built up to the early 1980s, will need pipe replacement to comply. Ask for the age and material of risers and a recent analysis at the tap.</li>
</ul>
<p>PFAS limits also apply at the tap from 2026 (sum of PFAS 0.10 µg/L); they concern the utility's water, but in areas with known contamination (parts of Veneto, and in 2026 a case in Liguria) they affect how a building is supplied. Our Italian guides on <a href="/acqua/acqua-del-rubinetto/">tap water</a> and <a href="/acqua/pfas/">PFAS</a> have the details.</p>
<h2>Mould, damp and ventilation</h2>
<p>Italy has no indoor air-quality limits for private buildings, but the National Institute of Health (ISS) uses 1,000 ppm of CO₂ as the threshold above which ventilation is insufficient, and the Ministry of Health recommends keeping indoor relative humidity below 50% to prevent mould. For a portfolio, the practical checks are: evidence of mould or rising damp on ground floors; whether the ground floor sits on a ventilated crawl space (vespaio aerato) or a slab in contact with the ground; and, in buildings renovated for energy efficiency, whether ventilation was addressed, because tighter envelopes without ventilation are the typical cause of new mould problems. Mechanical ventilation with heat recovery qualifies for energy tax deductions only under conditions set by ENEA.</p>
<h2>A checklist</h2>
<ol>
<li>Municipality in a regional radon priority area? (ARPA)</li>
<li>Any underground, semi-basement or ground-floor workplaces? Radon reports and risk assessment available?</li>
<li>Building type under Decree 18/2023: priority building? Water risk assessment done?</li>
<li>Age and material of water risers; last analysis at the tap (lead, Legionella where relevant).</li>
<li>Ground-floor construction: crawl space, slab, basement; radon membrane in new builds.</li>
<li>Visible mould or damp; ventilation strategy after any energy retrofit.</li>
</ol>
<p class="nota">This page summarises Italian rules as published and is not legal or technical advice. Obligations depend on the use, the location and the region; engage an Italian environmental consultant and a qualified radiation-protection or radon expert for a specific asset.</p>
""", sources=fonti("certifico_9941", "remetti", "inail_radon", "dlgs_18_2023", "dlgs_102_2025", "iss_co2_nota", "minsal_muffe", "enea_faq_vmc"),
    section="en", lang="en",
    breve=["Radon testing is mandatory in underground workplaces, in ground-floor and semi-basement workplaces inside regional priority areas, and in listed activities (Decree 101/2020, art. 16-17).",
           "Water inside buildings is the owner's responsibility from the meter; lead drops to 5 µg/L in 2036 and priority buildings must manage Legionella and lead risk (Decree 18/2023).",
           "Mould and ventilation: no legal limits in private buildings, but ISS and Ministry of Health benchmarks exist (1,000 ppm CO₂, 50% humidity)."],
    chiave=("24", "months", "deadline for the operator to complete a radon measurement in a workplace covered by the decree"))

add("/radon/rilevatori/", "I migliori rilevatori di radon per la casa: confronto 2026 con prezzi",
    "Dosimetri passivi da laboratorio o rilevatori elettronici: Airthings Corentium Home 2, Wave Radon, RadonEye RD200 e kit CR-39 a confronto, con prezzi verificati a novembre 2026 e quale scegliere a seconda dell'uso.",
    """
<p>Per sapere quanto radon c'è in casa ci sono due strade: un dosimetro passivo, che si lascia in una stanza per mesi e si spedisce a un laboratorio, oppure un rilevatore elettronico, che mostra i valori sul display o sull'app. Costano cifre diverse e rispondono a domande diverse. Questa guida le confronta, con i prezzi verificati alla data in fondo alla pagina.</p>
<h2>Prima la domanda, poi lo strumento</h2>
<ul>
<li><strong>"Voglio sapere se la mia casa è sopra o sotto i 300 Bq/m³."</strong> Serve una media annua, o almeno invernale: un dosimetro passivo con analisi di laboratorio, da 20 a 40 euro a stanza. È anche l'unico risultato che vale per la legge, per un contenzioso o per un acquisto.</li>
<li><strong>"Voglio vedere come cambia il radon e controllare se il risanamento funziona."</strong> Serve un rilevatore elettronico, da 130 a 230 euro: mostra la variazione giorno per giorno, per esempio quando si apre o si chiude la cantina, e resta in casa per anni.</li>
<li><strong>"Devo fare la misura per il mio negozio o ufficio."</strong> La legge chiede un servizio di dosimetria riconosciuto, con relazione tecnica: non un rilevatore comprato online. Vedi <a href="/radon/normativa/">cosa dice la legge</a>.</li>
</ul>
<p>Molte persone fanno bene a combinare le due cose: dosimetro per la misura ufficiale, rilevatore elettronico per capire e intervenire. Come si posizionano e per quanto tempo è spiegato in <a href="/radon/come-si-misura/">Come si misura il radon in casa</a>.</p>
<h2>Dosimetri passivi (CR-39): la misura di riferimento</h2>
<p>Un dischetto di plastica speciale in una piccola camera: le particelle alfa del radon lasciano tracce che il laboratorio conta al microscopio dopo l'esposizione. Nessuna batteria, nessun display, nessun errore di lettura. Si lascia in posizione da 2 a 6 mesi (meglio in inverno) e si rispedisce.</p>
<table class="tab">
<thead><tr><th>Prodotto</th><th>Cosa include</th><th>Prezzo verificato</th><th>Dove</th></tr></thead>
<tbody>
<tr><td>Kit FIDOtrack, 1 rivelatore CR-39</td><td>1 punto di misura, analisi di laboratorio e certificato inclusi; spedizione di ritorno a carico tuo</td><td>21,96 € (18,00 + IVA)</td><td>RadonMarket (Niton Srl)</td></tr>
<tr><td>Kit FIDOtrack, 3 rivelatori CR-39</td><td>3 punti di misura (per esempio taverna, soggiorno, camera), analisi inclusa; opzione secondo kit semestrale per la media annua</td><td>62,10 € (50,90 + IVA)</td><td>RadonMarket (Niton Srl)</td></tr>
<tr><td>Dosimetro passivo CR-39</td><td>1 rivelatore, analisi e certificato; spedizione di ritorno a carico tuo</td><td>35,00 €</td><td>Radonoff</td></tr>
<tr><td>Dosimetro passivo CR-39</td><td>1 rivelatore, analisi e certificato, busta per il laboratorio</td><td>39,90 €</td><td>FEM2 Ambiente</td></tr>
</tbody>
</table>
<p>I kit sono equivalenti nel principio: quello che cambia è il laboratorio che fa l'analisi. Prima di ordinare, cerca sul sito chi analizza i dosimetri e se è accreditato (ISO/IEC 17025): è quello che dà valore al certificato. Molte ARPA e alcuni Comuni distribuiscono dosimetri gratuiti nelle campagne di misura: controlla nelle <a href="/news/">notizie</a> e sul sito della tua Regione prima di comprare.</p>
<h2>Rilevatori elettronici: vedere il radon cambiare</h2>
<p>Una camera a ionizzazione o un sensore a stato solido conta i decadimenti in continuo; dopo 24 ore compaiono le prime medie, e dopo qualche settimana la lettura si stabilizza. Non sostituiscono il laboratorio per la media annua ufficiale, ma dicono subito se c'è un problema e dove.</p>
<table class="tab">
<thead><tr><th>Modello</th><th>Punti di forza</th><th>Limiti</th><th>Prezzo verificato</th></tr></thead>
<tbody>
<tr><td><strong>Airthings Corentium Home 2</strong></td><td>Display con medie 24 h, 7 giorni, 30 giorni e lungo periodo; Bluetooth e app; temperatura e umidità; 2 pile AA fino a 3 anni; garanzia 5 anni; sensore collaudato dal 2011</td><td>Nessun Wi-Fi: i dati si scaricano avvicinando il telefono; sensibilità più bassa del RadonEye, quindi serve più tempo per una lettura stabile</td><td>179,00 € sul sito Airthings (listino EU); con il codice CASARESPIRA-10OFF circa 161 €</td></tr>
<tr><td><strong>Airthings Corentium Home</strong> (prima generazione)</td><td>Stesso sensore, senza connettività: display e basta; pile AAA; molto diffuso, oltre 1.200 recensioni su Amazon.it</td><td>Nessuna app né storico esportabile; in esaurimento</td><td>129,92 € su Amazon.it (ne restano pochi, i prezzi oscillano)</td></tr>
<tr><td><strong>Airthings Wave Radon</strong></td><td>Senza display: si agita la mano davanti e un anello colorato dice verde, giallo o rosso; app con grafici; integrabile con hub Airthings</td><td>Per i numeri serve sempre il telefono; prezzo simile al Corentium Home 2 che ha anche il display</td><td>circa 195 € presso rivenditori europei (non disponibile sui negozi italiani che abbiamo controllato)</td></tr>
<tr><td><strong>Ecosense RadonEye RD200</strong></td><td>Camera a ionizzazione ad alta sensibilità: prima lettura in 10 minuti, risposta rapida alle variazioni; Bluetooth e app; certificato di calibrazione</td><td>Alimentato a rete (serve una presa vicino al punto di misura); design da laboratorio; manuale in italiano solo tramite il distributore</td><td>230,58 € (189,00 + IVA) da RadonMarket (Niton Srl); 189 € IVA inclusa da Radonshop (Germania), più spedizione</td></tr>
</tbody>
</table>
<h2>Il nostro consiglio</h2>
<ul>
<li><strong>Per la maggior parte delle case: un kit CR-39 da 3 rivelatori (62 €)</strong>, posato a novembre e rispedito a marzo. È la misura che conta e costa meno di un pieno di benzina.</li>
<li><strong>Se vivi in un'<a href="/radon/lombardia/">area prioritaria</a>, hai una taverna abitata o vuoi tenere il radon sotto controllo nel tempo: Corentium Home 2.</strong> Il display rende la lettura immediata per tutta la famiglia, le pile durano anni e la garanzia è di 5 anni. È il rilevatore che useremmo noi per una casa.</li>
<li><strong>Se devi verificare un risanamento o capire da dove entra il gas: RadonEye RD200.</strong> La risposta in minuti permette di fare prove (aprire una finestra, sigillare un passaggio) e vedere l'effetto in giornata. Per chi segue i lavori, vale la differenza.</li>
<li><strong>Da evitare:</strong> i "rilevatori di radon" sotto i 50 euro con sensore di gas generico, venduti sui marketplace. Non misurano il radon; misurano altro e lo chiamano radon.</li>
</ul>
<aside class="aff"><p class="aff-t">Codice sconto Airthings, con affiliazione</p><p>Sui prodotti Airthings il codice <strong>CASARESPIRA-10OFF</strong> su <a href="https://discount.airthings.com/" rel="nofollow sponsored noopener">discount.airthings.com</a> dà il 10% di sconto e a Casa Respira una commissione. Il consiglio qui sopra è lo stesso che daremmo senza il codice: lo dimostra il fatto che per la maggior parte delle case consigliamo un kit da 62 euro su cui non guadagniamo nulla.</p></aside>
<h2>Come abbiamo verificato i prezzi</h2>
<p>I prezzi sono quelli mostrati dai venditori indicati, IVA inclusa salvo dove specificato, letti il giorno indicato in fondo alla pagina. Non includono la spedizione. I prezzi Amazon cambiano spesso: quello riportato è un riferimento, non una promessa. Se trovi una differenza, scrivici e aggiorniamo.</p>
<p class="nota">Questa guida non sostituisce il parere di un esperto in interventi di risanamento radon né, per i luoghi di lavoro, un servizio di dosimetria riconosciuto.</p>
""", sources=fonti("airthings_ch2", "amazon_ch1", "radonmarket_fido", "radonmarket_eye", "radonshop_eye", "radonoff", "fem2", "iss_epicentro"),
    section="radon", data="11 novembre 2026",
    breve=["Per sapere se sei sopra i 300 Bq/m³ serve un dosimetro passivo da laboratorio: 22-40 € a stanza, esposto 2-6 mesi in inverno.",
           "Un rilevatore elettronico (130-230 €) mostra il radon cambiare e serve per controllare nel tempo e verificare i lavori.",
           "Il nostro consiglio: kit CR-39 da 3 rivelatori per quasi tutti; Airthings Corentium Home 2 per il controllo continuo; RadonEye per chi fa i lavori."])

add("/muffa/condensa-finestre/", "Condensa sulle finestre: perché si forma e cosa fare davvero",
    "Perché i vetri si bagnano d'inverno, cosa dice il punto di rugiada, quando è colpa delle finestre e quando dell'aria, e i rimedi in ordine di efficacia, dalle abitudini ai serramenti.",
    """
<p>Le gocce sui vetri la mattina sono il termometro dell'umidità di casa. Non sono un difetto della finestra, nella maggior parte dei casi, ma il segno che l'aria interna contiene più vapore di quanto le superfici fredde possano sopportare. Questa guida spiega il meccanismo, come capire la causa nel tuo caso e cosa fare, in ordine di efficacia.</p>
<h2>Perché si forma</h2>
<p>L'aria calda trattiene molto vapore, l'aria fredda poco. Quando l'aria della stanza tocca una superficie più fredda, si raffredda e il vapore in eccesso diventa acqua. La temperatura a cui succede si chiama punto di rugiada e dipende solo da temperatura e umidità dell'aria: con 20 °C e umidità relativa al 50% è circa 9 °C; al 65% sale a circa 13 °C. Un vetro singolo in una notte d'inverno sta ben sotto, e si bagna; un doppio vetro moderno resta intorno ai 15-17 °C sul lato interno, e si bagna solo se l'umidità è molto alta.</p>
<p>Per questo la condensa compare prima sui vetri: sono la superficie più fredda della stanza. Ma la stessa aria condensa anche, senza che si veda, sugli angoli delle pareti esterne e dietro i mobili: lì nasce la muffa. I vetri bagnati sono un avviso utile, non il problema.</p>
<h2>Tre casi diversi</h2>
<ul>
<li><strong>Condensa sul lato interno del vetro</strong>, la mattina, che sparisce arieggiando: aria troppo umida o vetro troppo freddo. È il caso di questa guida.</li>
<li><strong>Condensa tra i due vetri</strong> di un vetrocamera, che non si asciuga mai: la guarnizione del vetro è rotta e il gas isolante è uscito. Non c'entra l'aria di casa; va sostituito il vetro.</li>
<li><strong>Condensa sul lato esterno</strong>, in autunno all'alba: segno che il vetro isola bene (la faccia esterna resta fredda). Nessun problema.</li>
</ul>
<h2>Da dove viene il vapore</h2>
<p>Una famiglia produce in casa litri d'acqua al giorno sotto forma di vapore: respiro, docce, cucina, bucato steso dentro, piante, acquari. Se il ricambio d'aria non lo porta fuori, resta nell'aria e si deposita sui vetri. La camera da letto è il caso tipico: due persone respirano per otto ore a finestra chiusa e il mattino il vetro è grondante. Il Ministero della Salute consiglia di tenere l'umidità relativa sotto il 50% e di non asciugare i panni in ambienti chiusi e poco ventilati. Un igrometro da pochi euro, messo sul davanzale, dice subito a che punto sei.</p>
<h2>Cosa fare, in ordine</h2>
<ol>
<li><strong>Arieggiare bene, non a lungo.</strong> Appena svegli, finestra spalancata per pochi minuti insieme a una sul lato opposto; lo stesso dopo doccia e cucina, con la porta della stanza chiusa. Le indicazioni dell'ISS e il perché una ribalta aperta per ore peggiora le cose sono in <a href="/ventilazione/aprire-le-finestre/">Aprire le finestre bene</a>.</li>
<li><strong>Produrre meno vapore.</strong> Coperchi sulle pentole, cappa verso l'esterno, panni fuori o in una stanza ventilata con la porta chiusa. Se usi un umidificatore, spegnilo: con la condensa sui vetri non serve.</li>
<li><strong>Non raffreddare le finestre.</strong> Tende pesanti chiuse e tapparelle abbassate fino al vetro isolano la stanza dal vetro e lo lasciano gelare: la condensa aumenta. Un termosifone sotto la finestra, se c'è, va lasciato libero: il suo compito è proprio scaldare il vetro. I mobili non vanno addossati alle pareti esterne.</li>
<li><strong>Asciugare i vetri la mattina.</strong> Non risolve, ma evita che l'acqua coli sul telaio e sul davanzale, dove la muffa attacca il silicone e il legno.</li>
<li><strong>Deumidificatore</strong>, se con i primi tre punti l'umidità resta sopra il 55-60%: tampona nelle settimane più fredde. Il confronto tra modelli è in preparazione.</li>
<li><strong>Serramenti.</strong> Se i vetri sono singoli, o doppi di prima generazione senza canalina termica, condensano anche con l'aria in ordine: la sostituzione risolve, ma attenzione al rovescio della medaglia. Una casa con finestre nuove e ermetiche ricambia meno aria da sola: se non si arieggia di più, la condensa sparisce dai vetri e ricompare come muffa negli angoli. Chi cambia le finestre dovrebbe mettere in conto anche la ventilazione, con aeratori nel telaio o un impianto; quando conviene è spiegato nella guida sulle finestre.</li>
</ol>
<h2>Un numero da ricordare</h2>
<p>Se l'igrometro in camera segna oltre il 60% la mattina, i vetri condensano quasi con qualsiasi serramento: il problema è l'aria. Se segna sotto il 50% e i vetri sono comunque bagnati, il problema è il vetro. In mezzo, di solito, basta cambiare abitudini.</p>
<p class="nota">Questa guida non sostituisce la valutazione di un tecnico. Per la muffa che ne deriva e per distinguerla da infiltrazioni e risalita: <a href="/muffa/muffa-in-casa/">Muffa in casa: da dove viene e come eliminarla davvero</a>.</p>
""", sources=fonti("minsal_muffe", "iss_covid_11", "oms_dampness"),
    section="muffa", data="11 novembre 2026",
    breve=["I vetri si bagnano quando l'aria umida tocca la superficie più fredda della stanza: con 20 °C e 65% di umidità basta un vetro a 13 °C.",
           "Nove volte su dieci la causa è l'aria (respiro, docce, bucato, poco ricambio), non la finestra; l'igrometro lo dice subito.",
           "Prima arieggiare bene e produrre meno vapore, poi deumidificatore; i serramenti nuovi risolvono ma richiedono più ventilazione."],
    chiave=("13 °C", "punto di rugiada", "con aria a 20 °C e umidità al 65%: ogni superficie più fredda si bagna"))

add("/acqua/filtri-confronto/", "Caraffa, filtro al rubinetto o depuratore sotto il lavello: confronto con prezzi",
    "Cosa fa davvero ogni sistema (caraffe Brita e Laica, filtri al rubinetto, sotto lavello a carboni, osmosi inversa, impianti installati), cosa dice l'inchiesta Altroconsumo 2026, cosa serve contro calcare, cloro e PFAS, e quanto costa all'anno. Prezzi verificati l'11 novembre 2026.",
    """
<p>Il mercato dei filtri per l'acqua vive su un'idea: che l'acqua del rubinetto non sia abbastanza buona. In Italia, per la grande maggioranza delle case, non è vero: è controllata per legge e conforme. Un filtro ha senso per tre motivi concreti, gusto (cloro), calcare (durezza) e, in zone specifiche, PFAS o piombo dai tubi vecchi. Questa guida confronta i sistemi per quello che fanno davvero e per quanto costano nel tempo, non per quello che promettono.</p>
<h2>Prima di comprare: serve davvero?</h2>
<p>Altroconsumo, nella sua guida alle caraffe di ottobre 2026, mette al primo posto una domanda: l'acqua del tuo rubinetto ha davvero bisogno di essere trattata? Per rispondere bastano i valori del gestore per il tuo comune, come spiegato nella guida <a href="/acqua/acqua-del-rubinetto/">L'acqua del rubinetto è buona?</a>. Se cloro, durezza e PFAS sono nella norma e il sapore ti va bene, il filtro migliore è nessun filtro.</p>
<p>Nell'inchiesta pubblicata il 25 febbraio 2026, Altroconsumo ha fatto analizzare l'acqua prima e dopo 12 impianti installati in case di volontari (Grohe, Culligan, Acqualife, Better Life e altri). Il risultato in sintesi: i filtri migliorano gusto e alcuni parametri chimici, ma non sempre sono necessari; gli impianti a osmosi inversa riducono drasticamente calcio e magnesio, cioè producono un'acqua molto povera di sali; il prezzo medio degli impianti testati era intorno ai 2.300 euro, con una forchetta da 450 a oltre 4.000.</p>
<h2>I cinque sistemi, cosa fanno e cosa no</h2>
<table class="tab">
<thead><tr><th>Sistema</th><th>Cosa fa</th><th>Cosa non fa</th><th>Prezzo verificato</th><th>Costo cartucce</th></tr></thead>
<tbody>
<tr><td><strong>Caraffa filtrante</strong> (carboni attivi + resine)</td><td>Toglie il sapore di cloro, riduce la durezza (meno calcare in bollitore e macchina del caffè); le cartucce più recenti dichiarano anche una riduzione di PFAS e metalli</td><td>Non serve alla potabilità; la cartuccia va cambiata ogni 4 settimane o si peggiora l'acqua; filtra poco più di un litro alla volta</td><td>Brita Marella 2,4 l con 1 cartuccia Maxtra Pro: 24,95 € · Laica Stream Line 2,3 l: 14,90-17,46 € (Amazon.it)</td><td>Brita Maxtra Pro: 7-12 € a cartuccia secondo la confezione · Laica bi-flux: 39,90 € per 12 (3,30 € l'una). Un anno: 40-140 €</td></tr>
<tr><td><strong>Filtro al rubinetto</strong></td><td>Come la caraffa, ma in continuo e senza aspettare; comodo per cucinare</td><td>Portata ridotta; non toglie nitrati; il test Altroconsumo sui filtri da rubinetto non ha trovato variazioni di residuo fisso e conducibilità</td><td>Brita On Tap: 62,85 € · Laica FR01A01: 15,99 € (Amazon.it)</td><td>Brita On Tap: 1 cartuccia ogni 600 litri, circa 4 mesi; Laica: cartucce economiche ma vita breve. Un anno: 40-100 €</td></tr>
<tr><td><strong>Sotto lavello a carboni / ultrafiltrazione</strong></td><td>Cloro, sapore, sedimenti, in alcuni modelli batteri (ultrafiltrazione); mantiene i sali minerali; rubinetto dedicato</td><td>Non riduce la durezza né nitrati; sui PFAS i carboni attivi hanno risultati molto variabili (studio Duke: in media -73%, ma alcuni non toglievano nulla)</td><td>Philips AUT2015: 149,24 € (ForHome, via Trovaprezzi)</td><td>Cartuccia ogni 6-12 mesi, 30-80 €</td></tr>
<tr><td><strong>Osmosi inversa sotto lavello</strong></td><td>Toglie quasi tutto: calcare, nitrati, piombo, PFAS (studio Duke: in media -94%), microplastiche, residuo fisso; è il sistema con i risultati più costanti sui PFAS</td><td>Toglie anche calcio e magnesio (acqua "vuota", a meno di uno stadio di remineralizzazione); scarta una parte dell'acqua; serve una presa elettrica nei modelli senza serbatoio; manutenzione annuale da fare davvero</td><td><a href="https://www.waterdropfilter.eu/it-it/collections/systems-osmosi-inversa?ref=lppdszhh" rel="nofollow sponsored noopener">Waterdrop T3-M</a> 450 GPD con remineralizzazione: 219,99 € (sito Waterdrop EU) · Waterdrop G3P600: 399,99 € (Kaufland.it) · <a href="https://www.waterdropfilter.eu/it-it/collections/systems-osmosi-inversa?ref=lppdszhh" rel="nofollow sponsored noopener">Waterdrop X12</a>: 879-1.099 € (sito Waterdrop EU)</td><td>Filtri: Waterdrop dichiara 160-183 € l'anno per la serie X; membrana ogni 2-3 anni</td></tr>
<tr><td><strong>Impianto installato</strong> (Culligan, Grohe Blue, Acqualife e simili)</td><td>Acqua filtrata, spesso refrigerata e gassata, da un rubinetto dedicato; assistenza a domicilio; a seconda del modello carboni, ultrafiltrazione o osmosi</td><td>Costa 5-10 volte un sistema equivalente da montare da sé; vendita a domicilio con pratiche che Altroconsumo ha denunciato come poco trasparenti ("bonus acqua" inesistente, test gratuiti che sono visite di vendita)</td><td>Grohe Blue Home: 1.000-2.400 € · media degli impianti testati da Altroconsumo: circa 2.300 €, da 450 a oltre 4.000</td><td>Contratti di manutenzione annuale, spesso 100-250 € (varia per installatore: chiedere il prezzo scritto)</td></tr>
</tbody>
</table>
<p class="nota"><strong>Black Friday (14 novembre 2026).</strong> Waterdrop ha un banner di promozione con sconti "fino a 800 €", senza date di inizio e di fine. I prezzi in tabella sono quelli letti l'11 novembre 2026 e non includono promozioni: prima di comprare, controlla il prezzo del giorno sul sito del produttore.</p>
<h2>Cosa scegliere per ogni problema</h2>
<ul>
<li><strong>Sapore di cloro.</strong> Prima prova gratis: acqua in una caraffa aperta in frigorifero per un'ora, il cloro evapora. Se non basta, caraffa filtrante o filtro al rubinetto: fanno esattamente questo. Non serve altro.</li>
<li><strong>Calcare.</strong> Per bere, la caraffa riduce la durezza; per lavatrice, caldaia e doccia serve un addolcitore sull'impianto, che è un'altra cosa (guida in preparazione). L'osmosi toglie il calcare dall'acqua da bere ma è una soluzione sproporzionata se il problema è solo quello.</li>
<li><strong>Nitrati</strong> (pozzi, aree agricole): solo osmosi inversa o scambio ionico dedicato; caraffe e carboni non li toccano.</li>
<li><strong>PFAS.</strong> Se il gestore è conforme (somma di PFAS sotto 0,10 µg/L dal 2026), non serve un filtro. Se vivi in un'area con superamenti o hai un pozzo: osmosi inversa, oppure carboni attivi con cartuccia certificata per i PFAS (norma NSF/ANSI 53 o 58) e cambiata puntualmente. Le caraffe che dichiarano "riduce PFAS" riportano un dato del produttore su condizioni di laboratorio: non è verificato da noi e non vale come protezione in un'area contaminata. Il tema è spiegato nella guida ai <a href="/acqua/pfas/">PFAS nell'acqua del rubinetto</a>.</li>
<li><strong>Piombo</strong> (tubi vecchi): osmosi inversa, o carboni con certificazione specifica per il piombo; la soluzione vera è sostituire i tubi. Guida in preparazione.</li>
<li><strong>Acqua di pozzo.</strong> Prima l'analisi, poi il sistema, che spesso è un potabilizzatore a monte di tutta la casa, non un filtro al rubinetto.</li>
</ul>
<h2>Il costo vero è nelle cartucce</h2>
<p>Una caraffa da 20 euro costa 90-140 euro l'anno di cartucce se le cambi come prescritto, cioè ogni mese. Un sotto lavello da 150 euro costa 30-80 euro l'anno. Un'osmosi da 220-400 euro costa 100-180 euro l'anno. Un impianto installato da 2.000 euro costa anche 100-250 euro l'anno di manutenzione. Prima di scegliere, calcola tre anni di esercizio, non il prezzo di acquisto: la caraffa è il sistema con il costo d'ingresso più basso e tra i più cari nel tempo.</p>
<p>E c'è una regola che vale per tutti: un filtro con la cartuccia scaduta è peggio di nessun filtro. Trattiene batteri e rilascia quello che aveva accumulato. Se sai che non cambierai le cartucce, non comprarlo.</p>
<h2>Il nostro consiglio</h2>
<ul>
<li><strong>Acqua di rete conforme, sapore che non ti piace:</strong> caraffa Laica Stream Line o Brita Marella, scegliendo in base al costo delle cartucce, che è dove si spende. Oppure il filtro al rubinetto se bevi e cucini molto con acqua filtrata.</li>
<li><strong>Vuoi acqua filtrata in continuo senza stravolgere l'acqua:</strong> un sotto lavello a carboni/ultrafiltrazione come il Philips AUT2015. Mantiene i minerali, costa poco da mantenere.</li>
<li><strong>PFAS, nitrati, piombo o pozzo:</strong> osmosi inversa con remineralizzazione, come il <a href="https://www.waterdropfilter.eu/it-it/collections/systems-osmosi-inversa?ref=lppdszhh" rel="nofollow sponsored noopener">Waterdrop T3-M</a> o il G3P600. Chiedi sempre la certificazione NSF/ANSI 58 e metti in agenda il cambio filtri.</li>
<li><strong>Impianto installato:</strong> solo se vuoi acqua fredda e gassata dal rubinetto e il servizio a domicilio vale per te la differenza di prezzo. Pretendi un preventivo scritto con il costo della manutenzione, non firmare durante la visita e diffida di qualsiasi "bonus acqua": il credito d'imposta per i sistemi di filtraggio è finito nel 2024, come ricorda Altroconsumo.</li>
</ul>
<aside class="aff"><p class="aff-t">Affiliazioni, dichiarate</p><p>I link a Waterdrop in questa pagina sono link di affiliazione: se compri dopo averli seguiti, Casa Respira riceve una commissione, a prezzo invariato per te. Con Amazon il programma è in attivazione. Il confronto qui sopra non cambia: per la maggior parte delle case conformi il consiglio resta di non comprare nulla, e la caraffa o il sotto lavello a carboni, su cui non guadagniamo, vengono prima dell'osmosi.</p></aside>
<h2>Come abbiamo verificato i prezzi</h2>
<p>Prezzi letti il giorno indicato in fondo alla pagina sui siti citati, IVA inclusa, senza spedizione. I prezzi Amazon oscillano di giorno in giorno; quelli degli impianti installati vengono dall'inchiesta Altroconsumo e non da preventivi nostri. I dati sull'efficacia contro i PFAS vengono dallo studio Duke University / NC State e non da prove nostre. Se trovi una differenza, scrivici e aggiorniamo.</p>
<p class="nota">Questa guida non sostituisce l'analisi dell'acqua né il parere di un tecnico. Per acque di pozzo o superamenti dichiarati dal gestore, parti dall'analisi di un laboratorio accreditato.</p>
""", sources=fonti("altroconsumo_filtri_2026", "altroconsumo_bonus", "altroconsumo_caraffe_2026", "fattoalimentare_filtri", "amazon_brita", "amazon_laica", "waterdrop_t3", "waterdrop_ro", "kaufland_g3p600", "trovaprezzi_philips", "dlgs_18_2023"),
    section="acqua", data="11 novembre 2026",
    breve=["Con acqua di rete conforme, un filtro serve al gusto o al calcare, non alla potabilità: il filtro migliore spesso è nessun filtro (Altroconsumo, ottobre 2026).",
           "Caraffe e filtri al rubinetto costano poco all'acquisto e 40-140 € l'anno di cartucce; l'osmosi inversa (220-400 €) è l'unica costante su PFAS, nitrati e piombo, ma toglie anche i minerali.",
           "Gli impianti installati costano in media 2.300 € (Altroconsumo, febbraio 2026): valgono solo per acqua fredda e gassata e assistenza, mai per paura."],
    chiave=("2.300", "euro", "prezzo medio degli impianti domestici installati analizzati da Altroconsumo nel 2026; una caraffa costa 20"))

# ------------------------------------------------------------- bozze
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
    ("pfas-liguria-borgio-verezzi-novembre-2026", "2026-11-06", "6 novembre 2026",
     "PFAS nell'acqua in Liguria: a Borgio Verezzi e Pietra Ligure si lavora ai filtri a carboni attivi",
     "Il gestore Servizi Ambientali ha confermato il 4 novembre la priorità degli interventi di filtrazione a carboni attivi per ripristinare la potabilità dell'acqua nei Comuni di Borgio Verezzi e Pietra Ligure (Savona), dove sono stati trovati PFAS oltre i limiti. La Regione Liguria ha istituito una cabina di regia e la Procura di Savona ha aperto un fascicolo.",
     "Chi vive nei due Comuni deve seguire le ordinanze comunali e le comunicazioni del gestore sull'uso dell'acqua. Per tutti gli altri, il caso mostra come funziona la nuova norma: dal 2026 i PFAS sono un parametro di legge e, se superano il limite, il gestore deve intervenire. Cosa sono e come leggere i dati del proprio comune è spiegato nella guida ai PFAS nell'acqua.",
     [("Savonanews, PFAS nell'acqua, Servizi Ambientali accelera sugli interventi (6 novembre 2026)", "https://www.savonanews.it/2026/11/06/leggi-notizia/argomenti/attualit/articolo/pfas-nellacqua-servizi-ambientali-accelera-sugli-interventi-necessario-il-sostegno-economico-di.html"),
      ("Casa Respira, PFAS nell'acqua del rubinetto: cosa sono e cosa dice la legge", "https://casarespira.it/acqua/pfas/")]),
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
        else: classes.append("sec")
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
<link rel="apple-touch-icon" href="/assets/logo-192.png">
"""


def og(titolo, desc, path, slug):
    return f"""<meta property="og:type" content="website">
<meta property="og:site_name" content="Casa Respira">
<meta property="og:title" content="{esc(titolo)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/og/{slug}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
"""


EN_NAV = [("/en/", "English guides"), ("/en/radon-in-italy/", "Radon in Italy"), ("/en/property-due-diligence/", "Due diligence")]
DATA_EN = "6 November 2026"


def nav_html_en(current):
    items = "".join(f'<a href="{h}" class="sec{" on" if current == h else ""}">{esc(l)}</a>' for h, l in EN_NAV)
    items += '<a href="/" class="sec" lang="it">Italiano →</a>'
    return '<nav class="nav" aria-label="Sections">' + items + "</nav>"


def header(current, lang="it"):
    if lang == "en":
        return f"""<header class="top">
<div class="wrap top-in">
<a class="brand" href="/en/"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 120 120" width="44" height="44"><rect width="120" height="120" rx="26" fill="#16222E"/><path d="M24 78 A36 36 0 0 1 96 78" fill="none" stroke="#2E7FB8" stroke-width="10" stroke-linecap="round"/><path d="M40 78 A20 20 0 0 1 80 78" fill="none" stroke="#2E7FB8" stroke-width="7" stroke-linecap="round" opacity=".5"/><rect x="28" y="84" width="64" height="10" rx="5" fill="#C98A00"/><circle cx="60" cy="66" r="6" fill="#C98A00"/></svg></span><span class="brand-text"><span class="brand-name">Casa Respira</span><span class="brand-pay">indoor air and water in Italy, measured and explained</span></span></a>
{nav_html_en(current)}
</div>
</header>"""
    return f"""<header class="top">
<div class="wrap top-in">
<a class="brand" href="/"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 120 120" width="44" height="44"><rect width="120" height="120" rx="26" fill="#16222E"/><path d="M24 78 A36 36 0 0 1 96 78" fill="none" stroke="#2E7FB8" stroke-width="10" stroke-linecap="round"/><path d="M40 78 A20 20 0 0 1 80 78" fill="none" stroke="#2E7FB8" stroke-width="7" stroke-linecap="round" opacity=".5"/><rect x="28" y="84" width="64" height="10" rx="5" fill="#C98A00"/><circle cx="60" cy="66" r="6" fill="#C98A00"/></svg></span><span class="brand-text"><span class="brand-name">Casa Respira</span><span class="brand-pay">aria e acqua di casa, misurate e spiegate</span></span></a>
{nav_html(current)}
</div>
</header>"""


FOOTER_EN = """<footer class="foot">
<div class="wrap">
<p>Casa Respira is an independent Italian guide to indoor air and water. No bylines: texts are by the editorial staff. Some links are affiliate links, as explained (in Italian) in <a href="/come-lavoriamo/#come-ci-sosteniamo">Come lavoriamo</a>. It does not replace the advice of a technician or a doctor.</p>
<p><a href="/en/">English guides</a> · <a href="/">Italiano</a> · <a href="/feed.xml">RSS</a></p>
</div>
</footer>"""

FOOTER = """<footer class="foot">
<div class="wrap">
<p>Casa Respira è una guida indipendente su aria e acqua dentro casa. Nessuna firma: i testi sono della redazione. Alcuni link sono affiliati, come spiegato in <a href="/come-lavoriamo/#come-ci-sosteniamo">Come lavoriamo</a>. Non sostituisce il parere di un tecnico o del medico.</p>
<p><a href="/feed.xml">Feed RSS</a> · <a href="/chi-siamo/">Chi siamo</a> · <a href="/come-lavoriamo/">Come lavoriamo</a> · <a href="/come-lavoriamo/#come-ci-sosteniamo">Come ci sosteniamo</a> · <a href="/en/" lang="en">English guides</a></p>
</div>
</footer>"""


TEMI_NOMI = [v[0] for v in TEMI.values()]


def tema_di(path):
    for k, v in TEMI.items():
        if path.startswith(k): return v[0]
    return ""


HREFLANG = {"/en/": "/", "/en/radon-in-italy/": "/radon/guida-completa/", "/en/property-due-diligence/": "/radon/normativa/"}
HREFLANG_IT = {v: k for k, v in HREFLANG.items()}


def hreflang(path):
    if path in HREFLANG:
        return f'<link rel="alternate" hreflang="it" href="{SITE}{HREFLANG[path]}">\n<link rel="alternate" hreflang="en" href="{SITE}{path}">\n'
    if path in HREFLANG_IT:
        return f'<link rel="alternate" hreflang="en" href="{SITE}{HREFLANG_IT[path]}">\n<link rel="alternate" hreflang="it" href="{SITE}{path}">\n'
    return ""


def render_page(p):
    body, toc = add_ids(p["body"])
    noindex = p["status"] == "draft"
    en = p.get("lang") == "it" and False or p.get("lang") == "en"
    is_guide = p["section"] in TEMI_NOMI or (en and p["chiave"] is not None)
    T = dict(indice="On this page", breve="In short", fonti="Sources", link="Links checked on", verif="Sources checked on", corr="Corrections", nocorr="No corrections so far.", data=DATA_EN) if en else dict(indice="In questa pagina", breve="In breve", fonti="Fonti", link="Link controllati il", verif="Fonti verificate il", corr="Correzioni", nocorr="Nessuna correzione finora.", data=p.get("data") or DATA_ULTIMA_VERIFICA)

    aside = ""
    if is_guide:
        parts = []
        if p["chiave"]:
            n, u, d = p["chiave"]
            parts.append(f'<div class="chiave"><span class="chiave-n">{esc(n)}</span><span class="chiave-u">{esc(u)}</span><p>{esc(d)}</p></div>')
        if toc:
            lis = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
            parts.append(f'<nav class="indice" aria-label="{T["indice"]}"><p class="indice-t">{T["indice"]}</p><ol>{lis}</ol></nav>')
        aside = '<aside class="lato">' + "".join(parts) + "</aside>"

    breve = ""
    if p["breve"]:
        lis = "".join(f"<li>{esc(b)}</li>" for b in p["breve"])
        breve = f'<div class="breve"><p class="breve-t">{T["breve"]}</p><ul>{lis}</ul></div>'

    scala = f'<figure class="scala-box">{scala_svg()}<figcaption>Livelli di riferimento del D.Lgs. 101/2020 e raccomandazione OMS. Oltre il livello della tua casa, si interviene.</figcaption></figure>' if p["scala"] else ""

    fonti_html = ""
    if p["sources"]:
        lis = "".join(f'<li><a href="{esc(u)}" rel="nofollow noopener">{esc(l)}</a></li>' for l, u in p["sources"])
        fonti_html = f'<section class="fonti" id="fonti"><h2>{T["fonti"]}</h2><ul>{lis}</ul><p class="nota">{T["link"]} {T["data"]}.</p></section>'

    layout_cls = "pagina pagina-guida" if is_guide else "pagina"
    return f"""<!DOCTYPE html>
<html lang="{'en' if en else 'it'}">
<head>
{HEAD_COMMON}<title>{esc(p['title'])} | Casa Respira</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{SITE}{p['path']}">
{hreflang(p['path'])}{og(p['title'], p['desc'], p['path'], p['path'].strip('/').replace('/', '-') or 'home')}{'<meta name="robots" content="noindex, nofollow">' if noindex else ''}
<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body class="tema-{'radon' if en else tema_di(p['path'])}">
{header(p['path'], 'en' if en else 'it')}
<main class="wrap {layout_cls}">
<article class="testo">
<p class="verifica">{T["verif"]} {T["data"]}</p>
<h1>{esc(p['title'])}</h1>
{breve}
{scala}
{body}
{fonti_html}
<section class="correzioni"><h2>{T["corr"]}</h2><p>{T["nocorr"]}</p></section>
</article>
{aside}
</main>
{FOOTER_EN if en else FOOTER}
</body>
</html>
"""


def render_sezione(path, nome, lead, previste, guide):
    pubblicate = [p for p in guide if p["section"] == tema_di(path)]
    pub_html = ""
    if pubblicate:
        lis = "".join(f'<li><a href="{p["path"]}"><strong>{esc(p["title"])}</strong><span>{esc(p["desc"])}</span></a></li>' for p in pubblicate)
        pub_html = f'<h2>Le guide pubblicate</h2><ul class="lista-guide">{lis}</ul>'
    prev = "".join(f"<li>{esc(t)}</li>" for t in previste)
    titolo_prev = "In preparazione" if pubblicate else "Le guide in preparazione"
    prev_html = f'<h2>{titolo_prev}</h2><ul class="previste">{prev}</ul>' if previste else ''
    intro_vuota = "" if pubblicate else '<p>Questa sezione non ha ancora guide pubblicate. Le prime escono nelle prossime settimane, una alla volta, con le stesse regole delle altre: fonti istituzionali con link e data, prezzi verificati, correzioni dichiarate.</p>'
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>{esc(nome)} | Casa Respira</title>
<meta name="description" content="{esc(lead)}">
<link rel="canonical" href="{SITE}{path}">
{og(nome, lead, path, tema_di(path))}<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
</head>
<body class="tema-{tema_di(path)}">
{header(path)}
<main class="wrap pagina">
<article class="testo sezione">
<div class="sezione-testa"><div><h1>{esc(nome)}</h1>
<p class="lead">{esc(lead)}</p></div><figure class="sezione-casa">{casa_svg(tema_di(path))}</figure></div>
{intro_vuota}
{pub_html}
{prev_html}
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
{og(titolo, fatto[:150], f"/news/{slug}/", "news-" + slug)}
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
{og("News | Casa Respira", "Campagne di misura gratuite, nuove aree prioritarie, norme. Solo con fonte e data.", "/news/", "news")}
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


def render_home(guide_tutte):
    radon = [p for p in guide_tutte if p["section"] == "radon"]
    guide = "".join(
        f'<li><a href="{p["path"]}"><strong>{esc(p["title"])}</strong><span>{esc(p["desc"])}</span></a></li>'
        for p in radon)
    ultime = "".join(f'<li><time datetime="{n[1]}">{esc(n[2])}</time><a href="/news/{n[0]}/">{esc(n[3])}</a></li>' for n in NEWS[:3])
    def conta(path, prev):
        n = len([p for p in guide_tutte if p["section"] == TEMI[path][0]])
        pub = f"{n} guida pubblicata" if n == 1 else f"{n} guide pubblicate"
        return pub + (f" · {len(prev)} in preparazione" if prev else "")
    temi = "".join(
        f'<li class="t-{TEMI[path][0]}"><a href="{path}"><strong>{esc(nome)}</strong><span>{esc(lead)}</span><em>{conta(path, prev)}</em></a></li>'
        for path, nome, lead, prev in SEZIONI if path != "/radon/")
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
{HEAD_COMMON}<title>Casa Respira | Aria e acqua di casa, misurate e spiegate</title>
<meta name="description" content="Guida indipendente su aria e acqua dentro casa. Il radon è il tema di partenza: livelli di legge, come si misura, come si riduce.">
<link rel="canonical" href="{SITE}/">
{hreflang("/")}{og("Casa Respira | Aria e acqua di casa, misurate e spiegate", "Guida indipendente su aria e acqua dentro casa. Radon, muffa, aria, ventilazione e acqua, spiegati con i numeri delle fonti pubbliche.", "/", "home")}<link rel="alternate" type="application/rss+xml" title="Casa Respira" href="{SITE}/feed.xml">
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
<p class="nota">Ogni sezione cresce una pagina alla volta. Le nuove guide escono nel <a href="/feed.xml">feed RSS</a>.</p>
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
.nav{display:flex;gap:2px;flex-wrap:wrap;align-items:center}
.nav a{padding:10px 13px;border-radius:8px;text-decoration:none;color:var(--inchiostro);font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:20px;letter-spacing:-0.01em;font-variation-settings:"opsz" 24;display:inline-flex;align-items:center;gap:8px;line-height:1}
.nav a[class*="t-"]::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--tema);flex:none;transition:transform .15s}
.nav a[class*="t-"]:hover::before,.nav a[class*="t-"].on::before{transform:scale(1.35)}
.nav a:hover{background:var(--nebbia-chiara)}
.nav a.on{color:var(--inchiostro)}
.nav a.sec{font-family:"IBM Plex Sans",system-ui,sans-serif;font-weight:500;font-size:14.5px;color:var(--grigio);padding:8px 10px;letter-spacing:0.01em}
.nav a.sec:first-of-type{margin-left:0}
.nav a.t-acqua{margin-right:14px;position:relative}
.nav a.t-acqua::after{content:"";position:absolute;right:-9px;top:25%;height:50%;width:1px;background:var(--nebbia)}
.nav a.sec.on{color:var(--inchiostro);box-shadow:inset 0 -2px 0 var(--inchiostro)}

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
.tab{width:100%;border-collapse:collapse;margin:18px 0 22px;font-size:15px}
.tab th,.tab td{border-bottom:1px solid var(--nebbia);padding:10px 10px;text-align:left;vertical-align:top}
.tab th{font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--grigio);background:var(--nebbia-chiara)}
.tab td:first-child{font-weight:500}
@media (max-width:860px){.tab{display:block;overflow-x:auto;white-space:nowrap}.tab td,.tab th{white-space:normal;min-width:150px}}
.schema{margin:24px 0;background:var(--bianco);border:1px solid var(--nebbia);border-radius:10px;padding:12px}
.schema svg{width:100%;height:auto;display:block}
.schema figcaption{font-size:14px;color:var(--grigio);margin-top:10px;line-height:1.5}
.aff{background:var(--bianco);border:1px solid var(--nebbia);border-left:4px solid var(--tema,var(--ambra));border-radius:8px;padding:14px 18px;margin:22px 0;font-size:15.5px}
.aff .aff-t{margin:0 0 6px;font-weight:600;color:var(--inchiostro);font-size:14px;text-transform:uppercase;letter-spacing:.04em}
.aff p{margin:0}
.lista-guide{list-style:none;padding:0;margin:16px 0 20px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.lista-guide a{display:block;background:var(--bianco);border:1px solid var(--nebbia);border-left:4px solid var(--tema,#C98A00);border-radius:8px;padding:16px 18px;text-decoration:none;color:var(--testo);height:100%}
.lista-guide a:hover{background:var(--tema-ch,#FBFDFE)}
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
.nav a{padding:8px 9px;font-size:17px}
  .nav a.sec{font-size:13.5px;padding:6px 8px}
  .nav a.t-acqua{margin-right:0}
  .nav a.t-acqua::after{display:none}

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
.nav a[class*="t-"].on{background:var(--tema-ch)}
.nav a[class*="t-"]:hover{background:var(--tema-ch)}
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
    # pulisce solo ciò che genera, mai la radice del repository
    GENERATI = ["en", "chi-siamo", "come-lavoriamo", "come-ci-sosteniamo", "radon", "muffa", "aria",
                "ventilazione", "acqua", "news", "index.html", "feed.xml", "sitemap.xml", "robots.txt"]
    for g in GENERATI:
        pth = os.path.join(OUT, g)
        if os.path.isdir(pth): shutil.rmtree(pth)
        elif os.path.isfile(pth): os.remove(pth)
    if os.path.isdir(OUT_BOZZE):
        shutil.rmtree(OUT_BOZZE)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(os.path.join(OUT, "assets")) if os.path.isdir(os.path.join(OUT, "assets")) else []:
        if f.startswith("site-") and f.endswith(".css"):
            os.remove(os.path.join(OUT, "assets", f))
    write(OUT, f"/assets/site-{cssv}.css", CSS)

    live = [p for p in PAGES if p["status"] == "live"]
    guide_tutte = [p for p in live if p["section"] in TEMI_NOMI]

    for p in PAGES:
        base = OUT if p["status"] == "live" else OUT_BOZZE
        rel = p["path"].replace("/bozze", "") if p["status"] != "live" else p["path"]
        write(base, rel + "index.html", render_page(p))
    if os.path.isdir(OUT_BOZZE):
        shutil.copytree(os.path.join(OUT, "assets"), os.path.join(OUT_BOZZE, "assets"), dirs_exist_ok=True)

    write(OUT, "/index.html", render_home(guide_tutte))
    write(OUT, "/news/index.html", render_news_index())
    for n in NEWS:
        write(OUT, f"/news/{n[0]}/index.html", render_news_item(n))
    for path, nome, lead, prev in SEZIONI:
        write(OUT, path + "index.html", render_sezione(path, nome, lead, prev, guide_tutte))

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
</item>""" for p in guide_tutte)
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
