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



