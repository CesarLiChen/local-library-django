from django.db import models

# Create your models here.

class Genre(models.Model):
    """ Model representing a book genre. """
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Horror)")

    def __str__(self) -> str:
        """ String for representing the Model obj."""
        return self.name
    
    
