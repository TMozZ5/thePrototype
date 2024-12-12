FROM python:3.10-slim
WORKDIR /prototype
COPY . /app
RUN pip install --no-cache-dir -r "/app/.github/workflows/dependencies.txt"
EXPOSE 8000
CMD ["python", "main.py"]
