from fastapi import FastAPI, Depends, HTTPException
from auth import hash_password,verify_password,create_access_token,SECRET_KEY,ALGORITHM
from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine,Base,get_db
from models import User
import schemas,crud
from datetime import datetime
from jose import JWTError,jwt
from fastapi.security import OAuth2PasswordBearer
from execution import execute_code

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for now allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
Base.metadata.create_all(bind=engine)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    return user

@app.get("/")
def read_root(db:Session=Depends(get_db)):
  return {"message":"Database connected successfully"}

@app.post("/users",response_model=schemas.UserResponse)
def create_users(user:schemas.UserCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
  return crud.create_user(db,user)

@app.get("/users",response_model=list[schemas.UserResponse])
def read_users(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
  return crud.get_users(db)

@app.get("/users/{user_id}",response_model=schemas.UserResponse)
def read_user(user_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
  db_user=crud.get_user(db,user_id)
  if not db_user:
    raise HTTPException(status_code=404,detail="User not found")
  return db_user

@app.put("/users/{user_id}",response_model=schemas.UserResponse)
def update_user(user_id:int,user:schemas.UserCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
  db_user=crud.update_user(db,user_id,user)
  if not db_user:
    raise HTTPException(status_code=404,detail="User not found")
  return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
  db_user=crud.delete_user(db,user_id)
  if not db_user:
    raise HTTPException(status_code=404,detail="User not found")
  return {"message":"User deleted successfully"}

@app.post("/register")
def register_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
  existing_user=db.query(User).filter(User.email==user.email).first()

  if existing_user:
    raise HTTPException(status_code=400,detail="Email already registerd")
  new_user=User(
    name=user.name,
    email=user.email,
    password=hash_password(user.password)
  )

  db.add(new_user)
  db.commit()
  db.refresh(new_user)

  return {
    "message":"User registered successfully",
    "user":{
      "id":new_user.id,
      "name":new_user.name,
      "email":new_user.email
    }
  }

@app.post("/login")
def login_user(user:schemas.UserLogin,db:Session=Depends(get_db)):
  existing_user=db.query(User).filter(User.email==user.email).first()

  if not existing_user:
    raise HTTPException(status_code=404,detail="User not found")
  
  if not verify_password(user.password,existing_user.password):
    raise HTTPException(status_code=401,detail="Invalid password")
  
  access_token = create_access_token(data={"sub": existing_user.email})

  return{
    "message":"Login successful",
    "access_token": access_token,
    "token_type": "bearer",
    "user":{
      "id":existing_user.id,
      "name":existing_user.name,
      "email":existing_user.email
    }
  }

@app.get("/profile")
def get_profile(current_user:User = Depends(get_current_user)):
    return {
        "message": "Profile fetched successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    }

@app.delete("/profile")
def delete_profile(
   db:Session = Depends(get_db),
   current_user:User= Depends(get_current_user)
):
   db.delete(current_user)
   db.commit()

   return {"message":"Account deleted successfully"}

@app.put("/profile")
def update_profile(
   user:schemas.UserUpdate,
   db:Session=Depends(get_db),
   current_user:User=Depends(get_current_user)
):
   current_user.name=user.name
   current_user.email=user.email
   current_user.password=hash_password(user.password)

   db.commit()
   db.refresh(current_user)

   return {
      "message":"Profile updates successfully",
      "user":{
         "id":current_user.id,
         "name":current_user.name,
         "email":current_user.email
      }
   }




@app.post("/run")
def run_code(payload: dict, current_user: User = Depends(get_current_user)):
    code = payload.get("code", "")
    result = execute_code(code)
    return result

# @app.post("/run")
# def run_code(
#     payload: dict,
#     current_user: User = Depends(get_current_user)
# ):
#     code = payload.get("code", "")

#     try:
#         result = execute_code(code)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
