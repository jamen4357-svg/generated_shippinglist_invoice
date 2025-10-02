"""
This module provides utility classes for converting and transforming data.
"""

class DataConverter:
    """
    A utility class that groups related data conversion functions.
    Methods are static as they do not depend on the state of an instance.
    """
    @staticmethod
    def convert_pallet_string(pallet_string: str) -> int:
        """
        Converts a pallet string into a pallet count based on specific rules.

        The logic is as follows:
        - A range 'x-y' (e.g., '1-2', '3-5', '2-2') counts as 1 pallet.
        - A single number (e.g., '5') counts as 1 pallet.
        - '0' or an empty/invalid string counts as 0 pallets.

        Args:
            pallet_string (str): The string representing the pallet notation.

        Returns:
            int: The calculated number of pallets (0 or 1).
        
        Examples:
            >>> DataConverter.convert_pallet_string('1-2')
            1
            >>> DataConverter.convert_pallet_string('5')
            1
            >>> DataConverter.convert_pallet_string('2-2')
            1
            >>> DataConverter.convert_pallet_string('0')
            0
            >>> DataConverter.convert_pallet_string('')
            0
        """
        if not pallet_string or not isinstance(pallet_string, str):
            return 0

        pallet_string = pallet_string.strip()
        
        if not pallet_string:
            return 0

        if '-' in pallet_string:
            try:
                start, end = map(int, pallet_string.split('-'))
                # Any valid range counts as 1 pallet.
                return 1
            except (ValueError, IndexError):
                return 0  # Invalid range format
        else:
            try:
                num = int(pallet_string)
                # A single number entry counts as 1 if it's not zero.
                return 1 if num > 0 else 0
            except ValueError:
                return 0 # Not a valid number
