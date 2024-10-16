from fastapi import APIRouter, Depends, HTTPException
from functools import wraps
from inspect import signature, Parameter
from http import HTTPStatus
from typing import Callable
from models.user import User
from services.users import get_current_user

def superuser_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user: User = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated"
            )
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return await func(*args, **kwargs)

    original_sig = signature(func)
    parameters = list(original_sig.parameters.values())

    if 'current_user' not in original_sig.parameters:
        current_user_param = Parameter(
            'current_user',
            kind=Parameter.KEYWORD_ONLY,
            annotation=User,
            default=Depends(get_current_user)
        )
        parameters.append(current_user_param)
        wrapper.__signature__ = original_sig.replace(parameters=parameters)
    else:
        wrapper.__signature__ = original_sig

    return wrapper