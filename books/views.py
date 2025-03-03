from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Category
from django import forms
from django.db.models import Q
from django.http import HttpResponse
import csv

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'price', 'stock', 'published_date']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }

def book_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    books = Book.objects.all()
    categories = Category.objects.all()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category_id:
        books = books.filter(category_id=category_id)

    # CSV ডাউনলোড রিকোয়েস্ট চেক করা
    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="books_list.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Author', 'Category', 'Price', 'Stock', 'Published Date'])
        for book in books:
            writer.writerow([book.title, book.author, book.category.name, book.price, book.stock, book.published_date])

        return response

    return render(request, 'books/book_list.html', {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    })

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Create'})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Update'})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})