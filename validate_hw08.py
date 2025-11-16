#!/usr/bin/env python3
"""
Валідаційний скрипт для домашнього завдання 08
Перевіряє, що всі вимоги завдання були виконані:
1. Додані функції save_data() та load_data()
2. Використовується протокол pickle
3. Адекватна обробка помилок
4. Інтеграція в основний цикл програми
"""

import sys
import os
import inspect
import importlib.util
from pathlib import Path
import ast

def validate_hw08():
    """Перевіряє виконання всіх вимог домашнього завдання 08"""
    
    print("🔍 Перевірка домашнього завдання 08: Збереження даних")
    print("=" * 60)
    
    # Шлях до файлу завдання
    task_file = Path(__file__).parent / "task1" / "task1.py"
    
    if not task_file.exists():
        print("❌ Файл task1/task1.py не знайдено!")
        return False
    
    # Завантаження модуля
    spec = importlib.util.spec_from_file_location("task1", task_file)
    task_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(task_module)
    except Exception as e:
        print(f"❌ Помилка при завантаженні модуля: {e}")
        return False
    
    results = []
    
    # 1. Перевірка функції save_data
    print("\n1️⃣  Перевірка функції save_data():")
    if hasattr(task_module, 'save_data'):
        save_func = getattr(task_module, 'save_data')
        sig = inspect.signature(save_func)
        params = list(sig.parameters.keys())
        
        # Перевіряємо параметри
        if 'book' in params:
            print("   ✅ Функція save_data() знайдена з правильними параметрами")
            results.append(True)
        else:
            print("   ❌ Функція save_data() має неправильні параметри")
            results.append(False)
    else:
        print("   ❌ Функція save_data() не знайдена")
        results.append(False)
    
    # 2. Перевірка функції load_data
    print("\n2️⃣  Перевірка функції load_data():")
    if hasattr(task_module, 'load_data'):
        load_func = getattr(task_module, 'load_data')
        print("   ✅ Функція load_data() знайдена")
        results.append(True)
    else:
        print("   ❌ Функція load_data() не знайдена")
        results.append(False)
    
    # 3. Перевірка використання pickle
    print("\n3️⃣  Перевірка використання протоколу pickle:")
    with open(task_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'import pickle' in content or 'from pickle import' in content:
        print("   ✅ Протокол pickle імпортований")
        if 'pickle.dump' in content and 'pickle.load' in content:
            print("   ✅ Використовуються функції pickle.dump() та pickle.load()")
            results.append(True)
        else:
            print("   ❌ Не всі необхідні функції pickle використовуються")
            results.append(False)
    else:
        print("   ❌ Протокол pickle не імпортований")
        results.append(False)
    
    # 4. Перевірка обробки помилок
    print("\n4️⃣  Перевірка обробки помилок:")
    error_handlers = ['FileNotFoundError', 'PermissionError', 'pickle.PickleError']
    found_handlers = []
    
    for handler in error_handlers:
        if handler in content:
            found_handlers.append(handler)
    
    if len(found_handlers) >= 2:
        print(f"   ✅ Знайдено обробку помилок: {', '.join(found_handlers)}")
        results.append(True)
    else:
        print(f"   ⚠️  Знайдено лише частину обробників помилок: {', '.join(found_handlers)}")
        results.append(len(found_handlers) > 0)
    
    # 5. Перевірка інтеграції в main()
    print("\n5️⃣  Перевірка інтеграції в основний цикл:")
    if hasattr(task_module, 'main'):
        main_source = inspect.getsource(task_module.main)
        if 'load_data' in main_source and 'save_data' in main_source:
            print("   ✅ Функції збереження/завантаження інтегровані в main()")
            results.append(True)
        else:
            print("   ❌ Функції не інтегровані в main()")
            results.append(False)
    else:
        print("   ❌ Функція main() не знайдена")
        results.append(False)
    
    # 6. Перевірка зворотної сумісності
    print("\n6️⃣  Перевірка зворотної сумісності:")
    required_classes = ['AddressBook', 'Record', 'Name', 'Phone', 'Birthday']
    missing_classes = []
    
    for cls_name in required_classes:
        if not hasattr(task_module, cls_name):
            missing_classes.append(cls_name)
    
    if not missing_classes:
        print("   ✅ Всі необхідні класи присутні")
        results.append(True)
    else:
        print(f"   ❌ Відсутні класи: {', '.join(missing_classes)}")
        results.append(False)
    
    # 7. Перевірка CLI команд
    print("\n7️⃣  Перевірка CLI команд:")
    required_commands = ['add', 'change', 'phone', 'all', 'add-birthday', 'show-birthday', 'birthdays']
    
    # Аналіз AST для пошуку команд
    tree = ast.parse(content)
    found_commands = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Str):
            for cmd in required_commands:
                if cmd in node.s:
                    found_commands.append(cmd)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            for cmd in required_commands:
                if cmd in node.value:
                    found_commands.append(cmd)
    
    found_commands = list(set(found_commands))  # Унікальні значення
    
    if len(found_commands) >= 5:
        print(f"   ✅ Знайдено команди: {', '.join(found_commands)}")
        results.append(True)
    else:
        print(f"   ⚠️  Знайдено лише частину команд: {', '.join(found_commands)}")
        results.append(len(found_commands) > 3)
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТИ ВАЛІДАЦІЇ:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    status_emoji = "✅" if percentage >= 85 else "⚠️" if percentage >= 70 else "❌"
    
    print(f"{status_emoji} Пройдено тестів: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 85:
        print("🎉 Домашнє завдання 08 виконано успішно!")
        grade = "ВІДМІННО"
    elif percentage >= 70:
        print("👍 Домашнє завдання 08 виконано добре з незначними зауваженнями")
        grade = "ДОБРЕ"
    else:
        print("📝 Домашнє завдання 08 потребує доопрацювання")
        grade = "ПОТРЕБУЄ ДООПРАЦЮВАННЯ"
    
    print(f"\n🏆 ОЦІНКА: {grade}")
    
    return percentage >= 85

if __name__ == "__main__":
    success = validate_hw08()
    sys.exit(0 if success else 1)