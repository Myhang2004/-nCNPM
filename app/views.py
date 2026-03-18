from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Chi tiết sản phẩm
def detail(request):
    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)

    id = request.GET.get('id', '')  # Lấy ID sản phẩm từ URL
    products = Product.objects.filter(id=id)
    categories = Category.objects.filter(is_sub=False)

    context = {
        'products': products,
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/detail.html', context)


# Danh mục sản phẩm
def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')  # Lấy slug danh mục từ URL
    products = Product.objects.all()

    if active_category:
        products = products.filter(category__slug=active_category)

    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)

    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/category.html', context)


# Tìm kiếm sản phẩm
def search(request):
    searched = ''
    keys = []

    if request.method == "POST":
        searched = request.POST["searched"]  # Lấy từ khóa tìm kiếm
        keys = Product.objects.filter(name__icontains=searched)

    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)
    categories = Category.objects.filter(is_sub=False)

    context = {
        "searched": searched,
        "keys": keys,
        'categories': categories,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/search.html', context)


# Đăng ký
def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)
    categories = Category.objects.filter(is_sub=False)

    context = {
        'form': form,
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/register.html', context)


# Đăng nhập
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'User or password not correct!')

    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)
    categories = Category.objects.filter(is_sub=False)

    context = {
        'categories': categories,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/login.html', context)


# Đăng xuất
def logoutPage(request):
    logout(request)
    return redirect('login')


# Trang chủ
def home(request):
    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)
    categories = Category.objects.filter(is_sub=False)

    if order:  # Nếu đơn hàng hợp lệ (không phải None)
        # Tính số lượng đơn hàng đã duyệt
        orders = Order.objects.filter(customer=customer)  # Lấy tất cả đơn hàng của người dùng
        approved_orders_count = orders.filter(status='approved').count()  # Số đơn hàng đã duyệt
    else:
        approved_orders_count = 0  # Nếu không có đơn hàng (người dùng chưa đăng nhập hoặc chưa có đơn hàng)

    products = Product.objects.all()

    context = {
        'categories': categories,
        'products': products,
        'cartItems': cartItems,
        'approved_orders_count': approved_orders_count,  # Số lượng đơn hàng đã duyệt
        'user_not_login': user_not_login,
        'user_login': user_login,
    }

    return render(request, 'app/home.html', context)

# Giỏ hàng
def cart(request):
    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)
    categories = Category.objects.filter(is_sub=False)

    context = {
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/cart.html', context)


# Thanh toán
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from django.utils.timezone import localtime, now

def checkout(request):
    # Kiểm tra nếu người dùng đã đăng nhập
    if request.user.is_authenticated:
        user = request.user
        user_not_login = "hidden"
        user_login = "show"
    else:
        user = None
        user_not_login = "show"
        user_login = "hidden"
    
    cartItems = 0
    order = None
    items = []

    # Lấy thông tin giỏ hàng cho người dùng đã đăng nhập
    if user_login == "show":
        try:
            order = Order.objects.get(customer=user, complete=False)
            items = order.orderitem_set.all()  # Lấy tất cả các mục trong đơn hàng
            cartItems = order.get_cart_items
        except Order.DoesNotExist:
            messages.error(request, "Giỏ hàng của bạn trống! Vui lòng thêm sản phẩm vào giỏ hàng.")
            return redirect('cart')  # Chuyển hướng về giỏ hàng nếu không có đơn hàng
    else:
        messages.warning(request, "Bạn cần đăng nhập để đặt hàng!")
        return redirect('login')

    # Lấy tên người dùng (người đặt)
    user_name = user.get_full_name() if user.get_full_name() else user.username

    # Xử lý khi người dùng gửi yêu cầu đặt hàng
    if request.method == 'POST':
        note = request.POST.get('note')

        # 👉 Nếu có note từ CART
        if note:
            order.note = note
            order.save()

            return redirect('checkout')  # 👉 CHỈ reload, KHÔNG tạo đơn

        # 👉 Nếu bấm thanh toán ở CHECKOUT
        else:
            order.date_order = localtime(now())
            order.complete = True
            order.save()

            return redirect('invoice', order_id=order.id)
    # Kiểm tra nếu đơn hàng đã hoàn tất thì hiển thị các sản phẩm
    if order and order.complete:
        items = order.orderitem_set.all()

    categories = Category.objects.filter(is_sub=False)

    context = {
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }

    return render(request, 'app/checkout.html', context)
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Order, Category

def invoice(request, order_id):

    if request.user.is_authenticated:
        user = request.user
        user_not_login = "hidden"
        user_login = "show"

        # Lấy danh mục
        categories = Category.objects.filter(is_sub=False)

        # Lấy giỏ hàng hiện tại để hiển thị số trên icon
        order_cart, created = Order.objects.get_or_create(customer=user, complete=False)
        cartItems = order_cart.get_cart_items

    else:
        messages.warning(request, "Bạn cần đăng nhập!")
        return redirect('login')

    try:
        # Chỉ lấy đơn hàng của chính user
        order = Order.objects.get(id=order_id, customer=user)
        items = order.orderitem_set.all()

    except Order.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng!")
        return redirect('home')

    context = {
        'order': order,
        'items': items,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'cartItems': cartItems,  # ⭐ thêm để giỏ hàng hiện số
    }

    return render(request, 'app/invoice.html', context)
def order_history(request):
    if request.user.is_authenticated:
        user = request.user
        orders = Order.objects.filter(customer=user, complete=True).order_by('-date_order')
        categories = Category.objects.filter(is_sub=False)

        user_not_login = "hidden"
        user_login = "show"

        # Lấy giỏ hàng hiện tại
        order, created = Order.objects.get_or_create(customer=user, complete=False)
        cartItems = order.get_cart_items

        # Kiểm tra trạng thái đơn hàng
        for o in orders:
            if o.status == 'approved' and not hasattr(o, 'notified'):
                messages.success(request, f"Đơn hàng #{o.id} đã được duyệt!")
                o.notified = True

    else:
        messages.warning(request, "Bạn cần đăng nhập để xem lịch sử đơn hàng!")
        return redirect('login')

    context = {
        'orders': orders,
        'categories': categories,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'cartItems': cartItems
    }

    return render(request, 'app/order_history.html', context)

# Cập nhật giỏ hàng
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    if orderItem.quantity <= 0:
        orderItem.delete()
    else:
        orderItem.save()

    return JsonResponse({
        'quantity': orderItem.quantity,
        'cart_total': order.get_cart_total,
        'cart_items': order.get_cart_items,
    })


# Hàm phụ để lấy thông tin giỏ hàng
def get_cart_details(request):
    if request.user.is_authenticated:
        customer = request.user
        # Lấy hoặc tạo đơn hàng chưa hoàn tất (complete=False)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # Lấy tất cả các mục trong đơn hàng
        cartItems = order.get_cart_items  # Số lượng sản phẩm trong giỏ
        user_not_login = "hidden"
        user_login = "show"
    else:
        customer = None
        items = []
        order = None  # Khi người dùng chưa đăng nhập, order là None
        cartItems = 0
        user_not_login = "show"
        user_login = "hidden"

    return customer, order, items, cartItems, user_not_login, user_login
from django.utils.timezone import now






from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Order, Category




def dashboard(request, order_id=None):
    """
    Hiển thị trang Dashboard và thông báo khi đơn hàng được duyệt.
    """

    if request.user.is_authenticated:
        user = request.user

        # Lấy các đơn hàng đã hoàn tất
        orders = Order.objects.filter(customer=user, complete=True).order_by('-date_order')

        # Lấy giỏ hàng hiện tại
        order, created = Order.objects.get_or_create(customer=user, complete=False)
        cartItems = order.get_cart_items

        # Số đơn hàng đã duyệt
        approved_orders_count = orders.filter(status='approved').count()

        user_not_login = "hidden"
        user_login = "show"

    else:
        orders = []
        cartItems = 0
        approved_orders_count = 0
        user_not_login = "show"
        user_login = "hidden"

    # Lấy danh mục
    categories = Category.objects.filter(is_sub=False)

    order_message = None
    if order_id:
        try:
            order_check = Order.objects.get(id=order_id, customer=request.user)
            if order_check.status == 'approved':
                current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

                order_message = {
                    'order_id': order_check.id,
                    'current_time': current_time,
                    'message': f"Đơn hàng #{order_check.id} của bạn đã được duyệt vào lúc {current_time}!"
                }

                messages.success(request, order_message['message'])

        except Order.DoesNotExist:
            messages.error(request, "Không tìm thấy đơn hàng!")
            return redirect('home')

    context = {
        'orders': orders,
        'approved_orders_count': approved_orders_count,
        'order_message': order_message,
        'categories': categories,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'cartItems': cartItems,   # ⭐ thêm dòng này
    }

    return render(request, 'app/dashboard.html', context)

from django.http import JsonResponse
from .models import Product
def api_products(request):
    products = Product.objects.all()

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "image": str(p.image)
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4
        }
    )
def api_categories(request):
    categories = Category.objects.filter(is_sub=False)

    data = []
    for c in categories:
        data.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4
        }
    )
def api_cart(request):
    customer, order, items, cartItems, user_not_login, user_login = get_cart_details(request)

    data = {
        "cart_items": cartItems,
        "total_price": order.get_cart_total if order else 0
    }

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4
        }
    )
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Product, Order, OrderItem

@csrf_exempt
def api_update_cart(request):

    # Nếu mở bằng trình duyệt
    if request.method == "GET":
        return JsonResponse(
            {
                "message": "API Update Cart",
                "method": "POST",
                "body_example": {
                    "productId": 1,
                    "action": "add"
                }
            },
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )

    # Khi gọi POST thật
    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"})

        productId = data.get("productId")
        action = data.get("action")

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not login"})

        product = Product.objects.get(id=productId)

        order, created = Order.objects.get_or_create(
            customer=request.user,
            complete=False
        )

        orderItem, created = OrderItem.objects.get_or_create(
            order=order,
            product=product
        )

        if action == "add":
            orderItem.quantity += 1
        elif action == "remove":
            orderItem.quantity -= 1

        if orderItem.quantity <= 0:
            orderItem.delete()
            quantity = 0
        else:
            orderItem.save()
            quantity = orderItem.quantity

        return JsonResponse(
            {
                "product_id": productId,
                "quantity": quantity,
                "cart_items": order.get_cart_items,
                "cart_total": order.get_cart_total
            },
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )
    

def api_product_detail(request, id):

    try:
        product = Product.objects.get(id=id)

        data = {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "image": str(product.image)
        }

        return JsonResponse(
            data,
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )

    except Product.DoesNotExist:
        return JsonResponse(
            {"message": "Product not found"},
            json_dumps_params={"indent":4}
        )
def api_orders(request):

    orders = Order.objects.filter(customer=request.user)

    data = []

    for o in orders:
        data.append({
            "order_id": o.id,
            "total_price": o.get_cart_total,
            "total_items": o.get_cart_items,
            "complete": o.complete
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4
        }
    )
def api_order_detail(request, order_id):

    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()

    data = []

    for item in items:
        data.append({
            "product": item.product.name,
            "price": str(item.product.price),
            "quantity": item.quantity,
            "total": str(item.get_total)
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4
        }
    )
def api_search(request):

    keyword = request.GET.get("q")

    products = Product.objects.filter(name__icontains=keyword)

    data = []

    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": str(p.price)
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4
        }
    )

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_register(request):

    # GET -> lấy user trong database
    if request.method == "GET":
        users = list(User.objects.values("id", "username", "email"))

        return JsonResponse(
            {
                "message": "List users",
                "data": users
            },
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )

    # POST -> tạo user mới
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        return JsonResponse(
            {
                "message": "User created successfully",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



@csrf_exempt
def api_login(request):

    # GET -> xem user đang đăng nhập
    if request.method == "GET":

        if request.user.is_authenticated:
            return JsonResponse(
                {
                    "message": "User already logged in",
                    "username": request.user.username,
                    "email": request.user.email,
                    "user_id": request.user.id
                },
                json_dumps_params={
                    "ensure_ascii": False,
                    "indent": 4
                }
            )
        else:
            return JsonResponse(
                {
                    "API": "User Login",
                    "method": "POST",
                    "body": {
                        "username": "user1",
                        "password": "123456"
                    }
                },
                json_dumps_params={
                    "ensure_ascii": False,
                    "indent": 4
                }
            )

    # POST -> login
    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except:
            return JsonResponse(
                {"error": "Invalid JSON"},
                json_dumps_params={"indent": 4}
            )

        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return JsonResponse(
                {
                    "message": "Login successful",
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id
                },
                json_dumps_params={
                    "ensure_ascii": False,
                    "indent": 4
                }
            )

        else:
            return JsonResponse(
                {
                    "message": "Invalid username or password"
                },
                json_dumps_params={
                    "ensure_ascii": False,
                    "indent": 4
                }
            )
from django.contrib.auth.models import User
from django.http import JsonResponse

def api_users(request):

    users = User.objects.all()

    data = []
    for u in users:
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email
        })

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4
        }
    )
@csrf_exempt
def api_add_product(request):

    if request.method == "GET":

        products = Product.objects.all()

        data = []
        for p in products:
            data.append({
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category.name if p.category else None
            })

        return JsonResponse(
            data,
            safe=False,
            json_dumps_params={
                "ensure_ascii": False,
                "indent": 4
            }
        )

    if request.method == "POST":

        data = json.loads(request.body)

        name = data.get("name")
        price = data.get("price")

        product = Product.objects.create(
            name=name,
            price=price
        )

        return JsonResponse({
            "message": "Product created",
            "product_id": product.id
        })
from django.http import JsonResponse
from .models import Product

def api_delete_product(request, id):

    if request.method == "GET":
        return JsonResponse({
            "API": "Delete Product",
            "method": "DELETE",
            "url_example": f"/api/delete-product/{id}/"
        }, json_dumps_params={"indent":4})

    if request.method == "DELETE":

        try:
            product = Product.objects.get(id=id)
            product.delete()

            return JsonResponse({
                "message": "Product deleted successfully"
            }, json_dumps_params={"indent":4})

        except Product.DoesNotExist:
            return JsonResponse({
                "error": "Product not found"
            }, status=404)
from django.contrib.auth import logout
from django.http import JsonResponse

def api_logout(request):

    if request.method == "GET":
        return JsonResponse({
            "API": "Logout",
            "method": "POST"
        }, json_dumps_params={"indent":4})

    if request.method == "POST":

        logout(request)

        return JsonResponse({
            "message": "Logout successful"
        }, json_dumps_params={"indent":4})
    

#chat
def chat_api(request):

    if request.method == "POST":

        data = json.loads(request.body)
        message = data.get("message")

        # lưu tin nhắn user
        ChatMessage.objects.create(
            sender="user",
            message=message
        )

        reply = "Shop đã nhận tin nhắn, admin sẽ trả lời sớm."

        # lưu luôn phản hồi hệ thống
        ChatMessage.objects.create(
            sender="admin",
            message=reply
        )

        return JsonResponse({
            "reply": reply
        })
def get_messages(request):

    messages = ChatMessage.objects.all().order_by("created_at")

    data = []

    for m in messages:
        data.append({
            "sender": m.sender,
            "message": m.message
        })

    return JsonResponse(data, safe=False)
def admin_send(request):

    import json

    data = json.loads(request.body)

    message = data.get("message")

    ChatMessage.objects.create(
        sender="admin",
        message=message
    )

    return JsonResponse({"status":"ok"})