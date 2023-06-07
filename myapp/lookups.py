from ajax_select import register, LookupChannel
from .models import Brand


@register("brand")
class BrandLookup(LookupChannel):
    model = Brand

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def get_result(self, obj):
        return obj.name

    def format_match(self, obj):
        return obj.name

    def check_auth(self, request):
        pass
