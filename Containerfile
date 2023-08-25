FROM python:3.11-slim-bookworm
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["specification_extraction"]
