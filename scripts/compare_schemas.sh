#!/bin/bash
echo "=== Сравнение схем БД TEST и STAGE ==="

TEST_DB="/data/medical_cooperative.db"
STAGE_DB="/data/medical_cooperative.db"

# Экспорт схем
sqlite3 "$TEST_DB" .schema > /tmp/test_schema.sql
ssh kachmazov@172.20.10.8 "sqlite3 $STAGE_DB .schema" > /tmp/stage_schema.sql

# Сравнение
if diff /tmp/test_schema.sql /tmp/stage_schema.sql > /tmp/schema_diff.txt; then
    echo " Схемы идентичны"
    exit 0
else
    echo "  Схемы различаются:"
    cat /tmp/schema_diff.txt
    echo ""
    echo " Запуск Flyway для применения миграций на STAGE..."
    exit 1
fi
