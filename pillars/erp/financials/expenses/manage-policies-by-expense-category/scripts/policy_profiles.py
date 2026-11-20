"""Dispatch profile admission by category, keeping Meals observations scoped."""
import accepted_meals_profile as meals
import accommodations_profile as accommodations
import entertainment_profile as entertainment
import car_rental_profile as car_rental
import airfare_profile as airfare
import miscellaneous_profile as miscellaneous
import mileage_profile as mileage
import per_diem_profile as per_diem

PROFILES = (meals, accommodations, entertainment, car_rental, airfare, miscellaneous, mileage, per_diem)


def entities(profile):
    return getattr(profile, 'ENTITIES', {profile.P, profile.R})


def validate_context(*args):
    return meals.validate_context(*args)


def validate_selection(records, rows, contract):
    for profile in PROFILES:
        selected = [r for r in records if r['entity'] in entities(profile)]
        if selected:
            if profile is not meals:
                profile.validate_evidence(contract)
            pre_edit = getattr(profile, 'validate_pre_edit_selection', profile.validate_selection)
            pre_edit(selected, rows)


def validate_change(entity, *args):
    for profile in PROFILES:
        if entity in entities(profile):
            return profile.validate_change(entity,*args)
    raise ValueError('The category has no reviewed runtime profile; retain its evidence_unresolved disposition')


def verify_result(submitted, original_rows):
    reviews = []
    for profile in PROFILES:
        selected = [r for r in submitted if r['entity'] in entities(profile)]
        if selected:
            reviews.append(profile.verify_result(selected,original_rows))
    if len(reviews) == 1:
        return reviews[0]
    return {'profile':'expense-category-profiles','category_reviews':reviews,
        'requires_live_qualification':any(r['requires_live_qualification'] for r in reviews),
        'qualification':'category_extensions_live_pending','import_approved':False}
