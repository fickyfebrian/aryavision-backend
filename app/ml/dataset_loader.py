import pandas as pd
from sqlalchemy.orm import Session
from app.models.product import Product

def load_dataset_from_db(db: Session) -> pd.DataFrame:
    """
    Mengambil seluruh data produk dari tabel 'products' dan
    mengembalikannya sebagai Pandas DataFrame.
    """
    query = db.query(Product).statement
    # db.bind mengembalikan engine dari session
    df = pd.read_sql(query, db.bind)
    return df
