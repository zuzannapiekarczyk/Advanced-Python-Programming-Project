import datetime
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import sympy
from datetime import datetime
import cv2
from starlette.responses import StreamingResponse
import numpy
import io

fake_users_db = {
    "patrykkluska": {
        "username": "patrykkluska",
        "full_name": "Patryk Kluska",
        "email": "patrykkluska@gmail.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "helenapyra": {
        "username": "helenapyra",
        "full_name": "Helena Pyra",
        "email": "helenapyra@gmail.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()

# sprawdzenie, czy podana liczba jest pierwsza


@app.get("/prime/{number}")
async def czypierwsza(number: int):
    pierwsza = sympy.isprime(number)
    return pierwsza

# autoryzacja


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Błędne dane logowania",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Nieaktywne konto")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Błędna nazwa użytkownika lub hasło")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Błędna nazwa użytkownika lub hasło")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/time")
async def time_return(current_user: User = Depends(get_current_active_user)):
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    return time

# konwersja obrazka


@app.post("/picture/invert")
async def invert(file: UploadFile):
    pic_before = await file.read()
    pic_array = numpy.frombuffer(pic_before, numpy.uint8)
    pic_after = cv2.imdecode(pic_array, cv2.IMREAD_COLOR)
    pic_final = cv2.bitwise_not(pic_after)
    retval, buffer = cv2.imencode('.jpg', pic_final)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpg")
