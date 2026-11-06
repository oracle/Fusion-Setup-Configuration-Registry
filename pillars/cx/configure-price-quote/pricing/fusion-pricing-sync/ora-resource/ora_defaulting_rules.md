# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| business_object | CpqChargeSetSync | The task's Data Loader workflow starts | No |  |
| load_action | IMPORT_AND_LOAD | Core Data Loader initiates the approved archive | No |  |
| sync_direction | Fusion source to CPQ target | The prompt omits source or target without conflicting direction; recommend this direction without overriding an explicit reverse request | No |  |
| charge_set_source | Internal trigger-only sync data without business payload | The task workflow starts; never request charge-set rows or mappings | No |  |
| source_artifact | CpqChargeSetSync DAT from core.data-loader | The task workflow starts; generate with explicit operation create and format dat | No | resolve_loader_business_object |
| RestAction | POST | RestAction is included in the live template and generated DAT; use create-mode generation | No |  |
| chargeId | Core-generated metadata-valid integer, when included | The generic generator includes the optional surrogate field; its value has no business significance | No |  |
