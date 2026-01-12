from fastapi import APIRouter

from app.auth import routers as Auth
from app.modules.catalog.products_brand import routers as Brand
from app.modules.catalog.products_category import routers as ProductCategory
from app.modules.customers import routers as Customer
from app.modules.products import routers as Product
from app.modules.tasks import routers as Task

router = APIRouter()
# Core
router.include_router(Auth.router, prefix="/auth", tags=["Auth"])
# Modules
router.include_router(Task.router, prefix="/tasks", tags=["Tasks"])
router.include_router(Product.router, prefix="/products", tags=["Products"])
router.include_router(Customer.router, prefix="/customers", tags=["Customers"])
# Catalog
router.include_router(
    ProductCategory.router,
    prefix="/catalog/products_category",
    tags=["Products Category"],
)
router.include_router(
    Brand.router, prefix="/catalog/product_brand", tags=["Products Brand"]
)
