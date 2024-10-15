import typer
from src.models.user import User
from src.db.postgres import get_session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
import asyncio

app = typer.Typer()

@app.command()
def create_superuser(username: str,
                     password: str,
                     first_name: str = "",
                     last_name: str = ""):
    asyncio.run(_create_superuser(username, password, first_name, last_name))

async def _create_superuser(username: str,
                            password: str,
                            first_name: str,
                            last_name: str):
    async with get_session() as session:
        try:
            hashed_password = generate_password_hash(password)
            superuser = User(
                login=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                is_superuser=True
            )
            session.add(superuser)
            await session.commit()
            typer.echo(f"Superuser {username} created successfully!")
        except SQLAlchemyError as e:
            await session.rollback()
            typer.echo(f"Error creating superuser: {str(e)}")
        finally:
            await session.close()

if __name__ == "__main__":
    app()
