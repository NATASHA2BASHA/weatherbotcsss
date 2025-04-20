from app.database.models import Base, engine

def init():
    print("🔧 Инициализация базы данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы.")

if __name__ == "__main__":
    init()