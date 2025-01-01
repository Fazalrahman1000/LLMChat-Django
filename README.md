# LLMChat-Django-
This is the chatbot application like LLMChatBot in streamlit framework but this created in Django framework.
steps to open: 
create virtual environment (python -m venv env).
activate virtual environment (win: env/Scripts/activate)(mac: source/bin/activate).
Install Django (pip install django).
install all required libraries (pip install PyPDF2 faiss-cpu sentence-transformers groq numpy).
create super user (python manage.py createsuperuser) name: admin/ password: admin123
make migration (python manage.py makemigrations) and (python manage.py migrate)
run django server (python manage.py runserver)
use chat project
if you have any problem ask on issues
