from typing import List, Dict, Any
from modules.datamodel import Postkasse, Pakke, KapasitetKlasse

def beslutning_levering(postkasse: Postkasse, pakke: Pakke) -> bool:
    """
    Avgjør om en pakke kan leveres i postkassen.
    
    Regel:
    Postkassens kapasitet (int verdi) >= Pakkens volum (int verdi).
    
    Args:
        postkasse: Mottaker-postkassen.
        pakke: Pakken som skal leveres.
        
    Returns:
        True hvis den får plass (direkte levering).
        False hvis den må til hentekontor.
    """
    if postkasse.kapasitet_klasse.value >= pakke.volum_klasse.value:
        return True
    return False

def simuler_rute(pakker: List[Pakke], postkasser: List[Postkasse]) -> Dict[str, Any]:
    """
    Simulerer levering av en liste pakker til tilgjengelige postkasser.
    Pakkene antas å ha en 'mottaker_postkasse_id' som matcher en av postkassene.
    
    Args:
        pakker: Liste med pakker.
        postkasser: Liste med alle kjente postkasser.
        
    Returns:
        Dict med statistikk og en detaljert logg over beslutninger.
    """
    # Lag oppslagsverk for postkasser for rask tilgang
    pk_map = {pk.id: pk for pk in postkasser}
    
    resultat = {
        "antall_pakker": len(pakker),
        "direkte_i_postkasse": 0,
        "til_hentekontor": 0,
        "logg": []
    }
    
    for p in pakker:
        mottaker_pk = pk_map.get(p.mottaker_postkasse_id)
        
        beslutning = {
            "pakke_id": p.id,
            "volum": p.volum_klasse.name,
            "destinasjon_pk": p.mottaker_postkasse_id,
            "utfall": "UKJENT_MOTTAKER",
            "pk_kapasitet": "N/A"
        }
        
        if mottaker_pk:
            beslutning["pk_kapasitet"] = mottaker_pk.kapasitet_klasse.name
            
            kan_levere = beslutning_levering(mottaker_pk, p)
            if kan_levere:
                resultat["direkte_i_postkasse"] += 1
                beslutning["utfall"] = "LEVERT_I_POSTKASSE"
            else:
                resultat["til_hentekontor"] += 1
                beslutning["utfall"] = "HENTEKONTOR"
        else:
            # Hvis vi ikke finner postkassen i systemet (skal ikke skje i simuleringen)
            resultat["til_hentekontor"] += 1 # Default fallback
            beslutning["utfall"] = "UKJENT_POSTKASSE"
            
        resultat["logg"].append(beslutning)
        
    return resultat
