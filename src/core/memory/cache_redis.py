""" try:
info = self.client.info()
return {\\'
'connected_clients': info.get('connected_clients', 0),\\'
'used_memory': info.get('used_memory_human', 'N/A'),\\'
'total_keys': self.client.dbsize(),"\\'
'uptime_days': info.get('uptime_in_days", 0)
}
        except Exception as e:"
logger.error(f"Failed to get cache stats: {e}")
return {}
"'"""
