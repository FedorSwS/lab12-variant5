"""
СЛОЖНАЯ БИЗНЕС-ЛОГИКА: Расчёт загрузки номеров и динамическое ценообразование

Этот модуль демонстрирует сложную бизнес-логику из системы бронирования отелей:
1. Расчёт загрузки номеров (occupancy rate)
2. Динамическое ценообразование на основе спроса
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app import models


class DynamicPricingEngine:
    """
    Механизм динамического ценообразования для номеров отеля
    
    Бизнес-правила:
    1. Базовая цена умножается на коэффициент загрузки
    2. В выходные дни цена повышается на 20%
    3. При загрузке > 80% цена повышается на 15%
    4. При загрузке < 30% цена снижается на 10%
    5. Для длительных бронирований (>7 дней) скидка 5%
    """
    
    # Константы для бизнес-логики
    WEEKEND_SURCHARGE = 1.20  # +20% в выходные
    HIGH_DEMAND_THRESHOLD = 0.80  # 80% загрузки
    HIGH_DEMAND_SURCHARGE = 1.15  # +15% при высокой загрузке
    LOW_DEMAND_THRESHOLD = 0.30  # 30% загрузки
    LOW_DEMAND_DISCOUNT = 0.90  # -10% при низкой загрузке
    LONG_STAY_DAYS = 7  # дней для длительного бронирования
    LONG_STAY_DISCOUNT = 0.95  # -5% за длительное бронирование
    
    @classmethod
    def calculate_occupancy_rate(
        cls, 
        db: Session, 
        room_id: int, 
        start_date: date, 
        end_date: date
    ) -> float:
        """
        Рассчитывает процент загрузки конкретного номера за период
        
        Логика:
        - Находим все подтверждённые бронирования для номера в указанном периоде
        - Суммируем количество забронированных дней
        - Делим на общее количество дней в периоде
        - Возвращаем процент загрузки
        
        Args:
            db: Сессия БД
            room_id: ID номера
            start_date: Начало периода
            end_date: Конец периода
        
        Returns:
            float: Процент загрузки (0.0 - 1.0)
        """
        total_days = (end_date - start_date).days
        
        if total_days <= 0:
            return 0.0
        
        # Суммируем количество забронированных дней
        booked_days = db.query(
            func.sum(
                func.julianday(models.Booking.check_out_date) - 
                func.julianday(models.Booking.check_in_date)
            )
        ).filter(
            and_(
                models.Booking.room_id == room_id,
                models.Booking.status.in_([
                    models.BookingStatus.CONFIRMED,
                    models.BookingStatus.CHECKED_IN
                ]),
                models.Booking.check_in_date < end_date,
                models.Booking.check_out_date > start_date
            )
        ).scalar() or 0
        
        return min(booked_days / total_days, 1.0)
    
    @classmethod
    def get_optimal_price(
        cls,
        db: Session,
        room: models.Room,
        check_in_date: date,
        check_out_date: date
    ) -> float:
        """
        Вычисляет оптимальную цену для номера на основе спроса
        
        Алгоритм:
        1. Начинаем с базовой цены номера
        2. Рассчитываем загрузку отеля за период
        3. Применяем корректировки:
           - Выходные дни → +20%
           - Высокая загрузка (>80%) → +15%
           - Низкая загрузка (<30%) → -10%
           - Длительное бронирование (>7 дней) → -5%
        
        Args:
            db: Сессия БД
            room: Объект номера
            check_in_date: Дата заезда
            check_out_date: Дата выезда
        
        Returns:
            float: Оптимальная цена с учётом всех факторов
        """
        base_price = room.price_per_night
        nights = (check_out_date - check_in_date).days
        final_price = base_price
        
        # 1. Корректировка на выходные дни
        weekend_days = cls._count_weekend_days(check_in_date, check_out_date)
        if weekend_days > 0:
            # Пропорционально увеличиваем цену в зависимости от количества выходных
            weekend_ratio = weekend_days / nights
            final_price *= (1 + (cls.WEEKEND_SURCHARGE - 1) * weekend_ratio)
        
        # 2. Корректировка на загрузку отеля
        # Рассчитываем среднюю загрузку всех номеров
        total_rooms = db.query(models.Room).count()
        if total_rooms > 0:
            total_occupancy = cls._calculate_total_occupancy(db, check_in_date, check_out_date)
            avg_occupancy = total_occupancy / total_rooms
            
            if avg_occupancy >= cls.HIGH_DEMAND_THRESHOLD:
                final_price *= cls.HIGH_DEMAND_SURCHARGE
            elif avg_occupancy <= cls.LOW_DEMAND_THRESHOLD:
                final_price *= cls.LOW_DEMAND_DISCOUNT
        
        # 3. Корректировка на длительность бронирования
        if nights > cls.LONG_STAY_DAYS:
            final_price *= cls.LONG_STAY_DISCOUNT
        
        return round(final_price, 2)
    
    @classmethod
    def _count_weekend_days(cls, start: date, end: date) -> int:
        """Подсчёт количества выходных дней в периоде"""
        weekend_count = 0
        current = start
        while current < end:
            # 5 = Saturday, 6 = Sunday
            if current.weekday() >= 5:
                weekend_count += 1
            current += timedelta(days=1)
        return weekend_count
    
    @classmethod
    def _calculate_total_occupancy(
        cls, 
        db: Session, 
        start_date: date, 
        end_date: date
    ) -> float:
        """Рассчёт суммарной загрузки всех номеров"""
        total_days = (end_date - start_date).days
        
        if total_days <= 0:
            return 0.0
        
        # Суммируем забронированные дни по всем номерам
        total_booked_days = db.query(
            func.sum(
                func.julianday(models.Booking.check_out_date) - 
                func.julianday(models.Booking.check_in_date)
            )
        ).filter(
            and_(
                models.Booking.status.in_([
                    models.BookingStatus.CONFIRMED,
                    models.BookingStatus.CHECKED_IN
                ]),
                models.Booking.check_in_date < end_date,
                models.Booking.check_out_date > start_date
            )
        ).scalar() or 0
        
        return total_booked_days


# Документация по сложной логике
"""
ПОЧЕМУ ЭТА ЛОГИКА СЛОЖНАЯ?

1. **Множество факторов влияния**:
   - Загрузка отеля (спрос)
   - День недели (выходные/будни)
   - Длительность бронирования
   - Время года (можно расширить)

2. **Необходимость в оптимизации**:
   - Отель не может бесконечно повышать цену (конкуренция)
   - Слишком низкая цена → упущенная прибыль
   - Нужен баланс между заполняемостью и ценой

3. **Динамическое обновление**:
   - Цены меняются в реальном времени
   - Зависимость от текущей загрузки
   - Нужно пересчитывать при каждом запросе

4. **Бизнес-ограничения**:
   - Минимальная/максимальная цена
   - Правила для постоянных клиентов
   - Сезонные коэффициенты

КАК ИИ ПОМОГАЕТ:
- AI может анализировать исторические данные
- Прогнозировать оптимальную цену
- Учить модель на реальных бронированиях
- Адаптироваться к рыночным изменениям
"""

if __name__ == "__main__":
    print("Complex pricing logic documentation module")
    print("See docstrings for detailed explanation of business rules")
