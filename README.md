# Postkasse Optimalisering & Datafangst (MVP)

Dette prosjektet utvikler et system for å optimalisere postlevering ved å bygge en nøyaktig database over postkassestørrelser ("Infrastruktur-kartlegging").

## 🎯 Målsetting
Posten taper penger når bud tar med pakker på ruten som ikke får plass i mottakers postkasse. Dette medfører unødvendige turer og manuell omdirigering til hentekontor.

**Løsningen:**
1.  Et **Datafangst-verktøy (iOS App)** som postbudet bruker.
2.  Appen bruker **AI (Computer Vision)** og **AR** til å automatisk gjenkjenne og måle postkasser.
3.  Disse målene matches mot pakkedimensjoner *før* ruten starter (på terminalen), slik at "umulige" pakker sorteres ut direkte.

---

## 🏗️ Arkitektur

Prosjektet består av tre hoveddeler:

### 1. iOS App (Feltarbeid)
-   **Teknologi**: Swift, ARKit, Vision, CoreML.
-   **Funksjon**: Lar postbudet scanne oppganger.
-   **Egenskaper**:
    -   Live AR-guidance (tegner bokser på skjermen).
    -   Offline-støtte (lagrer bilder lokalt).
    -   *Kommer*: Automatisk måling av fysisk bredde/høyde.

### 2. AI og Trening (Hjernen)
-   **Teknologi**: Python, YOLOv8, PyTorch.
-   **Funksjon**: Lærer systemet å kjenne igjen norske postkasser (System, Stansefabrikken, etc.).
-   **Status**: Egenprodusert datasett (ca 30 bilder) og lokal trening.

### 3. Backend & Simulering (Analyse)
-   **Teknologi**: Python, Flask, OpenCV.
-   **Funksjon**: Mottar data, simulerer pakkelevering ("Fit Check"), og genererer rapporter.

---

## 🚦 Veikart (Roadmap) & Status

| Fase | Beskrivelse | Status |
| :--- | :--- | :--- |
| **Fase 1: MVP** | Grunnleggende iOS-app med server-side analyse (OpenCV). | ✅ **FERDIG** |
| **Fase 2: Datainnsamling** | Offline-modus i app, import fra web, og syntetiske data. | ✅ **FERDIG** |
| **Fase 3: Smart AI** | Trening av custom YOLOv8-modell på egne data. | ✅ **FERDIG (V1)** |
| **Fase 4: On-Device Intelligence** | Kjøre AI direkte på iPhone (CoreML) for sanntids feedback. | 🚧 **PÅGÅR (Neste steg)** |
| **Fase 5: AR Måling** | Koble AI-boksene mot AR-dybde for å få nøyaktige CM-mål. | 📅 Planlagt |
| **Fase 6: Integrasjon** | Koble måledataene mot Postens rutebok/API. | 📅 Fremtid |

---

## 🚀 Hvordan komme i gang

### 1. Oppsett (Mac)
Installer avhengigheter for trening og server:
```bash
pip install -r requirements.txt
pip install ultralytics coremltools
```

### 2. Kjøre Appen (iOS)
1.  Åpne `ios_app/PostkasseMVP` i Xcode.
2.  Endre IP-adresse i `NetworkManager.swift` til din Mac.
3.  Kjør på iPhone.

### 3. Trene AI-en ("The Ritual")
1.  Samle bilder i `data/import_queue/` eller ta bilder med Appen.
2.  Import: `python3 tools/import_data.py`
3.  Annoter: Bruk `labelImg` i `data/training_raw/`.
4.  Tren: `python3 tools/prepare_yolo_data.py && python3 train_model.py`
5.  Konverter til iPhone: `python3 tools/export_coreml.py`

---

## 📊 Resultater
Treningsresultater og grafer lagres fortløpende i mappen `AI_Trening_Resultater/`.
Siste modell ligger i `runs/detect/trainX/weights/best.mlpackage`.
