#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Версия 1.0.0

import os
import sys
import argparse
from generate_ipc_svg import main as generate_basic_svg
from ipc_port_mapper import IPCPortMapper

def main():
    """
    Главная функция для запуска генерации SVG изображений для IPC платформ
    """
    parser = argparse.ArgumentParser(description='Генератор SVG-схем портов для IPC платформ Континента')
    parser.add_argument('--mode', choices=['basic', 'advanced', 'all'], default='all',
                      help='Режим генерации: basic - простые схемы, advanced - детальные схемы, all - оба режима')
    parser.add_argument('--html', default='../pages/kstrcfg.html',
                      help='Путь к HTML-файлу kstrcfg.html')
    parser.add_argument('--img-dir', default='../img',
                      help='Путь к директории с изображениями')
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    if not os.path.exists(args.html):
        print(f"Ошибка: Файл {args.html} не найден")
        return 1
    
    # Создаем директорию для изображений, если не существует
    if not os.path.exists(args.img_dir):
        os.makedirs(args.img_dir)
        print(f"Создана директория {args.img_dir}")
    
    # Счетчики для статистики
    basic_created = 0
    advanced_created = 0
    
    # Генерация базовых SVG
    if args.mode in ['basic', 'all']:
        print("\n=== Генерация базовых SVG схем ===")
        try:
            # Здесь вызываем функцию из generate_ipc_svg.py
            generate_basic_svg()
        except Exception as e:
            print(f"Ошибка при генерации базовых SVG: {e}")
    
    # Генерация расширенных SVG
    if args.mode in ['advanced', 'all']:
        print("\n=== Генерация детальных SVG схем с анализом портов ===")
        try:
            # Используем класс IPCPortMapper
            mapper = IPCPortMapper(img_dir=args.img_dir)
            generated, skipped = mapper.generate_for_all_platforms(args.html)
            advanced_created = generated
        except Exception as e:
            print(f"Ошибка при генерации детальных SVG: {e}")
    
    print("\n=== Завершено ===")
    print(f"Всего сгенерировано SVG изображений: {basic_created + advanced_created}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
