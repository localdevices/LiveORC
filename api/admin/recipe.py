from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django_json_widget.widgets import JSONEditorWidget

from api.models import Recipe
from api.admin import BaseInstituteAdmin, BaseForm

import json
import pyorc
import yaml


# Register your models here.

class RecipeForm(BaseForm):

    class Meta:
        model = Recipe
        fields = ["name", "institute"]
        widgets = {"data": JSONEditorWidget}

    def clean(self):
        super().clean()
        # open the json file and try to parse
        if not self.request.user.get_active_membership():
            raise forms.ValidationError("You Must have an institute to continue")
        if "recipe_file" in self.files:
            try:
                self.files["recipe_file"].seek(0)
                body = self.files["recipe_file"].read()
                recipe = yaml.load(body, Loader=yaml.FullLoader)
            except BaseException as e:
                raise ValidationError(f"Recipe file seems not to be a valid .yaml recipe file: {e}")
                # verify that geojson contains the right data
        else:
            recipe = json.loads(self.data["data"])
        try:
            recipe = pyorc.cli.cli_utils.validate_recipe(recipe)
        except BaseException as e:
            raise ValidationError(f"Problem with recipe file: {e}")


class RecipeCreateForm(RecipeForm):
    recipe_file = forms.FileField()

    class Meta:
        model = Recipe
        fields = ["name", "institute"]


class RecipeAdmin(BaseInstituteAdmin):
    fieldsets = [
        ("User input", {"fields": ["name", "institute", "recipe_file"]}),
        ("Resulting recipe", {
            "fields": [
                "data",
            ]}
         )
    ]
    list_display = ["name", "institute"]
    search_fields = ["name"]
    list_filter = ["name"]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """A separate view for changing models"""
        self.form = RecipeForm
        self.fieldsets = [
            ("User input", {"fields": ["name", "institute", "data"]}),
        ]
        # self.readonly_fields = None
        return super(RecipeAdmin, self).change_view(request, object_id)

    def add_view(self, request, form_url="", extra_context=None):
        self.form = RecipeCreateForm
        self.fieldsets = [("User input", {"fields": ["name", "institute", "recipe_file"]})]
        self.exclude = ("data",)
        self.readonly_fields = ["data"]
        return super(RecipeAdmin, self).add_view(request)

    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def save_model(self, request, obj, form, change):
        if "recipe_file" in request._files:
            request._files["recipe_file"].seek(0)
            body = request._files["recipe_file"].read()
            try:
                recipe = yaml.load(body, Loader=yaml.FullLoader)
            except:
                raise ValidationError(f'File {request._files["recipe_file"]} is not a .yaml file')
        else:
            recipe = form.instance.data
        recipe = pyorc.cli.cli_utils.validate_recipe(recipe)
        form.instance.data = recipe
        super().save_model(request, obj, form, change)

