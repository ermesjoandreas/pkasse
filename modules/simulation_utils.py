import random
import os
import shutil
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime

# Import modules
from modules.datamodel import Postkasse, Pakke, Oppgang, VolumKlasse
import modules.bildeanalyse as vision
import modules.leveringslogikk as delivery

logger = logging.getLogger("SimUtils")

def generer_syntetiske_ruter(n_oppganger: int, n_postkasser_per_oppgang: int, n_pakker: int) -> Tuple[List[Dict[str, Any]], List[Pakke]]:
    """
    Genererer konfigurajson for oppganger og en liste pakker (logisk).
    Returnerer ikke Oppgang-objekter ennå, da de må hydreres via bildeanalyse.
    """
    # 1. Konfigurer oppganger (Vi trenger IDer for pakkegenerering)
    oppgang_configs = []
    alle_pk_ids = []
    
    for i in range(1, n_oppganger + 1):
        oppgang_id = f"TEST-OPP-{i}"
        
        # Generer IDer for postkassene som VI VET skal være der
        pk_ids = [f"{oppgang_id}-PK-{j}" for j in range(1, n_postkasser_per_oppgang + 1)]
        alle_pk_ids.extend(pk_ids)
        
        config = {
            "id": oppgang_id,
            "expected_pk_ids": pk_ids
        }
        oppgang_configs.append(config)
        
    # 2. Generer pakker tilfeldig fordelt
    pakker = []
    for k in range(n_pakker):
        if not alle_pk_ids: break
        
        recipient_id = random.choice(alle_pk_ids)
        vol = random.choice([VolumKlasse.S, VolumKlasse.M, VolumKlasse.L])
        
        p = Pakke(id=f"TEST-PKG-{k}", volum_klasse=vol, mottaker_postkasse_id=recipient_id)
        pakker.append(p)
        
    return oppgang_configs, pakker

def kjør_simulering(navn: str, oppgang_configs: List[Dict], pakker: List[Pakke], stoy_faktor: float = 0.05, antall_bilder: int = 3) -> Dict[str, Any]:
    """
    Kjører en full end-to-end simulering for gitt config.
    Genererer bilder -> Analyserer -> Simulerer levering.
    """
    logger.info(f"Start simulering: {navn}")
    
    # Temp mappe for bilder
    base_dir = os.getcwd()
    temp_img_dir = os.path.join(base_dir, "data", "temp_test_bilder", navn)
    if os.path.exists(temp_img_dir):
        shutil.rmtree(temp_img_dir)
    os.makedirs(temp_img_dir)
    
    hydrated_oppganger = []
    
    # 1. VISJON FASE
    for conf in oppgang_configs:
        opp_id = conf["id"]
        img_paths = []
        
        # Generer bilder
        for j in range(antall_bilder):
            fname = os.path.join(temp_img_dir, f"{opp_id}_img{j}.png")
            # Random shift for realism
            sx = random.randint(-5, 5)
            sy = random.randint(-5, 5)
            try:
                vision.generer_test_bilde(fname, shift_x=sx, shift_y=sy, stoy_faktor=stoy_faktor)
                img_paths.append(fname)
            except Exception as e:
                logger.error(f"Feil ved bildegenerering: {e}")
                
        # Analyser
        # Merk: Vi bruker API-et som returnerer en liste dicts
        raw_data = vision.analyser_bilder_av_oppgang(img_paths, opp_id)
        
        # Bygg Oppgang objekt
        postkasser = []
        for item in raw_data:
            # Merk: ID konstruksjon her matcher det vi gjorde i generer_test_bilde/analyser_bilde
            # analyser_bilde returnerer "PK-1", "PK-2". 
            # Vi må prefixe med oppgang_id for å matche pakkenes mottaker ID.
            pk_local_id = item["postkasse_id"] # "PK-1"
            
            # ! VIKTIG: I generer_syntetiske_ruter laget vi IDs som "TEST-OPP-1-PK-1".
            # Vi må sikre at IDene matcher. 
            full_id = f"{opp_id}-{pk_local_id}"
            
            pk = Postkasse(
                id=full_id,
                oppgang_id=opp_id,
                kapasitet_klasse=item["kapasitet_klasse"],
                sist_verifisert=datetime.now()
            )
            postkasser.append(pk)
            
        hydrated_oppganger.append(Oppgang(id=opp_id, postkasser=postkasser))
        
    # 2. LEVERING FASE
    alle_postkasser = [pk for opp in hydrated_oppganger for pk in opp.postkasser]
    res = delivery.simuler_rute(pakker, alle_postkasser)
    
    # Beregn nøkkeltall
    total = res["antall_pakker"]
    direkte = res["direkte_i_postkasse"]
    hent = res["til_hentekontor"]
    
    andel_direkte = (direkte / total * 100) if total > 0 else 0
    
    return {
        "navn": navn,
        "stoy": stoy_faktor,
        "n_oppganger": len(oppgang_configs),
        "n_pakker": total,
        "direkte": direkte,
        "hentekontor": hent,
        "andel_direkte_pst": andel_direkte
    }
