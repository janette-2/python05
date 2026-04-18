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
    def ingest(self, data: Any) -> None:
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
            # Determines True/False if all the data fits in the statement of being a numeric type
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
    """
    Handles strings and lists of strings
    """
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list):
            # Determines True/False if all the data in the lists fits in the statement of being a str
            return all(isinstance(x, str) for x in data)
        return False
    
    def ingest(self, data: Union[str, List[str]]) -> None:
        # Raises error if the data to be stored is not valid
        if not self.validate(data):
            raise ValueError("Improper text data")
        
        # Converts the data into a list if it is not a list already
        items = data if isinstance(data, list) else [data]
        # Stores the data and tracks their position(determines their rank)
        for val in items:
            # Stores the data converting it into str
            self._storage.append(val)
            # Tracks the elements stored, which translates into their rank
            self._count += 1 


class LogProcessor(DataProcessor):
    """
    Handles dicts of string key-value pairs and lists of dictionaries
    """

    def validate(self, data: Any) -> bool:
        # Validate dictionary keys and values are strings
        if isinstance(data, dict):
            # Checks that both the key and value returned are str
            return all(isinstance(x, str) and isinstance(y, str) for x, y in data.items()) --> PUEDO USAR ESTO? 
       
        if isinstance(data, list):
            # to each dictionary in the list, pass the actual function to validate
            return all(self.validate(d) for d in data)
        
        return False


    def ingest(self, data: Union[Dict[str, str], List[Dict[str, str]]]) -> None:
        # Raises error if the data to be stored is not valid
        if not self.validate(data):
            raise ValueError("Improper log data")
        

        entries = data if isinstance(data, list) else [data]
        for i in entries:
            # For each entry in the dictionaries stored in data...
            for key, value in i.items():
                # Stores one entry of the dictionary with the dict format and together
                self._storage.append(f"{key}: {value}")
                self._count += 1


if __name__ == "__main__":
    # Test script to demonstrate architecture functionality
    print("=== Code Nexus Data Processor ===")

    # 1. Instantiate specialized classes
    num_p = NumericProcessor()
    txt_p = TextProcessor()
    log_p = LogProcessor()

    # 2. Test validation[cite: 119].
    print(f"Validating 42 in Numeric: {num_p.validate(42)}")
    print(f"Validating 'Hello' in Numeric: {num_p.validate('Hello')}")

    # 3. Test exception on invalid ingestion without validation
    try:
        # This will trigger a mypy warning on purpose
        num_p.ingest("Invalid Data")  # type: ignore
    except ValueError as e:
        print(f"Got exception: {e}")

    # 4. Ingest and extract data
    num_p.ingest([1, 2, 3])
    log_p.ingest({"NOTICE": "Connection to server"})

    # Demonstrate FIFO output[cite: 122].
    rank, val = num_p.output()
    print(f"Numeric value {rank-1}: {val}")
    
    log_rank, log_val = log_p.output()
    print(f"Log entry {log_rank-1}: {log_val}")
