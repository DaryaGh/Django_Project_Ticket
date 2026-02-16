from django.contrib.auth.models import Group, Permission, User


ROLE_ORDER = {
    "SuperAdmin": 1,
    "Admin": 2,
    "Employee": 3,
}


def get_role(user):
    """دریافت نقش کاربر بر اساس Group"""
    if user.is_superuser:
        return "SuperAdmin"

    # پیدا کردن اولین گروه کاربر
    group = user.groups.first()
    return group.name if group else None


def get_role_level(user):
    """دریافت سطح نقش کاربر"""
    role = get_role(user)
    if role in ROLE_ORDER:
        return ROLE_ORDER[role]
    return None


def can_assign_ticket(assigner, assignee) -> bool:
    """بررسی آیا کاربر می‌تواند به کاربر دیگر تیکت assign کند"""
    role_from = get_role(assigner)
    role_to = get_role(assignee)

    if not role_from or not role_to:
        return False

    # SuperAdmin می‌تواند به همه assign کند
    if role_from == "SuperAdmin":
        return True

    # بقیه فقط به کاربران با سطح پایین‌تر یا مساوی می‌توانند assign کنند
    return ROLE_ORDER[role_from] <= ROLE_ORDER[role_to]



def get_assignees(assigner):
    """دریافت QuerySet از کاربرانی که assigner می‌تواند به آن‌ها تیکت assign کند"""
    from django.contrib.auth.models import User

    # فقط کاربرانی که حداقل یک Group دارند
    users_with_groups = User.objects.filter(
        is_active=True,
        groups__isnull=False  # این شرط تضمین می‌کند کاربر حداقل یک Group دارد
    ).exclude(id=assigner.id).distinct()

    if is_superadmin(assigner):
        # SuperAdmin می‌تواند به همه کاربران دارای Group assign کند
        return users_with_groups

    role_from = get_role(assigner)
    if not role_from:
        return User.objects.none()

    assigner_level = ROLE_ORDER.get(role_from)

    # فیلتر کردن بر اساس سطح نقش
    allowed_roles = []
    for role_name, level in ROLE_ORDER.items():
        if level >= assigner_level:  # سطح پایین‌تر یا مساوی
            allowed_roles.append(role_name)

    # فیلتر نهایی: کاربران دارای Group که نقش‌های مجاز دارند
    return users_with_groups.filter(
        groups__name__in=allowed_roles
    ).distinct()

def get_user_permissions(user):
    """دریافت همه permissions کاربر"""
    if user.is_superuser:
        return Permission.objects.all()

    # permissions از طریق groups
    group_permissions = Permission.objects.filter(group__user=user)

    # permissions اختصاصی کاربر
    user_permissions = user.user_permissions.all()

    return group_permissions.union(user_permissions).distinct()


def has_permission(user, codename):
    """بررسی آیا کاربر permission خاصی دارد"""
    if user.is_superuser:
        return True

    return user.has_perm(f"Tickets.{codename}")


def can_create_ticket(user):
    """بررسی آیا کاربر می‌تواند تیکت ایجاد کند"""
    # Employees نمی‌توانند تیکت ایجاد کنند
    role = get_role(user)
    if role == "Employee":
        return False
    return True


def can_edit_ticket(user, ticket):
    """بررسی آیا کاربر می‌تواند تیکت را ویرایش کند"""
    if user.is_superuser:
        return True

    role = get_role(user)

    # Admin فقط تیکت‌های خودش را می‌تواند ویرایش کند
    if role == "Admin":
        return ticket.created_by == user

    # بقیه فقط اگر creator باشند
    return ticket.created_by == user


def can_delete_ticket(user, ticket):
    """بررسی آیا کاربر می‌تواند تیکت را حذف کند"""
    if user.is_superuser:
        return True

    role = get_role(user)

    # Admin فقط تیکت‌های خودش را می‌تواند حذف کند
    if role == "Admin":
        return ticket.created_by == user

    # Employee فقط تیکت‌های خودش را می‌تواند حذف کند
    if role == "Employee":
        return ticket.created_by == user

    # بقیه فقط اگر creator باشند
    return ticket.created_by == user


def is_superadmin(user):
    """بررسی آیا کاربر SuperAdmin است"""
    if user.is_superuser:
        return True

    superadmin_group = Group.objects.filter(name="SuperAdmin").first()
    if superadmin_group and superadmin_group in user.groups.all():
        return True

    return False


def is_admin(user):
    """بررسی آیا کاربر Admin است"""
    if is_superadmin(user):
        return True  # SuperAdmin هم می‌تواند کارهای Admin را انجام دهد

    admin_group = Group.objects.filter(name="Admin").first()
    if admin_group and admin_group in user.groups.all():
        return True

    return False


def is_employee(user):
    """بررسی آیا کاربر Employee است"""
    employee_group = Group.objects.filter(name="Employee").first()
    if employee_group and employee_group in user.groups.all():
        return True

    return False


def get_user_role_display(user):
    """دریافت نام نمایشی نقش کاربر"""
    if is_superadmin(user):
        return "Super Admin"
    elif is_admin(user):
        return "Admin"
    elif is_employee(user):
        return "Employee"
    else:
        return "User"


def can_view_all_tickets(user):
    """بررسی آیا کاربر می‌تواند همه تیکت‌ها را ببیند"""
    return is_superadmin(user)


def can_view_assignment(user, assignment):
    """بررسی آیا کاربر می‌تواند assignment را ببیند"""
    if is_superadmin(user):
        return True

    # اگر کاربر assignee است
    if assignment.assignee == user:
        return True

    # اگر کاربر ایجادکننده assignment است
    if assignment.assigned_by == user:
        return True

    return False


def can_change_assignment_status(user, assignment):
    """بررسی آیا کاربر می‌تواند وضعیت assignment را تغییر دهد"""
    if is_superadmin(user):
        return True

    # اگر کاربر assignee است
    if assignment.assignee == user:
        return True

    return False