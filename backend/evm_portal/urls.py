from django.contrib import admin
from django.urls import path, include
from elections.views import active_elections, tally_results, cast_vote, verify_blockchain_log # <-- Import new view
# from .views import home # If you have a home view

urlpatterns = [
    # path('', home, name='home'), # Optional home view
    path('admin/', admin.site.urls),

    # Election APIs
    path('api/elections/active/', active_elections, name='active_elections'),
    path('api/elections/<int:election_id>/tally/', tally_results, name='tally_results'),
    path('api/elections/<int:election_id>/vote/', cast_vote, name='cast_vote'),

    # Account/Auth APIs
    path('api/auth/', include('accounts.urls')),

    # Blockchain Verification API
    path('api/blockchain/log/', verify_blockchain_log, name='verify_blockchain_log'), # <-- ADD THIS LINE
]