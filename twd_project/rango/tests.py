from django.test import TestCase
from .models import Category
from django.core.urlresolvers import reverse

def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

# Create your tests here.
class CategoryMethodsTest(TestCase):
    def test_ensure_views_are_positive(self):
        cat = Category(name='Something', views = -1, likes = 0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        cat = Category(name='Some Random title', views = -1, likes = 0)
        cat.save()
        self.assertEqual(cat.slug,'some-random-title')

class IndexViewTest(TestCase):
    def test_index_view_with_no_category(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'There are no categories to show')
        self.assertQuerysetEqual(response.context['categories'],[])

    def test_index_view_with_categories(self):
        add_cat('test',1,1)
        add_cat('temp',1,1)
        add_cat('tmp',1,1)
        add_cat('test temp',1,1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'test temp')

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats,4)
