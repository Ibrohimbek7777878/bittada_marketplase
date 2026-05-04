from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name_uz', 'name_ru', 'name_en')

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title_uz', 'title_ru', 'title_en', 'description_uz', 'description_ru', 'description_en')
