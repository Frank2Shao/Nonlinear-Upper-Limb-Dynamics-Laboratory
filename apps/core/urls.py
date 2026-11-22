from django.urls import path

from .views import about, beginners_safety, health, home, sitemap

urlpatterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("beginners-safety/", beginners_safety, name="beginners_safety"),
    path("sitemap.xml", sitemap, name="sitemap"),
    path("health/", health, name="health"),
]
