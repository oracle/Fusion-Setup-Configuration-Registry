"""Mileage rate resulting-state checks for the no-determinants input profile.

These checks do not qualify field operations or shared XML serialization.
Required add-on fields follow the Mileage UI upload validator; they are not
represented as independently demonstrated FSM import validators.
"""
from accepted_meals_profile import decimal_value, rate_date

P = 'ORA_EXM_MILEAGE_POLICY'
R = 'ORA_EXM_MILEAGE_LINE'
# MileagePolLineEO.AltKey, mapped through the exported service references.
IDENTITY = (P+'.PolicyName', 'AdditionalRateCode', 'CalculationMethodCode',
    'CurrencyCode', 'DistanceThreshold', 'EndDate', 'FuelType', 'GeoLocName',
    'PassengerThreshold', 'RoleName', 'StartDate', 'TypeOfRateCode',
    'VehicleCategory', 'VehicleType', 'ZoneCode', 'GenderCode')
DETERMINANTS = ('DistanceThreshold', 'FuelType', 'GeoLocName', 'RoleName',
    'VehicleCategory', 'VehicleType', 'ZoneCode', 'GenderCode', 'RoleCode',
    'RawCity', 'RawCountry', 'RawCounty', 'RawState')


def validate_rate(row, parent, *, require_amount=True, validate_applicability=True):
    """Validate the complete proposed row against its resolved owning policy."""
    if not parent.get('PolicyName') or row.get(P+'.PolicyName') != parent['PolicyName']:
        raise ValueError('Mileage rate requires its exact owning policy')
    if parent.get('CurrencyOptionCode') != 'SINGLE' or not parent.get('CurrencyCode'):
        raise ValueError('Mileage reduced rates require an explicit single-currency parent')
    for field in ('EnabledRoleFlag','EnabledLocationFlag','DistanceThresholdFlag',
                  'EnabledVehCategoryFlag','EnabledVehTypeFlag','EnabledFuelTypeFlag','EnabledGenderFlag'):
        if parent.get(field) not in ('N','',None):
            raise ValueError('Mileage reduced rates cannot use an enabled or unresolved parent determinant: '+field)
    if row.get('CurrencyCode') not in ('', None):
        raise ValueError('Mileage child currency is not derived from parent display')
    if any(row.get(f) not in ('', None) for f in DETERMINANTS):
        raise ValueError('Mileage rate determinants are outside the initial input profile')
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Mileage rate status is outside the initial input profile')
    if require_amount and decimal_value(row.get('Rate',''), 'Mileage Rate') is None:
        raise ValueError('Mileage Rate requires an explicit finite nonnegative amount')
    start=rate_date(row.get('StartDate',''),'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'],'EndDate') < start:
        raise ValueError('Mileage EndDate must be on or after StartDate')
    kind=row.get('TypeOfRateCode')
    if kind not in {'MILEAGE','PASSENGER','ADDITIONAL'}:
        raise ValueError('Mileage requires an explicit supported Rate Kind')
    if kind in {'PASSENGER','ADDITIONAL'} and not row.get('CalculationMethodCode'):
        raise ValueError('Mileage passenger and company-specific rates require Calculation Method')
    if row.get('CalculationMethodCode') and row['CalculationMethodCode'] not in {'AMOUNT','PERCENTAGE'}:
        raise ValueError('Mileage Calculation Method must use an EXM_CALCULATION_METHOD package code')
    if validate_applicability and kind=='PASSENGER' and parent.get('EnabledPassengerFlag')!='Y':
        raise ValueError('Mileage passenger rate requires the resolved parent passenger option enabled')
    if kind=='ADDITIONAL':
        if validate_applicability and (parent.get('EnabledAdditnlRatesFlag')!='Y' or not parent.get('AdditionalRatesListCode')):
            raise ValueError('Mileage company-specific rate requires the resolved parent option and lookup type')
        if not row.get('AdditionalRateCode'):
            raise ValueError('Mileage company-specific rate requires Company-Specific Rate Code')
    elif row.get('AdditionalRateCode'):
        raise ValueError('Company-Specific Rate Code applies only to company-specific rates')
    threshold=row.get('PassengerThreshold')
    if threshold not in ('',None):
        if kind!='PASSENGER':
            raise ValueError('Passenger range applies only to passenger rates')
        try:
            if not isinstance(threshold,str):
                raise ValueError()
            value=int(threshold)
        except (TypeError,ValueError):
            raise ValueError('Passenger range must be an integer') from None
        if value!=-1 and not 1<=value<=999:
            raise ValueError('Passenger range must be 1 through 999, or -1 for the upper-limit row')
