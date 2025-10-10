import re
from datetime import datetime

def validate(data, rules):
    errors = {}
    for field, field_rules in rules.items():
        # برای فیلدهای multiple choice از getlist استفاده کن
        if field == "tags":
            value = data.getlist(field)
        else:
            value = data.get(field)

        for rule in field_rules:
            if ":" in rule:
                rule_name, param = rule.split(":", 1)
            else:
                rule_name, param = rule, None

            if rule_name == "required":
                if field == "tags":
                    # برای tags حداقل یک آیتم انتخاب شده
                    if not value or len(value) == 0:
                        errors[field] = f"The {field.replace('_', ' ')} field is required."
                        # برای فیلدهای غیر چند در چند
                else:
                    if value is None or str(value).strip() == "":
                        errors[field] = f"The {field.replace('_', ' ')} field is required."

            elif rule_name == "min" and value and str(value).strip() != "":
                if len(str(value).strip()) < int(param):
                    errors[field] = f"The {field.replace('_', ' ')} must be at least {param} characters long."

            elif rule_name == "max" and value and str(value).strip() != "":
                if len(str(value).strip()) > int(param):
                    errors[field] = f"The {field.replace('_', ' ')} must be less than {param} characters long."

            elif rule_name == 'in' and value and str(value).strip() != "":
                allowed_values = param.split(",")
                if value not in allowed_values:
                    errors[field] = f"The {field.replace('_', ' ')} must be one of {', '.join(allowed_values)}."

            elif rule_name == 'future_date' and value and str(value).strip() != "":
                try:
                    dt = datetime.fromisoformat(value)
                    if dt <= datetime.now():
                        errors[field] = f"The {field.replace('_', ' ')} date must be in the future."
                except ValueError:
                    errors[field] = f"The {field.replace('_', ' ')} must be a valid date."

            elif rule_name == 'email' and value and str(value).strip() != "":
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    errors[field] = f"Please enter a valid email address."

            elif rule_name == 'phone' and value and str(value).strip() != "":
                phone_digits = re.sub(r'\D', '', str(value))
                if len(phone_digits) > 11:
                    errors[field] = f"Phone number must be maximum 11 digits."
                elif len(phone_digits) < 10:
                    errors[field] = f"Phone number must be at least 10 digits."

            elif rule_name == 'min_items' and field == "tags":
                if len(value) < int(param):
                    errors[field] = f"Please select at least {param} tags."

            elif rule_name == 'max_items' and field == "tags":
                if len(value) > int(param):
                    errors[field] = f"You can select maximum {param} tags."

    return errors
