"""
Modèles de données pour les slides et sections
"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class Slide:
    """Représente une slide avec ses éléments"""
    slide_type: str  # 'title', 'content', 'image'
    number: Optional[int] = None
    title: str = ""
    subtitle: str = ""
    content: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    has_annexes: bool = True
    image_url: str = ""
    image_caption: str = ""
    
    @property
    def max_view(self) -> int:
        """Retourne le niveau de navigation max (0=main, 1=+details, 2=+questions)"""
        if not self.has_annexes or not self.details:
            return 0
        elif not self.questions:
            return 1
        return 2
    
    def __repr__(self):
        return f"<Slide {self.slide_type} #{self.number}: {self.title}>"


@dataclass
class Section:
    """Représente une section pour l'extraction des détails"""
    title: str
    level: int  # 1 = #, 2 = ##, etc.
    details: List[Dict[str, str]] = field(default_factory=list)
    
    def __repr__(self):
        return f"<Section {self.level}: {self.title} ({len(self.details)} paragraphes)>"


@dataclass
class Presentation:
    """Représente une présentation complète"""
    metadata: Dict[str, str] = field(default_factory=dict)
    slides: List[Slide] = field(default_factory=list)
    
    @property
    def title(self) -> str:
        return self.metadata.get('title', 'Présentation')
    
    @property
    def total_slides(self) -> int:
        return len(self.slides)
