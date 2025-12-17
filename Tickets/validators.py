# # # import re
# # # from datetime import datetime
# # #
# # # def validate(data, rules):
# # #     errors = {}
# # #     for field, field_rules in rules.items():
# # #         # برای فیلدهای multiple choice از getlist استفاده کن
# # #         if field == "tags":
# # #             value = data.getlist(field)
# # #         else:
# # #             value = data.get(field)
# # #
# # #         for rule in field_rules:
# # #             if ":" in rule:
# # #                 rule_name, param = rule.split(":", 1)
# # #             else:
# # #                 rule_name, param = rule, None
# # #
# # #             if rule_name == "required":
# # #                 if field == "tags":
# # #                     # برای tags حداقل یک آیتم انتخاب شده
# # #                     if not value or len(value) == 0:
# # #                         errors[field] = f"The {field.replace('_', ' ')} field is required."
# # #                         # برای فیلدهای غیر چند در چند
# # #                 else:
# # #                     if value is None or str(value).strip() == "":
# # #                         errors[field] = f"The {field.replace('_', ' ')} field is required."
# # #
# # #             elif rule_name == "min" and value and str(value).strip() != "":
# # #                 if len(str(value).strip()) < int(param):
# # #                     errors[field] = f"The {field.replace('_', ' ')} must be at least {param} characters long."
# # #
# # #             elif rule_name == "max" and value and str(value).strip() != "":
# # #                 if len(str(value).strip()) > int(param):
# # #                     errors[field] = f"The {field.replace('_', ' ')} must be less than {param} characters long."
# # #
# # #             elif rule_name == 'in' and value and str(value).strip() != "":
# # #                 allowed_values = param.split(",")
# # #                 if value not in allowed_values:
# # #                     errors[field] = f"The {field.replace('_', ' ')} must be one of {', '.join(allowed_values)}."
# # #
# # #             elif rule_name == 'future_date' and value and str(value).strip() != "":
# # #                 try:
# # #                     dt = datetime.fromisoformat(value)
# # #                     if dt <= datetime.now():
# # #                         errors[field] = f"The {field.replace('_', ' ')} date must be in the future."
# # #                 except ValueError:
# # #                     errors[field] = f"The {field.replace('_', ' ')} must be a valid date."
# # #
# # #             elif rule_name == 'email' and value and str(value).strip() != "":
# # #                 email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
# # #                 if not re.match(email_pattern, value):
# # #                     errors[field] = f"Please enter a valid email address."
# # #
# # #             elif rule_name == 'phone' and value and str(value).strip() != "":
# # #                 phone_digits = re.sub(r'\D', '', str(value))
# # #                 if len(phone_digits) > 11:
# # #                     errors[field] = f"Phone number must be maximum 11 digits."
# # #                 elif len(phone_digits) < 10:
# # #                     errors[field] = f"Phone number must be at least 10 digits."
# # #
# # #             elif rule_name == 'min_items' and field == "tags":
# # #                 if len(value) < int(param):
# # #                     errors[field] = f"Please select at least {param} tags."
# # #
# # #             elif rule_name == 'max_items' and field == "tags":
# # #                 if len(value) > int(param):
# # #                     errors[field] = f"You can select maximum {param} tags."
# # #
# # #
# # #
# # #     return errors
# #
# # import re
# # from datetime import datetime
# #
# #
# # def validate(data, files=None, rules=None):
# #     errors = {}
# #
# #     for field, field_rules in rules.items():
# #         # برای فیلدهای multiple choice از getlist استفاده کن
# #         if field == "tags":
# #             value = data.getlist(field)
# #         elif field == "attachments":
# #             # دریافت فایل‌های آپلود شده
# #             if files:
# #                 value = files.getlist('attachments')
# #             else:
# #                 value = []
# #         else:
# #             value = data.get(field)
# #
# #         for rule in field_rules:
# #             if ":" in rule:
# #                 rule_name, param = rule.split(":", 1)
# #             else:
# #                 rule_name, param = rule, None
# #
# #             if rule_name == "required":
# #                 if field == "tags":
# #                     # برای tags حداقل یک آیتم انتخاب شده
# #                     if not value or len(value) == 0:
# #                         errors[field] = f"The {field.replace('_', ' ')} field is required."
# #                 elif field == "attachments":
# #                     # برای attachments - اجباری بودن
# #                     if not value or len(value) == 0:
# #                         errors[field] = f"The {field.replace('_', ' ')} field is required."
# #                 else:
# #                     if value is None or str(value).strip() == "":
# #                         errors[field] = f"The {field.replace('_', ' ')} field is required."
# #
# #             elif rule_name == "min" and value and str(value).strip() != "":
# #                 if len(str(value).strip()) < int(param):
# #                     errors[field] = f"The {field.replace('_', ' ')} must be at least {param} characters long."
# #
# #             elif rule_name == "max" and value and str(value).strip() != "":
# #                 if len(str(value).strip()) > int(param):
# #                     errors[field] = f"The {field.replace('_', ' ')} must be less than {param} characters long."
# #
# #             elif rule_name == 'in' and value and str(value).strip() != "":
# #                 allowed_values = param.split(",")
# #                 if value not in allowed_values:
# #                     errors[field] = f"The {field.replace('_', ' ')} must be one of {', '.join(allowed_values)}."
# #
# #             elif rule_name == 'future_date' and value and str(value).strip() != "":
# #                 try:
# #                     dt = datetime.fromisoformat(value)
# #                     if dt <= datetime.now():
# #                         errors[field] = f"The {field.replace('_', ' ')} date must be in the future."
# #                 except ValueError:
# #                     errors[field] = f"The {field.replace('_', ' ')} must be a valid date."
# #
# #             elif rule_name == 'email' and value and str(value).strip() != "":
# #                 email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
# #                 if not re.match(email_pattern, value):
# #                     errors[field] = f"Please enter a valid email address."
# #
# #             elif rule_name == 'phone' and value and str(value).strip() != "":
# #                 phone_digits = re.sub(r'\D', '', str(value))
# #                 if len(phone_digits) > 11:
# #                     errors[field] = f"Phone number must be maximum 11 digits."
# #                 elif len(phone_digits) < 10:
# #                     errors[field] = f"Phone number must be at least 10 digits."
# #
# #             elif rule_name == 'min_items' and field == "tags":
# #                 if len(value) < int(param):
# #                     errors[field] = f"Please select at least {param} tags."
# #
# #             elif rule_name == 'max_items' and field == "tags":
# #                 if len(value) > int(param):
# #                     errors[field] = f"You can select maximum {param} tags."
# #
# #             elif rule_name == 'file_type' and field == "attachments" and value:
# #                 allowed_types = param.split(",")
# #                 for file in value:
# #                     if file.content_type not in allowed_types:
# #                         errors[field] = f"File {file.name} has unsupported type. Allowed: {', '.join(allowed_types)}"
# #                         break
# #
# #             elif rule_name == 'max_size' and field == "attachments" and value:
# #                 max_size_bytes = int(param) * 1024 * 1024  # Convert MB to bytes
# #                 for file in value:
# #                     if file.size > max_size_bytes:
# #                         errors[field] = f"File {file.name} exceeds {param} MB size limit."
# #                         break
# #
# #             elif rule_name == 'max_files' and field == "attachments" and value:
# #                 if len(value) > int(param):
# #                     errors[field] = f"You can upload maximum {param} files."
# #
# #     return errors
#
#
# import re
# from datetime import datetime
# from django.contrib.auth.models import User
#
#
# def validate(data, files=None, rules=None):
#     """
#     اعتبارسنجی سفارشی برای داده‌های فرم
#
#     Args:
#         data: دیکشنری یا شیء request.POST
#         files: دیکشنری یا شیء request.FILES
#         rules: دیکشنری قوانین اعتبارسنجی
#
#     Returns:
#         dict: خطاهای اعتبارسنجی
#
#     Example:
#         rules = {
#             'users': ['required', 'min_items:1', 'max_items:5'],
#             'subject': ['required', 'min:10', 'max:200'],
#             'contact_email': ['required', 'email'],
#             'tags': ['required', 'min_items:1'],
#             'attachments': ['max_files:5', 'max_size:10']
#         }
#     """
#     errors = {}
#
#     if rules is None:
#         return errors
#
#     for field, field_rules in rules.items():
#         # دریافت مقدار فیلد با توجه به نوع آن
#         if field == "tags" or field == "users":
#             # برای فیلدهای multiple choice از getlist استفاده می‌کنیم
#             if hasattr(data, 'getlist'):
#                 value = data.getlist(field)
#             elif isinstance(data, dict):
#                 value = data.get(field, [])
#                 if not isinstance(value, list):
#                     value = [value] if value else []
#             else:
#                 value = []
#         elif field == "attachments":
#             # دریافت فایل‌های آپلود شده
#             if files:
#                 if hasattr(files, 'getlist'):
#                     value = files.getlist('attachments')
#                 elif isinstance(files, dict):
#                     value = files.get('attachments', [])
#                     if not isinstance(value, list):
#                         value = [value] if value else []
#                 else:
#                     value = []
#             else:
#                 value = []
#         else:
#             # برای فیلدهای عادی
#             if hasattr(data, 'get'):
#                 value = data.get(field)
#             elif isinstance(data, dict):
#                 value = data.get(field)
#             else:
#                 value = None
#
#         # اعتبارسنجی هر قانون
#         for rule in field_rules:
#             if ":" in rule:
#                 rule_name, param = rule.split(":", 1)
#             else:
#                 rule_name, param = rule, None
#
#             # قوانین اعتبارسنجی
#             if rule_name == "required":
#                 if field in ["tags", "users"]:
#                     # برای فیلدهای چند انتخابی
#                     if not value or len(value) == 0:
#                         errors[field] = f"The {field.replace('_', ' ')} field is required."
#                 elif field == "attachments":
#                     # برای فایل‌های پیوست
#                     if not value or len(value) == 0:
#                         errors[field] = f"The {field.replace('_', ' ')} field is required."
#                 else:
#                     # برای فیلدهای عادی
#                     if value is None or str(value).strip() == "":
#                         errors[field] = f"The {field.replace('_', ' ')} field is required."
#
#             elif rule_name == "min" and value and str(value).strip() != "":
#                 if len(str(value).strip()) < int(param):
#                     errors[field] = f"The {field.replace('_', ' ')} must be at least {param} characters long."
#
#             elif rule_name == "max" and value and str(value).strip() != "":
#                 if len(str(value).strip()) > int(param):
#                     errors[field] = f"The {field.replace('_', ' ')} must be less than {param} characters long."
#
#             elif rule_name == 'in' and value and str(value).strip() != "":
#                 allowed_values = [v.strip() for v in param.split(",")]
#                 if value not in allowed_values:
#                     errors[field] = f"The {field.replace('_', ' ')} must be one of {', '.join(allowed_values)}."
#
#             elif rule_name == 'future_date' and value and str(value).strip() != "":
#                 try:
#                     # تبدیل رشته به datetime
#                     dt_str = str(value).strip()
#                     if 'T' in dt_str:
#                         # فرمت ISO با زمان
#                         dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
#                     else:
#                         # فقط تاریخ
#                         from datetime import date
#                         dt = datetime.strptime(dt_str, '%Y-%m-%d')
#
#                     if dt <= datetime.now():
#                         errors[field] = f"The {field.replace('_', ' ')} date must be in the future."
#                 except (ValueError, AttributeError):
#                     errors[field] = f"The {field.replace('_', ' ')} must be a valid date."
#
#             elif rule_name == 'email' and value and str(value).strip() != "":
#                 email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#                 if not re.match(email_pattern, str(value)):
#                     errors[field] = f"Please enter a valid email address."
#
#             elif rule_name == 'phone' and value and str(value).strip() != "":
#                 phone_digits = re.sub(r'\D', '', str(value))
#                 if len(phone_digits) > 11:
#                     errors[field] = f"Phone number must be maximum 11 digits."
#                 elif len(phone_digits) < 10:
#                     errors[field] = f"Phone number must be at least 10 digits."
#
#             elif rule_name == 'min_items' and field in ["tags", "users"]:
#                 if len(value) < int(param):
#                     errors[field] = f"Please select at least {param} {field}."
#
#             elif rule_name == 'max_items' and field in ["tags", "users"]:
#                 if len(value) > int(param):
#                     errors[field] = f"You can select maximum {param} {field}."
#
#             elif rule_name == 'file_type' and field == "attachments" and value:
#                 allowed_types = [t.strip() for t in param.split(",")]
#                 for file in value:
#                     if hasattr(file, 'content_type') and file.content_type not in allowed_types:
#                         errors[field] = f"File {file.name} has unsupported type. Allowed: {', '.join(allowed_types)}"
#                         break
#
#             elif rule_name == 'max_size' and field == "attachments" and value:
#                 max_size_bytes = int(param) * 1024 * 1024  # تبدیل مگابایت به بایت
#                 for file in value:
#                     if hasattr(file, 'size') and file.size > max_size_bytes:
#                         errors[field] = f"File {file.name} exceeds {param} MB size limit."
#                         break
#
#             elif rule_name == 'max_files' and field == "attachments" and value:
#                 if len(value) > int(param):
#                     errors[field] = f"You can upload maximum {param} files."
#
#             elif rule_name == 'valid_users' and field == "users" and value:
#                 # اعتبارسنجی وجود کاربران در دیتابیس
#                 try:
#                     user_ids = [int(user_id) for user_id in value]
#                     existing_users = User.objects.filter(id__in=user_ids).count()
#                     if existing_users != len(user_ids):
#                         errors[field] = f"Some selected users are invalid."
#                 except (ValueError, TypeError):
#                     errors[field] = f"Invalid user selection."
#
#     return errors
#
#
# # تابع کمکی برای استفاده راحت‌تر
# def validate_ticket_form(data, files=None):
#     """
#     اعتبارسنجی فرم تیکت با قوانین پیش‌فرض
#     """
#     rules = {
#         'subject': ['required', 'min:10', 'max:200'],
#         'description': ['required', 'min:20'],
#         'contact_name': ['required', 'min:3', 'max:100'],
#         'contact_email': ['required', 'email'],
#         'contact_phone': ['required', 'phone'],
#         'priority': ['required', 'in:Low,Medium,High,Urgent'],
#         'category': ['required'],
#         'department': ['required'],
#         'max_replay_date': ['required', 'future_date'],
#         'due_date': ['future_date'],
#         'tags': ['required', 'min_items:1', 'max_items:5'],
#         'users': ['required', 'min_items:1', 'max_items:10', 'valid_users'],
#         'attachments': [
#             'max_files:5',
#             'max_size:10',  # 10MB
#             'file_type:application/pdf,image/jpeg,image/png,application/msword'
#         ]
#     }
#
#     return validate(data, files, rules)


import re
from datetime import datetime
from django.contrib.auth.models import User


def validate(data, files=None, rules=None):
    """
    اعتبارسنجی سفارشی برای داده‌های فرم

    Args:
        data: دیکشنری یا شیء request.POST
        files: دیکشنری یا شیء request.FILES
        rules: دیکشنری قوانین اعتبارسنجی

    Returns:
        dict: خطاهای اعتبارسنجی
    """
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
    """
    اعتبارسنجی فرم تیکت با قوانین پیش‌فرض
    """
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
