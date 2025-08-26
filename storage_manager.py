import json
import os
import uuid
from datetime import datetime, timedelta


class StorageManager:
    def __init__(self, storage_file='tasks_storage.json'):
        self.storage_file = storage_file
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Создает файл хранилища если он не существует"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({}, f)

    def _clean_old_tasks(self):
        """Очищает старые задачи (старше 24 часов)"""
        try:
            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            current_time = datetime.now()
            tasks_to_keep = {}

            for task_id, task_data in tasks.items():
                created_time = datetime.fromisoformat(
                    task_data.get('created_at', '2000-01-01T00:00:00'))
                if current_time - created_time < timedelta(hours=24):
                    tasks_to_keep[task_id] = task_data

            with open(self.storage_file, 'w') as f:
                json.dump(tasks_to_keep, f, indent=2, default=str)

        except Exception as e:
            print(f"Ошибка при очистке старых задач: {e}")

    def create_task(self, task_data):
        """Создает новую задачу"""
        try:
            self._clean_old_tasks()

            task_id = str(uuid.uuid4())
            task_data['task_id'] = task_id
            task_data['created_at'] = datetime.now().isoformat()
            task_data['updated_at'] = datetime.now().isoformat()

            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            tasks[task_id] = task_data

            with open(self.storage_file, 'w') as f:
                json.dump(tasks, f, indent=2, default=str)

            return task_id

        except Exception as e:
            print(f"Ошибка при создании задачи: {e}")
            return None

    def get_task(self, task_id):
        """Получает задачу по ID"""
        try:
            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            return tasks.get(task_id)

        except Exception as e:
            print(f"Ошибка при получении задачи: {e}")
            return None

    def update_task(self, task_id, updates):
        """Обновляет задачу"""
        try:
            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            if task_id in tasks:
                tasks[task_id].update(updates)
                tasks[task_id]['updated_at'] = datetime.now().isoformat()

                with open(self.storage_file, 'w') as f:
                    json.dump(tasks, f, indent=2, default=str)

                return True
            return False

        except Exception as e:
            print(f"Ошибка при обновлении задачи: {e}")
            return False

    def delete_task(self, task_id):
        """Удаляет задачу"""
        try:
            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            if task_id in tasks:
                del tasks[task_id]

                with open(self.storage_file, 'w') as f:
                    json.dump(tasks, f, indent=2, default=str)

                return True
            return False

        except Exception as e:
            print(f"Ошибка при удалении задачи: {e}")
            return False

    def get_all_tasks(self):
        """Получает все задачи"""
        try:
            with open(self.storage_file, 'r') as f:
                tasks = json.load(f)

            return tasks

        except Exception as e:
            print(f"Ошибка при получении всех задач: {e}")
            return {}


# Глобальный экземпляр менеджера хранилища
storage_manager = StorageManager()