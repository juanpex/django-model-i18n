from django.views.generic import ListView

from app.models import Item

class DefaultView(ListView):
	template_name = "base.html"
	queryset = Item.objects.all()
