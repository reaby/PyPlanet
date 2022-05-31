from peewee import *
from playhouse.migrate import migrate, SchemaMigrator
from ..models.player import Player


def upgrade(migrator: SchemaMigrator):
	allow_custom = BooleanField(default=1)

	migrate(
		migrator.add_column(Player._meta.db_table, 'allow_custom', allow_custom)
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Player._meta.db_table, 'allow_custom')
	)
