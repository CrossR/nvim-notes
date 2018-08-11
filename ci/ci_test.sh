SUCCESS=0
FAIL=1

echo "Starting testing script..."

if [ "${LINT_CODE:-0}" -eq 1 ]; then
    echo "Linting code..."
    pipenv run pylint rplugin/python3/nvim_diary_template 

    echo "Checking code syntax with Black..."
    pipenv run black rplugin/python3/deoplete --check

    if [ $? -ne 0 ]; then
        echo "Deoplete failed black check..."
        exit ${FAIL}
    fi

    pipenv run black rplugin/python3/nvim_diary_template --check

    if [ $? -ne 0 ]; then
        echo "Main code failed black check..."
        exit ${FAIL}
    fi
fi

if [ "${FULL_TYPING:-0}" -eq 1 ]; then
    echo "Running full mypy on code base..."
    pipenv run mypy rplugin/python3/nvim_diary_template --strict --ignore-missing-imports
    false # Should return 0 every time, meaning the CI doesn't stop
fi

if [ "${BASIC_TYPING-0}" -eq 1 ]; then
    echo "Running basic mypy on code base..."
    pipenv run mypy --config-file mypy.ini rplugin/python3/nvim_diary_template
fi

echo "Script finished!"
exit ${SUCCESS}