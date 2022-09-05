import ocpa.visualization.log.variants.versions.chevron_sequences as chevron_sequences


CHEVRON_SEQUENCES = "chevron_sequences"

VERSIONS = {
    CHEVRON_SEQUENCES: chevron_sequences.apply
}

def apply(obj, variant=CHEVRON_SEQUENCES, parameters ={}):
    '''
    Provides a variant layouting.

    :param obj: variant graph
    :type obj: nx.DiGraph

    :param variant: layouting algorithm, default = :func:`Chevron sequences <ocpa.visualization.log.variants.versions.chevron_sequences.apply>`
    :type variant: func

    :param parameters: parameter dictionary
    :type parameters: dict

    :return: variant layout
    :rtype:Tuple()

    '''
    return VERSIONS[variant](obj, parameters)