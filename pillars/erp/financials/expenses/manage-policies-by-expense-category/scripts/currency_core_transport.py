"""Declared currenciesLOV GET only, existing managed cache, no login or retry."""
import importlib
from pathlib import Path
import sys
from currency_receipt import digest, origin
from environment_identity import same_environment
from currency_reference import request_plan

class CurrencyTransportError(ValueError):
    def __init__(self, failure_class, message):
        self.failure_class=failure_class
        super().__init__(message)

def core_get(repo, properties, binding):
    repo,properties=Path(repo),Path(properties)
    auth_path=repo/'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py'
    common_path=repo/'core/fusion-api/rest-api-client/scripts/rest_client_common.py'
    sys.path.insert(0,str(auth_path.parent));sys.path.insert(0,str(common_path.parent))
    auth=importlib.import_module('fusion_auth');common=importlib.import_module('rest_client_common')
    if Path(auth.__file__).resolve()!=auth_path.resolve() or Path(common.__file__).resolve()!=common_path.resolve():
        raise ValueError('Loaded currency core transport differs from selected repository')
    watched=[properties,auth_path,common_path,Path(__file__),Path(__file__).with_name('currency_reference.py')]
    hashes={p:digest(p) for p in watched}
    def unchanged():
        if any(digest(p)!=sha for p,sha in hashes.items()):
            raise ValueError('Currency profile or transport changed')
    try:
        props=auth.read_properties(properties)
        if not same_environment(props.get('environment'), binding['environment']) or origin(props.get('restBaseUrl'))!=origin(binding['origin']):
            raise CurrencyTransportError('input_validation','Currency profile differs from explicit target')
        unchanged()
        auth.authorized_token_authority(props)
        scoped=common.props_with_scope_property(props,'scope')
        token=auth.load_cached_access_token(scoped,auth.token_cache_path(scoped,'auto'))
        if not token:raise ValueError('cache unavailable')
        bound=auth.BoundAccessToken(token,auth.request_context(scoped));token=None
    except CurrencyTransportError:raise
    except Exception:
        raise CurrencyTransportError('auth_authz','Existing authorized currency token cache unavailable; authenticate through the separate workflow') from None
    def get(request,response):
        unchanged();response=Path(response)
        if response.exists() or response.is_symlink():raise ValueError('Currency response destination must be new')
        expected=request_plan(request.get('currency_code'),binding['as_of'],request.get('query',{}).get('offset'))
        if request!=expected:raise ValueError('Only the exact declared currency GET request is permitted')
        url=common.build_url(scoped,origin(binding['origin'])+request['path'],request['query'])
        try:
            content,headers,status=common.request_bytes(scoped,url,method='GET',access_token=bound,
                headers=request['headers'],json_body=None,timeout=20)
        except auth.FusionHttpError as error:
            raise CurrencyTransportError('auth_authz' if error.status_code in {401,403} else 'fusion_api',
                'Currency GET failed with HTTP '+str(error.status_code)+'; no login or retry attempted') from None
        except Exception:
            raise CurrencyTransportError('transport_environment','Currency GET transport failed; no retry attempted') from None
        unchanged()
        if status!=200:raise CurrencyTransportError('auth_authz' if status in {401,403} else 'fusion_api','Currency GET did not return HTTP200; no retry attempted')
        with response.open('xb') as stream:stream.write(content)
        return status
    return get
