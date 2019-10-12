from django.urls import path

from apps.mine.view import admin, initial, miner, moderator
app_name = 'mine'
urlpatterns = [
]

admin_patterns = [
    path('admin/', admin.AdminInitialView.as_view(), name='admin-initial'),
    path('admin/texts/', admin.AdminRawTextListView.as_view(), name='admin-raw-texts'),
    path('admin/texts/create/', admin.AdminRawTextCreateView.as_view(), name='admin-raw-text-create'),
    path('admin/texts/<int:pk>/', admin.AdminRawTextDetailView.as_view(), name='admin-raw-text-detail'),
    path('admin/texts/<int:pk>/moderate/', admin.AdminModerateTextView.as_view(), name='admin-raw-text-moderate'),
    path('admin/texts/moderated/', admin.AdminModeratedTextListView.as_view(), name='admin-moderated-text'),
    path('admin/texts/moderated/<int:pk>/', admin.AdminModeratedTextDetailView.as_view(), name='admin-moderated-text-detail'),
    path('admin/users/miners/', admin.AdminMinerListView.as_view(), name='admin-miners'),
    path('admin/users/moderators/', admin.AdminModeratorListView.as_view(), name='admin-moderators'),
    path('admin/users/<int:pk>/activate/', admin.AdminUserActivateView.as_view(), name='admin-user-turn'),
    path('admin/profile/', admin.AdminProfileView.as_view(), name='admin-profile')
]
moderator_patterns = [
    path('moderator/', moderator.ModeratorClassroomListView.as_view(), name='moderator-initial'),
    path('moderator/texts/', moderator.ModeratorRawTextListView.as_view(), name='moderator-raw-texts'),
    path('moderator/texts/<int:pk>/', moderator.ModeratorRawTextDetailView.as_view(), name='moderator-raw-text-detail'),
    path('moderator/texts/<int:pk>/moderate/', moderator.ModeratorModerateTextView.as_view(), name='moderator-raw-text-moderate'),
    path('moderator/texts/moderated/', moderator.ModeratorModeratedTextListView.as_view(), name='moderator-moderated-text'),
    path('moderator/texts/moderated/<int:pk>/', moderator.ModeratorModeratedTextDetailView.as_view(), name='moderator-moderated-text-detail'),
    path('moderator/classroom/<int:pk>', moderator.ModeratorClassroomDetailView.as_view(), name='moderator-classroom-detail'),
    path('moderator/classrooms/', moderator.ModeratorClassroomListView.as_view(), name='moderator-classrooms'),
    path('moderator/classroom/create', moderator.ModeratorClassroomCreateView.as_view(), name='moderator-classroom-create'),
    path('moderator/classroom/<int:cpk>/user/<int:upk>/remove', moderator.ModeratorRemoveUserView.as_view(), name='moderator-classroom-user-remove'),
    path('moderator/classroom/<int:pk>/tasks/create/', moderator.ModeratorClassroomTaskCreateView.as_view(), name='moderator-classroom-task-create'),
    path('moderator/tasks/create/', moderator.ModeratorTaskCreateView.as_view(), name='moderator-task-create'),
    path('moderator/task/<int:pk>/', moderator.ModeratorTaskDetailView.as_view(), name='moderator-task'),
    path('moderator/tasks/', moderator.ModeratorTaskListView.as_view(), name='moderator-tasks'),
    path('moderator/profile/', moderator.ModeratorProfileView.as_view(), name='moderator-profile')
]
miner_patterns = [
    path('miner/', miner.MinerInitialViewBeginner.as_view(), name='miner-initial'),
    path('miner/tasks/beginner/', miner.MinerInitialViewBeginner.as_view(), name='miner-tasks-beginner'),
    path('miner/tasks/intermediate/', miner.MinerInitialViewIntermediate.as_view(), name='miner-tasks-intermediate'),
    path('miner/tasks/advanced/', miner.MinerInitialViewAdvanced.as_view(), name='miner-tasks-advanced'),
    path('miner/task/<int:pk>/', miner.MinerTaskDetailView.as_view(), name='miner-task-detail'),
    path('miner/classroom/join/', miner.MinerClassroomJoinView.as_view(), name='miner-classroom-join'),
    path('miner/classroom/<int:pk>', miner.MinerClassroomDetailView.as_view(), name='miner-classroom-detail'),
    path('miner/classroom/<int:pk>/results', miner.MinerClassroomResultsView.as_view(), name='miner-classroom-detail-results'),
    path('miner/classroom/<int:cpk>/task/<int:tpk>', miner.MinerClassroomTaskDetailView.as_view(), name='miner-classroom-task-detail'),
    path('miner/classrooms/', miner.MinerClassroomListView.as_view(), name='miner-classrooms'),
    path('miner/classroom/<int:cpk>/result/<int:tpk>/', miner.MinerClassroomResultDetailView.as_view(), name='miner-classroom-result-detail'),
    path('miner/notifications', miner.MinerNotificationsView.as_view(), name='miner-notifications'),
    path('miner/notifications/<int:pk>/toggle', miner.MinerNotificationToggleView.as_view(), name='miner-notification-status-toggle'),
    path('miner/profile/', miner.MinerProfileView.as_view(), name='miner-profile')
]
urlpatterns += admin_patterns
urlpatterns += moderator_patterns
urlpatterns += miner_patterns