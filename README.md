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

## Testing og Evaluering
Prosjektet inkluderer et automatiseringsskript for å teste robusthet under ulike støyforhold.

### Kjør automatiserte tester
```bash
python3 automatiser_test.py
```

Dette vil:
1.  Kjøre 4 scenarier (fra Baseline til Ekstrem støy).
2.  Generere hundrevis av testbilder i `data/temp_test_bilder/`.
3.  Logge resultatene til konsollen og filen `resultater.csv`.

**Eksempel på output:**
```text
=== TEST RESULTATER ===
| Scenario               |   Støy |   Oppganger |   Pakker |   Direkte |   Hentekontor | % Direkte   |
|------------------------|--------|-------------|----------|-----------|---------------|-------------|
| Baseline (Lav støy)    |   0    |           5 |      100 |        65 |            35 | 65.0%       |
| Realistisk (Litt støy) |   0.05 |           5 |      100 |        63 |            37 | 63.0%       |
```
