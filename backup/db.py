import sqlite3
import atexit
import uuid

import peewee as pw

DB_URL = "backup.db"
DATABASE = pw.SqliteDatabase(DB_URL)


class BaseModel(pw.Model):
    class Meta:
        database = DATABASE

class Store(BaseModel):
    _id = pw.PrimaryKeyField()
    # file_filters = pw.
    root_path = pw.TextField(null=False, unique=True, ),


# class DbConnection:
#     def __init__(self) -> None:
#         sqlite3.connect(DB_URL)
#         atexit.register(self.cleanup())

#     def push_file():
#         pass

#     def cleanup(self):
#         self.close()

#     def close(self):
#         pass
