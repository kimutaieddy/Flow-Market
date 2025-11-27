"""
Serializers for converting model instances to JSON for frontend/API use
"""
from .models import Product, Contact, Campaign

# Simple serializer for Product model
class ProductSerializer:
    def __init__(self, product):
        self.product = product
    
    def to_dict(self):
        return {
            'id': self.product.id,
            'name': self.product.name,
            'description': self.product.description,
            'price': float(self.product.price),
            'created_at': self.product.created_at.isoformat(),
            'is_active': self.product.is_active,
        }

# Example usage:
# product = Product.objects.first()
# serializer = ProductSerializer(product)
# data = serializer.to_dict()
