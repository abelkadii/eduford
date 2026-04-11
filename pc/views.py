from django.shortcuts import render, redirect
import json
from .models import PriceLog, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from eduford.settings import BASE_DIR
# Create your views here.

def compare(s1, s2, r=False, b=0):
    if not (-2<len(s1)-len(s2)<2):
        return 0
    m = min(len(s1), len(s2))
    s = m-1 if r else b+1
    e = b if r else m
    similarity_count = 0
    for i in range(m):
        if s1[i] == s2[i]:
            similarity_count += 1
        else:
            for j in range(m-i-1):
                if s1[len(s1)-j-1] == s2[len(s2)-j-1]:
                    similarity_count += 1
            break

    similarity_ratio = similarity_count / len(s1)
    return similarity_ratio*(.8+int(len(s1)==len(s2))*.2)

def search(query, phrase):
    count = 0
    qws = set(query.split(' '))
    pws = set(phrase.split(' '))
    for qw in qws:
        if not qw:
            continue
        sm = 0
        for pw in pws:
            if not qw:
                continue
            if pw==qw:
                sm+=3
            else:
                sm+=compare(pw, qw)
        count+=sm
    return count




def home(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    context = products_search_view(request)
    context['location']= 'pc'
    context['abbreviatedname'] = (request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...') if request.user.is_authenticated and request.user.email_verified else ""
    return render(request, 'pc/index.html', context)

def wrapstring(string, max_length):
    return string if len(string)<=max_length else string[:max_length]+'...'

def products_search_view(request):
    query = request.GET.get('query', '')
    page = int(request.GET.get('page', 1))
    PER_PAGE = 20
    if query:
        # Find similar products using trigram similarity
        products = []
        for product in Product.objects.all():
            products.append([product, search(query.lower(), product.name.lower())])
                
        products.sort(key=lambda k: k[1], reverse=True)
        products_similar=[]
        for i in range(len(products)):
            if i<10 or products[i][1]>=len(set(query.split(' ')))*2:
                products_similar.append(products[i][0])
                continue
            break
        objects = [i for i in Product.objects.filter(name__contains=query) if i not in products_similar] + products_similar
    else:
        objects = Product.objects.all().order_by('popularity')
    paginator = Paginator(objects, PER_PAGE) 
    serialized_products = []
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    for product in items:
        pricelogs = PriceLog.objects.filter(product=product.id)
        pr = {
        'id': product.id,
        'name': product.name,
        # 'name': pricelogs[0].nameOnStore,
        'bname': wrapstring(product.name, 50),
        'img': product.img,
        'details_text': " • ".join(list(json.loads(product.details).values())),
        'bdetails_text': wrapstring(" • ".join(list(json.loads(product.details).values())), 80),
        'offers': str(lg:=len(pricelogs)) + " Offer" + "s"*int(lg!=1),
        'currency_symbol': "£",
        'price': min([pl.price for pl in pricelogs]),
        }
        serialized_products.append(pr)
    text = f"found {len(objects)} books | "
    text += f"search results for {query} | " if query  else ""
    text += f"showing {min((page-1)*PER_PAGE, len(objects))} - {min(page*PER_PAGE, len(objects))} out of {len(objects)}" if serialized_products else ""
    context = {
        'products': serialized_products,
        'text': text,
        'query': query,
        'page_obj': items
    }
    return context

def products(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    context = products_search_view(request)
    return render(request, 'pc/search.html', context)

def product(request, id, name):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return HttpResponse('verify your account', status=400)
    else:
        return HttpResponse('login to your account or create a new account', status=400)
    prod = Product.objects.filter(id=id)
    if not prod:
        return HttpResponse(404)
    prod=prod[0]
    pricelogs = PriceLog.objects.filter(product=prod.id)
    store_logos = json.load(open(BASE_DIR/'pc/store_logo.json', 'r'))
    product_data = {
        'id': prod.id,
        # 'name': pricelogs[0].nameOnStore,
        'name': prod.name,
        'img': prod.img,
        'details_text': " • ".join(list(json.loads(prod.details).values())),
        'details': " • ".join([f"{i}: {j}" for i, j in json.loads(prod.details).items()]),
        'currency_symbol': "£",
        'price': min([pl.price for pl in pricelogs]),
        'stores': sorted([{
            'nameOnStore': pl.nameOnStore,
            'price': pl.price,
            'currency': "£",
            'store': pl.store,
            'store_img': store_logos[pl.store],
            'relocate': pl.relocate,
            'delivery_time': pl.delivery_time,
            'delivery_details': pl.delivery_details,
        } for pl in pricelogs], key=lambda i: i['price'])
    }
    product_data['min_price'] = "£" + str(product_data['stores'][0]['price'])
    product_data['max_price'] = "£" + str(product_data['stores'][-1]['price'])
    # return JsonResponse({'sucess': True, 'data': product_data})
    context = {
        # 'location': 'pc',
        # 'abbreviatedname': (request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...') if request.user.is_authenticated and request.user.email_verified else "",
        'product': product_data
    }
    return render(request, 'pc/product.html', context)

    # products = json.load(open(BASE_DIR/"pc/products-finalized.json", 'r'))[132:]
    # for product in products:
    #     prod = Product(id_on_store=product['id'], name=product['name'], popularity=product['popularity'], img=product['img'], details=json.dumps(product['details']), description="")
    #     prod.save()
    #     for store in product['stores']:
    #         pl = PriceLog(product=Product.objects.get(id_on_store=product['id']), nameOnStore=store['name_on_store'], price=store['price'], store=store['store_name'], relocate=store['url'], delivery_time=store['delevery'], delivery_details=store['delevery_details'])
    #         pl.save()
    #         print("saved ", pl)
    