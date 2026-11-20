"""Serialize reviewed Per Diem value effects with exact source-owned origin.

Existing LineValue updates join the exact-field uncertainty plan. Wholly new
policy groups may generate only their reviewed internal deduction companions.
No client IDs, independent value targets, inferred defaults or deletion.
"""
from per_diem_profile import V, SOURCE, plan_existing_value_updates, validate_evidence
import field_uncertainty


def append_existing_effects(records, rows, selected_rows, changes, changed, requests, contract, *, original_rows=None):
    new_review=[]
    new_names={next(f['after']for f in change['fields']if f['field']=='PolicyName')
        for change in changes if change['entity']=='ORA_EXM_PERDIEM_POLICY'and change['operation']=='create'}
    if new_names:
        if original_rows is None:raise ValueError('New Per Diem value effects require original-policy absence proof')
        from per_diem_create import new_value_rows,IDS
        from per_diem_profile import P,R,VALUE_IDENTITY,policy_rows,validate_change
        from operation_contract import resolve_policy_operation_contract
        from build_fsm_from_workbook import validate_create_empties
        entry=contract.get('entities',{}).get(V,{})
        if (resolve_policy_operation_contract(V,entry,contract)
                or entry.get('internal_new_policy_value_effects_only')is not True
                or 'create'not in entry.get('operations',[])):
            raise ValueError('Per Diem new values require exact internal new-policy ownership')
        for name in sorted(new_names):
            if any(policy_rows(original_rows,name,e)for e in [P,R,V]):
                raise ValueError('Existing Per Diem policy/line/value cannot be reused as a new internal group')
            parents=policy_rows(rows,name,P)
            if len(parents)!=1 or policy_rows(rows,name,V):raise ValueError('Per Diem new value group is ambiguous or prepopulated')
            for after in new_value_rows(parents[0],policy_rows(rows,name,R),contract):
                before=dict.fromkeys(after,'')
                validate_change(V,'create',before,after,original_rows)
                empty=validate_create_empties(after,entry,contract,V,set())
                rows[V].append(after);selected_rows[V].append(after);changed.add(V)
                change={'entity':V,'operation':'create','sources':[],
                    'generated_new_value_effect':True,'source_ids':IDS[:],
                    'targetKey':{f:after.get(f,'')for f in VALUE_IDENTITY},
                    'reason':'Explicit source-derived deduction companion for a wholly new policy, not FSM UI synchronization',
                    'create_empty_field_contracts':empty,
                    'fields':[{'field':f,'before':'','after':value}for f,value in after.items()if value!=''or f=='LineValue']}
                changes.append(change);new_review.append(change)
    effects = plan_existing_value_updates(records, rows,exclude_new_policies=new_names)
    if not effects:
        return new_review
    validate_evidence(contract)
    from operation_contract import resolve_policy_operation_contract
    entry = contract.get('entities', {}).get(V, {})
    if resolve_policy_operation_contract(V, entry, contract) or entry.get('internal_existing_value_effects_only') is not True:
        raise ValueError('Per Diem existing value effects require their exact reviewed internal ownership contract')
    review = new_review
    for effect in effects:
        before, after = effect['before'], effect['after']
        requests.append(field_uncertainty.request(V, 'update', 'LineValue', before, after, entry, contract))
        # Preserve every original field/key/audit. The explicit candidate CSV
        # contains only the already-existing rows whose value actually changes.
        rows[V][rows[V].index(before)] = after
        selected_rows[V].append(after)
        changed.add(V)
        change = {'entity': V, 'operation': 'update', 'sources': [],
            'generated_existing_value_effect': True, 'targetKey': effect['targetKey'],
            'reason': effect['reason'], 'source_ids': [SOURCE],
            'fields': [{'field': 'LineValue', 'before': before['LineValue'], 'after': after['LineValue']}]}
        changes.append(change)
        review.append(change)
    return review
