from django.urls import path

from .views import (
    member_detail,
    member_list,
    profile_edit,
    profile_preview,
    profile_publish,
    profile_unpublish,
)

app_name = "members"

urlpatterns = [
    path("members/", member_list, name="list"),
    path("members/<str:username>/", member_detail, name="detail"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("profile/preview/", profile_preview, name="profile_preview"),
    path("profile/publish/", profile_publish, name="profile_publish"),
    path("profile/unpublish/", profile_unpublish, name="profile_unpublish"),
]
