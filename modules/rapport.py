from typing import Dict, Any
from tabulate import tabulate

def rapport(simuleringsresultat: Dict[str, Any]) -> None:
    """
    Genererer og printer en rapport basert på simuleringsresultatet.
    
    Args:
        simuleringsresultat: Output fra simuler_rute funksjonen.
    """
    print("\n" + "="*50)
    print("LEVERINGSRAPPORT")
    print("="*50)
    
    total = simuleringsresultat["antall_pakker"]
    direkte = simuleringsresultat["direkte_i_postkasse"]
    hent = simuleringsresultat["til_hentekontor"]
    
    # Summary
    print(f"Totalt antall pakker: {total}")
    if total > 0:
        print(f"Levert i postkasse:   {direkte} ({direkte/total*100:.1f}%)")
        print(f"Sendt til hentekontor: {hent} ({hent/total*100:.1f}%)")
    else:
        print("Ingen pakker behandlet.")
        
    print("\nDetaljert Logg (Siste 10 transaksjoner):")
    
    logg_data = simuleringsresultat["logg"]
    # Vis bare de siste 10 for å ikke spamme konsollen, men i ekte system ville vi logget alt til fil
    sample_logg = logg_data[:10] if len(logg_data) <= 10 else logg_data[:10] 
    
    tabell_data = []
    for rad in sample_logg:
        tabell_data.append([
            rad["pakke_id"],
            rad["destinasjon_pk"],
            rad["volum"],
            rad["pk_kapasitet"],
            rad["utfall"]
        ])
        
    headers = ["Pakke ID", "Postkasse ID", "Pakke Volum", "PK Kapasitet", "Beslutning"]
    print(tabulate(tabell_data, headers=headers, tablefmt="simple"))
    
    if len(logg_data) > 10:
        print(f"... og {len(logg_data) - 10} flere.")
    print("="*50 + "\n")
