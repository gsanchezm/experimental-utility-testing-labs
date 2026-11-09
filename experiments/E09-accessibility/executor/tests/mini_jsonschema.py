"""A deliberately small JSON Schema validator for the keywords used by schemas/run-manifest.schema.v2.json.

DRAFT (operation OP-PREP-E09). The sandbox has no jsonschema package; this validator implements only the keywords listed in
SUPPORTED and raises on any other keyword found in the schema, so that a schema feature this check does not cover is never
silently passed. The workflow validates the same file with Ajv (draft 2020-12) in CI.
"""
import re

SUPPORTED = {'$schema', '$id', 'title', 'description', 'type', 'enum', 'const', 'properties', 'required', 'additionalProperties',
             'items', 'minItems', 'uniqueItems', 'minLength', 'pattern', 'format', 'minimum', 'default', 'examples'}
DATE_TIME = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$')


def unsupported_keywords(schema, found=None):
    found = set() if found is None else found
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k not in SUPPORTED and k not in ('description',):
                found.add(k)
            if k in ('properties',) and isinstance(v, dict):
                for sub in v.values():
                    unsupported_keywords(sub, found)
            elif k == 'items' and isinstance(v, dict):
                unsupported_keywords(v, found)
            elif k == 'additionalProperties' and isinstance(v, dict):
                unsupported_keywords(v, found)
    return found


def _is_type(value, name):
    return {'string': isinstance(value, str), 'integer': isinstance(value, int) and not isinstance(value, bool),
            'number': isinstance(value, (int, float)) and not isinstance(value, bool), 'boolean': isinstance(value, bool),
            'null': value is None, 'object': isinstance(value, dict), 'array': isinstance(value, list)}[name]


def validate(value, schema, path='$'):
    """Return a list of error strings (empty when the value conforms)."""
    errors = []
    t = schema.get('type')
    if t is not None:
        names = t if isinstance(t, list) else [t]
        if not any(_is_type(value, n) for n in names):
            return [f'{path}: expected type {names}, got {type(value).__name__}']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: {value!r} not in enum')
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path}: {value!r} is not const {schema["const"]!r}')
    if isinstance(value, str):
        if 'minLength' in schema and len(value) < schema['minLength']:
            errors.append(f'{path}: shorter than minLength {schema["minLength"]}')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{path}: does not match pattern {schema["pattern"]}')
        if schema.get('format') == 'date-time' and not DATE_TIME.match(value):
            errors.append(f'{path}: not a date-time')
    if isinstance(value, (int, float)) and not isinstance(value, bool) and 'minimum' in schema and value < schema['minimum']:
        errors.append(f'{path}: below minimum {schema["minimum"]}')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for req in schema.get('required', []):
            if req not in value:
                errors.append(f'{path}: missing required {req}')
        addl = schema.get('additionalProperties', True)
        for k, v in value.items():
            if k in props:
                errors += validate(v, props[k], f'{path}.{k}')
            elif addl is False:
                errors.append(f'{path}: additional property {k} not allowed')
            elif isinstance(addl, dict):
                errors += validate(v, addl, f'{path}.{k}')
    if isinstance(value, list):
        if 'minItems' in schema and len(value) < schema['minItems']:
            errors.append(f'{path}: fewer than minItems {schema["minItems"]}')
        if schema.get('uniqueItems') and len({repr(v) for v in value}) != len(value):
            errors.append(f'{path}: items not unique')
        if 'items' in schema:
            for i, v in enumerate(value):
                errors += validate(v, schema['items'], f'{path}[{i}]')
    return errors
