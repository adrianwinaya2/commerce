from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("", views.index, name="index"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:cat_name>", views.categories, name="categories"),
    path("watchlist", views.see_watchlist, name="see_watchlist"),
    path("new", views.new_listing, name="new"),

    path("item/<int:item_id>", views.see_details, name="details"),
    path("item/<int:item_id>/<str:errorShow>", views.see_details, name="details"),
    path("bid/<int:item_id>", views.bid_item, name="bid"),
    path("close/<int:item_id>", views.close_auction, name="close"),
    path("watchlist/<int:item_id>", views.add_watchlist, name="watch"),
    path("comment/<int:item_id>", views.add_comment, name="comment"),
]

urlpatterns += staticfiles_urlpatterns()

# TODO: 20 July
# 1. Bid:
#     - bid must be bigger than the cur price
#     - bid confirmation modal (JS?)
#     - Add to user's active bid
# 2. Closed :
#     - No "Add to watchlist" button
#     - Disable input & button bid
#     - Announce the winner only to the winner
# 3. User == uploader:
#     - No "Add to watchlist" button
#     - Disable input & button bid
#     - Add "Close bid" button
# 4. Watchlist
#     - jquery to change bgcolor button
#     - toggle add/remove from DB
# 5. Comments section
#     - username
#     - comment
#     - comment date
#    *System
#     - comment feature
#     - reply feature

# 6. Navbar:
#     - breadcrumbs
#     - pagination
# 7. Watchlist list:
#     - mirip index view (get list by FK)
#     - kalo closed, gray the image & disable details btn
# 8. Category:
#     - category list
#     - get cat by FK
# 9. Require login