from core_lib.helpers.shell_utils import input_str, input_int


def generate_solr_template() -> dict:
    solr_protocol = input_str('Enter solr protocol (http/https)', 'https')
    solr_port = input_int('Enter solr port no.', 8983)
    solr_host = input_str('Enter solr host', 'localhost')
    solr_file = input_str('Enter solr file name (solr/core_name)', 'solr/mycore')
    print(f'Solr on {solr_host}:{solr_port}')
    return {
        'env': {
            'SOLR_HOST': solr_host,
            'SOLR_PORT': solr_port,
        },
        'config': {
            'url': {
                'protocol': solr_protocol,
                'host': f'${{oc.env:SOLR_HOST}}',
                'port': f'${{oc.env:SOLR_PORT}}',
                'file': solr_file,
            },
        },
    }
