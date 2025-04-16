#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Версия 1.0.0

import os
import re
import sys
from html import escape

# Путь к директории с изображениями
IMG_DIR = '../img'

# Получение списка всех существующих SVG-файлов
def get_existing_svg_files():
    return [f for f in os.listdir(IMG_DIR) if f.endswith('.svg')]

# Получение списка IPC платформ из kstrcfg.html
def get_ipc_platforms():
    platforms = []
    html_path = '../pages/kstrcfg.html'
    
    with open(html_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Ищем все опции в выпадающем списке
        option_pattern = r'<option[^>]*>(.*?)</option>'
        options = re.findall(option_pattern, content)
        
        for option in options:
            # Только IPC платформы
            if 'IPC' in option:
                platforms.append(option)
    
    return platforms

# Генерация SVG схемы для IPC платформы
def generate_ipc_svg(platform_name):
    # Извлекаем информацию о платформе
    match = re.search(r'IPC-(\d+)\w*', platform_name)
    if not match:
        print(f"Не удалось распознать платформу: {platform_name}")
        return None
    
    model_number = match.group(1)
    
    # Определяем количество портов на основе модели
    port_count = 4  # Базовое количество
    
    # Для более мощных моделей - больше портов
    if int(model_number) >= 100:
        port_count = 8
    if int(model_number) >= 500:
        port_count = 12
    if int(model_number) >= 1000:
        port_count = 16
    if int(model_number) >= 3000:
        port_count = 24
    
    # Разбор названия для определения типов портов
    has_fiber = 'F' in platform_name
    has_r_model = 'R' in platform_name
    
    # Создаем SVG
    svg_width = 800
    svg_height = 300
    box_width = 600
    box_height = 200
    
    # Начало SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .hardware {{
      fill: #f8f8f8;
      stroke: #444;
      stroke-width: 2;
    }}
    .port {{
      fill: #ddd;
      stroke: #666;
      stroke-width: 1;
    }}
    .fiber {{
      fill: #b3d9ff;
      stroke: #666;
      stroke-width: 1;
    }}
    .text {{
      font-family: Arial, sans-serif;
      font-size: 12px;
      fill: #333;
      text-anchor: middle;
    }}
    .title {{
      font-family: Arial, sans-serif;
      font-size: 16px;
      font-weight: bold;
      fill: #333;
      text-anchor: middle;
    }}
    .subtitle {{
      font-family: Arial, sans-serif;
      font-size: 14px;
      fill: #555;
      text-anchor: middle;
    }}
  </style>
  
  <!-- Основной прямоугольник устройства -->
  <rect x="{(svg_width - box_width) / 2}" y="{(svg_height - box_height) / 2}" 
        width="{box_width}" height="{box_height}" class="hardware" rx="5" ry="5" />
  
  <!-- Заголовок -->
  <text x="{svg_width / 2}" y="30" class="title">{escape(platform_name)}</text>
  <text x="{svg_width / 2}" y="50" class="subtitle">Схема расположения портов</text>
'''
    
    # Добавляем порты
    port_width = 30
    port_height = 20
    spacing = (box_width - port_count * port_width) / (port_count + 1)
    
    # Верхние порты (медные)
    for i in range(port_count // 2):
        x = (svg_width - box_width) / 2 + spacing + i * (port_width + spacing)
        y = (svg_height - box_height) / 2
        
        svg += f'''  <!-- Порт igb{i} -->
  <rect x="{x}" y="{y - port_height}" width="{port_width}" height="{port_height}" class="port" />
  <text x="{x + port_width / 2}" y="{y - port_height / 2 + 4}" class="text">igb{i}</text>
'''
    
    # Нижние порты (могут быть оптическими)
    for i in range(port_count // 2):
        x = (svg_width - box_width) / 2 + spacing + i * (port_width + spacing)
        y = (svg_height + box_height) / 2
        
        port_class = "fiber" if has_fiber and i < 2 else "port"
        port_name = f"ix{i}" if has_r_model and i < 2 else f"igb{i + port_count // 2}"
        
        svg += f'''  <!-- Порт {port_name} -->
  <rect x="{x}" y="{y}" width="{port_width}" height="{port_height}" class="{port_class}" />
  <text x="{x + port_width / 2}" y="{y + port_height / 2 + 4}" class="text">{port_name}</text>
'''
    
    # Консольный порт
    console_x = svg_width - (svg_width - box_width) / 2 - 60
    console_y = (svg_height - box_height) / 2 + box_height / 2
    
    svg += f'''  <!-- Консольный порт -->
  <rect x="{console_x}" y="{console_y - 10}" width="40" height="20" class="port" />
  <text x="{console_x + 20}" y="{console_y + 4}" class="text">CON</text>
'''
    
    # Закрываем SVG
    svg += '</svg>'
    
    return svg

# Основная функция
def main():
    # Получаем списки
    existing_files = get_existing_svg_files()
    platforms = get_ipc_platforms()
    
    # Проверяем наличие директории
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    
    # Подсчет статистики
    created_count = 0
    already_exists = 0
    
    # Создаем недостающие SVG
    for platform in platforms:
        file_name = f"{platform}.svg"
        file_path = os.path.join(IMG_DIR, file_name)
        
        # Проверяем, существует ли уже файл
        if any(platform in existing_file for existing_file in existing_files):
            print(f"Файл для платформы '{platform}' уже существует")
            already_exists += 1
            continue
        
        # Генерируем SVG
        svg_content = generate_ipc_svg(platform)
        if svg_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Создан файл SVG для платформы '{platform}'")
            created_count += 1
    
    print(f"\nИтого: создано {created_count} новых SVG, {already_exists} уже существовало")

if __name__ == "__main__":
    main() 
