from decimal import Decimal

from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from rest_framework import status

from orders.models import Order, OrderItem
from products.models import Category, Product


class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.category = Category.objects.create(
            name="test_category"
        )

        self.product = Product.objects.create(
            name="test_product",
            description="test_product description",
            price=Decimal("120.00"),
            stock=10,
            category=self.category
        )

    def test_list_products(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get("/api/products/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        names = [product["name"] for product in response.data]
        prices = [product["price"] for product in response.data]
        stocks = [product["stock"] for product in response.data]

        self.assertIn(
            self.product.name,
            names
        )

        self.assertIn(
            str(self.product.price),
            prices
        )

        self.assertIn(
            self.product.stock,
            stocks
        )

    def test_retrieve_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(f"/api/products/{self.product.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["name"],
            self.product.name
        )

    def test_retrieve_nonexistent_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        nonexistent_id = 999999

        response = self.client.get(f"/api/products/{nonexistent_id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_create_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "name": "New Product",
            "description": "New Product Description",
            "price": "150.00",
            "stock": 20,
            "category": self.category.id,
        }

        response = self.client.post("/api/products/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Product.objects.filter(
                name="New Product"
            ).exists()
        )

    def test_create_product_without_name(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "name": "New Product",
            "description": "New Product Description",
            "price": "150.00",
            "stock": 20,
            "category": self.category.id,
        }

        data.pop("name")

        response = self.client.post("/api/products/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            Product.objects.filter(
                name="New Product"
            ).exists()
        )

        self.assertIn(
            "name",
            response.data
        )

    def test_create_product_with_invalid_category(self):
        self.client.force_authenticate(
                    user=self.user
                )
        
        data = {
            "name": "New Product",
            "description": "New Product Description",
            "price": "150.00",
            "stock": 20,
            "category": 999999
        }

        response = self.client.post("/api/products/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            Product.objects.filter(
                name="New Product"
            ).exists()
        )

    def test_create_product_with_negative_stock(self):
        self.client.force_authenticate(
                    user=self.user
                )
        
        data = {
            "name": "New Product",
            "description": "New Product Description",
            "price": "150.00",
            "stock": -1,
            "category": self.category.id
        }

        response = self.client.post("/api/products/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_update_product(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        data = {
            "name": "Updated Product",
            "description": "Updated Description",
            "price": "200.00",
            "stock": 30,
            "category": self.category.id
        } 

        response = self.client.put(f"/api/products/{self.product.id}/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["name"],
            "Updated Product"
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.name,
            "Updated Product"
        )

    def test_partial_update_product(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        data = {
            "price": "250.00"
        } 

        response = self.client.patch(f"/api/products/{self.product.id}/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["price"],
            "250.00"
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.price,
            Decimal("250.00")
        )

        self.assertEqual(
            self.product.name,
            "test_product"
        )

    def test_update_product_with_negative_stock(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        data = {
            "stock": -1
        } 

        response = self.client.patch(f"/api/products/{self.product.id}/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10,
        )

    def test_update_product_with_invalid_category(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        data = {
            "category": 999999
        } 

        response = self.client.patch(f"/api/products/{self.product.id}/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.category,
            self.category
        )

    def test_delete_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(f"/api/products/{self.product.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Product.objects.filter(id=self.product.id).exists()
        )

    def test_delete_product_with_order_item(self):
        self.client.force_authenticate(
            user=self.user
        )

        order = Order.objects.create(
            created_by=self.user,
            status=Order.Status.PENDING,
            total_price=Decimal("120.00")
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )

        response = self.client.delete(f"/api/products/{self.product.id}/")

        self.assertTrue(
            Product.objects.filter(id=self.product.id).exists()
        )
            