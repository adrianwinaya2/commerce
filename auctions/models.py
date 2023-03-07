from turtle import ondrag
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class ActiveListings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    image = models.URLField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="ctg_item")

    price = models.DecimalField(decimal_places=2, max_digits=6)

    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_item")
    watchlist = models.ManyToManyField(User, blank=True, related_name="user_watching")

    status = models.CharField(default="Active", max_length=6)
    creation_date = models.DateField(auto_now=True)

    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winning", blank=True, default=None, null=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_item")
    item = models.ForeignKey(ActiveListings, on_delete=models.CASCADE, related_name="bid_list")
    price = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self) -> str:
        return f"%s bid %s on $%s" % (self.bidder, self.item, self.price)

class Comments(models.Model):
    item = models.ForeignKey(ActiveListings, on_delete=models.CASCADE, related_name="comment_section")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="comment")
    comment_date = models.DateField(auto_now=True)
    content = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return f"%s comment on %s" % (self.commenter, self.item)