from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
from datetime import datetime

class VolumKlasse(Enum):
    """
    Klassifisering av pakkestørrelse.
    """
    S = 1 # Small
    M = 2 # Medium
    L = 3 # Large

class KapasitetKlasse(Enum):
    """
    Klassifisering av postkassekapasitet.
    Verdien indikerer den største pakkestørrelsen som får plass.
    """
    LITEN = 1    # Passer kun S
    STANDARD = 2 # Passer S og M
    STOR = 3     # Passer S, M og L

@dataclass
class Postkasse:
    """
    Representerer en fysisk postkasse i en oppgang.
    """
    id: str  # Unik ID, f.eks. "PK-1"
    oppgang_id: str # ID til oppgangen postkassen tilhører
    kapasitet_klasse: KapasitetKlasse # Estimert kapasitet
    sist_verifisert: datetime # Tidsstempel for når bildeanalysen ble kjørt

@dataclass
class Pakke:
    """
    Representerer en pakke som skal leveres.
    """
    id: str # Sporingsnummer e.l.
    volum_klasse: VolumKlasse # Størrelse på pakken
    mottaker_postkasse_id: str # ID til postkassen den skal til

@dataclass
class Oppgang:
    """
    Representerer en oppgang (inngangsparti) med flere postkasser.
    """
    id: str
    postkasser: List[Postkasse]
