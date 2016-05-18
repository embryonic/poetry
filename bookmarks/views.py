from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
import os, sys, traceback
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from bookmarks.models import Bookmark 

# Create your views here.

@login_required
def add_bookmark(request):
    '''
    Add a bookmark for the user on given object
    '''
    if request.method == "POST":
        content_type_id = request.POST.get('content_type')
        object_id = request.POST.get('object_id')        
        bookmark_id = 0
        print "DBG:: bookmark add - content_type_id, object_id :", content_type_id, object_id

        # Validate content_type_id and object_id
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)            
            content_object = content_type.get_object_for_this_type(pk=object_id)               
        except ObjectDoesNotExist:
            print "DBG:: The content of object doesn't exist"
            data = {}
            data['status'] = 404
            data['id'] = bookmark_id
            return JsonResponse(data)                      
        
        # Add bookmark
        obj = Bookmark.objects.add_bookmark(content_object, request.user)        
        if obj:            
            status = 200 # OK
            bookmark_id = obj.id
        else:
            print "ERR:: add bookmark, content_type_id", content_type_id, "obj", object_id
            status = 500 # Internal server error
            
        data = {}
        data['status'] = status
        data['id'] = bookmark_id
        
        return JsonResponse(data)
    
    else:
        raise PermissionDenied        
            

@login_required
def remove_bookmark(request):
    '''
    Remove the bookmark by the user on given object
    '''
    if request.method == "POST":
        content_type_id = request.POST.get('content_type')
        object_id = request.POST.get('object_id')
        print "DBG:: bookmark remove - content_type_id, object_id :", content_type_id, object_id

        # Validate content_type_id and object_id
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)            
            content_object = content_type.get_object_for_this_type(pk=object_id)
            # Delete bookmark
            id = Bookmark.objects.remove_bookmark(content_object, request.user)           
        except ObjectDoesNotExist:
            status = 404
        
        status = 200 # Ok
            
        data = {}
        data['status'] = status
        data['id'] = 0
        
        return JsonResponse(data)
    
    else:
        raise PermissionDenied