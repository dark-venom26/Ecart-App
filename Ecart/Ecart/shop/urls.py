from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about", views.about, name="ShopAbout"),
    path("contact", views.contact, name="ShopContact"),
    path("tracker", views.tracker, name="TrackingStatus"),
    path("search", views.search, name="ShopSearch"),
    path("product/<int:prodId>", views.product, name="ProductView"),
    path("checkout", views.checkout, name="checkout"),
    path("handlepayment", views.handlepayment, name="HandlePayment"),
]
