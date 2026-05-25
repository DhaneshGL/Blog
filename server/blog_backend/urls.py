from django.http import FileResponse, Http404
from django.urls import include, path

from . import settings

urlpatterns = [
    path('api/user/', include('api.urls_user')),
    path('api/auth/', include('api.urls_auth')),
    path('api/post/', include('api.urls_post')),
    path('api/comment/', include('api.urls_comment')),
]

CLIENT_DIST = settings.BASE_DIR / 'client' / 'dist'

if CLIENT_DIST.exists():

    def serve_spa(request, resource=''):
        candidate = CLIENT_DIST / resource
        if resource and candidate.is_file():
            return FileResponse(open(candidate, 'rb'))
        index_file = CLIENT_DIST / 'index.html'
        if index_file.exists():
            return FileResponse(open(index_file, 'rb'))
        raise Http404

    urlpatterns += [
        path('', serve_spa),
        path('<path:resource>', serve_spa),
    ]
