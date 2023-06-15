from __future__ import annotations

import csv
import json
import logging

from enum import Enum, unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional

@unique
class DataOutputType(Enum):
    CSV = "csv"
    JSON = "json"

class DataAccumulator():
    """Defines a utility to accumulate the extracted data
        in addition to functions to assist in its manipulation.
    """    
    def __init__(self: DataAccumulator) -> None:
        self._data = None

    def add_json_data(self: DataAccumulator, data: Dict[str, str]) -> None:
        """Adds a set of JSON (dict) data into the accumulator

        Parameters
        ----------
        data : Dict[str, str]
            The data to be added in a JSON (Dict) format
        """        
        if not self._data:
            self._data = data
        else:
            self._data.update(data)

    def dump(self: DataAccumulator, output_path: str, output_type: DataOutputType, data_filters: List[str] = None) -> None:
        """Stores the accumulated information onto the defined output path

        Parameters
        ----------
        output_path : str
            The local filesystem path in which to store the information
        output_type : DataOutputType
            The data output type
        data_filters : List[str], optional
            The set of data headers to retain, by default None

        Raises
        ------
        NotImplementedError
            Raises a not implemented error should the output_type not be implemented
        """        
        if len(self._data) > 0:
            match(output_type):
                case DataOutputType.CSV:
                    self._to_csv(output_path=output_path, data_filters=data_filters)
                case DataOutputType.JSON:
                    self._to_json(output_path=output_path, data_filters=data_filters)
                case _:
                    raise NotImplementedError(f"Accumulator dump not implemented for output type {output_type}")
                
        else:
            logging.warning("Skipping data saving due to no data being provided.")
            
    def _to_csv(self: DataAccumulator, output_path: str, data_filters: List[str] = None) -> None:
        """Stores the data into a CSV format

        Parameters
        ----------
        output_path : str
            The local filesystem path in which to store the information
        data_filters : List[str], optional
            The set of data headers to retain, by default None
        """        
        filtered_data: Dict[str, Any] = self._filter_data(data_filters=data_filters)
        csv_headers: List[str] = filtered_data[0].keys()

        with open(output_path, 'w', newline='', encoding='UTF-8') as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerows(filtered_data)

    def _to_json(self: DataAccumulator, output_path: str, data_filters: List[str] = None) -> None:
        """Stores the data into a JSON format

        Parameters
        ----------
        output_path : str
            The local filesystem path in which to store the information
        data_filters : List[str], optional
            The set of data headers to retain, by default None
        """  
        filtered_data: Dict[str, Any] = self._filter_data(data_filters=data_filters)

        with open(output_path, 'w', newline='', encoding='UTF-8') as outfile:
            json.dump(filtered_data, outfile, indent=4, ensure_ascii=False)

    def _filter_data(self: DataAccumulator, data_filters: List[str] = None) -> List[Any]:
        """Filters the existing data by selecting only data whose key
            is present in data_filters

        Parameters
        ----------
        data_filters : List[str], optional
            The set of data headers to retain, by default None

        Returns
        -------
        List[Any]
            The filtered information
        """        
        if not data_filters:
            return self._data
        
        output_data: List[Optional[Dict[str, Any]]] = []

        for list_item in self._data:
            filtered_list_item: Dict[str, Any] = {}
            for (k, v) in list_item.items():
                if k in data_filters:
                    filtered_list_item[k] = v

            output_data.append(filtered_list_item)

        return output_data