from django.db import models
from django.core.exceptions import ValidationError
import pyorc


class Recipe(models.Model):
    """
    Contains settings to process videos
    """
    data = models.JSONField(help_text="JSON formatted recipe for processing videos. See https://localdevices.github.io/pyorc/user-guide/cli.html")
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)

    def clean(self):
        super().clean()
        # data = json.loads(json.dumps(self.data))
        # print(data)
        # json_object = json.dumps(data, indent=4)
        # with open("recipe.json", "w") as f:
        #     f.write(json_object)
        try:
            pyorc.cli.cli_utils.validate_recipe(self.data)
        except BaseException as e:
            raise ValidationError(f"Problem with recipe: {e}")

