from django.shortcuts import render, redirect, HttpResponse
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.contrib.auth.models import User


		
class ProductView(View):
	def get(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))  
		totalitem = 0
		topwears = Product.objects.filter(category='TW')
		bottomwears = Product.objects.filter(category='BW')
		mobiles = Product.objects.filter(category='M')
		fitnessproducts =Product.objects.filter(category='FP')
		sports =Product.objects.filter(category='7T')
		shoes =Product.objects.filter(category='SU')
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		data = {
			'topwears': topwears,
			'bottomwears': bottomwears,
			'mobiles': mobiles,
			'fitnessproducts': fitnessproducts,
			'totalitem': totalitem,
			'sports':sports,
			'shoes':shoes,
		}

		# context = {'data': data}
		# this list is for payment images on the home page...
		image_paths = [
			'app/images/payavail/cc.jpg',
			'app/images/payavail/upi.jpg',
			'app/images/payavail/nb.jpg',
			'app/images/payavail/bj.jpg'
		]
		context= {'data': data,'totalitem':totalitem,'image_paths':image_paths}

		return render(request, 'app/home.html', context)

class ProductDetailView(View):
	def get(self, request, pk):
		totalitem = 0
		product = Product.objects.get(pk=pk)
		print(product.id)
		item_already_in_cart=False
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
			item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
		return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})
	
def bottom(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	bottomwears = Product.objects.filter(category='BW')

	return render(request,'app/bottom.html',{'bottomwears':bottomwears,'totalitem':totalitem})

def topwear(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	topwears = Product.objects.filter(category='TW')

	return render(request,'app/topwear.html',{'topwears':topwears,'totalitem':totalitem})

def fitnessproduct(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	fitnessproducts = Product.objects.filter(category='FP')

	return render(request,'app/fitnessproduct.html',{'fitnessproducts':fitnessproducts,'totalitem':totalitem})


def all_product(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	products = Product.objects.all()
	return render(request,'app/all_products.html',{'products':products,'totalitem':totalitem})

def _7T7T(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	products = Product.objects.filter(category='7T')
	return render(request,'app/7T7T.html',{'products':products,'totalitem':totalitem})

def shoes(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))  
	products = Product.objects.filter(category='SU')
	return render(request,'app/shoes.html',{'shoes':products,'totalitem':totalitem})

@login_required()
def add_to_cart(request):
	user = request.user
	item_already_in_cart1 = False
	product = request.GET.get('prod_id')
	item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
	if item_already_in_cart1 == False:
		product_title = Product.objects.get(id=product)
		Cart(user=user, product=product_title).save()
		messages.success(request, 'Product Added to Cart Successfully !!' )
		return redirect('/cart')
	else:
		return redirect('/cart')
  # Below Code is used to return to same page
  # return redirect(request.META['HTTP_REFERER'])

@login_required
def show_cart(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
		user = request.user
		cart = Cart.objects.filter(user=user)
		amount = 0.0
		shipping_amount = 70.0
		totalamount=0.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		print(cart_product)
		if cart_product:
			for p in cart_product:
				tempamount = (p.quantity * p.product.discounted_price)
				amount += tempamount
				totalamount = amount+shipping_amount
			return render(request, 'app/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount, 'totalitem':totalitem})
		else:
			return render(request, 'app/emptycart.html', {'totalitem':totalitem})
	else:
		return render(request, 'app/emptycart.html', {'totalitem':totalitem})

def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity+=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity-=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")
	
@login_required
def checkout(request):
	user = request.user
	add = Customer.objects.filter(user=user)
	# cart_items = Cart.objects.filter(user=request.user)
	cart_items = Cart.objects.filter(user=user)


	# subject = f"{user},  Your order has been successfully placed!"
	# message = f"""Hello {user},\n\nThank you for your order:\n\n"""
	# for item in cart_items:
	# 	message += f"{item.product.title} - Quantity: {item.quantity}\n"

	# 	message += """\nWe are happy that you choose v2kart for shopping.\n\nIf you are facing any problem or have any query, feel free to reach us at:\n\nMob: 8979871918\n\nEmail: infotechmalan@gmail.com"""

	# from_email = "infotechmalan@gmail.com"
	# recipient_list = [user.email]
	# try:
	# 	send_mail(
	# 		subject,
	# 		message,
	# 		from_email,
	# 		recipient_list,
	# 		fail_silently=False,
	# 	)
	# except:
	# 	messages.success(request, 'could not send email !!' )

	return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items})

@login_required
def payment_done(request):
	user = request.user
	cart_items = Cart.objects.filter(user=user)
	subject = f"{user},  Your order has been successfully placed!"
	message = f"""Hello {user},\n\nThank you for your order:\n\n"""
	for item in cart_items:
		message += f"{item.product.title} - Quantity: {item.quantity}\n"

		message += """\nWe are happy that you choose v2kart for shopping.\n\nIf you are facing any problem or have any query, feel free to reach us at:\n\nMob: 8979871918\n\nEmail: infotechmalan@gmail.com"""

	from_email = "infotechmalan@gmail.com"
	recipient_list = [user.email,'vijaymalan7@gmail.com','']
	try:
		send_mail(
			subject,
			message,
			from_email,
			recipient_list,
			fail_silently=False,
		)
	except:
		messages.success(request, 'could not send email !!' )

	custid = request.GET.get('custid')
	print("Customer ID", custid)
	user = request.user
	cartid = Cart.objects.filter(user = user)
	customer = Customer.objects.get(id=custid)
	print(customer)
	for cid in cartid:
		OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
		print("Order Saved")
		cid.delete()
		print("Cart Item Deleted")
	
	return redirect("orders")



def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

@login_required
def address(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	add = Customer.objects.filter(user=request.user)
	return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})

@login_required
def orders(request):
	op = OrderPlaced.objects.filter(user=request.user)
	return render(request, 'app/orders.html', {'order_placed':op})

def mobile(request, data=None):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data==None :
			mobiles = Product.objects.filter(category='M')
	elif data == 'Redmi' or data == 'Samsung':
			mobiles = Product.objects.filter(category='M').filter(brand=data)
	elif data == 'below':
			mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
	elif data == 'above':
			mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
	return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem':totalitem})


class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html', {'form':form})
  
 def post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'Congratulations!! Registered Successfully.')
   form.save()
  return render(request, 'app/customerregistration.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
	def get(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm()
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
		
	def post(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm(request.POST)
		if form.is_valid():
			usr = request.user
			name  = form.cleaned_data['name']
			mob = form.cleaned_data['mob']
			locality = form.cleaned_data['locality']
			city = form.cleaned_data['city']
			state = form.cleaned_data['state']
			zipcode = form.cleaned_data['zipcode']
			reg = Customer(user=usr, name=name, mob=mob, locality=locality, city=city, state=state, zipcode=zipcode) #mob=mob,
			reg.save()
			messages.success(request, 'Congratulations!! Profile Updated Successfully.')
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})

def contact(request):
	if request.method == "POST":
		name = request.POST.get('name')
		mob = request.POST.get('mob')
		email = request.POST.get('email')
		message = request.POST.get('message')

		# user = request.user
		# cart_items = Cart.objects.filter(user=user)
		subject = f"New Contact Form Submission from {name}"
		message = f"Name: {name}\nMob: {mob}\nEmail: {email}\n\nMsg: {message}"
		
		from_email = "infotechmalan@gmail.com"
		recipient_list = ['vijaymalan7@gmail.com']
		try:
			send_mail(
				subject,
				message,
				from_email,
				recipient_list,
				fail_silently=False,
			)
			messages.success(request, 'Your message sent successfully !' )
		except:
			messages.error(request, 'could not send email !' )
		return redirect('/contact-us/')

	return render(request,"app/contact.html")


