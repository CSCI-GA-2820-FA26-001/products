FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install runtime dependencies from the committed lock file.
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && \
    pipenv sync --system && \
    pip cache purge

RUN useradd --uid 1001 --create-home appuser
COPY --chown=appuser:appuser service ./service
COPY --chown=appuser:appuser wsgi.py ./

USER appuser
EXPOSE 8080

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile - wsgi:app"]
