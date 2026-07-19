# ============================================================
# Dockerfile — offline build (packages pre-downloaded)
#
# All .whl files are in ./packages/ — pip installs from disk.
# No internet connection needed inside Docker at build time.
# This is the reliable solution for slow/unstable connections.
# ============================================================

FROM python:3.12-slim

WORKDIR /app

# Copy pre-downloaded wheels into the image
COPY packages/ /packages/

# Install from local wheels — no network calls at all
RUN pip install --no-index --find-links=/packages /packages/*.whl

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
