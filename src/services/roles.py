from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.role import Role
from models.user import User
from db.postgres import get_session


@dataclass
class RoleService:
    pg_session: AsyncSession

    async def create_role(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Role:
        existing_role = await self.pg_session.execute(
            select(Role).filter_by(name=name)
        )
        if existing_role.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists."
            )

        new_role = Role(name=name, description=description)
        self.pg_session.add(new_role)
        await self.pg_session.commit()
        await self.pg_session.refresh(new_role)
        return new_role

    async def get_role(self, role_id: UUID) -> Optional[Role]:
        result = await self.pg_session.execute(select(Role).filter(Role.id == role_id))
        return result.scalars().first()

    async def get_roles(self, offset: int = 0, limit: int = 100) -> List[Role]:
        result = await self.pg_session.execute(select(Role).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def update_role(
        self,
        role_id: UUID,
        name: str,
        description: Optional[str] = None
    ) -> Role:
        db_role = await self.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found."
            )

        db_role.name = name
        db_role.description = description
        await self.pg_session.commit()
        await self.pg_session.refresh(db_role)
        return db_role

    async def delete_role(self, role_id: UUID) -> None:
        db_role = await self.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found."
            )

        await self.pg_session.delete(db_role)
        await self.pg_session.commit()

    async def assign_role_to_user(self, login: str, role_name: str) -> User:
        user = await self.get_user(login)
        role = await self.get_role_by_name(role_name)
        if not user or not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or Role not found."
            )

        if role in user.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{login}' already has role '{role_name}'."
            )

        user.roles.append(role)
        await self.pg_session.commit()
        await self.pg_session.refresh(user)
        return user

    async def remove_role_from_user(self, login: str, role_name: str) -> User:
        user = await self.get_user(login)
        role = await self.get_role_by_name(role_name)
        if not user or not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or Role not found."
            )

        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' not found for user '{login}'."
            )

        user.roles.remove(role)
        await self.pg_session.commit()
        await self.pg_session.refresh(user)
        return user

    async def get_user(self, login: str) -> Optional[User]:
        result = await self.pg_session.execute(select(User).filter_by(login=login).options())
        return result.scalars().first()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        result = await self.pg_session.execute(select(Role).filter_by(name=name))
        return result.scalars().first()


async def get_role_service(
    pg_session: AsyncSession = Depends(get_session)
) -> RoleService:
    return RoleService(pg_session)
