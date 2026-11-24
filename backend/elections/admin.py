from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Election, Candidate

@staff_member_required
def tally_view(request):
    """
    A custom admin view to render the vote tally dashboard.
    """
    # We pass an empty context, as the chart data will be fetched
    # by JavaScript from our API endpoint.
    context = {
        'title': 'Vote Tally Dashboard',
    }
    return render(request, 'admin/tally_dashboard.html', context)

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'starts_at', 'ends_at')
    list_filter = ('status',)
    
    def get_urls(self):
        """
        Add our custom tally view URL to the admin URLs.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'tally/',
                self.admin_site.admin_view(tally_view),
                name='tally_dashboard' # We name the URL
            ),
        ]
        return custom_urls + urls

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'election')
    list_filter = ('election',)

# Register your models with the admin site
admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)

# Note: Your other models (Voter, AuditLog, etc.) are registered in
# their own app's admin.py files (e.g., accounts/admin.py), which is correct.