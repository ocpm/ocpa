import ocpa.visualization.log.variants.versions.chevron_sequences as chevron_sequences


CHEVRON_SEQUENCES = "chevron_sequences"

VERSIONS = {
    CHEVRON_SEQUENCES: chevron_sequences.apply
}

def apply(obj, variant=CHEVRON_SEQUENCES, parameters ={}):
    return VERSIONS[variant](obj, parameters)