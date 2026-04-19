# Authorized: builtins, standard types, import typing, import abc
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

        # Calculate the rank based on the global original count
        #  and the remaining items (length of storage) always being the
        # first rank at '1'.
        rank = self._count - len(self._storage) + 1
        # FIFO extraction: removes and returns the first item
        item = self._storage.pop(0)
        return rank, item


class NumericProcessor(DataProcessor):
    """
    Handles int, float, and lists of numeric types.
    """
    def validate(self, data: Any) -> bool:
        # Check for single numeric (if the data fits into the
        #  specified types = TRUE)
        if isinstance(data, (int, float)):
            return True
        if isinstance(data, list):
            # Determines True/False if all the data fits in the statement
            #  of being a numeric type
            return all(isinstance(i, (int, float)) for i in data)
        return False

    def ingest(self, data: Union[int, float, List[Union[int, float]]]) -> None:
        if not self.validate(data):
            # Raise exception if data is invalid
            raise ValueError("Improper numeric data")

        # Converts the data into a list if it is not a list already
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
            # Determines True/False if all the data in the lists fits in
            #  the statement of being a str
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
            return all(isinstance(x, str) and isinstance(y, str) for
                       x, y in data.items())

        if isinstance(data, list):
            # to each dictionary in the list, pass the actual function
            #  to validate
            return all(self.validate(d) for d in data)

        return False

    def ingest(self, data: Union[Dict[str, str],
                                 List[Dict[str, str]]]) -> None:
        # Raises error if the data to be stored is not valid
        if not self.validate(data):
            raise ValueError("Improper log data")

        entries = data if isinstance(data, list) else [data]
        for i in entries:
            # Extract the data of the 'log_level' entry in the dict
            level = i.get('log_level', 'UNKNOWN')
            # If 'log_level' is not found, returns 'UNKNOWN' as the value

            # Extract the data of the 'log_message' entry in the dict
            message = i.get('log_message', 'No message')
            # If 'log_message' is not found, returns 'No message' as the value
            self._storage.append(f"{level}: {message}")
            self._count += 1


# NEW CODE: ---------------------------------------------------
class DataStream:

    def __init__(self) -> None:
        # List to store the registred processors
        self.processors: List[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        # Add a new processos to the list
        self.processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for element in stream:
            handled = False
            for processor in self.processors:
                if processor.validate(element):
                    processor.ingest(element)
                    handled = True
                    break
            if not handled:
                # If it doesn't fit any type
                print(f"DataStream error - Can't process element in stream:"
                      f" {element}")

    def print_processors_stats(self) -> None:
        if not self.processors:
            print("== DataStream statistics ==")
            print("No processor found, no data")
            return

        print("== DataStream statistics ==")
        for proc in self.processors:
            # For whichever class, obtains its name
            name = proc.__class__.__name__.replace("Processor", "Processor")
            # total: self._count | remaining: len(self._storage)
            # Note: to access these attributes, make sure they are not
            # private(__) but protected (_), so the DataStream can see them
            total = proc._count
            remaining = len(proc._storage)
            print(f"{name}: total {total} items processed,"
                  f" remaining {remaining} on processor")


if __name__ == "__main__":
    # Test script to demonstrate architecture functionality
    print("=== Code Nexus - Data Stream ===\n")

    data_p = DataStream()
    print("Initialize Data Stream...")
    data_p.print_processors_stats()

    print("\nRegistering Numeric Processor\n")

    num_p = NumericProcessor()
    n_list = ['Hello world', [3.14, -1, 2.71],
              [{'log_level': 'WARNING',
                'log_message': 'Telnet access! Use ssh instead'},
               {'log_level': 'INFO', 'log_message': 'User wil is connected'}],
              42, ['Hi', 'five']]
    print(f"Send first batch of data on stream: {n_list}")

    # Indicate the kind of procedurement to implement (NumericProcessor,
    #  TextProcessor, LogProcessor)
    data_p.register_processor(num_p)
    # Indicate the data to pass to the processor indicated
    data_p.process_stream(n_list)
    # Printing the stats
    data_p.print_processors_stats()

    print("\nRegistering other data processors\n")
    print("Send the same batch again")
    txt_p = TextProcessor()
    data_p.register_processor(txt_p)
    data_p.process_stream(n_list)
    data_p.print_processors_stats()

    log_p = LogProcessor()
    data_p.register_processor(log_p)
    data_p.process_stream(n_list)
    data_p.print_processors_stats()

    
