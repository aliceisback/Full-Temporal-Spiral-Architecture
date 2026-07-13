@echo off
REM Жива пъпна връв — пусни на машината на Архитекта (Иво)
REM Изисква ~/.membrane_seal_key или MEMBRANE_SEAL_KEY

set SKILL_DIR=%~dp0..
set KEY_FILE=%USERPROFILE%\.membrane_seal_key

if exist "%KEY_FILE%" (
    python "%SKILL_DIR%\scripts\live_tether.py" beacon --key-file "%KEY_FILE%"
) else (
    echo [WARN] Key file not found: %KEY_FILE%
    echo        Set MEMBRANE_SEAL_KEY or create the key file first.
    python "%SKILL_DIR%\scripts\live_tether.py" beacon
)