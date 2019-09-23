from django.urls import path

from apps.mine import views
from django.contrib.auth.decorators import login_required

app_name = 'mine'
urlpatterns = [
]

admin_patterns = [
    path('admin/', views.AdminInitialView.as_view(), name='admin-initial'),
    path('admin/texts/', views.AdminRawTextListView.as_view(), name='admin-raw-texts'),
    path('admin/texts/create/', views.AdminRawTextCreateView.as_view(), name='admin-raw-text-create'),
    path('admin/texts/<int:pk>/', views.AdminRawTextDetailView.as_view(), name='admin-raw-text-detail'),
    path('admin/texts/<int:pk>/moderate/', views.AdminModerateTextView.as_view(), name='admin-raw-text-moderate'),
    path('admin/texts/moderated/', views.AdminModeratedTextListView.as_view(), name='admin-moderated-text'),
    path('admin/texts/moderated/<int:pk>/', views.AdminModeratedTextDetailView.as_view(), name='admin-moderated-text-detail'),
    path('admin/users/miners/', views.AdminMinerListView.as_view(), name='admin-miners'),
    path('admin/users/moderators/', views.AdminModeratorListView.as_view(), name='admin-moderators'),
    path('admin/users/<int:pk>/activate/', views.AdminUserActivateView.as_view(), name='admin-user-turn'),
    path('admin/profile/', views.AdminProfileView.as_view(), name='admin-profile')
]
moderator_patterns = [
    path('moderator/', views.ModeratorInitialView.as_view(), name='moderator-initial'),
    path('moderator/texts/', views.ModeratorRawTextListView.as_view(), name='moderator-raw-texts'),
    path('moderator/texts/<int:pk>/', views.ModeratorRawTextDetailView.as_view(), name='moderator-raw-text-detail'),
    path('moderator/texts/<int:pk>/moderate/', views.ModeratorModerateTextView.as_view(), name='moderator-raw-text-moderate'),
    path('moderator/texts/moderated/', views.ModeratorModeratedTextListView.as_view(), name='moderator-moderated-text'),
    path('moderator/texts/moderated/<int:pk>/', views.ModeratorModeratedTextDetailView.as_view(), name='moderator-moderated-text-detail'),
    path('moderator/profile/', views.ModeratorProfileView.as_view(), name='moderator-profile')
]
miner_patterns = [
    path('miner/', login_required(views.MinerInitialViewBeginner.as_view()), name='miner-initial'),
    path('miner/tasks/beginner', login_required(views.MinerInitialViewBeginner.as_view()), name='miner-tasks-beginner'),
    path('miner/tasks/intermediate', login_required(views.MinerInitialViewIntermediate.as_view()), name='miner-tasks-intermediate'),
    path('miner/tasks/advanced', login_required(views.MinerInitialViewAdvanced.as_view()), name='miner-tasks-advanced'),
    path('miner/task/<int:pk>/', login_required(views.MinerTaskDetailView.as_view()), name='miner-task-detail'),
    #path('miner/task/intermediate/<int:pk>/', login_required(views.MinerTaskDetailView.as_view()), name='miner-task-detail-intermediate'),
    #path('miner/task/advanced/<int:pk>/', login_required(views.MinerTaskDetailView.as_view()), name='miner-task-detail-advanced'),
    path('miner/texts/', views.MinerRawTextListView.as_view(), name='miner-raw-texts'),
    path('miner/texts/create/', views.MinerRawTextCreateView.as_view(), name='miner-raw-text-create'),
    path('miner/texts/<int:pk>/', views.MinerRawTextDetailView.as_view(), name='miner-raw-text-detail'),
    path('miner/profile/', views.MinerProfileView.as_view(), name='miner-profile')
]
urlpatterns += admin_patterns
urlpatterns += moderator_patterns
urlpatterns += miner_patterns