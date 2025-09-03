"""
DTO - Body Type Enum for API
"""

from enum import Enum


class BodyTypeResponse(str, Enum):
    """Body type options for API response"""
    HOURGLASS = "hourglass"
    APPLE = "apple"
    PEAR = "pear"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"
    
    @classmethod
    def from_domain_type(cls, domain_body_type) -> "BodyTypeResponse":
        """Convert from domain BodyType to DTO"""
        return cls(domain_body_type.value)
