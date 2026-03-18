from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Category model
class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


# User registration form
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Kiểm tra nếu tên đăng nhập đã tồn tại
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Kiểm tra nếu email đã tồn tại
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã tồn tại. Vui lòng chọn email khác.")
        return email


# Product model
class Product(models.Model):
    category = models.ManyToManyField(Category, related_name='products')  # Quan hệ nhiều-nhiều với Category
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    detail = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


# Order model
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chưa duyệt'),
        ('approved', 'Đã duyệt'),
        ('canceled', 'Đã hủy'),
    ]

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')  # Thêm related_name
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    approved_date = models.DateTimeField(null=True, blank=True)  # Lưu thời gian duyệt đơn
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Thêm trạng thái

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def get_cart_items(self):
        """Tổng số lượng sản phẩm trong giỏ hàng."""
        return sum(item.quantity for item in self.orderitem_set.all())

    @property
    def get_cart_total(self):
        """Tổng giá trị đơn hàng."""
        total = sum(item.product.price * item.quantity for item in self.orderitem_set.all() if item.product and item.product.price)
        return total

    @property
    def customer_name(self):
        """Tên khách hàng (ưu tiên họ tên, sau đó là username)."""
        if self.customer:
            full_name = f"{self.customer.first_name} {self.customer.last_name}".strip()
            return full_name if full_name else self.customer.username
        return "Không có tên khách hàng"

    @property
    def customer_email(self):
        """Email khách hàng."""
        return self.customer.email if self.customer else "Không có email khách hàng"

    @property
    def is_approved(self):
        """Kiểm tra đơn hàng đã được duyệt hay chưa."""
        return self.status == 'approved'

# OrderItem model
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity


# ShippingAddress model
class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

#chat



class ChatMessage(models.Model):
    sender = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    