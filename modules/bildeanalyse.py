import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime
from modules.datamodel import KapasitetKlasse

logger = logging.getLogger(__name__)

# --- DEL 1: Syntetisk Bildegenerering (Demo-formål) ---

def generer_test_bilde(filnavn: str, shift_x: int = 0, shift_y: int = 0, stoy_faktor: float = 0.0) -> None:
    """
    Genererer et syntetisk bilde av en postkassereol for testing.
    Kan legge til støy og forskyvning for å simulere realisme.
    """
    # ... (Samme logikk som før) ...
    # Kopierer inn logikken fra image_analysis.py for å gjøre modulen selvstendig
    
    height, width = 600, 800
    image = np.ones((height, width, 3), dtype=np.uint8) * 255 # Hvit bakgrunn

    # Tegn en "reol"
    pk_start_x, pk_start_y = 50 + shift_x, 50 + shift_y
    rader, kolonner = 4, 3 
    
    # Definer "sanne" størrelser for simuleringen
    # Rad 0: Små (LITEN) - h=80
    # Rad 1: Standard (STANDARD) - h=120
    # Rad 2: Standard (STANDARD) - h=120
    # Rad 3: Store (STOR) - h=160
    
    rad_hoyder = [80, 120, 120, 160]
    pk_bredde = 150
    margin = 10
    
    current_y = pk_start_y
    pk_counter = 0

    for r in range(rader):
        h = rad_hoyder[r]
        current_x = pk_start_x
        for c in range(kolonner):
            pk_counter += 1
            if pk_counter > 11: break # Stopp etter 11 for asymmetri

            # Tegn postkasse
            # Legg til litt tilfeldig variasjon hvis støy er på
            noise_h = int(np.random.normal(0, 50 * stoy_faktor)) if stoy_faktor > 0 else 0
            
            top_left = (current_x, current_y)
            bottom_right = (current_x + pk_bredde, current_y + h + noise_h)
            
            cv2.rectangle(image, top_left, bottom_right, (0, 0, 0), 2)
            
            # Etikett (for visuell debug)
            cv2.putText(image, str(pk_counter), (current_x+10, current_y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
            
            current_x += pk_bredde + margin
        current_y += h + margin

    if stoy_faktor > 0:
        noise = np.random.normal(0, 25 * stoy_faktor, image.shape).astype(np.uint8)
        image = cv2.add(image, noise)

    cv2.imwrite(filnavn, image)
    logger.info(f"Testbilde generert: {filnavn}")


# --- DEL 2: Bildeanalyse (Kjerne) ---

def analyser_bilde(bilde_sti: str) -> List[Tuple[str, KapasitetKlasse]]:
    """
    Analyserer et enkeltbilde og returnerer funn.
    """
    try:
        img = cv2.imread(bilde_sti)
        if img is None:
            raise FileNotFoundError(f"Fant ikke bildet: {bilde_sti}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
        
        pk_count = 0
        resultater = []
        
        for cnt in sorted_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w < 20 or h < 20: continue # Støyfilter
            
            pk_count += 1
            pk_id = f"PK-{pk_count}"
            
            # Klassifisering (Kalibrerte verdier)
            if h < 100: kap = KapasitetKlasse.LITEN
            elif h < 140: kap = KapasitetKlasse.STANDARD
            else: kap = KapasitetKlasse.STOR
            
            resultater.append((pk_id, kap))
            
        return resultater
    except Exception as e:
        logger.error(f"Feil i analyser_bilde({bilde_sti}): {e}")
        return []

# --- DEL 3: Aggregering (API) ---

def analyser_bilder_av_oppgang(bilder: List[str], oppgang_id: str) -> List[Dict[str, Any]]:
    """
    Tar flere bilder av samme oppgang, aggregerer resultatene og returnerer strukturert data.
    """
    logger.info(f"Analyserer {len(bilder)} bilder for oppgang {oppgang_id}")
    
    observasjoner = {} # {pk_id: [KapasitetKlasse, ...]}
    
    # 1. Samle data fra alle bilder
    for sti in bilder:
        res = analyser_bilde(sti)
        for pk_id, kap in res:
            if pk_id not in observasjoner:
                observasjoner[pk_id] = []
            observasjoner[pk_id].append(kap)
            
    # 2. Beslutt klasse (Konservativ Aggregering)
    output_data = []
    
    # Sorter på ID for ryddig output
    def sort_key(pk_id_str):
        try: return int(pk_id_str.split("-")[1])
        except: return 0
        
    for pk_id in sorted(observasjoner.keys(), key=sort_key):
        klasser = observasjoner[pk_id]
        verdier = [k.value for k in klasser]
        
        # Hvis uenighet, velg største verdi (Konservativ)
        max_val = max(verdier)
        besluttet_klasse = KapasitetKlasse(max_val)
        
        data = {
            "postkasse_id": pk_id, # Lokal ID (PK-1)
            "oppgang_id": oppgang_id,
            "kapasitet_klasse": besluttet_klasse, # Sender Enum objekt
            "bilde_info": {
                "antall_observasjoner": len(klasser),
                "konservativt_valg": max(verdier) != min(verdier),
                "tidspunkt": datetime.now().isoformat()
            }
        }
        output_data.append(data)
        
    return output_data
