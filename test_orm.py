import sqlite3


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
