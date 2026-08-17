from django.urls import path
from .views import (
    login_api, 
    register_api, 
    missing_checkouts_api, 
    assign_missing_checkouts_api, 
    test_auth_api,
    # Team Management APIs
    teams_list_api,
    team_detail_api,
    team_create_api,
    team_update_api,
    team_delete_api,
    team_add_member_api,
    team_remove_member_api,
    team_bulk_add_members_api,
    my_teams_api,
    team_members_api,
)

urlpatterns = [
    # Authentication
    path('login/', login_api),
    path('register/', register_api),
    path('test-auth/', test_auth_api),
    
    # Bulk Checkout
    path('missing-checkouts/', missing_checkouts_api),
    path('assign-missing-checkouts/', assign_missing_checkouts_api),
    
    # Team Management (TEAM-005, TEAM-006, TEAM-010, TEAM-011)
    path('teams/', teams_list_api, name='teams_list'),
    path('teams/create/', team_create_api, name='team_create'),
    path('teams/bulk-add-members/', team_bulk_add_members_api, name='team_bulk_add_members'),
    path('teams/my-teams/', my_teams_api, name='my_teams'),
    path('teams/<int:team_id>/', team_detail_api, name='team_detail'),
    path('teams/<int:team_id>/update/', team_update_api, name='team_update'),
    path('teams/<int:team_id>/delete/', team_delete_api, name='team_delete'),
    path('teams/<int:team_id>/add-member/', team_add_member_api, name='team_add_member'),
    path('teams/<int:team_id>/remove-member/', team_remove_member_api, name='team_remove_member'),
    path('teams/<int:team_id>/members/', team_members_api, name='team_members'),
]