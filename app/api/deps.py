from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_session
from app.models import User
from app.api.auth import SECRET_KEY, ALGORITHM  

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Dependency to extract and validate the JWT token from the Authorization header.
    Returns the current authenticated User if the token is valid.
    """
    token = credentials.credentials.strip()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        print(f"✅ Decoded JWT for user: {username}")
    except JWTError as e:
        print(f"❌ JWT decoding error: {e}")
        raise credentials_exception

    # Fetch user from the database
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        print(f"🔴 No user found for username: {username}")
        raise credentials_exception

    print(f"✅ Authenticated user: {user.username}")
    return user
