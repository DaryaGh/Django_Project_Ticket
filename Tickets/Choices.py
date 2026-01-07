PRIORITY_CHOICES = [
    ("low", 'Low'),
    ("middle", 'Middle'),
    ("high", 'High'),
    ('secret', 'Secret'),
    ('critical', 'Critical'),
]

PRIORITY_COLORS = {
    "low": '#6a994e',
    "middle": '#1d3557',
    "high": '#800e13',
    'secret':'#ee6c4d',
    'critical': '#ef476f',
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

RESPONSE_STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('seen', 'Seen'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]

RESPONSE_STATUS_COLORS = {
    "sent": "#bb8588",
    "seen": "#dc2f02",
    "read": "#5e503f",
    "replied": "#656d4a",
}

DEPARTMENT_CHOICES = [
    ('developer', 'Developer'),
    ('fullstack', 'Full Stack'),
    ("python", 'Python'),
    ("django", 'Django'),
    ('react', 'React'),
]

DEPARTMENT_COLORS = {
    'developer': '#007ea7',
    'fullstack': '#7b2cbf',
    'python': '#ff7d00',
    'django': '#274c77',
    'react': '#fee440',
}

EMAIL_CHOICES = [
    ("yahoo.com", "Yahoo.com"),
    ("gmail.com", "Gmail.com"),
    ("hotmail.com", "Hotmail.com"),
]

ACTION_CHOICES = [
    ("view" , "View"),
    ("create" , "Create"),
    ("update" , "Update"),
    ("delete" , "Delete"),
    # ("status_change" , "Change Status"),
]
