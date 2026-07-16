from dataclasses import dataclass


@dataclass
class User:
    """
    Documento de la colección 'users'.
    Representa a una persona del sistema: autor de recetas y/o autor
    de reseñas. El campo role distingue tres perfiles:

    - "chef"   : publica recetas
    - "foodie" : consume y califica recetas de otros
    - "admin"  : gestión general de la plataforma

    Un mismo usuario puede publicar recetas y también dejar reseñas
    en recetas de otros — el rol es orientativo para la UI, no una
    restricción dura de permisos a nivel de datos.

    Ejemplo
    -------
    chef = User(username="Jamie Oliver", email="jamie@foodies.com", role="chef")
    chef_id = dao.create_user(chef)
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
