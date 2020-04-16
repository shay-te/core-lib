class Alembic(object):

    def __init__(self, db_url: str, alembic_ini_path: str, version_folder_path: str, version_file_name: str = ".migration_ver"):
        self.db_url = db_url
        self.alembic_ini_path = alembic_ini_path

        if not os.path.isdir(version_folder_path):
            raise ValueError("version_folder_path dose not exists")

        if not version_file_name:
            raise ValueError("version_file_name cannot be None")

        self.version_folder_path = version_folder_path
        self.version_file_path = os.path.join(version_folder_path, version_file_name)
        if not os.path.isfile(self.version_file_path):
            raise ValueError("`{}` dose not exists".format(self.version_file_path))

    def __migrate_to_revision(self, update_rev: str, migrate_up: bool = True):
        script_path = os.path.dirname(migrations.__file__)
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", script_path)
        alembic_cfg.set_main_option("sqlalchemy.url", str(self.__engine.engine.url))
        alembic_cfg.set_main_option("version_table", conversation_alembic_version)

        with self.__engine.begin() as connection:
            alembic_cfg.attributes['connection'] = connection
            script = ScriptDirectory.from_config(alembic_cfg)

            def downgrade(rev, context):
                return script._downgrade_revs(update_rev, rev)

            def upgrade(rev, context):
                return script._upgrade_revs(update_rev, rev)

            fn = upgrade
            if not migrate_up:
                fn = downgrade

            from alembic.runtime.environment import EnvironmentContext
            with EnvironmentContext(alembic_cfg,
                                    script,
                                    fn=fn) as context:
                context.configure(version_table=conversation_alembic_version, connection=connection)
                script.run_env()

    def upgrade(self, revision: str = "base"):
        self.__migrate_to_revision(revision, True)

    def downgrade(self, revision: str = "base"):
        self.__migrate_to_revision(revision, False)


    def create_migration(self, migration_name):
        if not migration_name:
            raise ValueError("Migration name must be set")

        alembic_conf = Config(file_=self.alembic_ini_path)
        alembic_conf.set_main_option("script_location", self.version_folder_path)
        alembic_conf.set_main_option("sqlalchemy.url", self.db_url)

        version = self._read_version()
        new_version = version + 1
        command.revision(alembic_conf, message=migration_name, rev_id=str(new_version))
        self._write_version(new_version)

    def _read_version(self):
        with open(self.version_file_path, 'r') as file:
            content = file.read()

        if not content.isdigit():
            raise ValueError("Version file `{}` content must be a number".format(self.version_file_path))

        return int(content)

    def _write_version(self, version):
        with open(self.version_file_path, 'w') as file:
            file.write(str(version))
