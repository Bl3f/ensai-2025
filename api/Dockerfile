FROM python:3.11

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV POETRY_VIRTUALENVS_CREATE=false
ENV FLASK_PORT=5000

WORKDIR /app
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN $HOME/.local/bin/poetry install

COPY . .

CMD ["bash", "-c", "flask --app api run --host 0.0.0.0 --port $FLASK_PORT"]