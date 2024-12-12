from rest_framework import serializers
from .models import MenuItem, Category
from decimal import Decimal
from rest_framework.validators import UniqueValidator
import bleach

# class MenuItemSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)

class CategorySerializer(serializers.ModelSerializer):
     class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255,validators=[UniqueValidator(queryset=MenuItem.objects.all())] )
    stock = serializers.IntegerField(source='inventory')
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only = True)
   
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'stock', 'price_after_tax', 'category', 'category_id']
    
    def calculate_tax(self, product:MenuItem):
        return product.price * Decimal(1.1)
    
    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        if attrs['price'] < 2:
            raise serializers.ValidationError("The price cannot be less than 2")
        if attrs['inventory'] < 0:
            raise serializers.ValidationError("The stock cannot be a negative number")
        return attrs
    