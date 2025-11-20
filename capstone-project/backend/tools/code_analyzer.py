"""
Code Analyzer Tool
==================

Week 3: Structured output for code analysis
"""

from langchain_core.tools import tool
import ast
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

@tool
def analyze_code_quality(code: str) -> str:
    """
    Analyze Python code for quality, style, and potential issues.
    
    Use this when reviewing student code to provide structured feedback.
    
    Args:
        code: Python code to analyze
    
    Returns:
        Structured analysis with scores and suggestions
    
    Example:
        >>> analyze_code_quality("def f(x):\\n  return x+1")
        "Code Analysis:
        - Style: Use descriptive function names (f -> calculate_next)
        - Spacing: Add spaces around operators (x+1 -> x + 1)
        ..."
    """
    
    logger.info(f"Analyzing code: {code[:50]}...")
    
    issues = []
    good_practices = []
    score = 100
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"❌ Syntax Error: {e}"
    
    # Analyze AST
    for node in ast.walk(tree):
        # Check for good practices
        if isinstance(node, ast.FunctionDef):
            # Check docstrings
            docstring = ast.get_docstring(node)
            if docstring:
                good_practices.append(f"✓ Function '{node.name}' has docstring")
            else:
                issues.append(f"⚠ Function '{node.name}' missing docstring")
                score -= 10
            
            # Check function name
            if len(node.name) <= 2 and node.name not in ['_', '__']:
                issues.append(f"⚠ Function name '{node.name}' is too short - use descriptive names")
                score -= 5
            
            if not node.name.islower():
                issues.append(f"⚠ Function '{node.name}' should use lowercase_with_underscores")
                score -= 5
        
        # Check for bare except
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append("⚠ Avoid bare 'except:' - catch specific exceptions")
                score -= 15
        
        # Check for print statements (should use logging in production)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                issues.append("ℹ Consider using logging instead of print() for production code")
    
    # Check code style with simple heuristics
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Line length
        if len(line) > 100:
            issues.append(f"⚠ Line {i} exceeds 100 characters (PEP 8)")
            score -= 2
        
        # Check for spaces around operators
        if '+=' in line or '-=' in line or '*=' in line:
            good_practices.append("✓ Using augmented assignment operators")
    
    # Calculate complexity score (simplified)
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
            complexity += 1
    
    if complexity > 10:
        issues.append(f"⚠ High complexity ({complexity}) - consider breaking into smaller functions")
        score -= 10
    elif complexity > 5:
        issues.append(f"ℹ Moderate complexity ({complexity}) - still manageable")
    
    # Build response
    result = f"""
📊 **Code Quality Analysis**

**Overall Score: {max(0, score)}/100**

**Complexity**: {complexity}/10 {'(Good)' if complexity <= 5 else '(Could be improved)'}

**Good Practices** ({len(good_practices)}):
"""
    
    for practice in good_practices[:5]:
        result += f"\n  {practice}"
    
    if not good_practices:
        result += "\n  (None detected - code is minimal or needs improvement)"
    
    result += f"\n\n**Issues & Suggestions** ({len(issues)}):"
    
    for issue in issues[:10]:
        result += f"\n  {issue}"
    
    if not issues:
        result += "\n  ✓ No issues found! Great job!"
    
    result += "\n\n**Recommendations**:"
    if score >= 90:
        result += "\n  Excellent code! Keep it up! 🎉"
    elif score >= 70:
        result += "\n  Good code with room for improvement"
    else:
        result += "\n  Several areas need attention - focus on readability and best practices"
    
    return result

def get_code_metrics(code: str) -> Dict[str, Any]:
    """
    Get detailed code metrics
    
    Returns metrics like:
    - Lines of code
    - Number of functions
    - Number of classes
    - Cyclomatic complexity
    """
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"error": "Syntax error in code"}
    
    metrics = {
        "lines_of_code": len(code.split('\n')),
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "complexity": 1
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            metrics["functions"] += 1
        elif isinstance(node, ast.ClassDef):
            metrics["classes"] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            metrics["imports"] += 1
        elif isinstance(node, (ast.If, ast.For, ast.While)):
            metrics["complexity"] += 1
    
    return metrics
