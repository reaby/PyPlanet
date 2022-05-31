from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.player import Player

def upgrade(migrator: SchemaMigrator):
	uplay_nickname = CharField(max_length=100, default="", null=True)

	migrate(
		migrator.add_column(Player._meta.db_table, 'uplay_nickname', uplay_nickname)
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Player._meta.db_table, 'uplay_nickname')
	)
