from typing import Any, Dict
from django.shortcuts import render
from .models import Author, Book, BookInstance, Genre, Language
from django.views import generic

# Create your views here.

def index(request):
    """ View function for home page of site. """

    # Generate counts of some of the main objects.
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_genres_with_word = Genre.objects.filter(name__icontains='horror').count()
    num_books_with_word_the = Book.objects.filter(title__icontains='the ').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_with_word': num_genres_with_word,
        'num_books_with_word_the': num_books_with_word_the,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list' # app_name/templates/app_name/booK_list
    queryset = Book.objects.filter(title__icontains='war'[:5]) # Get 5 books containing the title 'war'
    """ Can also do above by overriding the method. Is more flexible.
    def get_queryset(self):
        return Book.objects.filter(title_icontains='war')[:5] 
    """

    # template_name = 'books/book_list.html' # If needed to specify own template name/location

    # Overriding context data
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # Call base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)

        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context