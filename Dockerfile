FROM python:3.12-alpine

WORKDIR /app

COPY script/fetch_weather.py .

# Varnostna izboljšava: ustvarimo uporabnika, ki ne bo imel root privilegijev.
RUN adduser -D appuser \
    && mkdir -p /app/output \
    && chown -R appuser:appuser /app

USER appuser

ENV OUTPUT_DIR=/app/output
VOLUME ["/app/output"]

# Container ob zagonu počaka v shellu. 
# To bi lahko izboljšali z entrypoint, ki bi ob zagonu izvedla skripto.
CMD ["sh"]
