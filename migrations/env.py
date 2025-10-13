# migrations/env.py
import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

def get_engine():
    try:
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine

def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")

config.set_main_option("sqlalchemy.url", get_engine_url())
target_db = current_app.extensions["migrate"].db

def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata

def _force_import_models():
    # บังคับโหลดโมเดลที่มีอยู่จริงเท่านั้น (กัน lazy import ทำให้ autogenerate มองไม่เห็น)
    for mod in (
        "app.models.property",
        "app.models.user",
        "app.models.approval",
        "app.models.review",  # ถ้าไม่มีจะข้าม
    ):
        try:
            __import__(mod)
        except ModuleNotFoundError:
            logger.warning("Optional model module not found: %s", mod)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    _force_import_models()
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,
        render_as_batch=True,           # สำคัญมากสำหรับ SQLite
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    conf_args = current_app.extensions["migrate"].configure_args
    conf_args.setdefault("process_revision_directives", process_revision_directives)
    conf_args.setdefault("compare_type", True)
    conf_args.setdefault("render_as_batch", True)  # สำคัญมากสำหรับ SQLite

    connectable = get_engine()
    _force_import_models()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
