from django.db import models
import phonenumbers


class PhoneNumberField(models.CharField):
    description = "Phone number"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, phonenumbers.PhoneNumber):
            return value
        try:
            parsed = phonenumbers.parse(value, "US")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return parsed
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number")

    def get_prep_value(self, value):
        if value is None:
            return value
        return phonenumbers.format_number(value, phonenumbers.PhoneNumberFormat.E164)
