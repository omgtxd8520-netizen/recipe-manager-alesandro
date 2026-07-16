from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Review:
    """
    Documento de la colección 'reviews': la calificación (1-5) y el
    comentario de un usuario sobre una receta puntual. Se listan siempre
    de más reciente a más antigua y alimentan el rating promedio que se
    muestra junto a cada receta en la API.
    """
    recipe_id: str
    user_id: str
    rating: int  # escala de 1 a 5
    comment: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str | None = None

    def to_dict(self) -> dict:
        """Convierte la reseña a dict serializable para MongoDB."""
        return {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        """Crea una instancia de Review desde un diccionario de MongoDB."""
        _id = str(data.get("_id")) if "_id" in data else data.get("id")
        c_at = data.get("created_at")
        if isinstance(c_at, str):
            try:
                c_at = datetime.fromisoformat(c_at)
            except Exception:
                c_at = datetime.now(timezone.utc)
        elif not isinstance(c_at, datetime):
            c_at = datetime.now(timezone.utc)

        return cls(
            recipe_id=data.get("recipe_id", ""),
            user_id=data.get("user_id", ""),
            rating=data.get("rating", 5),
            comment=data.get("comment", ""),
            created_at=c_at,
            id=_id
        )
