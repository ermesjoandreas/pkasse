import logging
import csv
import sys
from modules import simulation_utils
from tabulate import tabulate

# Config logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AutoTest")

def main():
    logger.info("Starter automatisert testing...")
    
    # Definer test-scenarioer
    scenarios = [
        {"navn": "Baseline (Lav støy)", "oppganger": 5, "pakker": 100, "stoy": 0.0, "bilder": 1},
        {"navn": "Realistisk (Litt støy)", "oppganger": 5, "pakker": 100, "stoy": 0.05, "bilder": 3},
        {"navn": "Vanskelig (Mye støy)", "oppganger": 5, "pakker": 100, "stoy": 0.15, "bilder": 3},
        {"navn": "Ekstrem (Kraftig støy)", "oppganger": 5, "pakker": 100, "stoy": 0.25, "bilder": 5}, # Tester om flere bilder kompenserer
    ]
    
    results = []
    
    for scen in scenarios:
        logger.info(f"Kjører scenario: {scen['navn']}")
        
        # 1. Generer data
        opp_conf, pakker = simulation_utils.generer_syntetiske_ruter(
            n_oppganger=scen["oppganger"],
            n_postkasser_per_oppgang=11, # Matcher visjon generator
            n_pakker=scen["pakker"]
        )
        
        # 2. Kjør simulering
        res = simulation_utils.kjør_simulering(
            navn=scen["navn"],
            oppgang_configs=opp_conf,
            pakker=pakker,
            stoy_faktor=scen["stoy"],
            antall_bilder=scen["bilder"]
        )
        
        results.append(res)
        
    # Skriv til CSV
    csv_file = "resultater.csv"
    keys = results[0].keys()
    with open(csv_file, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
        
    logger.info(f"Resultater lagret til {csv_file}")
    
    # Print tabell
    print("\n=== TEST RESULTATER ===")
    headers = ["Scenario", "Støy", "Oppganger", "Pakker", "Direkte", "Hentekontor", "% Direkte"]
    table_data = [[r["navn"], r["stoy"], r["n_oppganger"], r["n_pakker"], r["direkte"], r["hentekontor"], f"{r['andel_direkte_pst']:.1f}%"] for r in results]
    print(tabulate(table_data, headers=headers, tablefmt="github"))
    
if __name__ == "__main__":
    main()
