import re
from datetime import datetime

def validate(data, files=None, rules=None):
    errors = {}

    if rules is None:
        return errors

    for field, field_rules in rules.items():
        # دریافت مقدار فیلد
        if field == "tags" or field == "users":
            if hasattr(data, 'getlist'):
                value = data.getlist(field)
            elif isinstance(data, dict):
                value = data.get(field, [])
                if not isinstance(value, list):
                    value = [value] if value else []
            else:
                value = []
        elif field == "attachments":
            if files:
                if hasattr(files, 'getlist'):
                    value = files.getlist('attachments')
                elif isinstance(files, dict):
                    value = files.get('attachments', [])
                    if not isinstance(value, list):
                        value = [value] if value else []
                else:
                    value = []
            else:
                value = []
        else:
            if hasattr(data, 'get'):
                value = data.get(field)
            elif isinstance(data, dict):
                value = data.get(field)
            else:
                value = None

        # اعتبارسنجی هر قانون
        for rule in field_rules:
            if ":" in rule:
                rule_name, param = rule.split(":", 1)
            else:
                rule_name, param = rule, None

            # اجرای قوانین اعتبارسنجی
            if rule_name == "required":
                if field in ["tags", "users"]:
                    if not value or len(value) == 0:
                        errors[field] = f"The {field.replace('_', ' ')} field is required."
                elif field == "attachments":
                    if not value or len(value) == 0:
                        errors[field] = f"The {field.replace('_', ' ')} field is required."
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

            elif rule_name == 'min_items' and field in ["tags", "users"]:
                if len(value) < int(param):
                    errors[field] = f"Please select at least {param} {field}."

            elif rule_name == 'max_items' and field in ["tags", "users"]:
                if len(value) > int(param):
                    errors[field] = f"You can select maximum {param} {field}."

            elif rule_name == 'file_type' and field == "attachments" and value:
                allowed_types = param.split(",")
                for file in value:
                    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                        errors[field] = f"File {file.name} has unsupported type. Allowed: {', '.join(allowed_types)}"
                        break

            elif rule_name == 'max_size' and field == "attachments" and value:
                max_size_bytes = int(param) * 1024 * 1024
                for file in value:
                    if hasattr(file, 'size') and file.size > max_size_bytes:
                        errors[field] = f"File {file.name} exceeds {param} MB size limit."
                        break

            elif rule_name == 'max_files' and field == "attachments" and value:
                if len(value) > int(param):
                    errors[field] = f"You can upload maximum {param} files."

    return errors


def validate_ticket_form(data, files=None):
    rules = {
        'subject': ['required', 'min:10', 'max:200'],
        'description': ['required', 'min:20'],
        'contact_name': ['required', 'min:3', 'max:100'],
        'contact_email': ['required', 'email'],
        'contact_phone': ['required', 'phone'],
        'priority': ['required'],
        'category': ['required'],
        'department': ['required'],
        'max_replay_date': ['required', 'future_date'],
        'due_date': ['future_date'],
        'tags': ['required', 'min_items:1', 'max_items:5'],
        'users': ['required', 'min_items:1', 'max_items:10'],
        'attachments': [
            'max_files:5',
            'max_size:10',
            'file_type:application/pdf,image/jpeg,image/png,application/msword'
        ]
    }

    return validate(data, files, rules)
