# Alembic 마이그레이션 가이드

## Alembic 설정 완료

Alembic이 설정되었습니다! 이제 데이터베이스 마이그레이션을 생성하고 실행할 수 있습니다.

## 1단계: 첫 마이그레이션 생성

Backend 컨테이너에서 다음 명령어를 실행하세요:

```bash
docker exec -it stocktheme-backend alembic revision --autogenerate -m "create initial tables"
```

이 명령어는:
- ORM 모델을 분석하여 자동으로 마이그레이션 스크립트 생성
- `alembic/versions/` 폴더에 새 파일 생성
- `themes`, `stocks`, `theme_stocks` 테이블 생성 코드 포함

## 2단계: 마이그레이션 실행

생성된 마이그레이션을 데이터베이스에 적용하세요:

```bash
docker exec -it stocktheme-backend alembic upgrade head
```

이 명령어는:
- 생성된 마이그레이션 스크립트를 PostgreSQL에 실행
- 실제로 테이블이 생성됨
- `alembic_version` 테이블에 현재 버전 기록

## 3단계: 테이블 확인

PostgreSQL에서 테이블이 생성되었는지 확인:

```bash
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme
```

PostgreSQL 내부에서:
```sql
-- 모든 테이블 확인
\dt

-- themes 테이블 구조 확인
\d themes

-- stocks 테이블 구조 확인
\d stocks

-- theme_stocks 테이블 구조 확인
\d theme_stocks

-- 종료
\q
```

**예상 출력:**
```
              List of relations
 Schema |      Name       | Type  |   Owner   
--------+-----------------+-------+-----------
 public | alembic_version | table | stockuser
 public | theme_stocks    | table | stockuser
 public | themes          | table | stockuser
 public | stocks          | table | stockuser
```

## 추가 Alembic 명령어

### 현재 마이그레이션 버전 확인
```bash
docker exec -it stocktheme-backend alembic current
```

### 마이그레이션 히스토리 확인
```bash
docker exec -it stocktheme-backend alembic history
```

### 특정 버전으로 다운그레이드
```bash
docker exec -it stocktheme-backend alembic downgrade -1  # 한 단계 뒤로
docker exec -it stocktheme-backend alembic downgrade base  # 처음으로
```

### 새 마이그레이션 생성 (모델 변경 후)
```bash
docker exec -it stocktheme-backend alembic revision --autogenerate -m "description"
```

## 문제 해결

### 오류: "Can't locate revision identified by..."
마이그레이션 히스토리가 꼬인 경우:
```bash
# alembic_version 테이블 확인
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme -c "SELECT * FROM alembic_version;"

# 필요시 초기화
docker exec -it stocktheme-postgres psql -U stockuser -d stocktheme -c "TRUNCATE alembic_version;"
```

### 오류: "Target database is not up to date"
```bash
docker exec -it stocktheme-backend alembic stamp head
```

### 모델 import 오류
`alembic/env.py`에서 모든 모델이 import되었는지 확인:
```python
from app.models import Theme, Stock, ThemeStock
```

## 다음 단계

마이그레이션이 성공적으로 완료되면:
1. ✅ 데이터베이스 테이블 생성 완료
2. ✅ ORM 모델 준비 완료
3. 📝 다음: API 엔드포인트 개발 시작
