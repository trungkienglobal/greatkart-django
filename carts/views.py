from unicodedata import category
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    cart_id = request.session._session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for key in request.POST:
            print(key)
            value = request.POST[key]
            try:
                variation = Variation.object.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
                print(product_variation)
            except:
                pass
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    is_cart_item_exists = CartItem.objects.filter(cart=cart, product=product).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(cart=cart, product=product)
        print(cart_item)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            print(existing_variation)
            ex_var_list.append(list(existing_variation))
            print(ex_var_list)
            id.append(item.id)
        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            print(index)
            item_id = id[index]
            print(item_id)
            item = CartItem.objects.get(cart=cart, product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:     
            item = CartItem.objects.create(cart=cart, product=product, quantity=1)               
            if len(product_variation) > 0:
                #item.variation.clear()
                item.variation.add(*product_variation)
            item.save()
        print(ex_var_list)
    else: 
        cart_item = CartItem.objects.create(
            cart = cart,
            product = product,      
            quantity = 1,
        )
        if len(product_variation) > 0:
            #cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, cart_item_id):
    try:
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        # product = Product.objects.get(id=product_id)
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')

def cart(request, total=0, quantity=0, tax=0, grand_total=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * 10/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)