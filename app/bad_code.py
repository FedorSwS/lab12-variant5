"""
ПЛОХОЙ КОД - НУЖЕН РЕФАКТОРИНГ
Проблемы:
1. Длина функции > 30 строк
2. Магические числа
3. Отсутствие обработки ошибок
4. Неинформативные имена переменных
5. Дублирование кода
"""

def bad_func(a, b, c, d, e, f, g, h):
    x = 0
    y = 0
    z = 0
    
    if a > 100:
        x = a * 0.9
    else:
        x = a * 0.95
    
    if b > 100:
        y = b * 0.9
    else:
        y = b * 0.95
    
    if c > 100:
        z = c * 0.9
    else:
        z = c * 0.95
    
    t1 = x + y + z
    t2 = 0
    if d == 1:
        t2 = 10
    elif d == 2:
        t2 = 20
    elif d == 3:
        t2 = 30
    else:
        t2 = 0
    
    t3 = t1 + t2
    
    if e > 5:
        t3 = t3 * 0.85
    else:
        t3 = t3 * 0.9
    
    if f > 10:
        for i in range(f):
            t3 = t3 + 5
    else:
        t3 = t3 + 50
    
    if g == "VIP":
        t3 = t3 - 50
    elif g == "REGULAR":
        t3 = t3 - 10
    else:
        t3 = t3
    
    if h < 0:
        t3 = -1
    elif h > 1000:
        t3 = -1
    else:
        t3 = t3
    
    return t3

# Пример использования
result = bad_func(50, 150, 200, 2, 3, 8, "VIP", 500)
print(f"Result: {result}")
