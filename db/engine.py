from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_path() -> Path:
    # Dev-mode for now — later this becomes %LOCALAPPDATA%\Autodidex\
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "autodidex.db"

DB_PATH = get_db_path()
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)