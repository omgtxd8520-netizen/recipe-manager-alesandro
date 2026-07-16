from dataclasses import dataclass, field


@dataclass
class Recipe:
    """
    Documento de la colección 'recipes'.
    Representa una receta en la base de datos con tipado seguro y métodos de mapeo.
    """
    title: str
    ingredients: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    servings: int = 1
    id: str | None = None

    def to_dict(self) -> dict:
        """Convierte la receta a dict serializable para MongoDB."""
        return {
            "title": self.title,
            "ingredients": self.ingredients,
            "tags": self.tags,
            "servings": self.servings
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Crea una instancia de Recipe desde un diccionario de MongoDB."""
        _id = str(data.get("_id")) if "_id" in data else data.get("id")
        return cls(
            title=data.get("title", ""),
            ingredients=data.get("ingredients", []),
            tags=data.get("tags", []),
            servings=data.get("servings", 1),
            id=_id
        )
