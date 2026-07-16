from dataclasses import dataclass


@dataclass
class User:
    """
    Documento de la colección 'users'.
    Representa un usuario del sistema (autor de recetas y reseñas).
    """
    username: str
    email: str
    role: str = "foodie"  # chef | foodie | admin
    id: str | None = None

    def to_dict(self) -> dict:
        """Convierte el usuario a dict serializable para MongoDB."""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Crea una instancia de User desde un diccionario de MongoDB."""
        _id = str(data.get("_id")) if "_id" in data else data.get("id")
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            role=data.get("role", "foodie"),
            id=_id
        )
