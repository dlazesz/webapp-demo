import sys
from pathlib import Path

from yamale import make_schema, make_data, validate, YamaleError


def load_and_validate(schema_fname, fname, strict=True):
    # Load schema and data
    config_schema = make_schema(schema_fname)
    data = make_data(fname)

    # Validate
    try:
        validate(config_schema, data, strict)
    except YamaleError as e:
        for result in e.results:
            print('Error validating data {0} with {1}:'.format(result.data, result.schema), file=sys.stderr)
            for error in result.errors:
                print('', error, sep='\t', file=sys.stderr)
        exit(1)
    return data[0][0]


if __name__ == '__main__':
    repo_config = load_and_validate(Path(__file__).parent / 'config_schema.yaml',
                                    Path(__file__).parent / 'config.yaml')
