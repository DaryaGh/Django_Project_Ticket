from datetime import datetime


def validate(data,rules):
    errors = {}
    for field,field_rules in rules.items():
        value = data.get(field)
        for rule in field_rules:
            if ":" in rule:
                rule_name, param = rule.split(":",1)
            else:
                rule_name, param = rule, None


            if rule_name == "required" and (value is  None or str(value).strip() == ""):
                errors[field] = f"The {field.replace('_','')} field is required."

            elif rule_name == "min" and (value is None or len(str(value)) < int(param)):
                errors[field] = f"The {field.replace('_','')} must be a least {param} character long."

            elif rule_name == "max" and (value is None or len(str(value)) > int(param)):
                errors[field] = f"The {field.replace('_', '')} must be a greater than {param} character long."

            elif rule_name == 'in' and value and value not in param.split(","):
                errors[field] = f"The {field.replace('_', '')} must be a one of {param} ."

            elif rule_name == 'future_date' and value:
                try:
                    dt = datetime.fromisoformat(value)
                    if dt <=datetime.now():
                        errors[field] = f"The {field.replace('_','')} date must be in the future."
                except Exception:
                    errors[field] = f"The {field.replace('_','')} must be valid date."

            # elif rule_name == 'min_items' and value :
            #     if len(value.getlist(field)) < int(param):
            #         errors[field] = f"The please select at least {param} tags."
            #
            # elif rule_name == 'max_items' and value :
            #     if len(value.getlist(field)) > int(param):
            #         errors[field] = f"You can max of {param} tags."
    return errors