PRIORITY_CHOICES = [
    ("", "Select Priority"),
    ("low", 'Low'),
    ("middle", 'Middle'),
    ("high", 'High'),
    ('secret', 'Secret')
]

DEPARTMENT_CHOICES = [
    ("", "Select Department"),
    ('developer', 'Developer'),
    ('fullstack', 'Full Stack'),
    ("python", 'Python'),
    ("django", 'Django'),
    ('react', 'React'),
]

PRIORITY_COLORS = {
    "low": '#198754',
    "middle": '#0d6efd',
    "high": '#dc3545',
}

STATUS_CHOICES = [
    ("new", "New"),
    ("in-progress", "In Progress"),
    ("solved", "Solved"),
    ("impossible", "Impossible"),
]

STATUS_COLORS = {
    "new": "#0dcaf0",
    "in-progress": "#0d6efd",
    "solved": "#198754",
    "impossible": "#dc3545",
}

EMAIL_CHOICES = [
    ("yahoo.com", "Yahoo.com"),
    ("gmail.com", "Gmail.com"),
    ("hotmail.com", "Hotmail.com"),
]
