#!/usr/bin/env python3
"""
Демонстрація функціональності збереження даних для домашнього завдання 08
Показує:
1. Створення адресної книги
2. Додавання контактів
3. Збереження в файл
4. Завантаження з файла
5. Перевірка цілісності даних
"""

import sys
import os
from pathlib import Path

# Додаємо шлях до модуля task1
sys.path.insert(0, str(Path(__file__).parent / "task1"))

try:
    from task1 import AddressBook, Record, Name, Phone, Birthday, save_data, load_data
    import pickle
    from datetime import datetime, date
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

def demonstrate_persistence():
    """Демонструє функціональність збереження даних"""
    
    print("🎯 Демонстрація збереження даних (Домашнє завдання 08)")
    print("=" * 70)
    
    # 1. Створюємо адресну книгу та додаємо контакти
    print("\n1️⃣  Створення адресної книги з тестовими даними:")
    book = AddressBook()
    
    # Додаємо кілька контактів з різними даними
    contacts_data = [
        ("Іван Петров", ["1234567890"], "15.03.1990"),
        ("Марія Коваленко", ["0987654321", "0501234567"], "22.07.1985"),
        ("Олексій Шевченко", ["0631112233"], None),
        ("Анна Мельник", ["0442345678"], "08.12.1992"),
        ("Дмитро Іванов", ["0509876543", "0672345678"], "03.05.1988")
    ]
    
    for name, phones, birthday in contacts_data:
        record = Record(name)
        
        # Додаємо телефони
        for phone in phones:
            record.add_phone(phone)
        
        # Додаємо день народження, якщо є
        if birthday:
            record.add_birthday(birthday)
        
        book.add_record(record)
        print(f"   ✅ Додано контакт: {name} ({len(phones)} тел.{', ДН: ' + birthday if birthday else ''})")
    
    print(f"\n📊 Створено адресну книгу з {len(book)} контактами")
    
    # 2. Збереження в файл
    print("\n2️⃣  Збереження адресної книги в файл:")
    demo_file = "demo_addressbook.pkl"
    
    try:
        save_data(book, demo_file)
        file_size = Path(demo_file).stat().st_size
        print(f"   ✅ Дані збережено в файл '{demo_file}' (розмір: {file_size} байт)")
    except Exception as e:
        print(f"   ❌ Помилка збереження: {e}")
        return False
    
    # 3. Очищуємо поточну книгу
    print("\n3️⃣  Очищення поточної адресної книги:")
    original_count = len(book)
    book.data.clear()
    print(f"   📝 Книга очищена (було {original_count} контактів, залишилось {len(book)})")
    
    # 4. Завантаження з файла
    print("\n4️⃣  Завантаження адресної книги з файла:")
    
    try:
        loaded_book = load_data(demo_file)
        if loaded_book:
            print(f"   ✅ Дані успішно завантажено з файла")
            print(f"   📊 Завантажено {len(loaded_book)} контактів")
        else:
            print("   ❌ Не вдалося завантажити дані")
            return False
    except Exception as e:
        print(f"   ❌ Помилка завантаження: {e}")
        return False
    
    # 5. Перевірка цілісності даних
    print("\n5️⃣  Перевірка цілісності завантажених даних:")
    
    integrity_checks = []
    
    # Перевіряємо кількість контактів
    if len(loaded_book) == original_count:
        print(f"   ✅ Кількість контактів збережена ({len(loaded_book)})")
        integrity_checks.append(True)
    else:
        print(f"   ❌ Кількість контактів не збігається (було {original_count}, завантажено {len(loaded_book)})")
        integrity_checks.append(False)
    
    # Перевіряємо конкретні контакти
    test_contacts = ["Іван Петров", "Марія Коваленко", "Анна Мельник"]
    
    for contact_name in test_contacts:
        if contact_name in loaded_book.data:
            record = loaded_book.data[contact_name]
            phones = [phone.value for phone in record.phones]
            if record.birthday:
                if isinstance(record.birthday.value, str):
                    birthday = record.birthday.value
                else:
                    birthday = record.birthday.value.strftime("%d.%m.%Y")
            else:
                birthday = "Немає"
            
            print(f"   ✅ {contact_name}: {len(phones)} тел., ДН: {birthday}")
            integrity_checks.append(True)
        else:
            print(f"   ❌ Контакт '{contact_name}' не знайдено")
            integrity_checks.append(False)
    
    # 6. Демонстрація збереження після модифікацій
    print("\n6️⃣  Демонстрація збереження після модифікацій:")
    
    # Додаємо новий контакт
    new_record = Record("Тестовий Користувач")
    new_record.add_phone("1111111111")
    new_record.add_birthday("01.01.2000")
    loaded_book.add_record(new_record)
    
    print(f"   📝 Додано новий контакт: Тестовий Користувач")
    
    # Зберігаємо оновлену книгу
    modified_file = "demo_modified.pkl"
    save_data(loaded_book, modified_file)
    print(f"   ✅ Оновлена книга збережена в '{modified_file}'")
    
    # Завантажуємо та перевіряємо
    final_book = load_data(modified_file)
    if "Тестовий Користувач" in final_book.data:
        print(f"   ✅ Новий контакт успішно збережено та завантажено")
        integrity_checks.append(True)
    else:
        print(f"   ❌ Новий контакт не збережено")
        integrity_checks.append(False)
    
    # 7. Демонстрація обробки помилок
    print("\n7️⃣  Демонстрація обробки помилок:")
    
    # Спроба завантажити неіснуючий файл
    missing_book = load_data("nonexistent_file.pkl")
    if missing_book is None or len(missing_book) == 0:
        print("   ✅ Правильно оброблено відсутність файла")
        integrity_checks.append(True)
    else:
        print("   ❌ Неправильна обробка відсутнього файла")
        integrity_checks.append(False)
    
    # Спроба зберегти в неіснуючу директорію (буде створена)
    nested_file = "test_dir/nested_book.pkl"
    try:
        save_data(loaded_book, nested_file)
        if Path(nested_file).exists():
            print("   ✅ Правильно створено директорію для збереження")
            integrity_checks.append(True)
        else:
            print("   ❌ Не вдалося створити директорію")
            integrity_checks.append(False)
    except Exception as e:
        print(f"   ⚠️  Обробка створення директорії: {e}")
        integrity_checks.append(False)
    
    # Підсумок
    print("\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТИ ДЕМОНСТРАЦІЇ:")
    print("=" * 70)
    
    passed_checks = sum(integrity_checks)
    total_checks = len(integrity_checks)
    success_rate = (passed_checks / total_checks) * 100
    
    status_emoji = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 75 else "❌"
    
    print(f"{status_emoji} Успішних перевірок: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 Функціональність збереження даних працює ідеально!")
        result_status = "ВІДМІННО"
    elif success_rate >= 75:
        print("👍 Функціональність збереження даних працює добре")
        result_status = "ДОБРЕ"  
    else:
        print("📝 Функціональність збереження даних потребує перевірки")
        result_status = "ПОТРЕБУЄ ПЕРЕВІРКИ"
    
    print(f"\n🏆 СТАТУС: {result_status}")
    
    # Очищення демо-файлів
    print(f"\n🧹 Очищення демонстраційних файлів:")
    demo_files = [demo_file, modified_file, nested_file]
    
    for file_path in demo_files:
        try:
            if Path(file_path).exists():
                Path(file_path).unlink()
                print(f"   🗑️  Видалено: {file_path}")
        except Exception as e:
            print(f"   ⚠️  Помилка видалення {file_path}: {e}")
    
    # Видаляємо тестову директорію
    try:
        test_dir = Path("test_dir")
        if test_dir.exists():
            test_dir.rmdir()
            print(f"   🗑️  Видалено директорію: test_dir")
    except Exception as e:
        print(f"   ⚠️  Помилка видалення директорії: {e}")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = demonstrate_persistence()
    print(f"\n{'🎯 ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА УСПІШНО! 🎯' if success else '⚠️ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА З ЗАУВАЖЕННЯМИ ⚠️'}")
    sys.exit(0 if success else 1)