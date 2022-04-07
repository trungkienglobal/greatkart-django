from .models import CartItem
from .views import _cart_id

def counter(request):
    if 'admin' in request.path:
        return {}
    else:
        cart_count=0
        cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))
        for cart_item in cart_items:
            cart_count += cart_item.quantity
        return dict(cart_count=cart_count)
