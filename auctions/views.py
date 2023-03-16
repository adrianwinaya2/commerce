from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import ActiveListings, Bid, Category, User, Comments


def index(request):
    items = ActiveListings.objects.filter(status="Active")
    # watch_count = len(request.user.user_watching.all())

    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "items": items,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class NewListingForm(forms.ModelForm):
    class Meta:
        model = ActiveListings
        fields = ['title', 'description', 'image', 'category', 'price']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control col-md-5',
                'placeholder': 'Add your item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control col-md-10',
                'rows': 5,
                'placeholder': 'Add your item description'
            }),
            'image': forms.URLInput(attrs={
                'class': 'form-control col-md-10',
                'placeholder': 'Image URL (optional)'
            }),
            'category': forms.Select(choices=Category.objects.all(),
                attrs={
                'class': 'form-control col-md-5',
                'rows': 5,
                'placeholder': 'Add your item description'
            }),
            'price': forms.TextInput(attrs={
                'class': 'form-control col-md-5',
                'placeholder': 'Add your starting price'
            }),
        }
    
    def save(self, request):
        instance = super(NewListingForm, self).save(commit=False)
        instance.uploader = request.user
        if not instance.image:
            instance.image = "https://i.pinimg.com/474x/c3/dd/68/c3dd68d0c850a966a4c3c16887163a98.jpg"
        instance.save()

class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        widgets = {
            'price': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bid Price'
            }),
        }
        labels = {
            'price': ''
        }
    
    def save(self, request, item):
        instance = super(NewBidForm, self).save(commit=False)
        instance.bidder = request.user
        instance.item = item
        instance.save()

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your comment'
            }),
        }
        labels = {
            'content': ''
        }
    
    def save(self, request, item):
        instance = super(NewCommentForm, self).save(commit=False)
        instance.commenter = request.user
        instance.item = item
        instance.save()

@login_required(login_url="login")
def new_listing(request):
    listing_form = NewListingForm()

    if request.method == "POST":
        listing_form = NewListingForm(request.POST)

        if listing_form.is_valid():
            listing_form.save(request)
            return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/new.html", {
        "form": listing_form,
    })

def see_details(request, item_id, errorShow="hidden"):
    item = ActiveListings.objects.get(pk=item_id)
    comments = Comments.objects.filter(item=item)
    bid_form = NewBidForm()
    comment_form = NewCommentForm()
    stat_color = ("success" if item.status == "Active" else "danger")
    print(errorShow)
    
    return render(request, "auctions/item.html", {
        "error": errorShow,
        "item": item,
        "color": stat_color,
        "bid_form": bid_form,
        "in_watchlist": True if request.user in item.watchlist.all() else False,
        "comments": comments,
        "comment_form": comment_form,
    })

@login_required(login_url="login")
def bid_item(request, item_id):
    item = ActiveListings.objects.get(pk=item_id)
    print(item)

    if request.method == "POST" and request.user != item.uploader:
        bid_form = NewBidForm(request.POST)
        price = float(request.POST['price'])

        if bid_form.is_valid() and price > item.price:
            bid_form.save(request, item)
            item.price = price
            item.save()
            return HttpResponseRedirect(reverse("details", args=[item.id]))
    
    return HttpResponseRedirect(reverse("details", args=[item.id, "show"]))

@login_required(login_url="login")
def close_auction(request, item_id):
    item = ActiveListings.objects.get(pk=item_id)

    if request.user == item.uploader:
        item.status = "Closed"
        item.winner = item.bid_list.get(price=item.price).bidder
        item.save()
    
    return HttpResponseRedirect(reverse("details", args=[item.id]))

@login_required(login_url="login")
def add_watchlist(request, item_id):
    item = ActiveListings.objects.get(pk=item_id)

    if request.user != item.uploader:
        if request.user in item.watchlist.all():
            item.watchlist.remove(request.user)
        else:
            item.watchlist.add(request.user)
    
    return HttpResponseRedirect(reverse("details", args=[item.id]))

@login_required(login_url="login")
def add_comment(request, item_id):
    item = ActiveListings.objects.get(pk=item_id)

    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)

        if comment_form.is_valid():
            comment_form.save(request, item)
            return HttpResponseRedirect(reverse("details", args=[item_id]))
    
    return HttpResponseRedirect(reverse("details", args=[item_id]))

@login_required(login_url="login")
def see_watchlist(request):
    user_watchlist = request.user.user_watching.all()

    return render(request, "auctions/index.html", {
        "title": "Watchlists",
        "items": user_watchlist
    })

def categories(request, cat_name=None):
    items = None

    if cat_name:
        ctg = Category.objects.get(name=cat_name)
        items = ActiveListings.objects.filter(category=ctg)

    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
        "items": items,
        "cat_name": cat_name
    })

# TODO: 20 July
# 1. Bid:
#     - bid confirmation modal (JS?)
#     - Add to user's active bid
# 2. Closed :
# 3. User == uploader:
# 4. Watchlist
# 5. Comments section
# 6. Navbar:
#     - breadcrumbs
#     - pagination
# 7. Watchlist list:
# 8. Category:
#     - category list
#     - get cat by FK
# 9. Require login