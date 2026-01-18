# Postkasse Optimalisering MVP

Dette prosjektet er en Minimum Viable Product (MVP) for å optimere postlevering ved hjelp av datasyn (Computer Vision).

## Mål
Formålet er å redusere unødvendige turer til hentekontor ved å:
1.  Automatisk analysere postkassereoler med mobilkamera.
2.  Klassifisere postkassenes størrelse (Liten, Standard, Stor).
3.  Simulere levering for å se om dagens pakker får plass.

## Struktur
Prosjektet er modulært oppbygd:
-   `modules/datamodel.py`: Definisjon av Postkasse og Pakke.
-   `modules/bildeanalyse.py`: Bildeanalyse-logikk (OpenCV).
-   `modules/leveringslogikk.py`: Algoritmer for å matche pakke mot postkasse.
-   `modules/rapport.py`: Generering av statistikk.

## Installasjon
Prosjektet krever Python 3.8+ og noen avhengigheter.

```bash
pip install -r requirements.txt
```

## Kjøring av Demo
Vi har lagt ved en `main.py` som kjører en full demonstrasjon med syntetiske data.
Denne vil generere testbilder i `data/test_bilder`, analysere dem, og simulere en leveringsrute.

```bash
python3 main.py
```

## Utvidelse
For å bruke dette med ekte data:
1.  Ta bilder av reelle oppganger.
2.  Legg bildene i en mappe.
3.  Bruk `modules.bildeanalyse.analyser_bilder_av_oppgang(bildeliste, id)` for å hente data.
4.  Koble dataene mot Postens API for pakkedimensjoner.
