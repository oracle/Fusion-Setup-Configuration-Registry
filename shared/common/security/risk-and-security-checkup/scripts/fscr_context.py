"""Resolve non-secret environment provenance with FSCR's shared configuration reader.

This helper never authenticates, reads token caches, or calls Fusion.
"""
import importlib.util
from pathlib import Path
import sys
from urllib.parse import urlsplit

REPOSITORY = Path(__file__).resolve().parents[5]
DEFAULT_PROPERTIES = REPOSITORY / 'core/auth/fusionEnv.properties'


def environment_from_properties(properties=None):
    path = Path(properties) if properties is not None else DEFAULT_PROPERTIES
    module_path = REPOSITORY / 'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py'
    spec = importlib.util.spec_from_file_location('_rsc_fscr_auth', module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    props = module.read_properties(path)
    module.require_props(props, ['environment', 'restBaseUrl'])
    parsed = urlsplit(props['restBaseUrl'])
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment):
        raise ValueError('FSCR restBaseUrl must be an HTTPS URL without credentials, query, or fragment')
    # Use the configured origin, not a potentially nonunique environment label,
    # to prevent an assessment/catalog from crossing environments.
    host = parsed.hostname.lower()
    host = '[' + host + ']' if ':' in host else host
    port = parsed.port
    return 'https://' + host + (':' + str(port) if port not in (None, 443) else '')


def bind_request(request, properties=None):
    if not isinstance(request, dict):
        raise ValueError('Request must be an object')
    if 'applicationUser' in request:
        raise ValueError('Remove applicationUser from assessment input; FSCR core services manage authentication')
    environment = environment_from_properties(properties)
    if 'environment' in request and request['environment'] != environment:
        raise ValueError('Assessment environment does not match the selected FSCR configuration')
    return dict(request, environment=environment)
