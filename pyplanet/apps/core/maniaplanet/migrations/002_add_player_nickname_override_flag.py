from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.player import Player


def upgrade(migrator: SchemaMigrator):
	nickname_override = BooleanField(default=False, null=False)

	migrate(
		migrator.add_column(Player._meta.db_table, 'nickname_override', nickname_override)
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Player._meta.db_table, 'nickname_override')
	)
