FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Use enhanced processing by default, fallback to simple if needed
CMD ["python", "process_pdfs_enhanced.py"]