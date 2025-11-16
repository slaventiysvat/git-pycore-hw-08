"""
Enhanced Assistant Bot with Persistent Data Storage

This module extends the previous address book system with:
- Persistent data storage using pickle protocol
- Automatic save/load functionality on program start/exit
- Robust error handling for file operations
- Data integrity preservation across sessions
- All previous functionality maintained (birthday management, CLI commands)

Key Features:
- save_data(): Serialize AddressBook to file using pickle
- load_data(): Deserialize AddressBook from file with error handling  
- Automatic persistence integration in main loop
- Graceful handling of missing/corrupted files
- Maintains all contacts, phones, and birthdays between sessions

Commands supported (all from previous homework):
- add [name] [phone]: Add contact or phone to existing contact
- change [name] [old_phone] [new_phone]: Change phone number
- phone [name]: Show phones for contact
- all: Show all contacts
- add-birthday [name] [DD.MM.YYYY]: Add birthday to contact
- show-birthday [name]: Show birthday for contact
- birthdays: Show upcoming birthdays this week
- hello: Get greeting from bot
- close/exit: Close program (with automatic save)
"""

from collections import UserDict
from datetime import datetime, timedelta
from functools import wraps
import re
import pickle
import os
from typing import List, Optional, Dict, Any


def input_error(func):
    """Decorator for handling input errors with user-friendly messages."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            contact_name = str(e).strip("'")
            return f"Contact not found: {contact_name}"
        except ValueError as e:
            return f"Invalid input: {str(e)}"
        except IndexError:
            return "Not enough arguments provided. Please check command format."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return wrapper


class Field:
    """Base class for record fields."""
    
    def __init__(self, value: str):
        """Initialize field with value."""
        self.value = value

    def __str__(self) -> str:
        """Return string representation of field value."""
        return str(self.value)


class Name(Field):
    """Class for storing contact name. Required field."""
    
    def __init__(self, value: str):
        """Initialize name field with validation."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip())


class Phone(Field):
    """Class for storing phone number with format validation (10 digits)."""
    
    def __init__(self, value: str):
        """Initialize phone field with validation."""
        if not self._is_valid_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)
    
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Validate phone number format (exactly 10 digits)."""
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) == 10 and digits_only.isdigit()


class Birthday(Field):
    """Class for storing birthday with date validation (DD.MM.YYYY format)."""
    
    def __init__(self, value: str):
        """Initialize birthday field with date validation."""
        try:
            # Parse and validate date format DD.MM.YYYY
            parsed_date = datetime.strptime(value.strip(), "%d.%m.%Y")
            # Store as datetime object for easy manipulation
            self.date = parsed_date
            # Store original string format for display
            super().__init__(parsed_date.strftime("%d.%m.%Y"))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    """Class for storing contact information including name, phones, and birthday."""
    
    def __init__(self, name: str):
        """Initialize record with name and empty phone list."""
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        """Add phone number to the record."""
        phone_obj = Phone(phone)
        # Check if phone already exists
        if any(p.value == phone_obj.value for p in self.phones):
            raise ValueError(f"Phone number {phone} already exists for this contact")
        self.phones.append(phone_obj)

    def remove_phone(self, phone: str) -> None:
        """Remove phone number from the record."""
        for i, p in enumerate(self.phones):
            if p.value == phone:
                self.phones.pop(i)
                return
        raise ValueError(f"Phone number {phone} not found")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Edit existing phone number."""
        # Validate new phone first
        new_phone_obj = Phone(new_phone)
        
        # Find and replace the phone
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone_obj.value
                return
        raise ValueError(f"Phone number {old_phone} not found")

    def find_phone(self, phone: str) -> Optional[str]:
        """Find phone number in the record."""
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, birthday: str) -> None:
        """Add birthday to the record."""
        self.birthday = Birthday(birthday)

    def days_to_birthday(self) -> Optional[int]:
        """Calculate days until next birthday."""
        if not self.birthday:
            return None
        
        today = datetime.now().date()
        birthday_this_year = self.birthday.date.replace(year=today.year).date()
        
        # If birthday already passed this year, calculate for next year
        if birthday_this_year < today:
            birthday_this_year = self.birthday.date.replace(year=today.year + 1).date()
        
        return (birthday_this_year - today).days

    def __str__(self) -> str:
        """Return string representation of the record."""
        phones_str = '; '.join(p.value for p in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones_str}"
        if self.birthday:
            result += f", birthday: {self.birthday.value}"
        return result


class AddressBook(UserDict):
    """Class for storing and managing contact records with birthday functionality and persistence."""
    
    def add_record(self, record: Record) -> None:
        """Add record to address book."""
        if record.name.value in self.data:
            raise ValueError(f"Contact {record.name.value} already exists")
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """Find record by name."""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Delete record by name."""
        if name not in self.data:
            raise ValueError(f"Contact {name} not found")
        del self.data[name]

    def get_upcoming_birthdays(self) -> List[Dict[str, str]]:
        """Get list of contacts with upcoming birthdays in the next 7 days."""
        today = datetime.now().date()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if not record.birthday:
                continue
                
            # Get birthday for this year
            birthday_this_year = record.birthday.date.replace(year=today.year).date()
            
            # If birthday already passed this year, check next year
            if birthday_this_year < today:
                birthday_this_year = record.birthday.date.replace(year=today.year + 1).date()
            
            # Check if birthday is within next 7 days
            days_until = (birthday_this_year - today).days
            if 0 <= days_until <= 7:
                # Adjust for weekends - move to Monday
                congratulation_date = birthday_this_year
                if congratulation_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    # Move to next Monday
                    days_to_monday = 7 - congratulation_date.weekday()
                    congratulation_date += timedelta(days=days_to_monday)
                
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        # Sort by congratulation date
        upcoming_birthdays.sort(key=lambda x: datetime.strptime(x["congratulation_date"], "%d.%m.%Y"))
        return upcoming_birthdays

    def __str__(self) -> str:
        """Return string representation of address book."""
        if not self.data:
            return "Address book is empty"
        return "\n".join(str(record) for record in self.data.values())


# Persistent data management functions

def save_data(book: AddressBook, filename: str = "addressbook.pkl") -> bool:
    """
    Save AddressBook to file using pickle serialization.
    
    Args:
        book: AddressBook instance to save
        filename: File path to save to (default: addressbook.pkl)
    
    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(book, f)
        return True
    except (IOError, OSError, pickle.PickleError) as e:
        print(f"Error saving data to {filename}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving data: {e}")
        return False


def load_data(filename: str = "addressbook.pkl") -> AddressBook:
    """
    Load AddressBook from file using pickle deserialization.
    
    Args:
        filename: File path to load from (default: addressbook.pkl)
    
    Returns:
        AddressBook: Loaded address book or new empty one if file not found/corrupted
    """
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            # Verify loaded object is AddressBook instance
            if isinstance(book, AddressBook):
                return book
            else:
                print(f"Warning: File {filename} doesn't contain valid AddressBook data")
                return AddressBook()
    except FileNotFoundError:
        # Normal case when running for first time - return empty book
        return AddressBook()
    except (IOError, OSError) as e:
        print(f"Error reading file {filename}: {e}")
        return AddressBook()
    except pickle.PickleError as e:
        print(f"Error deserializing data from {filename}: {e}")
        print("The file may be corrupted. Starting with empty address book.")
        return AddressBook()
    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        print("Starting with empty address book.")
        return AddressBook()


# Bot command functions (unchanged from previous homework)

def parse_input(user_input: str) -> tuple:
    """Parse user input into command and arguments."""
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """Add new contact or phone to existing contact."""
    if len(args) < 2:
        raise IndexError("Please provide both name and phone")
    
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    
    if phone:
        record.add_phone(phone)
    
    return message


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """Change phone number for existing contact."""
    if len(args) < 3:
        raise IndexError("Please provide name, old phone, and new phone")
    
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    
    if record is None:
        raise KeyError(name)
    
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """Show phone numbers for contact."""
    if len(args) < 1:
        raise IndexError("Please provide contact name")
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise KeyError(name)
    
    if not record.phones:
        return f"No phones found for {name}"
    
    phones = '; '.join(p.value for p in record.phones)
    return f"{name}: {phones}"


@input_error
def show_all(args: List[str], book: AddressBook) -> str:
    """Show all contacts in address book."""
    if not book.data:
        return "No contacts in address book."
    
    return str(book)


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """Add birthday to existing contact."""
    if len(args) < 2:
        raise IndexError("Please provide name and birthday (DD.MM.YYYY)")
    
    name, birthday, *_ = args
    record = book.find(name)
    
    if record is None:
        raise KeyError(name)
    
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """Show birthday for contact."""
    if len(args) < 1:
        raise IndexError("Please provide contact name")
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise KeyError(name)
    
    if record.birthday is None:
        return f"No birthday set for {name}"
    
    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    """Show upcoming birthdays in the next week."""
    upcoming = book.get_upcoming_birthdays()
    
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    result = "Upcoming birthdays:\n"
    for birthday_info in upcoming:
        result += f"{birthday_info['name']}: {birthday_info['congratulation_date']}\n"
    
    return result.rstrip()


def main():
    """Main bot loop with command processing and persistent data management."""
    # Load existing data or create new address book
    filename = "addressbook.pkl"
    book = load_data(filename)
    
    # Show status message about loaded data
    if book.data:
        print(f"Welcome back! Loaded {len(book.data)} contacts from previous session.")
    else:
        print("Welcome to the assistant bot!")
    
    try:
        while True:
            try:
                user_input = input("Enter a command: ")
                command, args = parse_input(user_input)

                if command in ["close", "exit"]:
                    # Save data before exiting
                    if save_data(book, filename):
                        print("Data saved successfully.")
                    else:
                        print("Warning: Could not save data.")
                    print("Good bye!")
                    break

                elif command == "hello":
                    print("How can I help you?")

                elif command == "add":
                    print(add_contact(args, book))

                elif command == "change":
                    print(change_contact(args, book))

                elif command == "phone":
                    print(show_phone(args, book))

                elif command == "all":
                    print(show_all(args, book))

                elif command == "add-birthday":
                    print(add_birthday(args, book))

                elif command == "show-birthday":
                    print(show_birthday(args, book))

                elif command == "birthdays":
                    print(birthdays(args, book))

                else:
                    print("Invalid command.")
            
            except KeyboardInterrupt:
                # Save data on Ctrl+C
                print("\nSaving data before exit...")
                if save_data(book, filename):
                    print("Data saved successfully.")
                else:
                    print("Warning: Could not save data.")
                print("Good bye!")
                break
            except EOFError:
                # Save data on EOF
                print("\nSaving data before exit...")
                if save_data(book, filename):
                    print("Data saved successfully.")
                else:
                    print("Warning: Could not save data.")
                print("Good bye!")
                break
    except Exception as e:
        # Emergency save on unexpected error
        print(f"\nUnexpected error occurred: {e}")
        print("Attempting to save data...")
        if save_data(book, filename):
            print("Data saved successfully.")
        else:
            print("Warning: Could not save data.")
        raise


if __name__ == "__main__":
    main()
