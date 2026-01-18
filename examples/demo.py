import logging
import random
import os
from typing import List

# Import from MVP modules
from modules.datamodel import Postkasse, Pakke, Oppgang, VolumKlasse, KapasitetKlasse
import modules.bildeanalyse as vision
import modules.leveringslogikk as delivery
import modules.rapport as reporting

logger = logging.getLogger("MVPDemo")

def run_demo():
    logger.info("Starting MVP Demo Scenario")
    
    # Paths
    # Ensure we write to data/test_bilder relative to where main.py runs
    base_dir = os.getcwd()
    img_dir = os.path.join(base_dir, "data", "test_bilder")
    
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        logger.info(f"Created directory: {img_dir}")
        
    # Config
    ANTALL_OPPGANGER = 3 # Keep it short for main demo
    PAKKE_TOTAL = 20
    
    alle_oppganger = []
    
    # 1. Vision Phase
    logger.info("--- Phase 1: Image Acquisition & Analysis ---")
    
    for i in range(1, ANTALL_OPPGANGER + 1):
        oppgang_id = f"OPP-{i}"
        
        # 1.1 Generate Synthetic Images
        img_paths = []
        for j in range(2): # 2 images per entrance
            fname = os.path.join(img_dir, f"{oppgang_id}_img{j}.png")
            # Random noise
            vision.generer_test_bilde(fname, shift_x=random.randint(-2,2), stoy_faktor=0.05)
            img_paths.append(fname)
            
        # 1.2 Analyze
        analysis_result = vision.analyser_bilder_av_oppgang(img_paths, oppgang_id)
        
        # 1.3 Hydrate Models
        pk_list = []
        for item in analysis_result:
            p = Postkasse(
                id=f"{item['oppgang_id']}-{item['postkasse_id']}",
                oppgang_id=item['oppgang_id'],
                kapasitet_klasse=item['kapasitet_klasse'],
                sist_verifisert=datetime.now()
            )
            pk_list.append(p)
            
        alle_oppganger.append(Oppgang(id=oppgang_id, postkasser=pk_list))
        logger.info(f"Processed {oppgang_id}: {len(pk_list)} mailboxes identified.")
        
    all_mailboxes = [pk for opp in alle_oppganger for pk in opp.postkasser]
    
    # 2. Package Generation
    logger.info("--- Phase 2: Package Generation ---")
    packages = []
    for k in range(PAKKE_TOTAL):
        if not all_mailboxes: break
        
        # Random valid recipient
        recipient = random.choice(all_mailboxes)
        
        # Random size
        vol = random.choice([VolumKlasse.S, VolumKlasse.M, VolumKlasse.L])
        
        pkg = Pakke(
            id=f"PKG-{k+1:03d}",
            volum_klasse=vol,
            mottaker_postkasse_id=recipient.id
        )
        packages.append(pkg)
        
    logger.info(f"Generated {len(packages)} packages.")
        
    # 3. Delivery Simulation
    logger.info("--- Phase 3: Delivery Simulation ---")
    results = delivery.simuler_rute(packages, all_mailboxes)
    
    # 4. Reporting
    logger.info("--- Phase 4: Reporting ---")
    reporting.rapport(results)
    
    logger.info("MVP Demo Finished Successfully.")
    
from datetime import datetime # Late import fix for line 48
