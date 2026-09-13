from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name",]


class ProductSerializer(serializers.ModelSerializer):
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )
        return value

    class Meta:
        model = Product 
        fields = ["id", "name", "description", "price", 
                  "stock", "category",]