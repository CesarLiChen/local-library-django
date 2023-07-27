from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Author, Book, BookInstance, Genre, Language, Secret
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

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

    # Number of visits to this view, as counted in the session variable.
    # Gets a session value, setting default it is not present (0).
    num_visits = request.session.get('num_visits', 0) 
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_with_word': num_genres_with_word,
        'num_books_with_word_the': num_books_with_word_the,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    """
    /locallibrary/catalog/templates/catalog/book_list.html
        The DEFAULT template file expected by the generic class-based list view 
        (for a model named Book in an application named catalog)
    """
    #==============IF YOU WANT TO CHANGE THE DEFAULT BEHAVIOUR============================
    # # Your own name for the list as a template variable
    # context_object_name = 'book_list' 
    #
    # # Get 5 books containing the title 'war'
    # queryset = Book.objects.filter(title__icontains='war'[:5]
    #
    # """ Can also do above by overriding the method. Is more flexible.
    # def get_queryset(self):
    #     return Book.objects.filter(title_icontains='war')[:5] 
    # """
    #
    # # If needed to specify own template name/location
    # template_name = 'books/book_list.html'
    #
    # # Overriding context data
    # def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    #     # Call base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context
    #=====================================================================================

class BookDetailView(generic.DetailView):
    model = Book

    # ============== Without Generics ==============================================
    # def book_detail_view(request, primary_key):
    #     try:
    #         book = Book.objects.get(pk=primary_key)
    #     except Book.DoesNotExist:
    #         raise Http404('Book does not exist')
    #
    #     return render(request, 'catalog/book_detail.html', context={'book': book})
    # ==============================================================================

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class SecretListView(LoginRequiredMixin, generic.ListView):    
    login_url = '/accounts/login/'
    # redirect_field_name = '' # Diff URL parameter instead of 'next'.

    model = Secret

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing ALL the books currently on loan."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self) -> QuerySet[Any]:
        return (
            BookInstance.objects.filter(status__exact='o')
            .order_by('due_back')
        )
