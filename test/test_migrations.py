"""test_migrations.py

Exercises every Alembic migration by running a full round-trip against a
throwaway SQLite database: base -> head -> base -> head. This verifies that
each revision's upgrade() and downgrade() applies cleanly and is reversible,
and covers the alembic env.py online-migration path.
"""

import io
import os
import sys
import tempfile
import unittest
import pathlib
from contextlib import redirect_stdout

import alembic.command
import alembic.config
import alembic.script
import sqlalchemy as sa

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class MigrationsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmp.close()
        db_folder = pathlib.Path(os.path.dirname(synack.__file__)) / 'db'
        self.config = alembic.config.Config()
        self.config.set_main_option('script_location', str(db_folder / 'alembic'))
        self.config.set_main_option('version_locations',
                                    str(db_folder / 'alembic/versions'))
        self.config.set_main_option('path_separator', 'os')
        self.config.set_main_option('sqlalchemy.url',
                                    f'sqlite:///{self.tmp.name}')

    def _current_revision(self):
        engine = sa.create_engine(f'sqlite:///{self.tmp.name}')
        with engine.connect() as conn:
            row = conn.execute(
                sa.text('SELECT version_num FROM alembic_version')).fetchone()
        return row[0] if row else None

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_migration_round_trip(self):
        """Every migration should upgrade and downgrade cleanly and be reversible"""
        script = alembic.script.ScriptDirectory.from_config(self.config)
        head = script.get_current_head()

        # base -> head applies every upgrade()
        alembic.command.upgrade(self.config, 'head')
        self.assertEqual(self._current_revision(), head)

        # 'config' table exists with the widened otp_secret column
        engine = sa.create_engine(f'sqlite:///{self.tmp.name}')
        cols = {c['name']: c for c in sa.inspect(engine).get_columns('config')}
        self.assertIn('otp_secret', cols)
        self.assertIn('duo_akey', cols)
        url_constraints = {c['name']: c for c in sa.inspect(engine).get_unique_constraints('urls')}
        self.assertIn('uq_url', url_constraints)
        self.assertEqual(['ip', 'url'], url_constraints['uq_url']['column_names'])

        # head -> base applies every downgrade()
        alembic.command.downgrade(self.config, 'base')
        self.assertIsNone(self._current_revision())

        # base -> head again to confirm reversibility
        alembic.command.upgrade(self.config, 'head')
        self.assertEqual(self._current_revision(), head)

    def test_unique_url_migration_dedupes_existing_rows(self):
        """The URL uniqueness migration should clean duplicates before constraining"""
        alembic.command.upgrade(self.config, 'e1b2c3d4f5a6')
        engine = sa.create_engine(f'sqlite:///{self.tmp.name}')
        with engine.begin() as conn:
            conn.execute(sa.text(
                "INSERT INTO urls (ip, url, screenshot_url) VALUES "
                "(1, 'https://example.com', 'one'), "
                "(1, 'https://example.com', 'two'), "
                "(1, 'https://other.example.com', 'three')"
            ))
        alembic.command.upgrade(self.config, 'head')
        with engine.connect() as conn:
            duplicate_count = conn.execute(sa.text(
                "SELECT COUNT(*) FROM urls WHERE ip = 1 AND url = 'https://example.com'"
            )).scalar_one()
            total_count = conn.execute(sa.text("SELECT COUNT(*) FROM urls")).scalar_one()
        self.assertEqual(1, duplicate_count)
        self.assertEqual(2, total_count)

    def test_offline_sql_generation(self):
        """Offline (--sql) mode should emit SQL via run_migrations_offline

        Scoped to the initial revision: later migrations use SQLite batch
        operations that require a live connection for table reflection and
        cannot run in --sql mode. Upgrading to the initial revision still
        drives run_migrations_offline() and emits CREATE TABLE DDL.
        """
        script = alembic.script.ScriptDirectory.from_config(self.config)
        base_rev = script.get_base()
        buf = io.StringIO()
        with redirect_stdout(buf):
            alembic.command.upgrade(self.config, base_rev, sql=True)
        output = buf.getvalue()
        self.assertIn('CREATE TABLE', output.upper())


if __name__ == '__main__':
    unittest.main()
