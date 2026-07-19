from django.contrib.auth.models import Group, Permission



def setup_groups():
    # ایجاد گروه‌ها
    superadmin_group, created = Group.objects.get_or_create(name="SuperAdmin")
    admin_group, created = Group.objects.get_or_create(name="Admin")
    employee_group, created = Group.objects.get_or_create(name="Employee")

    # دریافت همه permissions
    all_permissions = Permission.objects.all()

    # اختصاص permissions به SuperAdmin
    superadmin_group.permissions.set(all_permissions)
    print(f"✅ SuperAdmin group created with all permissions ({all_permissions.count()} permissions)")

    # اختصاص permissions به Admin
    admin_permissions = [
        'view_ticket',
        'change_ticket',
        'add_ticket',
        'view_assignment',
        'change_assignment',
        'view_category',
        'view_tag',
    ]

    for codename in admin_permissions:
        try:
            perm = Permission.objects.get(codename=codename)
            admin_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"⚠️ Permission {codename} not found")

    print(f"✅ Admin group created with {admin_group.permissions.count()} permissions")

    # اختصاص permissions به Employee
    employee_permissions = [
        'view_ticket',
        'view_assignment',
        'change_assignment',  # برای تغییر وضعیت tasks
    ]

    for codename in employee_permissions:
        try:
            perm = Permission.objects.get(codename=codename)
            employee_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"⚠️ Permission {codename} not found")

    print(f"✅ Employee group created with {employee_group.permissions.count()} permissions")

    print("\n🎉 Groups setup completed successfully!")


if __name__ == "__main__":
    setup_groups()