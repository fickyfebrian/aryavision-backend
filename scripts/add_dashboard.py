import os
import re

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {path}")

# 1. Add get_dashboard_statistics to app/repositories/product.py
repo_path = 'app/repositories/product.py'
with open(repo_path, 'r', encoding='utf-8') as f:
    repo_content = f.read()

# Make sure func is imported from sqlalchemy
if "from sqlalchemy import" in repo_content and "func" not in repo_content:
    repo_content = repo_content.replace("from sqlalchemy import", "from sqlalchemy import func,")
elif "from sqlalchemy import func" not in repo_content:
    repo_content = "from sqlalchemy import func\n" + repo_content

stats_repo_code = """
    def get_dashboard_statistics(self) -> dict:
        total_products = self.db.query(func.count(Product.id)).scalar() or 0
        total_brands = self.db.query(func.count(func.distinct(Product.brand))).scalar() or 0
        budget_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 0).scalar() or 0
        mid_range_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 1).scalar() or 0
        premium_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 2).scalar() or 0
        
        return {
            "total_products": total_products,
            "total_brands": total_brands,
            "budget_cluster": budget_cluster,
            "mid_range_cluster": mid_range_cluster,
            "premium_cluster": premium_cluster
        }
"""
if "def get_dashboard_statistics" not in repo_content:
    repo_content += stats_repo_code
    write_file(repo_path, repo_content)

# 2. Add get_dashboard_statistics to app/services/product.py
service_path = 'app/services/product.py'
with open(service_path, 'r', encoding='utf-8') as f:
    service_content = f.read()

stats_service_code = """
    def get_dashboard_statistics(self) -> dict:
        return self.repository.get_dashboard_statistics()
"""
if "def get_dashboard_statistics" not in service_content:
    service_content += stats_service_code
    write_file(service_path, service_content)

# 3. Create app/api/dashboard.py
dashboard_api_path = 'app/api/dashboard.py'
dashboard_api_content = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.product import ProductService
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    service: ProductService = Depends(get_product_service)
):
    stats = service.get_dashboard_statistics()
    return success_response(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )
"""
write_file(dashboard_api_path, dashboard_api_content)

# 4. Update main.py
main_path = 'main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    main_content = f.read()

if "from app.api import health, product, ml, recommendation, auth" in main_content:
    main_content = main_content.replace(
        "from app.api import health, product, ml, recommendation, auth",
        "from app.api import health, product, ml, recommendation, auth, dashboard"
    )
elif "from app.api import health, product, ml, recommendation, auth, dashboard" not in main_content:
    main_content = main_content.replace(
        "from app.api import ",
        "from app.api import dashboard, "
    )

if "app.include_router(dashboard.router, prefix=\"/api\")" not in main_content:
    main_content = main_content.replace(
        "app.include_router(recommendation.router, prefix=\"/api\")",
        "app.include_router(recommendation.router, prefix=\"/api\")\napp.include_router(dashboard.router, prefix=\"/api\")"
    )

write_file(main_path, main_content)

# 5. Fix app/api/__init__.py if necessary
init_path = 'app/api/__init__.py'
if os.path.exists(init_path):
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    if "dashboard" not in init_content:
        with open(init_path, 'a', encoding='utf-8') as f:
            f.write("\nfrom . import dashboard\n")
        print(f"Fixed: {init_path}")
