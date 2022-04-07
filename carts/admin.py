from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_cart', 'get_product', 'get_variation', 'quantity', 'is_active')

    #django 3.2 tro len:
    # @display(ordering='cart__cart_id', description='cart')
    # def get_cart(self, obj):
    #     return obj.cart.cart_id

    def get_cart(self, obj):
        return obj.cart.cart_id
    get_cart.short_description = 'Cart_id' #Renames column head
    get_cart.admin_order_field = 'cart_id'#Allows column order sorting

    def get_product(self, obj):
        return obj.product.product_name
    get_product.short_description = 'Product name'
    get_product.short_order_field = 'product_name'

    def get_variation(self, obj):
        return "\n".join([var.variation_value for var in obj.variation.all()])

admin.site.register(Cart)
admin.site.register(CartItem, CartItemAdmin)