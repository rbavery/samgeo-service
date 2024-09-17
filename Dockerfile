FROM giswqs/segment-geospatial:v0.11.0
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="${PATH}:/home/user/.local/bin"
ENV LANG C.UTF-8

USER root
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py
RUN pip install --no-cache-dir --root-user-action=ignore torch==2.3.1+cu121 torchvision==0.18.1+cu121 torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libegl1 \
    libgles2 \
    libopengl0

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r /app/requirements.txt

COPY ./app /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]