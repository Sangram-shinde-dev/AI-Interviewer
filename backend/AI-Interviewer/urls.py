

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(api_urls)),
]
