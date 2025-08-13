from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from carts.models import Cart, CartItem
from store.models import Product, Variation

# Create your views here.

def _cart_id(request):

    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []

    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            print(key, value)  # For debugging

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variations.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exist:
        cart_items = CartItem.objects.filter(product=product, cart=cart)

        ex_var_list = []
        id_list = []
        for cart_item in cart_items:
            existing_variation = cart_item.variations.all()
            ex_var_list.append(sorted([v.id for v in existing_variation]))
            id_list.append(cart_item.id)

        current_var_ids=sorted([v.id for v in product_variations])

        if current_var_ids in ex_var_list:
            # Increase cart item quantity
            index = ex_var_list.index(current_var_ids)
            item_id = id_list[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            # Create a new cart item with variations
            new_cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variations) > 0:
                new_cart_item.variations.clear()
                new_cart_item.variations.add(*product_variations)
            new_cart_item.save()
    else:
        # Create a completely new cart item
        cart_item = CartItem.objects.create(product=product,quantity=1,cart=cart)
        if len(product_variations) > 0:
            cart_item.variations.add(*product_variations)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product, id=product_id)

    try:
        cart_item=CartItem.objects.filter(product=product, cart=cart, id=cart_item_id)
        if cart_item.exists():
            cart_item=cart_item.first()
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except:
        pass 
        
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product, id=product_id)
    cart_item=CartItem.objects.filter(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity +=cart_item.quantity
        
        tax=(2 * total)/100
        grand_total=total+ tax
    except ObjectDoesNotExist:

        pass
        
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

        }
    
    return render(request, 'store/cart.html',context)