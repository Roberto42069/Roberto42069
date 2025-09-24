
from dataclasses import dataclass
import os

@dataclass
class UserIdentity:
    full_name: str
    aliases: list[str]
    birthplace: str
    parents_origin: str
    driver_license: str

def load_identity_from_env() -> UserIdentity:
    aliases = os.getenv("USER_ALIASES", "")
    return UserIdentity(
        full_name=os.getenv("USER_FULL_NAME", "Roberto Villarreal Martinez"),
        aliases=[a.strip() for a in aliases.split(",") if a.strip()],
        birthplace=os.getenv("USER_BIRTHPLACE", "Houston, TX"),
        parents_origin=os.getenv("USER_PARENTS_ORIGIN", "Monterrey, Nuevo León, Mexico"),
        driver_license=os.getenv("USER_DRIVER_LICENSE", "")
    )

# fallback inline (use only if .env not found)
INLINE_IDENTITY = UserIdentity(
    full_name="Roberto Villarreal Martinez",
    aliases=["Betin"],
    birthplace="Houston, TX",
    parents_origin="Monterrey, Nuevo León, Mexico",
    driver_license="42016069"
)

if __name__ == "__main__":
    identity = load_identity_from_env()
    print(identity)
