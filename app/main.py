from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book = BookModel(keyword="파이썬", publisher="BJPO", price=12000, image='me.png')  #test
    # await mongodb.engine.save(book)  # DB에 저장
    return templates.TemplateResponse(
        "./index.html",
        {
            "request": request,
            "title": "Book Finder"
        }
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    # 1. 쿼리에서 검색어(keyword) 추출
    keyword = q  # query에서 keyword 추출
    if not keyword:
        # keyword가 없으면, 사용자에게 검색을 요구
        context = {"request": request, "title": "Book Finder"}
        return templates.TemplateResponse("index.html", context=context)
    if await mongodb.engine.find_one(BookModel, BookModel.keyword == keyword):
        # keyword에 대해 수집된 데이터가 DB에 존재하면, 해당 데이터를 사용자에게 보여줌
        books = await mongodb.engine.find(BookModel, BookModel.keyword == keyword)
        context = {
            "request": request,
            "keyword": keyword,
            "books": books
        }
        return templates.TemplateResponse("/index.html", context=context)

    # 2. 데이터수집기로 해당 검색어 데이터를 수집
    naver_book_scraper = NaverBookScraper()  # 수집지 인스턴스
    books = await naver_book_scraper.search(keyword, 10)  # 데이터를 수집
    book_models = []
    for book in books:  # 수집된 각 데이터에 대해 DB에 들어갈 모델 인스턴스를 찍는다.
        book_model = BookModel(
            keyword = keyword,
            publisher = book["publisher"],
            price = book["discount"],
            image = book["image"],
        )
        book_models.append(book_model)

    # 3. DB에 수집된 데이터를 저장
    await mongodb.engine.save_all(book_models)  # 각 모델 인스턴스를 DB에 저장

    return templates.TemplateResponse(
        "./index.html",
        {
            "request": request,
            "title": "Book Search Engine"
        },
    )


@app.on_event("startup")
def on_app_start():
    '''before app starts'''
    mongodb.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    '''atfer app shutdown'''
    mongodb.close()