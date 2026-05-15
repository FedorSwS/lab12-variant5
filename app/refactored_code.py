"""
РЕФАКТОРИНГ - ХОРОШИЙ КОД
Применены принципы:
1. Single Responsibility Principle
2. Убраны магические числа → константы
3. Добавлена обработка ошибок
4. Информативные имена переменных
5. Устранено дублирование через функцию apply_discount
"""

from typing import Optional
from enum import Enum

class CustomerTier(str, Enum):
    VIP = "VIP"
    REGULAR = "REGULAR"
    STANDARD = "STANDARD"

class BookingCalculator:
    """Калькулятор стоимости бронирования с применением скидок и надбавок"""
    
    # Константы вместо магических чисел
    HIGH_PRICE_THRESHOLD = 100
    HIGH_PRICE_DISCOUNT_RATE = 0.9
    STANDARD_DISCOUNT_RATE = 0.95
    
    LOYALTY_BONUS = {
        1: 10,
        2: 20,
        3: 30
    }
    DEFAULT_LOYALTY_BONUS = 0
    
    LONG_TERM_BOOKING_DAYS_THRESHOLD = 5
    LONG_TERM_DISCOUNT = 0.85
    SHORT_TERM_DISCOUNT = 0.9
    
    SERVICE_FEE_LARGE_BOOKING_THRESHOLD = 10
    SERVICE_FEE_LARGE = 5
    SERVICE_FEE_SMALL = 50
    
    CUSTOMER_TIER_DISCOUNT = {
        CustomerTier.VIP: 50,
        CustomerTier.REGULAR: 10,
        CustomerTier.STANDARD: 0
    }
    
    MIN_VALID_PRICE = 0
    MAX_VALID_PRICE = 1000
    
    @classmethod
    def _apply_price_discount(cls, price: float) -> float:
        """Применить скидку в зависимости от цены"""
        discount_rate = (
            cls.HIGH_PRICE_DISCOUNT_RATE 
            if price > cls.HIGH_PRICE_THRESHOLD 
            else cls.STANDARD_DISCOUNT_RATE
        )
        return price * discount_rate
    
    @classmethod
    def _calculate_loyalty_bonus(cls, loyalty_level: int) -> float:
        """Рассчитать бонус за лояльность"""
        return cls.LOYALTY_BONUS.get(loyalty_level, cls.DEFAULT_LOYALTY_BONUS)
    
    @classmethod
    def _calculate_booking_discount(cls, booking_days: int) -> float:
        """Рассчитать скидку в зависимости от длительности бронирования"""
        if booking_days > cls.LONG_TERM_BOOKING_DAYS_THRESHOLD:
            return cls.LONG_TERM_DISCOUNT
        return cls.SHORT_TERM_DISCOUNT
    
    @classmethod
    def _calculate_service_fee(cls, num_services: int) -> float:
        """Рассчитать сервисный сбор"""
        if num_services > cls.SERVICE_FEE_LARGE_BOOKING_THRESHOLD:
            return num_services * cls.SERVICE_FEE_LARGE
        return cls.SERVICE_FEE_SMALL
    
    @classmethod
    def _apply_customer_tier_discount(cls, price: float, tier: CustomerTier) -> float:
        """Применить скидку в зависимости от статуса клиента"""
        discount = cls.CUSTOMER_TIER_DISCOUNT.get(tier, 0)
        return price - discount
    
    @classmethod
    def _validate_final_price(cls, price: float) -> float:
        """Валидация итоговой цены"""
        if price < cls.MIN_VALID_PRICE or price > cls.MAX_VALID_PRICE:
            raise ValueError(f"Price {price} is out of valid range [{cls.MIN_VALID_PRICE}, {cls.MAX_VALID_PRICE}]")
        return price
    
    @classmethod
    def calculate_booking_price(
        cls,
        room_price: float,
        additional_services_price: float,
        nights: int,
        loyalty_level: int,
        num_services: int,
        customer_tier: CustomerTier,
        total_booking_price: float
    ) -> float:
        """
        Рассчитать итоговую стоимость бронирования
        
        Args:
            room_price: Базовая цена номера за ночь
            additional_services_price: Стоимость дополнительных услуг
            nights: Количество ночей
            loyalty_level: Уровень лояльности (1, 2, 3)
            num_services: Количество заказанных услуг
            customer_tier: Статус клиента (VIP, REGULAR, STANDARD)
            total_booking_price: Общая стоимость для валидации
        
        Returns:
            float: Итоговая стоимость бронирования
        
        Raises:
            ValueError: Если итоговая цена выходит за допустимые пределы
        """
        # Базовая стоимость номера со скидкой по цене
        discounted_room_price = cls._apply_price_discount(room_price)
        
        # Стоимость услуг со скидкой по цене
        discounted_services_price = cls._apply_price_discount(additional_services_price)
        
        # Промежуточная сумма
        subtotal = discounted_room_price + discounted_services_price
        
        # Бонус за лояльность
        loyalty_bonus = cls._calculate_loyalty_bonus(loyalty_level)
        subtotal += loyalty_bonus
        
        # Скидка за длительность бронирования
        booking_discount_rate = cls._calculate_booking_discount(nights)
        subtotal *= booking_discount_rate
        
        # Сервисный сбор
        service_fee = cls._calculate_service_fee(num_services)
        subtotal += service_fee
        
        # Скидка по статусу клиента
        final_price = cls._apply_customer_tier_discount(subtotal, customer_tier)
        
        # Валидация
        return cls._validate_final_price(final_price)


# Пример использования с обработкой ошибок
def calculate_booking_safe(
    room_price: float,
    additional_services_price: float,
    nights: int,
    loyalty_level: int,
    num_services: int,
    customer_tier: str,
    total_booking_price: float
) -> Optional[float]:
    """Безопасная обёртка с обработкой ошибок"""
    try:
        tier = CustomerTier(customer_tier.upper())
        return BookingCalculator.calculate_booking_price(
            room_price, additional_services_price, nights,
            loyalty_level, num_services, tier, total_booking_price
        )
    except ValueError as e:
        print(f"Validation error: {e}")
        return None
    except KeyError:
        print(f"Invalid customer tier: {customer_tier}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


if __name__ == "__main__":
    # Тестирование рефакторинга
    result = calculate_booking_safe(
        room_price=50,
        additional_services_price=150,
        nights=3,
        loyalty_level=2,
        num_services=8,
        customer_tier="VIP",
        total_booking_price=500
    )
    print(f"Refactored result: {result}")
    
    # Тест с невалидными данными
    invalid_result = calculate_booking_safe(
        room_price=50,
        additional_services_price=150,
        nights=100,
        loyalty_level=5,
        num_services=8,
        customer_tier="GOLD",
        total_booking_price=5000
    )
    print(f"Invalid case result: {invalid_result}")
