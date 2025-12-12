---
description: 'Use placeholder code with docstrings instead of full implementations for code.'
---
Create interface stubs with comprehensive docstrings that include module documentation,
class descriptions, method signatures with full type annotations, parameter descriptions, 
return types, potential exceptions, and usage examples. Do not implement any business logic.
Classes may be organized across multiple files (e.g., models in `models.py`, main classes 
in separate modules, exceptions in `exceptions.py`).

# Example
## prompt provided by the user

Create a vehicle management system with the following requirements:

1. A Driver model that stores driver information including name, license number, and optional license expiry date
2. A Car class that can:
   - Be initialized with make, model, and year
   - Start and stop the engine
   - Drive a specified distance (updating odometer and consuming fuel)
   - Assign a driver to the vehicle
   - Check engine status, odometer reading, and remaining fuel
3. Custom exceptions for:
   - Engine-related errors (general engine failures, attempting to start already running engine)
   - Invalid operations (no driver assigned, engine not running)
   - Invalid or expired license
   - Insufficient fuel for driving distance

Organize the code into separate files: exceptions.py for custom exceptions, models.py for data models, and vehicle.py for the main Car class. Include comprehensive docstrings with type annotations, parameter descriptions, return values, raised exceptions, and usage examples. Use defensive programming patterns and do not implement any business logic (use NotImplementedError for method bodies).

## Code generated 

**File: exceptions.py**
```python
"""Custom exceptions for the vehicle management system.

This module defines all custom exception types used throughout the vehicle
system for specific error conditions.

Classes:
    VehicleError: Base exception for all vehicle-related errors.
    EngineError: Raised when engine operations fail.
    EngineAlreadyRunningError: Raised when attempting to start running engine.
    InvalidOperationError: Raised when operation cannot be performed.
    InvalidLicenseError: Raised when driver license is invalid or expired.
    InsufficientFuelError: Raised when fuel is insufficient for operation.
"""


class VehicleError(Exception):
    """Base exception for all vehicle-related errors.
    
    All custom vehicle exceptions inherit from this base class, allowing
    for catch-all exception handling when needed.
    
    Example:
        try:
            car.start_engine()
        except VehicleError as e:
            print(f"Vehicle error occurred: {e}")
    """


class EngineError(VehicleError):
    """Raised when engine operations fail due to mechanical issues.
    
    This exception indicates a problem with starting, stopping, or
    operating the engine that is not related to preconditions.
    
    Example:
        raise EngineError("Engine failed to start: battery dead")
    """


class EngineAlreadyRunningError(VehicleError):
    """Raised when attempting to start an engine that is already running.
    
    Prevents redundant start operations that could damage the engine.
    
    Example:
        if self._engine_running:
            raise EngineAlreadyRunningError(
                "Cannot start engine: already running"
            )
    """


class InvalidOperationError(VehicleError):
    """Raised when an operation cannot be performed in current state.
    
    Used for state violations such as attempting to drive without a driver
    or without the engine running.
    
    Example:
        if not self._current_driver:
            raise InvalidOperationError(
                "Cannot start engine: no driver assigned"
            )
    """


class InvalidLicenseError(VehicleError):
    """Raised when a driver's license is invalid or expired.
    
    Prevents assignment of drivers who cannot legally operate vehicles.
    
    Attributes:
        license_number: The invalid license number.
        reason: Description of why the license is invalid.
    
    Example:
        if driver.license_expiry and driver.license_expiry < datetime.now():
            raise InvalidLicenseError(
                f"License {driver.license_number} expired on "
                f"{driver.license_expiry}"
            )
    """


class InsufficientFuelError(VehicleError):
    """Raised when fuel level is insufficient for requested operation.
    
    Prevents driving operations that would exceed available fuel capacity.
    
    Attributes:
        required_fuel: Amount of fuel needed for operation.
        available_fuel: Current fuel level in tank.
    
    Example:
        if fuel_needed > self._fuel_level:
            raise InsufficientFuelError(
                f"Need {fuel_needed:.2f} gallons, "
                f"only {self._fuel_level:.2f} available"
            )
    """
```

**File: models.py**
```python 
"""Data models for the vehicle management system.

This module contains immutable data classes representing core entities
in the vehicle system.

Classes:
    Driver: Represents a licensed vehicle operator.
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class Driver:
    """Represents a licensed driver who can operate vehicles.
    
    Immutable dataclass containing driver identification and licensing info.
    Uses frozen=True for immutability and slots=True for memory efficiency.
    
    Attributes:
        name: Full name of the driver.
        license_number: Unique driver's license identifier.
        license_expiry: Optional expiration date of the license.
    
    Example:
        driver = Driver(
            name="Jane Smith",
            license_number="DL789012",
            license_expiry=datetime(2026, 12, 31)
        )
    """
    name: str
    license_number: str
    license_expiry: Optional[datetime] = None
```

**File: vehicle.py**
```python
"""Vehicle management system with driver assignments.

This module provides classes for managing vehicles and their operations.
Demonstrates proper interface design with comprehensive docstrings following
Google-style documentation standards.

Classes:
    Car: Represents a vehicle with engine and driving operations.

Example:
    Basic usage of the vehicle system:
    
        from models import Driver
        from vehicle import Car
        
        driver = Driver(name="John Doe", license_number="DL123456")
        car = Car(make="Toyota", model="Camry", year=2024)
        
        car.assign_driver(driver)
        car.start_engine()
        car.drive(distance=50.5)
        car.stop_engine()
"""
from models import Driver


class Car:
    """Represents a vehicle with engine control and driving capabilities.
    
    Manages vehicle state including engine status, odometer readings, and
    driver assignments. Follows defensive programming with validation and
    proper exception handling.
    
    Attributes:
        make: Vehicle manufacturer (e.g., "Toyota", "Honda").
        model: Vehicle model name (e.g., "Camry", "Accord").
        year: Manufacturing year of the vehicle.
        _engine_running: Internal state tracking if engine is on.
        _odometer: Internal odometer reading in miles.
        _current_driver: Currently assigned driver, if any.
    
    Example:
        Basic vehicle operations:
        
            car = Car(make="Honda", model="Civic", year=2023)
            driver = Driver(name="Bob Jones", license_number="DL456789")
            
            car.assign_driver(driver)
            car.start_engine()
            car.drive(distance=25.0)
            remaining = car.get_remaining_fuel()
            car.stop_engine()
    """
    
    def __init__(self, *, make: str, model: str, year: int) -> None:
        """Initialize a new car with specified details.
        
        Args:
            make: Vehicle manufacturer name.
            model: Vehicle model name.
            year: Manufacturing year (must be between 1900 and current year).
            
        Raises:
            ValueError: If make or model is empty, or year is invalid.
            
        Example:
            car = Car(make="Ford", model="F-150", year=2024)
        """
        raise NotImplementedError

    def start_engine(self) -> None:
        """Start the car's engine if conditions are met.
        
        Validates that a driver is assigned and engine is not already running
        before attempting to start. Updates internal engine state on success.
        
        Raises:
            EngineError: If engine fails to start due to mechanical issues.
            InvalidOperationError: If no driver is assigned.
            EngineAlreadyRunningError: If engine is already running.
            
        Example:
            car.assign_driver(driver)
            car.start_engine()  # Engine now running
        """
        raise NotImplementedError

    def stop_engine(self) -> None:
        """Stop the car's engine if it is running.
        
        Safely stops the engine and updates internal state. This is a safe
        operation that will not raise if engine is already stopped.
        
        Raises:
            EngineError: If engine fails to stop due to mechanical issues.
            
        Example:
            car.stop_engine()  # Engine now stopped
        """
        raise NotImplementedError

    def drive(self, *, distance: float) -> float:
        """Drive the car for a specified distance.
        
        Updates the odometer and consumes fuel proportionally to distance.
        Requires engine to be running and valid driver assignment.
        
        Args:
            distance: Distance to drive in miles (must be positive).
            
        Returns:
            Updated odometer reading in miles after driving.
            
        Raises:
            ValueError: If distance is negative or zero.
            InvalidOperationError: If engine is not running.
            InsufficientFuelError: If fuel tank cannot support the distance.
            
        Example:
            car.start_engine()
            new_odometer = car.drive(distance=100.5)
            print(f"Total miles: {new_odometer}")
        """
        raise NotImplementedError
    
    def assign_driver(self, driver: Driver) -> None:
        """Assign a licensed driver to operate this vehicle.
        
        Validates driver license status before assignment. Only one driver
        can be assigned at a time.
        
        Args:
            driver: Driver instance with valid license information.
            
        Raises:
            ValueError: If driver is None.
            InvalidLicenseError: If driver's license is expired or invalid.
            
        Example:
            driver = Driver(name="Alice", license_number="DL111222")
            car.assign_driver(driver)
        """
        raise NotImplementedError
    
    def get_odometer_reading(self) -> float:
        """Get current odometer reading.
        
        Returns:
            Current odometer value in miles.
            
        Example:
            miles = car.get_odometer_reading()
            print(f"Vehicle has traveled {miles} miles")
        """
        raise NotImplementedError
    
    def get_remaining_fuel(self) -> float:
        """Get remaining fuel in the tank.
        
        Returns:
            Remaining fuel in gallons.
            
        Example:
            fuel = car.get_remaining_fuel()
            if fuel < 2.0:
                print("Low fuel warning!")
        """
        raise NotImplementedError
    
    @property
    def is_engine_running(self) -> bool:
        """Check if the engine is currently running.
        
        Returns:
            True if engine is running, False otherwise.
            
        Example:
            if car.is_engine_running:
                print("Engine is on")
        """
        raise NotImplementedError
```