def update_channel_in_file(filename, channel_name, public_link):
    """
    Альтернативная версия с построчной обработкой
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        updated = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Если это нужный канал и он еще не отмечен #
            if stripped == channel_name and not line.startswith('#'):
                new_lines.append(f"#{channel_name}\n")
                new_lines.append(f"{public_link}\n")
                new_lines.append("\n")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            print(f"Канал '{channel_name}' не найден или уже отмечен")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"Файл обновлен для канала '{channel_name}'")

    except Exception as e:
        print(f"Ошибка: {e}")
