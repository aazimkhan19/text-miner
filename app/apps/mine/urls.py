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
    path('moderator/texts/<int:pk>/', moderator.ModeratorInitialView.as_view(), name='moderator-texts'),
    path('moderator/texts/<int:pk>/text/<int:tpk>', moderator.ModeratorTextDetailView.as_view(), name='moderator-text-detail'),
    path('moderator/classrooms/', moderator.ModeratorClassroomListView.as_view(), name='moderator-classrooms'),
    path('moderator/classroom/<int:pk>', moderator.ModeratorClassroomDetailView.as_view(), name='moderator-classroom-detail'),
    path('moderator/classroom/create', moderator.ModeratorClassroomCreateView.as_view(), name='moderator-classroom-create'),
    path('moderator/classroom/<int:cpk>/user/<int:upk>/remove', moderator.ModeratorRemoveUserView.as_view(), name='moderator-classroom-user-remove'),
    path('moderator/classroom/<int:pk>/tasks/create/', moderator.ModeratorClassroomTaskCreateView.as_view(), name='moderator-classroom-task-create'),
    path('moderator/classroom/<int:cpk>/task/<int:tpk>/edit', moderator.ModeratorClassroomTaskEditView.as_view(), name='moderator-classroom-edit-task'),
    path('moderator/classroom/<int:cpk>/text/<int:tpk>/moderate/', moderator.ModeratorClassroomModerateTextView.as_view(), name='moderator-classroom-text-moderate'),
    path('moderator/classroom/<int:cpk>/text/moderated/<int:tpk>/', moderator.ModeratorClassroomModeratedTextView.as_view(), name='moderator-classroom-moderated-text'),
    path('moderator/notifications/unread', moderator.ModeratorUnreadNotificationsView.as_view(), name='moderator-notifications-unread'),
    path('moderator/notifications/read', moderator.ModeratorReadNotificationsView.as_view(), name='moderator-notifications-read'),
    path('moderator/notifications/<int:pk>/toggle', moderator.ModeratorNotificationToggleView.as_view(), name='moderator-notification-status-toggle'),
    path('moderator/profile/', moderator.ModeratorProfileView.as_view(), name='moderator-profile')
]
miner_patterns = [
    path('miner/', miner.MinerInitialView.as_view(), name='miner-initial'),
    path('miner/tasks/<int:pk>/', miner.MinerInitialView.as_view(), name='miner-tasks'),
    path('miner/results/<int:pk>/', miner.MinerResultsInitialView.as_view(), name='miner-results'),
    path('miner/tasks/<int:pk>/task/<int:tpk>', miner.MinerTaskDetailView.as_view(), name='miner-task-detail'),
    path('miner/results/<int:pk>/result/<int:tpk>', miner.MinerResultDetailView.as_view(), name='miner-result-detail'),
    path('miner/classroom/join/', miner.MinerClassroomJoinView.as_view(), name='miner-classroom-join'),
    path('miner/classroom/<int:pk>', miner.MinerClassroomDetailView.as_view(), name='miner-classroom-detail'),
    path('miner/classroom/<int:pk>/results', miner.MinerClassroomResultsView.as_view(), name='miner-classroom-detail-results'),
    path('miner/classroom/<int:cpk>/task/<int:tpk>', miner.MinerClassroomTaskDetailView.as_view(), name='miner-classroom-task-detail'),
    path('miner/classrooms/', miner.MinerClassroomListView.as_view(), name='miner-classrooms'),
    path('miner/classroom/<int:cpk>/result/<int:tpk>/', miner.MinerClassroomResultDetailView.as_view(), name='miner-classroom-result-detail'),
    path('miner/notifications/unread', miner.MinerUnreadNotificationsView.as_view(), name='miner-notifications-unread'),
    path('miner/notifications/read', miner.MinerReadNotificationsView.as_view(), name='miner-notifications-read'),
    path('miner/notifications/<int:pk>/toggle', miner.MinerNotificationToggleView.as_view(), name='miner-notification-status-toggle'),
    path('miner/profile/', miner.MinerProfileView.as_view(), name='miner-profile'),
]
urlpatterns += admin_patterns
urlpatterns += moderator_patterns
urlpatterns += miner_patterns