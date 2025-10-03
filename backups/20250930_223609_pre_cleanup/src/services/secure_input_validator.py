""" result = {" "valid": True," "sanitized_data": {}," "warnings": []," "errors": [] } for key, value in request_data.items():
            if isinstance(value, str):
validation = self.validate_text_input(value)"
result["sanitized_data"][key] = validation["sanitized"]
"
                if not validation["valid"]:"
result["valid"] = False"
result["errors"].extend(validation["errors"])
"
result["warnings"].extend(validation["warnings"])
else:"
result["sanitized_data"][key] = value

return result

    def is_safe_content(self, content: str) -> bool:"
validation = self.validate_text_input(content)"
return validation["valid"] and len(validation["warnings"]) == 0
"'"""
