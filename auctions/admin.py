from django.contrib import admin
from .models import Bid, User, Category, ActiveListings, Comments

class ListingsAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(ActiveListings, ListingsAdmin)
admin.site.register(Bid)
admin.site.register(Comments)