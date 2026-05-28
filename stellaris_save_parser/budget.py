"""
Module for parsing empire budget and resource income/expenses.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import re


@dataclass
class ResourceBudget:
    """
    Represents the complete resource budget for an empire.
    
    This includes all income sources, expenses, and market trades.
    """
    income: Dict[str, float] = field(default_factory=dict)
    expenses: Dict[str, float] = field(default_factory=dict)
    trade_balance: Dict[str, float] = field(default_factory=dict)
    
    def get_net(self, resource: str) -> float:
        """
        Calculate net income for a resource.
        
        Formula: Income - Expenses + Trade Balance
        
        Args:
            resource: Resource name (e.g., 'energy', 'minerals')
            
        Returns:
            Net monthly income
        """
        income = self.income.get(resource, 0)
        expenses = self.expenses.get(resource, 0)
        trade = self.trade_balance.get(resource, 0)
        
        return income - expenses + trade
    
    def get_all_net(self) -> Dict[str, float]:
        """
        Get net income for all resources.
        
        Returns:
            Dictionary mapping resource names to net income
        """
        all_resources = set(self.income.keys()) | set(self.expenses.keys()) | set(self.trade_balance.keys())
        
        return {res: self.get_net(res) for res in all_resources}
    
    @property
    def net_energy(self) -> float:
        """Net energy income per month."""
        return self.get_net('energy')
    
    @property
    def net_minerals(self) -> float:
        """Net mineral income per month."""
        return self.get_net('minerals')
    
    @property
    def net_food(self) -> float:
        """Net food income per month."""
        return self.get_net('food')
    
    @property
    def net_alloys(self) -> float:
        """Net alloy income per month."""
        return self.get_net('alloys')
    
    @property
    def net_consumer_goods(self) -> float:
        """Net consumer goods income per month."""
        return self.get_net('consumer_goods')
    
    @property
    def net_unity(self) -> float:
        """Net unity income per month."""
        return self.get_net('unity')
    
    @property
    def net_influence(self) -> float:
        """Net influence income per month."""
        return self.get_net('influence')
    
    @property
    def net_physics_research(self) -> float:
        """Net physics research per month."""
        return self.get_net('physics_research')
    
    @property
    def net_society_research(self) -> float:
        """Net society research per month."""
        return self.get_net('society_research')
    
    @property
    def net_engineering_research(self) -> float:
        """Net engineering research per month."""
        return self.get_net('engineering_research')
    
    @property
    def total_research(self) -> float:
        """Total research per month (all fields combined)."""
        return (self.net_physics_research + 
                self.net_society_research + 
                self.net_engineering_research)


@dataclass
class BudgetBreakdown:
    """
    Detailed breakdown of income and expenses by category.
    """
    income_by_category: Dict[str, Dict[str, float]] = field(default_factory=dict)
    expenses_by_category: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def get_income_for_resource(self, resource: str) -> Dict[str, float]:
        """
        Get all income sources for a specific resource.
        
        Args:
            resource: Resource name
            
        Returns:
            Dictionary mapping category names to income amounts
        """
        result = {}
        for category, resources in self.income_by_category.items():
            if resource in resources:
                result[category] = resources[resource]
        return result
    
    def get_expenses_for_resource(self, resource: str) -> Dict[str, float]:
        """
        Get all expense categories for a specific resource.
        
        Args:
            resource: Resource name
            
        Returns:
            Dictionary mapping category names to expense amounts
        """
        result = {}
        for category, resources in self.expenses_by_category.items():
            if resource in resources:
                result[category] = resources[resource]
        return result


def parse_budget(country_data: str) -> Optional[ResourceBudget]:
    """
    Parse the empire budget from country data.
    
    Args:
        country_data: The country block data from save file
        
    Returns:
        ResourceBudget object or None if not found
    """
    # Find current_month budget section
    budget_match = re.search(
        r'current_month=\s*\{(.*?)\n\t\t\t\}',
        country_data,
        re.DOTALL
    )
    
    if not budget_match:
        return None
    
    budget_data = budget_match.group(1)
    
    # Parse income
    income_match = re.search(
        r'income=\s*\{(.*?)\n\t\t\t\t\}',
        budget_data,
        re.DOTALL
    )
    
    # Parse expenses
    expenses_match = re.search(
        r'expenses=\s*\{(.*?)\n\t\t\t\t\}',
        budget_data,
        re.DOTALL
    )
    
    # Parse trade balance
    trade_balance_match = re.search(
        r'trade_balance=\s*\{([^}]+)\}',
        budget_data
    )
    
    # Sum up all income
    total_income = {}
    if income_match:
        for cat_match in re.finditer(r'([a-z_]+)=\s*\{([^}]+)\}', income_match.group(1)):
            for res_match in re.finditer(r'([a-z_]+)=([-0-9.]+)', cat_match.group(2)):
                res_name = res_match.group(1)
                res_value = float(res_match.group(2))
                total_income[res_name] = total_income.get(res_name, 0) + res_value
    
    # Sum up all expenses
    total_expenses = {}
    if expenses_match:
        for cat_match in re.finditer(r'([a-z_]+)=\s*\{([^}]+)\}', expenses_match.group(1)):
            for res_match in re.finditer(r'([a-z_]+)=([-0-9.]+)', cat_match.group(2)):
                res_name = res_match.group(1)
                res_value = float(res_match.group(2))
                total_expenses[res_name] = total_expenses.get(res_name, 0) + res_value
    
    # Parse trade balance
    trade_balance = {}
    if trade_balance_match:
        for res_match in re.finditer(r'([a-z_]+)=([-0-9.]+)', trade_balance_match.group(1)):
            res_name = res_match.group(1)
            res_value = float(res_match.group(2))
            trade_balance[res_name] = res_value
    
    return ResourceBudget(
        income=total_income,
        expenses=total_expenses,
        trade_balance=trade_balance
    )


def parse_budget_breakdown(country_data: str) -> Optional[BudgetBreakdown]:
    """
    Parse detailed budget breakdown by category.
    
    Args:
        country_data: The country block data from save file
        
    Returns:
        BudgetBreakdown object or None if not found
    """
    budget_match = re.search(
        r'current_month=\s*\{(.*?)\n\t\t\t\}',
        country_data,
        re.DOTALL
    )
    
    if not budget_match:
        return None
    
    budget_data = budget_match.group(1)
    
    # Parse income by category
    income_by_category = {}
    income_match = re.search(
        r'income=\s*\{(.*?)\n\t\t\t\t\}',
        budget_data,
        re.DOTALL
    )
    
    if income_match:
        for cat_match in re.finditer(r'([a-z_]+)=\s*\{([^}]+)\}', income_match.group(1)):
            cat_name = cat_match.group(1)
            cat_data = cat_match.group(2)
            
            resources = {}
            for res_match in re.finditer(r'([a-z_]+)=([-0-9.]+)', cat_data):
                res_name = res_match.group(1)
                res_value = float(res_match.group(2))
                resources[res_name] = res_value
            
            if resources:
                income_by_category[cat_name] = resources
    
    # Parse expenses by category
    expenses_by_category = {}
    expenses_match = re.search(
        r'expenses=\s*\{(.*?)\n\t\t\t\t\}',
        budget_data,
        re.DOTALL
    )
    
    if expenses_match:
        for cat_match in re.finditer(r'([a-z_]+)=\s*\{([^}]+)\}', expenses_match.group(1)):
            cat_name = cat_match.group(1)
            cat_data = cat_match.group(2)
            
            resources = {}
            for res_match in re.finditer(r'([a-z_]+)=([-0-9.]+)', cat_data):
                res_name = res_match.group(1)
                res_value = float(res_match.group(2))
                resources[res_name] = res_value
            
            if resources:
                expenses_by_category[cat_name] = resources
    
    return BudgetBreakdown(
        income_by_category=income_by_category,
        expenses_by_category=expenses_by_category
    )
