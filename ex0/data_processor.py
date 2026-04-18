from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union

class DataProcessor(ABC):

    def __init__(self) -> None:
        # Internal storage for processed strings
        self._storage: List[str] = []
        # Counter to track the global processing rank
        self._count: int = 0

    # Abstract methods: Methods that will be developed in the future
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Abstract method to verify if the input data matches the processor type
        Returns True if valid, False otherwise
        """
        pass

    @abstractmethod
    def ignore(self, data: Any) -> bool:
        """
        Abstract method to process and store data
        Must be overridden by specialized subclasses.
        """
        pass

    def output(self) -> tuple[int, str]:
        """
        Standard method to extract the oldest data (FIFO)
        Returns a tuple containing the processing rank and the data string
        """
        if not self._storage:
            raise IndexError("No data available in the processor.")
        
        # Calculate the rank based on current count and remaining items.
        rank = self._count - len(self._storage) + 1
        # FIFO extraction: remove and return the first item
        item = self._storage.pop(0) --> PUEDO USAR ESTO? 
        return rank, item


class NumericProcessor(DataProcessor):
    """
    Handles int, float, and lists of numeric types.
    """
    def validate(self, data: Any) -> bool:
        # Check for single numeric (if the data fits into the specified types = TRUE)
        if isinstance(data, (int, float)):
            return True
        if isinstance(data, list):
            # Determines True/False if all the data fits in the statement
            return all(isinstance(i, (int, float)) for i in data)
        return False
        
    def ingest(self, data: Union[int, float, List[Union[int, float]]]) -> None:
        if not self.validate(data):
            # Raise exception if data is invalid
            raise ValueError("Improper numeric data")

        #Converts the data into a list if it is not a list already
        items = data if isinstance(data, list) else [data]
        for val in items:
            # Stores the data converting it into str
            self._storage.append(str(val))
            # Tracks the elements stored, which translates into their rank
            self._count += 1


class TextProcessor(DataProcessor):


class LogProcessor(DataProcessor):

