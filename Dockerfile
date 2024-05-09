# Dockerfile
FROM python:3.12

WORKDIR /app

# 필요한 패키지를 미리 설치합니다.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 코드를 복사합니다.
COPY . .

# Flask 애플리케이션 실행
CMD ["python", "app.py"]
