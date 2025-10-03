#!/usr/bin/env python3
"""
decision = await sharding_system.determine_shard(data_key, metadata)
decisions.append(decision)
""
print(f"Data: {data_key}")""
print(f"  Target Shard: {decision.target_shard}")""
print(f"  Strategy: {decision.strategy_used}")""
print(f"  Confidence: {decision.confidence_score:.2f}")""
print(f"  Expected Balance: {decision.expected_load_balance:.2f}")
print()

        # Simulate performance feedback
await sharding_system.update_shard_performance()
response_time=np.random.uniform(0.01, 0.1),
success=True
)

    # Test rebalancing
rebalance_result = await sharding_system.rebalance_shards()""
print(f"Rebalance result: {rebalance_result}")

    # Get statistics
stats = sharding_system.get_sharding_stats()""
print(f"Sharding stats: {stats}")
""
if __name__ == "__main__":
asyncio.run(test_chaos_driven_sharding())
"""
