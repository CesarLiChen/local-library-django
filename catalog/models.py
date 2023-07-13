from django.db import models
from django.urls import reverse # for generating URLS by reversing the URL patterns.
import uuid

# Create your models here.

class Genre(models.Model):
    """ Model representing a book genre. """
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Horror)')

    def __str__(self) -> str:
        """ String for representing the Model obj."""
        return self.name

class Book(models.Model):
    """ Model that represents a book. """
    title = models.CharField(max_length=200)

    # Foreign Key because a Book can only have 1 author, but authors can have many books.
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')

    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book.')

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        """ Returns the URL to access a detail record for current book. """
        # For this to work, defining a URL mapping that has the name 'book-detail',
        # and defining an associated view and template is necessary.
        return reverse('book-detail', args=[str(self.id)])
    
class BookInstance(models.Model):
    """ Model that represents a specific copy of a book. """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library.')
    # Book many copies, a copy can only have 1 book.
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)  
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = ( # A tuple of tuples (ordered, unchangeable).
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1, choices=LOAN_STATUS, blank=True,
        default='m', help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']

    def __str__(self) -> str:
        return f'{self.id} ({self.book.title})' # Python 3.6
        # return '{0} ({1})'.format(self.id, self.book.title) # For older Python versions.