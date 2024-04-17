import sqlite3

import pytest


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author
    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"


def test_create_tables(db, Author, Book):
    db.create(Author)
    db.create(Book)
    assert (
        Author._get_create_sql()
        == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    )
    assert (
        Book._get_create_sql()
        == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"
    )

    for table in ("author", "book"):
        assert table in db.tables


def test_create_author_instance(db, Author):
    db.create(Author)
    fidy = Author(name="50 Cent", age=50)
    assert fidy.name == "50 Cent"
    assert fidy.age == 50
    assert fidy.id is None


def test_save_author_instances(db, Author):
    db.create(Author)
    john = Author(name="Lebron", age=23)
    db.save(john)
    assert john._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [23, "Lebron"],
    )
    assert john.id == 1
    man = Author(name="John Cena", age=33)
    db.save(man)
    assert man.id == 2

    wick = Author(name="Wick", age=40)
    db.save(wick)
    assert wick.id == 3

    rooney = Author(name="Wayne", age=30)
    db.save(rooney)
    assert rooney.id == 4


def test_query_all_authors(db, Author):
    db.create(Author)
    david = Author(name="David", age=33)
    ryan = Author(name="Ryan", age=24)
    db.save(david)
    db.save(ryan)
    authors = db.all(Author)
    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"],
    )
    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {24, 33}
    assert {a.name for a in authors} == {"David", "Ryan"}


def test_get_author(db, Author):
    db.create(Author)
    david = Author(name="David", age=22)
    db.save(david)
    david_from_db = db.get(Author, id=1)
    assert Author._get_select_where_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id = ?;",
        ["id", "age", "name"],
        [1],
    )
    assert type(david_from_db) == Author
    assert david_from_db.age == 22
    assert david_from_db.name == "David"
    assert david_from_db.id == 1


def test_get_book(db, Author, Book):
    db.create(Author)
    db.create(Book)
    david = Author(name="David", age=22)
    messi = Author(name="Messi", age=33)
    book = Book(title="Hello World", published=False, author=david)
    book1 = Book(title="Trivela Book", published=True, author=messi)
    db.save(david)
    db.save(messi)
    db.save(book)
    db.save(book1)
    book_from_db = db.get(Book, 2)
    assert book_from_db.title == "Trivela Book"
    assert book_from_db.author.name == "Messi"
    assert book_from_db.author.id == 2


def test_query_all_books(db, Author, Book):
    db.create(Author)
    db.create(Book)
    david = Author(name="David", age=22)
    messi = Author(name="Messi", age=33)
    book = Book(title="Hello World", published=False, author=david)
    book1 = Book(title="Trivela Book", published=True, author=messi)
    db.save(david)
    db.save(messi)
    db.save(book)
    db.save(book1)

    books = db.all(Book)

    assert len(books) == 2
    assert books[1].author.name == "Messi"


def test_update_author(db, Author):
    db.create(Author)
    david = Author(name="David", age=20)
    db.save(david)

    david.age = 43
    david.name = "Rio"
    db.update(david)
    david_from_db = db.get(Author, id=david.id)
    assert david_from_db.age == 43
    assert david_from_db.name == "Rio"


def test_delete_author(db, Author):
    db.create(Author)
    david = Author(name="David", age=23)
    db.save(david)
    db.delete(Author, id=1)
    with pytest.raises(Exception):
        db.get(Author, 1)
