# Задание 9: Генерация SQL-запросов

## Система бронирования отелей - аналитические отчёты

---

## Запрос 1: Топ-5 самых загруженных номеров

### Описание задачи
Вывести 5 номеров отеля с наибольшим количеством бронирований за всё время. В результат включить: номер комнаты, тип комнаты, количество бронирований и общую выручку.

### SQL - запрос
SELECT 
    r.room_number,
    r.room_type,
    COUNT(b.id) AS total_bookings,
    SUM(b.total_price) AS total_revenue
FROM rooms r
JOIN bookings b ON r.id = b.room_id
WHERE b.status IN ('confirmed', 'checked_out')
GROUP BY r.id
ORDER BY total_bookings DESC
LIMIT 5;

### Объяснение логики
    JOIN - соединяет таблицы номеров и бронирований
    WHERE - фильтрует только подтверждённые и завершённые бронирования
    GROUP BY - группирует данные по каждому номеру
    ORDER BY total_bookings DESC - сортирует от большего к меньшему
    LIMIT 5 - оставляет только топ-5 записей

## Запрос 2: Клиенты с максимальной суммой заказов

### Описание задачи
Найти топ-10 клиентов, которые потратили больше всего денег на бронирования. Вывести ФИО, email, количество бронирований, общую сумму трат и средний чек.

### SQL - запрос
SELECT 
    c.full_name,
    c.email,
    COUNT(b.id) AS total_bookings,
    SUM(b.total_price) AS total_spent,
    ROUND(AVG(b.total_price), 2) AS avg_booking_value
FROM customers c
JOIN bookings b ON c.id = b.customer_id
WHERE b.status IN ('confirmed', 'checked_out')
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 10;

### Объяснение логики
    JOIN - соединяет клиентов с их бронированиями
    WHERE - учитывает только подтверждённые и завершённые бронирования
    GROUP BY c.id - группирует все бронирования одного клиента
    ORDER BY total_spent DESC - сортирует по убыванию суммы трат
    LIMIT 10 - оставляет топ-10 клиентов

## Запрос 3: Анализ отмен бронирований по месяцам

### Описание задачи
Проанализировать динамику отмен бронирований по месяцам за последние 6 месяцев. Вывести месяц, общее количество бронирований, количество отмен и процент отмен.

### SQL - запрос
SELECT 
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
    ROUND(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate
FROM bookings
WHERE created_at >= date('now', '-6 months')
GROUP BY month
ORDER BY month DESC;

### Объяснение логики
    strftime('%Y-%m', created_at) - извлекает год и месяц из даты создания
    CASE WHEN - условное суммирование для подсчёта отмен
    cancellation_rate - процент отмен = (отмены / всего) * 100
    date('now', '-6 months') - фильтр за последние 6 месяцев
    GROUP BY month - группировка по месяцам
    ORDER BY month DESC - сначала свежие месяцы