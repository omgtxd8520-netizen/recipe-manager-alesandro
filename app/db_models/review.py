from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Review:
    """
    Documento de la colección 'reviews'.
    Representa la valoración de un usuario sobre una receta puntual:
    una calificación de 1 a 5 estrellas más un comentario libre.

    Las reseñas se listan siempre ordenadas por created_at descendente
    (ver RecipeManagerDAO.list_reviews_by_recipe) y alimentan el cálculo
    de rating promedio que se expone junto a cada receta en la API.

    Ejemplo
    -------
    reseña = Review(
        recipe_id=receta_id,
        user_id=usuario_id,
        rating=5,
        comment="El equilibrio perfecto de acidez y frescura.",
    )
    reseña_id = dao.create_review(reseña)
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
