FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY='django-insecure-8ry#q14f=9i(uf=9((^57=ckmzu!p3!zmycugp3b9iuc#wxy$w'
ENV SECRET="QYmXTKt6bnzaFi76H7R88FQ"
ENV DB_NAME=''
ENV DB_USER=''
ENV DB_PASSWORD=''
ENV DB_HOST=''
ENV DB_PORT=''

# Install Python dependencies
RUN pip install --upgrade pip && pip install gunicorn

WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "-w", "4", "library_manager.wsgi:application", "-b", "0.0.0.0:8000"]
