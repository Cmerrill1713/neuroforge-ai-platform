""" total_entries = len(self.cache) if total_entries == 0:
return {\\'
'total_entries': 0,\\'
'hit_rate': 0.0,\\'
'avg_ttl': 0
}

current_time = time.time()
valid_entries = sum(1 for entry in self.cache.values()\\'
                          if current_time < entry['expires_at'])
'
avg_ttl = sum(entry['ttl'] for entry in self.cache.values()) / total_entries

return {\\'
'total_entries': total_entries,\\'
'valid_entries': valid_entries,\\'
'max_size': self.max_size,"\\'
'avg_ttl": round(avg_ttl, 1)
}
"'"""
