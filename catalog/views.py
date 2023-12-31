import datetime

from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Author, Book, BookInstance, Genre, Language, Secret
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from catalog.forms import RenewBookForm
from catalog.models import Author

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

@login_required
@permission_required('catalog.can_renew', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        
        # Create new form instance and populate with data from 
        # the request (binding)
        form = RenewBookForm(request.POST)

        if form.is_valid():
            # Process the data in form.cleaned_data as required
            # (here we jsut write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # Redirect to new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # If this is a GET request (or any other) create the default form.
    else: 
        propose_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': propose_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'} # Example
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = [
        'title', 'author', 'summary', 'isbn',
        'genre', 'language'
    ]
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = [
        'title', 'author', 'summary', 'isbn',
        'genre', 'language'
    ]
    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'