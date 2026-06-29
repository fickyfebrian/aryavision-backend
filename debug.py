import asyncio
from app.database.connection import SessionLocal
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService

def test():
    db = SessionLocal()
    try:
        service = ProductService(db)
        product = service.get_product_by_id(692)
        print("Got product:", product)
        
        # Test serialization
        product_dict = ProductResponse.model_validate(product).model_dump()
        print("Serialized:", product_dict)
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test()
