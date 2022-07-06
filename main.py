from fastapi import FastAPI, Response, status, Body, Header, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Dict, Union

VALIDATE_TOKEN = False


app = FastAPI()
db = { "books": [{"id": 1, "title": "Dom Quixote", "author": "Miguel de Cervantes"}, 
                 {"id": 2, "title": "Guerra e Paz", "author": "Liev Tolstói"},
                 {"id": 3, "title": "Do seu primeiro milhão a zero reais", "author": "William Mingardi"}],
       "users": [{"id": 1, "name": "Amendoa", "roles": ["admin", "author"], "password" : "admin", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"},
                 {"id": 2, "name": "William", "roles": [], "password" : "user", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFtZW5kb2EiLCJpYXQiOjE1MTYyMzkwMjJ9.KZ-TodclOU9czUULni7iLwIVcYwSnA8oeSoK5AFBhWE"}]}

class Book(BaseModel):
    title: str
    author: str


def validate_token(x_token: Union[str, None] = Header(default=None)) -> Dict:
    if not VALIDATE_TOKEN:
        return {}

    user = next((item for item in db["users"] if item["token"] == x_token), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Token missing or invalid")

    return user


@app.get("/books", tags=["Book"])
def index():
    return db["books"]


@app.get("/books/{id}", tags=["Book"])
def show(id: int):
    book = next((item for item in db["books"] if item["id"] == id), None)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED, tags=["Book"])
def create(response: Response, book: Book = Body()):
    new_index = db["books"][-1].get("id", 0) + 1 if db["books"] else 1
    new_book = { "id": new_index, **book.dict()}
    db["books"].append(new_book)
    return JSONResponse(content=new_book, headers={"location" : f"/books/{new_index}"})


@app.put("/books/{id}", tags=["Book"])
def update(id: int, update_book: Book = Body()):
    book = next((item for item in db["books"] if item["id"] == id), None)
    
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    book["title"] = update_book.title
    book["author"] = update_book.author
    return book



@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, tags=["Book"])
def delete(id: int, user: Dict = Depends(validate_token)):
    if VALIDATE_TOKEN and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The client does not have access rights to the content")


    book = next((item for item in db["books"] if item["id"] == id), None)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    db["books"] = list(filter(lambda item: item["id"] != id, db["books"]))



class Login(BaseModel):
    user: str
    password: str

@app.post("/login", status_code=status.HTTP_200_OK, tags=["Authorization"])
def login(login: Login = Body()):
    user = next((item for item in db["users"] if item["name"] == login.user), None)

    if not user or user["password"] != login.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User missing or wrong password")

    return {"token": user["token"]}