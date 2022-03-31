from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n= len(prod)
        nSlides = n // 3 + ceil((n / 3) - (n // 3))
        allProds.append([prod, range(1,nSlides), nSlides])

    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searching(query, item):
    if query.lower() in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searching(query, item)]
        n= len(prod)
        if len(prod) !=0:
            nSlides = n // 3 + ceil((n / 3) - (n // 3))
            allProds.append([prod, range(1,nSlides), nSlides])
            params = {'allProds':allProds, 'msg': ""}
            return render(request, 'shop/search.html', params)
        else:
            params = {'msg': "Please enter a relevant product"}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method == "POST":
        email = request.POST.get('email')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name=name, email=email, phone= phone, desc= desc)
        contact.save()
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method == "POST":
        email = request.POST.get('email')
        order_id = request.POST.get('orderId')
        try:
            order = Order.objects.filter(order_id= order_id, email= email)
            if (len(order)> 0):
                update = OrderUpdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({"success": "true","msg": item.update_desc, "order": order[0].item_json, 'time': item.timestamp})
                    response = json.dumps(updates, default=str)
                return HttpResponse(response)
            else:
                data = [{"success": "false",
                    "msg": "Please check your order id or email and please try again later."
                }]
                response = json.dumps(data, default=str)
                return HttpResponse(response)
        except Exception as e:
            data = [{"success": "false", "msg": e}]
            response = json.dumps(data, default=str)
            return HttpResponse(response)

    return render(request, 'shop/tracker.html')

def product(request, prodId):
    # Fetching product using id
    product = Product.objects.filter(id=prodId)
    return render(request, 'shop/product.html', {'product': product[0]})


MERCHANT_KEY = 'MERCHANT_KEY';

def checkout(request):
    if request.method == "POST":
        item_json = request.POST.get('itemsJson')
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        phone = request.POST.get('phone')
        order = Order(item_json=item_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id = order.order_id, update_desc= "The Order has been Placed")
        update.save()
        id = order.order_id

        #request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID':'MERCHANT_ID',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlepayment',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html',{'param_dict': param_dict})
    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlepayment(request):
    #paytm will send you request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)

    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order successful')
        else:
            print('Order was not successfull because'+ response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html',{'response': response_dict})
