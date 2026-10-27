# School Management System — Dashboard

Nadiif ah, xirfad leh, una diyaarsan isticmaalka dhabta ah.

---

## Fayl-yada la siiyey

```
school_dashboard/
├── templates/
│   └── dashboard/
│       ├── base.html          ← Template-ka asaasiga ah (extend this)
│       └── index.html         ← Dashboard home page
├── static/
│   ├── css/
│   │   └── dashboard.css      ← Dhammaan styles
│   └── js/
│       └── dashboard.js       ← Mobile menu + auto-dismiss messages
└── preview.html               ← Muuqaalka HTML-ka nadiifka ah
```

---

## Django Xiriirinta (Integration)

### 1. Settings.py

```python
TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / 'templates'],
        ...
    }
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 2. URL Patterns

Sidebar-ku wuxuu isticmaalaa URL names sidan:

| URL Name              | App      |
|-----------------------|----------|
| `dashboard:home`      | dashboard |
| `dashboard:activity`  | dashboard |
| `students:list`       | students  |
| `students:add`        | students  |
| `teachers:list`       | teachers  |
| `teachers:add`        | teachers  |
| `classes:list`        | classes   |
| `classes:add`         | classes   |
| `subjects:list`       | subjects  |
| `subjects:add`        | subjects  |
| `attendance:index`    | attendance |
| `attendance:mark`     | attendance |
| `exams:list`          | exams     |
| `exams:add`           | exams     |
| `results:list`        | results   |
| `fees:list`           | fees      |
| `fees:collect`        | fees      |
| `reports:index`       | reports   |
| `reports:generate`    | reports   |
| `users:list`          | users     |
| `settings:index`      | settings  |
| `notices:list`        | notices   |
| `notifications:list`  | notifications |
| `auth:logout`         | auth      |

### 3. Dashboard View (views.py)

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date

@login_required
def dashboard_home(request):
    context = {
        'today': date.today(),
        # Ku dar qiimayaasha ka timid database-ka:
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classes':  Class.objects.count(),
        'total_subjects': Subject.objects.count(),
        # Dhaqdhaqaaqyada dambe:
        'recent_activities': ActivityLog.objects.order_by('-created_at')[:8],
        # Ogeysiisyada:
        'notices': Notice.objects.filter(active=True)[:3],
        # Ogeysiisyada aan la aqrin:
        'unread_notifications_count': request.user.notifications.filter(read=False).count(),
    }
    return render(request, 'dashboard/index.html', context)
```

### 4. Template Extending (Tusaale: Ardayda)

```html
{% extends "dashboard/base.html" %}
{% load static %}

{% block title %}Ardayda{% endblock %}
{% block nav_students %}active{% endblock %}

{% block breadcrumb %}
  <a href="{% url 'dashboard:home' %}">Dashboard</a>
  <span class="breadcrumb-sep">/</span>
  <span class="breadcrumb-current">Ardayda</span>
{% endblock %}

{% block content %}
  <!-- Xogta ardayda halkan ku qor -->
{% endblock %}
```

### 5. School Name

`base.html` waxa ku jira:
```html
{% block school_name %}Dugsiga{% endblock %}
```

View-ga ama URL-ka waxaad ku beddeli kartaa magaca dhabta ah:
```html
{% block school_name %}Al-Nuur Primary School{% endblock %}
```

---

## Activity Log (Tusaale Model)

```python
class ActivityLog(models.Model):
    COLOR_CHOICES = [
        ('blue',   'Blue'),
        ('green',  'Green'),
        ('amber',  'Amber'),
        ('violet', 'Violet'),
    ]
    text       = models.CharField(max_length=255)
    color      = models.CharField(max_length=10, choices=COLOR_CHOICES, default='blue')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

---

## CSS Classes Reference

| Class | Isticmaalka |
|-------|-------------|
| `.btn.btn-primary` | Badhanka caadigga ah |
| `.btn.btn-outline` | Badhanka xuduudda leh |
| `.btn.btn-ghost`   | Badhanka cad |
| `.btn-sm`          | Cabbirka yar |
| `.badge-blue/green/amber/rose/gray` | Status badges |
| `.notice.info/success/warn` | Ogeysiisyada |
| `.card` + `.card-header` + `.card-body` | Card container |
| `.empty-state`     | Marka xog la'aan jirto |
| `.stats-grid`      | 4-tiir stats |
| `.two-col-grid`    | 2-tiir layout |
