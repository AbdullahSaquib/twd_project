from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.search.mysearch import compare_strings
from datetime import datetime

#test git
def get_search_categories(search_string, max_results = 5, threshold = 0):
    search_result_cats = []
    cat_score_list = []
    cat_id_list = []
    category_list = Category.objects.all()

    #Filling cat_score_list, cat_id_list
    for category in category_list:
        cat_score_list.append(compare_strings(search_string, category.name))
        cat_id_list.append(category.id)

    #Collecting matched ids
    for i in range(0, max_results):
        max1 = max(cat_score_list)
        if max1 > threshold:
            index = cat_score_list.index(max1)
            search_result_cats.append(category_list.get(id=cat_id_list[index]))
            cat_score_list[index] = 0
    return search_result_cats

def get_search_pages(search_string, max_results = 5, threshold = 0):
    search_result_pages = []
    page_score_list = []
    page_id_list = []
    page_list = Page.objects.all()
    #Filling page_score_list, page_id_list
    for page in page_list:
        page_score_list.append(compare_strings(search_string, page.title))
        page_id_list.append(page.id)

    #Collecting matched ids
    for i in range(0, max_results):
        max1 = max(page_score_list)
        if max1 > threshold:
            index = page_score_list.index(max1)
            search_result_pages.append(page_list.get(id=page_id_list[index]))
            page_score_list[index] = 0
    return search_result_pages


# Create your views here.

@login_required
def like_category(request):
    cat_id = None
    likes = 0
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        print(category)
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()
    return HttpResponse(likes)

@login_required
def search_category(request, category_name_slug):
    max_results = 5
    threshold = 0.2
    search_result_pages = []
    page_score_list = []
    page_id_list = []

    category = Category.objects.get(slug = category_name_slug)
    page_list = Page.objects.filter(category=category)
    search_string = request.POST.get('search_string')

    for page in page_list:
        page_score_list.append(compare_strings(search_string,page.title))
        page_id_list.append(page.id)

    #Collecting matched ids
    for i in range(0, max_results):
        max1 = max(page_score_list)
        if max1 > threshold:
            index = page_score_list.index(max1)
            search_result_pages.append(page_list.get(id=page_id_list[index]))
            page_score_list[index] = 0

    context_dict = {
        'search_result_pages':search_result_pages
    }

    return render(request, 'rango/search.html', context_dict)

def track_url(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET['page_id']
        try :
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            return redirect(page.url)
        except Page.DoesNotExist:
            pass
    return redirect('/rango/')

def search(request):
    search_string = request.POST.get('search_string')

    context_dict = {
        'search_result_cats':get_search_categories(search_string, threshold = 0.25),
        'search_result_pages':get_search_pages(search_string, threshold = 0.25)
    }

    return render(request, 'rango/search.html', context_dict)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = authenticate(username=username,password=password)
        password = request.POST.get('password')
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your rango account is disabled.")
        else:
            print "Invalid login details:{0},{1}".format(username,password)
            return HttpResponse('Invalid login details supplied.')
    else:
        return render(request, 'rango/login.html',{})

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit = False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dict = {
        'user_form':user_form,
        'profile_form':profile_form,
        'registered':registered
    }
    return render(request, 'rango/register.html', context_dict)

@login_required
def add_page(request, category_name_slug):
    try :
        cat = Category.objects.get(slug = category_name_slug)
    except Category.DoesNotExist:
        cat = None
    if request.method == 'POST':
        form = PageForm(request.POST)
        if cat:
            page = form.save(commit = False)
            page.category = cat
            page.views = 0
            page.save()
            return redirect('/rango/category/'+category_name_slug+'/')
        else :
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form':form, 'slug':category_name_slug}
    return render(request, 'rango/add_page.html', context_dict)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form':form})

def index(request):
    category_list=Category.objects.all()
    page_list=Page.objects.order_by('-views')[:5]
    context_dict = {
    'categories':category_list,
    'pages':page_list
    }
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')
        if (datetime.now()-last_visit_time).seconds>5:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    response = render(request, 'rango/index.html', context_dict)
    return response

def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug = category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', context_dict)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html',{})

def about(request):
    return render(request, 'rango/about.html',{})
