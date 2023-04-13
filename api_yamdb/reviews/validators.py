from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework.validators import ValidationError

year_regex = RegexValidator(
    r'^\d{4}$',
    'Enter a valid year. The format should be YYYY.'
)


def year_validator(value):
    if value < 1900 or value > timezone.now().year:
        raise ValidationError(
            ('%(value)s is not a correcrt year!'),
            params={'value': value},
        )
