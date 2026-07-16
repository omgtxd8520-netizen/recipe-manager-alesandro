from dataclasses import dataclass, field


@dataclass
class Recipe:
    """
    Documento de la colección 'recipes'. author_id vincula la receta con
    el usuario que la publicó (la API resuelve ese id contra 'users'
    para no duplicar el nombre del autor en cada receta).
    """
    title: str
    ingredients: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    servings: int = 1
    author_id: str | None = None
    id: str | None = None

    def to_dict(self) -> dict:
        """Convierte la receta a dict serializable para MongoDB."""
        d = {
            "title": self.title,
            "ingredients": self.ingredients,
            "tags": self.tags,
            "servings": self.servings
        }
        if self.author_id:
            d["author_id"] = self.author_id
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Crea una instancia de Recipe desde un diccionario de MongoDB."""
        _id = str(data.get("_id")) if "_id" in data else data.get("id")
        return cls(
            title=data.get("title", ""),
            ingredients=data.get("ingredients", []),
            tags=data.get("tags", []),
            servings=data.get("servings", 1),
            author_id=data.get("author_id"),
            id=_id
        )
