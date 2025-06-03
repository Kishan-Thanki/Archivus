# Archivus

## Project Setup & Environment

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/archivus.git
cd archivus
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🔐 Environment Variables
Create .env in project root (beside manage.py):

### Git Workflow
>#### Branching:
>    - main: Production releases
> 
>    - develop: Active development
> 
>    - feature/*: Feature branches

>#### Common Commands:
> ##### Sync with develop
>   - git checkout develop
>   - git pull origin develop
>
> ##### Create feature branch
>   - git checkout -b feature/your-feature
>
> ##### Commit changes
>   - git add .
>   - git commit -m "Descriptive message"
>   - git push origin feature/your-feature

### Running Locally:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Access admin at: http://127.0.0.1:8000/admin/

### Collect Static:
```bash
python manage.py collectstatic
```

### Project Structure:
```bash
archivus/
├── archivus/          # Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/ 
│   ├── forms         # Reusable class components.
│   ├── middleware
│   ├── migrations
│   ├── mixins
│   ├── permissions
│   ├── serializers
│   ├── services
│   ├── tests
│   ├── urls
│   ├── validators
│   ├── views
│   ├── _init__.py
│   ├── admin.py
│   └── apps.py
├── static/ 
├── staticfiles/      # Collected static files
├── .env              # Local environment
├── .gitignore
├── Procfile
├── README.md
├── manage.py
└── requirement.txt
```