"""
Интерфейс командной строки для транслятора конфигурационного языка.
"""

import argparse
import sys
from src.translator import Translator, TranslationError


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description='Транслятор учебного конфигурационного языка в YAML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s -i config.txt -o config.yaml
  %(prog)s --input input.txt --output output.yaml
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        metavar='FILE',
        help='Путь к входному файлу с конфигурацией'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        metavar='FILE',
        help='Путь к выходному YAML файлу'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Чтение файла: {args.input}")
            
        translator = Translator()
        translator.translate_file(args.input, args.output)
        
        if args.verbose:
            print(f"Успешно записано в: {args.output}")
        else:
            print(f"Трансляция завершена успешно")
            
        return 0
        
    except TranslationError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1
        
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        return 130
        
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())