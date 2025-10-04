"""
Media file serving views for production
"""
import os
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.utils.http import http_date
from django.views.static import was_modified_since
import mimetypes
import time


@require_GET
@cache_control(max_age=3600)  # Cache for 1 hour
def serve_media(request, path):
    """
    Serve media files in production with proper caching and headers
    """
    # Security check - only serve files from MEDIA_ROOT
    document_root = settings.MEDIA_ROOT
    fullpath = os.path.join(document_root, path)
    
    # Normalize the path to prevent directory traversal attacks
    fullpath = os.path.normpath(fullpath)
    if not fullpath.startswith(document_root):
        raise Http404("Requested file not found")
    
    # Check if file exists
    if not os.path.exists(fullpath) or os.path.isdir(fullpath):
        raise Http404("Requested file not found")
    
    # Get file stats
    stat = os.stat(fullpath)
    
    # Check if file was modified since last request
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              stat.st_mtime, stat.st_size):
        return HttpResponse(status=304)  # Not Modified
    
    # Determine content type
    content_type, encoding = mimetypes.guess_type(fullpath)
    content_type = content_type or 'application/octet-stream'
    
    # Read and serve file
    try:
        with open(fullpath, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            
        # Set proper headers
        response['Last-Modified'] = http_date(stat.st_mtime)
        response['Content-Length'] = stat.st_size
        
        if encoding:
            response['Content-Encoding'] = encoding
            
        # Set cache headers
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except IOError:
        raise Http404("Error reading file")