from django.shortcuts import render, get_object_or_404, redirect
import os, sys, traceback
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.template.context_processors import request
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils import timezone
import json

from repository.models import *
from repository.forms import *


class CreateThingView(View):
    '''
    Base class for Add/Edit an Item(Thing)
    '''
    model = None
    form_class = None
    template_name = None
    ajax_template_name = None
    cancel_url = '/'
    item_type = None    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        obj = form.save(self.request.user)
        return HttpResponseRedirect(obj.get_absolute_url()) 
    
    #@login_required(function, redirect_field_name, login_url)
    def get(self, request, *args, **kwargs):
        # Check the parameters passed in the URL and process accordingly
        # Prepare the cancel_url for 'Cancel button' to be passed with the context    
        self.cancel_url = request.GET.get('cancel', '/') 
        
        if request.is_ajax():
            self.template_name = self.ajax_template_name
            
        if kwargs.get('pk', None) is None:
            # Create
            form = self.form_class(initial=None)
        else:
            # Update
            self.obj = get_object_or_404(self.model, pk=kwargs.get('pk', None))
            form = self.form_class(instance=self.obj)

        return render(request, self.template_name, {'form': form, 'cancel_url': self.cancel_url, 'item_type': self.item_type})

    def post(self, request, *args, **kwargs):
        print "Post data"
        if request.is_ajax():
            self.template_name = self.ajax_template_name
                    
        if kwargs.get('pk', None) is None:
            # Create
            instance = self.model()         
        else:
            # Update
            instance = self.model.objects.get(id=kwargs.get('pk', None))
            
        form = self.form_class(request.POST, request.FILES, instance=instance)
        
        if form.is_valid():
            print "Form is valid"
            try:          
                obj = form.save(self.request.user, commit=False)
                if not obj.pk:          
                    obj.added_by = self.request.user                    
                obj.modified_by = self.request.user                
                obj.save()
                # Without this next line the M2M fields won't be saved.
                form.save_m2m()                  
                        
                if request.is_ajax():
                    # Create JSON response and send
                    res = {}
                    res['result'] = 'success'
                    res['url'] = obj.get_absolute_url()
                    return JsonResponse(res)
                                
                messages.success(request, 'Changes on item %s are successful! '%obj.name)        
                return HttpResponseRedirect(obj.get_absolute_url())
                            
            except:
                print ("Error: Unexpected error:", sys.exc_info()[0])
                for frame in traceback.extract_tb(sys.exc_info()[2]):
                    fname,lineno,fn,text = frame
                    print ("DBG:: Error in %s on line %d" % (fname, lineno))
                    
                # Add non_field_errors to the form to convey the message    
                form.add_error(None, "Unexpected error occured! Checking the fields may help.")                 
                               
        if request.is_ajax():
            # Create JSON response alongwith the rendered form and send
            res = {}
            res['result'] = 'failure'
            res['data'] = render_to_string(self.template_name, {'form': form})                
            return JsonResponse(res)
                        
        return render(request, self.template_name, {'form': form, 'cancel_url': self.cancel_url, 'item_type': self.item_type})

  
class AddItem(CreateThingView):
    '''
    Add/Edit an Item
    '''
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        type = kwargs.get('type', None)
        self.item_type = type
        print "DBG: requested content type > ", type
        # Check the type i.e. item_type and derive the data model etc.
        if type == Snippet.item_type():
            self.model = Snippet
            self.form_class = SnippetForm
            self.template_name = 'repository/items/add-snippet.html'
            self.ajax_template_name = 'repository/include/forms/snippet.html' 
            
        elif type == Poetry.item_type():
            self.model = Poetry
            self.form_class = PoetryForm
            self.template_name = 'repository/items/add-poetry.html'
            self.ajax_template_name = 'repository/include/forms/poetry.html'
            
        elif type == Person.item_type():
            self.model = Person
            self.form_class = PersonForm
            self.template_name = 'repository/items/add-person.html'
            self.ajax_template_name = 'repository/include/forms/person.html'
            
        elif type == Place.item_type():
            self.model = Place
            self.form_class = PlaceForm
            self.template_name = 'repository/items/add-place.html'
            self.ajax_template_name = 'repository/include/forms/place.html'
                   
        elif type == Product.item_type():
            self.model = Product
            self.form_class = ProductForm
            self.template_name = 'repository/items/add-product.html'
            self.ajax_template_name = 'repository/include/forms/product.html'
                      
        elif type == Event.item_type():
            self.model = Event
            self.form_class = EventForm
            self.template_name = 'repository/items/add-event.html'
            self.ajax_template_name = 'repository/include/forms/event.html'
                     
        elif type == Organization.item_type():
            self.model = Organization
            self.form_class = OrganizationForm
            self.template_name = 'repository/items/add-organization.html'
            self.ajax_template_name = 'repository/include/forms/organization.html' 
    
        elif type == Book.item_type():
            self.model = Book
            self.form_class = BookForm
            self.template_name = 'repository/items/add-book.html'
            self.ajax_template_name = 'repository/include/forms/book.html'
                    
        else:
            print "Error: content type is not found"
            raise Http404
                
        return super(self.__class__, self).dispatch(request, *args, **kwargs) 

      
def add(request):
    '''
    Add an item
    '''    
    ##
    # Make the context and render  
    context = {'obj': None }
    template = "repository/items/add.html"  
    return render(request, template, context)    
 
    
def publish(request, type, pk, slug):
    """
    Publish or unpublish a creative work type item
    """
    
    print "DBG: requested content type > ", type
    # Check the type i.e. item_type and derive the data model etc.
    if type == Snippet.item_type():
        item_cls = Snippet
        template = "repository/items/publish.html"  
                
    elif type == Poetry.item_type():
        item_cls = Poetry
        template = "repository/items/publish.html"
        
    else:
        print "Error: content type is not found"
        raise Http404

    # Get the object from the `pk`, raises a Http404 if not found
    obj = get_object_or_404(item_cls, pk=pk)
        
    if request.method == "POST":
        action = request.POST.get('submit')
        if action == 'Publish':
            obj.date_published = timezone.now()
        elif action == 'Unpublish':
            obj.date_published = None
        obj.save()
        messages.success(request, 'Changes on item %s are successful! '%obj.name)
        return HttpResponseRedirect(obj.get_absolute_url())                                   
           
    ##
    # Make the context and render  
    context = {'obj': obj }    
    return render(request, template, context)
                                               