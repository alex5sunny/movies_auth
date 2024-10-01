from typing import Optional

from db.Storage import Storage

storage: Optional[Storage] = None


async def get_storage() -> Storage:
    return storage
