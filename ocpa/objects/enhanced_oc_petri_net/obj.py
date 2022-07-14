from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Any
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet


@dataclass
class EnhancedObjectCentricPetriNet(object):
    ocpn: ObjectCentricPetriNet
    behavior: List[str]
    diagnostics: Dict[str, Any]
