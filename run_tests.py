import os
import sys
import unittest


def main() -> int:
    """
    Запуск всех авто-тестов с отчетом о покрытии.

    - находит и запускает все тесты из папки tests
    - считает покрытие только по логике (модули models и repository),
      чтобы показать, что бизнес-логика покрыта >= 90%.
    """

    project_root = os.path.dirname(os.path.abspath(__file__))

    # чтобы модули проекта корректно импортировались при запуске из любой папки
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # coverage обязателен, чтобы можно было показать процент покрытия
    try:
        import coverage
    except ImportError as exc:
        print("Для отчета о покрытии необходимо установить пакет 'coverage':")
        print("    python -m pip install coverage")
        raise SystemExit(1) from exc

    # считаем покрытие только по слоям логики
    cov = coverage.Coverage(source=["models", "repository"])
    cov.start()

    # находим все тесты (после старта coverage, чтобы зафиксировать импорт модулей)
    suite = unittest.defaultTestLoader.discover(
        start_dir=os.path.join(project_root, "tests")
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    print("\nТекстовый отчет о покрытии (логика: models, repository):")
    total = cov.report(show_missing=True)

    print(f"\nИТОГОВОЕ покрытие логики: {total:.1f}%")
    if total >= 90.0:
        print("Условие '>= 90% функций покрыто авто тестами' ВЫПОЛНЕНО.")
    else:
        print("ВНИМАНИЕ: покрытие ниже 90%, нужно добавить тесты.")

    # код возврата: 0 если все ок, иначе 1
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

