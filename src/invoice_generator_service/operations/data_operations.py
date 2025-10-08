#!/usr/bin/env python3
"""
Data Operations - Clean Data Processing Logic
Single responsibility: Data transformation and mapping operations
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from decimal import Decimal


class DataOperations:
    """Clean, focused data operations without scattered utility functions"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def prepare_data_rows(
        self,
        raw_data: List[Dict[str, Any]],
        column_mapping: Dict[str, str],
        fallback_rules: Optional[Dict[str, Any]] = None
    ) -> List[List[Any]]:
        """
        Prepare data rows for Excel output
        
        Args:
            raw_data: List of raw data dictionaries
            column_mapping: Mapping from column IDs to data keys
            fallback_rules: Rules for handling missing data
            
        Returns:
            List of rows, each row being a list of cell values
        """
        prepared_rows = []
        
        for data_item in raw_data:
            row_values = []
            
            for column_id, data_key in column_mapping.items():
                value = self._extract_data_value(data_item, data_key, fallback_rules)
                normalized_value = self._normalize_data_value(value)
                row_values.append(normalized_value)
            
            prepared_rows.append(row_values)
        
        return prepared_rows
    
    def aggregate_data(
        self,
        data_items: List[Dict[str, Any]],
        group_by: str,
        aggregations: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate data by grouping key
        
        Args:
            data_items: List of data items to aggregate
            group_by: Key to group by
            aggregations: Dictionary mapping output keys to aggregation methods
            
        Returns:
            List of aggregated data items
        """
        groups = {}
        
        # Group data items
        for item in data_items:
            group_key = item.get(group_by)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        
        # Aggregate each group  
        aggregated_results = []
        for group_key, group_items in groups.items():
            aggregated_item = {group_by: group_key}
            
            for output_key, agg_method in aggregations.items():
                aggregated_value = self._apply_aggregation(group_items, output_key, agg_method)
                aggregated_item[output_key] = aggregated_value
            
            aggregated_results.append(aggregated_item)
        
        return aggregated_results
    
    def calculate_totals(
        self,
        data_items: List[Dict[str, Any]],
        total_fields: List[str]
    ) -> Dict[str, Union[int, float, Decimal]]:
        """
        Calculate totals for specified fields
        
        Args:
            data_items: List of data items
            total_fields: List of field names to total
            
        Returns:
            Dictionary mapping field names to their totals
        """
        totals = {}
        
        for field in total_fields:
            total_value = 0
            
            for item in data_items:
                value = item.get(field, 0)
                numeric_value = self._to_numeric(value)
                if numeric_value is not None:
                    total_value += numeric_value
            
            totals[field] = total_value
        
        return totals
    
    def transform_data_structure(
        self,
        input_data: Dict[str, Any],
        transformation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform data structure according to rules
        
        Args:
            input_data: Input data dictionary
            transformation_rules: Transformation rules
            
        Returns:
            Transformed data dictionary
        """
        transformed_data = {}
        
        for output_key, rule in transformation_rules.items():
            if isinstance(rule, str):
                # Simple key mapping
                transformed_data[output_key] = input_data.get(rule)
            elif isinstance(rule, dict):
                # Complex transformation rule
                if 'source_key' in rule:
                    source_value = input_data.get(rule['source_key'])
                    
                    # Apply transformations
                    if 'format' in rule:
                        source_value = self._apply_format(source_value, rule['format'])
                    if 'default' in rule and source_value is None:
                        source_value = rule['default']
                    
                    transformed_data[output_key] = source_value
                elif 'computed' in rule:
                    # Computed field
                    transformed_data[output_key] = self._compute_field(input_data, rule['computed'])
        
        return transformed_data
    
    def validate_data_completeness(
        self,
        data_items: List[Dict[str, Any]],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Validate data completeness
        
        Args:
            data_items: List of data items to validate
            required_fields: List of required field names
            
        Returns:
            Validation results with statistics
        """
        total_items = len(data_items)
        field_stats = {}
        missing_data = []
        
        for field in required_fields:
            missing_count = 0
            empty_count = 0
            
            for i, item in enumerate(data_items):
                if field not in item:
                    missing_count += 1
                    missing_data.append({'row': i, 'field': field, 'issue': 'missing'})
                elif not item[field] or str(item[field]).strip() == '':
                    empty_count += 1
                    missing_data.append({'row': i, 'field': field, 'issue': 'empty'})
            
            field_stats[field] = {
                'total': total_items,
                'missing': missing_count,
                'empty': empty_count,
                'valid': total_items - missing_count - empty_count,
                'completeness_rate': (total_items - missing_count - empty_count) / total_items if total_items > 0 else 0
            }
        
        return {
            'total_items': total_items,
            'field_stats': field_stats,
            'missing_data': missing_data,
            'overall_completeness': sum(stats['completeness_rate'] for stats in field_stats.values()) / len(field_stats) if field_stats else 0
        }
    
    def _extract_data_value(
        self,
        data_item: Dict[str, Any],
        data_key: str,
        fallback_rules: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Extract value from data item with fallback handling"""
        # Handle nested keys (e.g., "address.street")
        if '.' in data_key:
            keys = data_key.split('.')
            value = data_item
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
        else:
            value = data_item.get(data_key)
        
        # Apply fallback rules if value is None/empty
        if (value is None or str(value).strip() == '') and fallback_rules:
            if data_key in fallback_rules:
                fallback_rule = fallback_rules[data_key]
                if isinstance(fallback_rule, str):
                    # Use another field as fallback
                    value = self._extract_data_value(data_item, fallback_rule)
                elif isinstance(fallback_rule, dict) and 'default' in fallback_rule:
                    # Use default value
                    value = fallback_rule['default']
        
        return value
    
    def _normalize_data_value(self, value: Any) -> Any:
        """Normalize data value for Excel output"""
        if value is None:
            return ''
        elif isinstance(value, str):
            return value.strip()
        elif isinstance(value, (int, float, Decimal)):
            return value
        else:
            return str(value)
    
    def _to_numeric(self, value: Any) -> Optional[Union[int, float, Decimal]]:
        """Convert value to numeric type"""
        if value is None:
            return None
        
        if isinstance(value, (int, float, Decimal)):
            return value
        
        if isinstance(value, str):
            value = value.strip().replace(',', '')
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return None
        
        return None
    
    def _apply_aggregation(
        self,
        group_items: List[Dict[str, Any]],
        field: str,
        agg_method: str
    ) -> Any:
        """Apply aggregation method to grouped data"""
        values = [item.get(field) for item in group_items]
        numeric_values = [self._to_numeric(v) for v in values if self._to_numeric(v) is not None]
        
        if not numeric_values:
            return 0
        
        if agg_method == 'sum':
            return sum(numeric_values)
        elif agg_method == 'avg' or agg_method == 'average':
            return sum(numeric_values) / len(numeric_values)
        elif agg_method == 'count':
            return len(group_items)
        elif agg_method == 'min':
            return min(numeric_values)
        elif agg_method == 'max':
            return max(numeric_values)
        else:
            return sum(numeric_values)  # Default to sum
    
    def _apply_format(self, value: Any, format_rule: str) -> Any:
        """Apply formatting rule to value"""
        if value is None:
            return value
        
        if format_rule == 'upper':
            return str(value).upper()
        elif format_rule == 'lower':
            return str(value).lower()
        elif format_rule == 'title':
            return str(value).title()
        elif format_rule.startswith('round:'):
            try:
                decimal_places = int(format_rule.split(':')[1])
                return round(float(value), decimal_places)
            except (ValueError, IndexError):
                return value
        else:
            return value
    
    def _compute_field(self, data_item: Dict[str, Any], computation_rule: str) -> Any:
        """Compute field value based on computation rule"""
        # Simple computation rules - can be expanded
        if computation_rule == 'full_name':
            first_name = data_item.get('first_name', '')
            last_name = data_item.get('last_name', '')
            return f"{first_name} {last_name}".strip()
        elif computation_rule == 'total_amount':
            quantity = self._to_numeric(data_item.get('quantity', 0)) or 0
            unit_price = self._to_numeric(data_item.get('unit_price', 0)) or 0
            return quantity * unit_price
        else:
            return None