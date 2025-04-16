#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Версия 1.0.0

import os
import re
import json
from html import escape

class IPCPortMapper:
    """
    Класс для анализа строк конфигурации IPC платформ и генерации
    детальных SVG схем портов с учетом их типов и настроек.
    """
    
    # Типы интерфейсов и их сопоставления с цветами
    PORT_TYPES = {
        'igb': {'name': 'Медный порт', 'color': '#ddd', 'color_active': '#90EE90'},
        'ix': {'name': 'Оптический порт', 'color': '#b3d9ff', 'color_active': '#87CEFA'},
        'ixl': {'name': 'Оптический порт 10G', 'color': '#add8e6', 'color_active': '#00BFFF'},
        'em': {'name': 'Встроенный сетевой порт', 'color': '#f0e68c', 'color_active': '#FFD700'},
        're': {'name': 'Realtek сетевой порт', 'color': '#e6e6fa', 'color_active': '#ba55d3'},
    }
    
    def __init__(self, img_dir='../img'):
        """
        Инициализация с указанием директории для изображений
        """
        self.img_dir = img_dir
        
        # Убедиться, что директория существует
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        # Кэш для уже обработанных платформ
        self.platform_cache = {}
        
    def parse_config_string(self, config_string):
        """
        Анализ строки конфигурации для извлечения информации о портах

        Формат: [кол-во_портов][тип_порта][номер_порта]*[опции]...
        """
        ports = []
        
        # Регулярное выражение для извлечения портов из строки конфигурации
        port_pattern = r'(\d+)([a-z]+)(\d+)\*([0-9A-F]+)'
        matches = re.findall(port_pattern, config_string)
        
        for match in matches:
            count = int(match[0])
            port_type = match[1]
            start_num = int(match[2])
            config = match[3]
            
            # Определение свойств порта на основе конфигурации
            is_active = config != '02BD'  # Предполагаем, что 02BD - неактивный порт
            is_special = config == '3001'  # Предполагаем, что 3001 - особая конфигурация
            
            # Добавление портов
            for i in range(count):
                port_num = start_num + i
                ports.append({
                    'type': port_type,
                    'number': port_num,
                    'active': is_active,
                    'special': is_special,
                    'config': config
                })
        
        return sorted(ports, key=lambda x: (x['type'], x['number']))
    
    def generate_platform_svg(self, platform_name, config_string):
        """
        Генерация SVG схемы для платформы на основе строки конфигурации
        """
        # Извлекаем информацию о портах
        ports = self.parse_config_string(config_string)
        
        # Базовые размеры SVG
        svg_width = 800
        svg_height = 400
        box_width = 700
        box_height = 300
        
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
    .legend {{
      font-family: Arial, sans-serif;
      font-size: 12px;
      fill: #333;
    }}
    .legend-box {{
      width: 15px;
      height: 15px;
      stroke: #666;
      stroke-width: 1;
    }}
  </style>
  
  <!-- Основной прямоугольник устройства -->
  <rect x="{(svg_width - box_width) / 2}" y="{(svg_height - box_height) / 2}" 
        width="{box_width}" height="{box_height}" class="hardware" rx="5" ry="5" />
  
  <!-- Заголовок -->
  <text x="{svg_width / 2}" y="30" class="title">{escape(platform_name)}</text>
  <text x="{svg_width / 2}" y="50" class="subtitle">Схема расположения портов</text>
'''
        
        # Группируем порты по типу
        port_groups = {}
        for port in ports:
            port_type = port['type']
            if port_type not in port_groups:
                port_groups[port_type] = []
            port_groups[port_type].append(port)
        
        # Рассчитываем размещение портов
        port_width = 30
        port_height = 20
        port_margin = 10
        
        # Верхние порты
        top_ports = []
        for port_type in ['em', 're']:
            if port_type in port_groups:
                top_ports.extend(port_groups[port_type])
        
        # Нижние порты
        bottom_ports = []
        for port_type in ['igb', 'ix', 'ixl']:
            if port_type in port_groups:
                bottom_ports.extend(port_groups[port_type])
        
        # Ограничиваем число портов на строку
        max_ports_per_row = 16
        
        # Рисуем верхние порты
        if top_ports:
            top_row_count = min(len(top_ports), max_ports_per_row)
            top_spacing = (box_width - top_row_count * port_width) / (top_row_count + 1)
            
            for i, port in enumerate(top_ports[:max_ports_per_row]):
                x = (svg_width - box_width) / 2 + top_spacing + i * (port_width + top_spacing / 2)
                y = (svg_height - box_height) / 2
                
                port_type = port['type']
                port_num = port['number']
                fill_color = self.PORT_TYPES[port_type]['color_active'] if port['active'] else self.PORT_TYPES[port_type]['color']
                
                svg += f'''  <!-- Порт {port_type}{port_num} -->
  <rect x="{x}" y="{y - port_height - port_margin}" width="{port_width}" height="{port_height}" class="port" fill="{fill_color}" />
  <text x="{x + port_width / 2}" y="{y - port_height / 2 - port_margin + 4}" class="text">{port_type}{port_num}</text>
'''
        
        # Рисуем нижние порты (разделяем на строки, если больше max_ports_per_row)
        if bottom_ports:
            rows = [bottom_ports[i:i+max_ports_per_row] for i in range(0, len(bottom_ports), max_ports_per_row)]
            
            for row_idx, row_ports in enumerate(rows):
                bottom_spacing = (box_width - len(row_ports) * port_width) / (len(row_ports) + 1)
                row_y_offset = row_idx * (port_height + port_margin) * 1.5
                
                for i, port in enumerate(row_ports):
                    x = (svg_width - box_width) / 2 + bottom_spacing + i * (port_width + bottom_spacing / 2)
                    y = (svg_height + box_height) / 2 + row_y_offset
                    
                    port_type = port['type']
                    port_num = port['number']
                    fill_color = self.PORT_TYPES[port_type]['color_active'] if port['active'] else self.PORT_TYPES[port_type]['color']
                    
                    svg += f'''  <!-- Порт {port_type}{port_num} -->
  <rect x="{x}" y="{y + port_margin}" width="{port_width}" height="{port_height}" class="port" fill="{fill_color}" />
  <text x="{x + port_width / 2}" y="{y + port_height / 2 + port_margin + 4}" class="text">{port_type}{port_num}</text>
'''
        
        # Добавляем консольный порт
        console_x = svg_width - (svg_width - box_width) / 2 - 60
        console_y = (svg_height - box_height) / 2 + box_height / 2
        
        svg += f'''  <!-- Консольный порт -->
  <rect x="{console_x}" y="{console_y - 10}" width="40" height="20" class="port" fill="#d3d3d3" />
  <text x="{console_x + 20}" y="{console_y + 4}" class="text">CON</text>
'''
        
        # Добавляем легенду
        legend_x = 15
        legend_y = svg_height - 80
        legend_spacing = 25
        
        svg += f'''  <!-- Легенда -->
  <text x="{legend_x}" y="{legend_y - 20}" class="legend" font-weight="bold">Типы портов:</text>
'''
        
        for i, (port_type, info) in enumerate(self.PORT_TYPES.items()):
            if any(port['type'] == port_type for port in ports):  # Показывать только используемые типы
                svg += f'''  <rect x="{legend_x}" y="{legend_y + i * legend_spacing}" width="15" height="15" class="legend-box" fill="{info['color']}" />
  <text x="{legend_x + 25}" y="{legend_y + i * legend_spacing + 12}" class="legend">{info['name']} ({port_type})</text>
'''
        
        # Показываем активные порты в легенде
        svg += f'''  <rect x="{legend_x + 200}" y="{legend_y}" width="15" height="15" class="legend-box" fill="#90EE90" />
  <text x="{legend_x + 225}" y="{legend_y + 12}" class="legend">Активный порт</text>
'''
        
        # Закрываем SVG
        svg += '</svg>'
        
        return svg
    
    def generate_for_all_platforms(self, html_file_path):
        """
        Генерирует SVG для всех платформ в HTML файле
        """
        # Чтение HTML
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Ищем все опции в выпадающем списке с их значениями
        pattern = r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>'
        matches = re.findall(pattern, content)
        
        generated_count = 0
        skipped_count = 0
        
        for value, name in matches:
            if 'IPC' in name:
                # Проверяем, существует ли уже файл
                file_name = f"{name}.svg"
                file_path = os.path.join(self.img_dir, file_name)
                
                if os.path.exists(file_path):
                    print(f"Файл для платформы '{name}' уже существует, пропускаем")
                    skipped_count += 1
                    continue
                
                # Генерируем SVG
                svg_content = self.generate_platform_svg(name, value)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                print(f"Создан файл SVG для платформы '{name}'")
                generated_count += 1
        
        print(f"\nИтого: создано {generated_count} новых SVG, пропущено {skipped_count} существующих")
        
        return generated_count, skipped_count

# Пример использования
if __name__ == "__main__":
    mapper = IPCPortMapper()
    
    # Генерируем для всех платформ из HTML
    mapper.generate_for_all_platforms('../pages/kstrcfg.html')
    
    # Или для одной конкретной платформы
    # config = "8igb0*3001igb1*3001igb2*02BDigb3*02BDigb4*02BDigb5*02BDigb6*02BDigb7*02BDffff"
    # svg = mapper.generate_platform_svg("IPC-100(шасси S102)", config)
    # with open(os.path.join(mapper.img_dir, "test_ipc100.svg"), 'w', encoding='utf-8') as f:
    #     f.write(svg) 
