from django.views.generic import ListView, DetailView

from app.models import Item


class DefaultView(ListView):
    template_name = "base.html"
    model = Item


class ItemDetailView(DetailView):
    template_name = "detail.html"
    model = Item
