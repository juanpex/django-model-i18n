from django.views.generic import ListView, DetailView

from app.models import Item


class DefaultView(ListView):
    template_name = "base.html"
    model = Item

    def get_context_data(self, **kwargs):
        from django.db.models import Q
        lala =  list(Item.objects.all())
        return super(DefaultView, self).get_context_data(**kwargs)


class ItemDetailView(DetailView):
    template_name = "detail.html"
    model = Item
