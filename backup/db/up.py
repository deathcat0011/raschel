from peewee import *
from peewee.playhouse.migrate import migrate, SqliteMigrator

from backup.config import Config

db = SqliteDatabase('../backup.db')
migrator = SqliteMigrator()


db.create_tables([])


migrate(
    migrator.add_column('store', 'root_path', TextField(null=false, default=None)),
    migrator.add_column('store', '', TextField(null=false, default=None))
)



