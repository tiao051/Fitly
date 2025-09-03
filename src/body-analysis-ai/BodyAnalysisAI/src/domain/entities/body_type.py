"""
Domain Entity - Body Type Classification
"""

from enum import Enum


class BodyType(Enum):
    """Body type classification categories"""
    HOURGLASS = "hourglass"      # X-shape: shoulders ≈ hips, small waist
    APPLE = "apple"              # O-shape: fuller midsection
    PEAR = "pear"                # A-shape: hips > shoulders
    RECTANGLE = "rectangle"      # H-shape: shoulders ≈ waist ≈ hips
    INVERTED_TRIANGLE = "inverted_triangle"  # V-shape: shoulders > hips
    
    @classmethod
    def from_string(cls, value: str) -> "BodyType":
        """Create BodyType from string value"""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid body type: {value}")
    
    def get_description(self) -> str:
        """Get human-readable description"""
        descriptions = {
            self.HOURGLASS: "X-shape with balanced shoulders and hips, defined waist",
            self.APPLE: "O-shape with fuller midsection",
            self.PEAR: "A-shape with hips wider than shoulders",
            self.RECTANGLE: "H-shape with similar shoulder, waist, and hip measurements",
            self.INVERTED_TRIANGLE: "V-shape with shoulders wider than hips"
        }
        return descriptions[self]
