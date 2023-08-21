'''
/app/models/book.py
'''

from odmantic import AIOEngine, Model


class BookModel(Model):
    '''Book Model 객체'''
    keyword: str
    publisher: str
    price: int
    image: str

    class Config:
        collection = "books"